"""PPOBound（getup/ppo_bound.py）に、方策の平均の目標角が周期ごとに跳ぶことへの罰（CAPS の時間の項）を足したもの（2026-11-21）。

段階 0b の方策は目標角が 9 割の周期で速さの制限に当たっていた（experiments/unified/saturation/README.md）。
報酬で「制限の前の目標角」の変化を罰した unified0r は、std 0.5 の探索のゆらぎ（目標角で約 0.5 rad、v31 の約 25 倍）が罰に入り、
方策が行動の平均を ±1 の外に張りつけて崩れた。そこで、ゆらぎの入らない方策の平均（決定的な出力）だけを損失で罰する。
本人（11/21）:「止めて平均だけ罰する（勧め）」。

  CAPS（Mysore ら 2021, "Regularizing Action Policies for Smooth Control with Reinforcement Learning"）の時間の項を、目標角の単位にしたもの:
    L_T = 平均_{(t, t+1)} 平均_関節 ((r(μ(s_t)) − r(μ(s_{t+1}))) / δ)²
    r(μ) = s₊ · max(μ, 0) + s₋ · min(μ, 0)   （ActionPost の写像から公称を引いたもの。±1 で切らない: 切ると外で勾配が消えるため）
    δ = 0.06 rad（速さの制限）。L_T = 1 は「平均の目標角が毎周期ちょうど制限の分だけ動く」に当たる。
  (s_t, s_{t+1}) は集めた 24 周期の中の続く 2 周期で、間にリセットを挟まないもの（dones[t] = 0）。ミニバッチごとに 8192 組を引く。
  損失 = PPOBound の損失 + caps_coef · L_T。

update() は PPOBound.update（rsl-rl 5.4.0 の PPO.update の写し）を写し、「# unified-0c」の印の行だけを足した。
s₊・s₋ は学習の前に set_caps_post(env.post) で渡す。TensorBoard の Loss/caps・Loss/caps_step_rad に記録される。
"""

from __future__ import annotations

import torch
import torch.nn as nn

from getup.ppo_bound import PPOBound


class PPOCaps(PPOBound):
    def __init__(self, *args, caps_coef: float = 0.1, caps_delta: float = 0.06, caps_pairs: int = 8192, **kwargs):
        super().__init__(*args, **kwargs)
        self.caps_coef = float(caps_coef)
        self.caps_delta = float(caps_delta)
        self.caps_n = int(caps_pairs)
        self.s_plus = None
        self.s_minus = None

    def set_caps_post(self, post) -> None:
        """ActionPost から写像の倍率 s₊・s₋ を受け取る（関節ごと）。"""
        self.s_plus = torch.as_tensor(post.s_plus, dtype=torch.float32, device=self.device)
        self.s_minus = torch.as_tensor(post.s_minus, dtype=torch.float32, device=self.device)

    def _caps_pairs(self):
        if self.s_plus is None:
            raise RuntimeError("PPOCaps: 学習の前に set_caps_post(env.post) を呼ぶこと")
        st = self.storage
        T, N = st.dones.shape[0], st.dones.shape[1]
        ok = st.dones[:-1, :, 0] == 0                       # t と t+1 の間にリセットがない
        t_idx, n_idx = torch.nonzero(ok, as_tuple=True)
        obs = st.observations.flatten(0, 1)                  # [(T·N)]
        return obs, t_idx * N + n_idx, (t_idx + 1) * N + n_idx

    def _caps_loss(self, obs, i0, i1):
        k = min(self.caps_n, i0.numel())
        sel = torch.randint(0, i0.numel(), (k,), device=i0.device)
        m0 = self.actor(obs[i0[sel]])                       # 決定的な出力（平均）
        m1 = self.actor(obs[i1[sel]])
        r0 = self.s_plus * m0.clamp(min=0.0) + self.s_minus * m0.clamp(max=0.0)
        r1 = self.s_plus * m1.clamp(min=0.0) + self.s_minus * m1.clamp(max=0.0)
        d = r0 - r1
        return ((d / self.caps_delta) ** 2).mean(), d.detach().abs().mean().item()

    def update(self) -> dict[str, float]:
        """Run optimization epochs over stored batches and return mean losses."""
        mean_value_loss = 0
        mean_surrogate_loss = 0
        mean_entropy = 0
        mean_bound_loss = 0.0  # getup-v2
        mean_mu_outside = 0.0  # getup-v2
        mean_caps = 0.0  # unified-0c
        mean_caps_step = 0.0  # unified-0c
        pairs = self._caps_pairs() if self.caps_coef > 0 else None  # unified-0c
        # RND loss
        mean_rnd_loss = 0 if self.rnd else None
        # Symmetry loss
        mean_symmetry_loss = 0 if self.symmetry else None

        # Get mini-batch generator
        if self.actor.is_recurrent or self.critic.is_recurrent:
            generator = self.storage.recurrent_mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)
        else:
            generator = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)

        # Iterate over mini-batches
        for batch in generator:
            original_batch_size = batch.observations.batch_size[0]

            # Check if we should normalize advantages per mini-batch
            if self.normalize_advantage_per_mini_batch:
                with torch.no_grad():
                    batch.advantages = (batch.advantages - batch.advantages.mean()) / (batch.advantages.std() + 1e-8)  # type: ignore

            # Perform symmetric augmentation if enabled
            if self.symmetry:
                self.symmetry.augment_batch(batch, original_batch_size)

            # Recompute actions log prob and entropy for current batch of transitions
            # Note: We need to do this because we updated the policy with new parameters
            self.actor(
                batch.observations,
                masks=batch.masks,
                hidden_state=batch.hidden_states[0],
                stochastic_output=True,
            )
            actions_log_prob = self.actor.get_output_log_prob(batch.actions)  # type: ignore
            values = self.critic(batch.observations, masks=batch.masks, hidden_state=batch.hidden_states[1])
            # Note: We only keep the following tensors for the original samples in case of symmetry augmentation
            distribution_params = tuple(p[:original_batch_size] for p in self.actor.output_distribution_params)
            entropy = self.actor.output_entropy[:original_batch_size]

            # Compute KL divergence and adapt the learning rate
            if self.desired_kl is not None and self.schedule == "adaptive":
                with torch.inference_mode():
                    kl = self.actor.get_kl_divergence(batch.old_distribution_params, distribution_params)  # type: ignore
                    kl_mean = torch.mean(kl)

                    # Reduce the KL divergence across all GPUs
                    if self.is_multi_gpu:
                        torch.distributed.all_reduce(kl_mean, op=torch.distributed.ReduceOp.SUM)
                        kl_mean /= self.gpu_world_size

                    # Update the learning rate only on the main process
                    if self.gpu_global_rank == 0:
                        if kl_mean > self.desired_kl * 2.0:
                            self.learning_rate = max(1e-5, self.learning_rate / 1.5)
                        elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
                            self.learning_rate = min(1e-2, self.learning_rate * 1.5)

                    # Update the learning rate for all GPUs
                    if self.is_multi_gpu:
                        lr_tensor = torch.tensor(self.learning_rate, device=self.device)
                        torch.distributed.broadcast(lr_tensor, src=0)
                        self.learning_rate = lr_tensor.item()

                    # Update the learning rate for all parameter groups
                    for param_group in self.optimizer.param_groups:
                        param_group["lr"] = self.learning_rate

            # Surrogate loss
            ratio = torch.exp(actions_log_prob - torch.squeeze(batch.old_actions_log_prob))  # type: ignore
            surrogate = -torch.squeeze(batch.advantages) * ratio  # type: ignore
            surrogate_clipped = -torch.squeeze(batch.advantages) * torch.clamp(  # type: ignore
                ratio, 1.0 - self.clip_param, 1.0 + self.clip_param
            )
            surrogate_loss = torch.max(surrogate, surrogate_clipped).mean()

            # Value function loss
            if self.use_clipped_value_loss:
                value_clipped = batch.values + (values - batch.values).clamp(-self.clip_param, self.clip_param)
                value_losses = (values - batch.returns).pow(2)
                value_losses_clipped = (value_clipped - batch.returns).pow(2)
                value_loss = torch.max(value_losses, value_losses_clipped).mean()
            else:
                value_loss = (batch.returns - values).pow(2).mean()

            loss = surrogate_loss + self.value_loss_coef * value_loss - self.entropy_coef * entropy.mean()

            # ---- getup-v2 で足した項: 行動の平均が ±bound を超えた分の 2 乗（rl_games の bound loss と同じ考え方） ----
            mu = self.actor.output_mean[:original_batch_size]
            bound_loss = ((mu - self.bound).clamp(min=0.0) ** 2 + (mu + self.bound).clamp(max=0.0) ** 2).sum(dim=-1).mean()
            loss = loss + self.bound_loss_coef * bound_loss
            mean_bound_loss += bound_loss.item()
            mean_mu_outside += (mu.abs() > self.bound).float().mean().item()

            # RND loss
            rnd_loss = self.rnd.compute_loss(batch.observations[:original_batch_size]) if self.rnd else None  # type: ignore

            # Symmetry loss
            if self.symmetry:
                symmetry_loss = self.symmetry.compute_loss(self.actor, batch, original_batch_size)
                if self.symmetry.use_mirror_loss:
                    loss = loss + self.symmetry.mirror_loss_coeff * symmetry_loss

            # ---- unified-0c で足した項: 方策の平均の目標角が続く 2 周期で跳ぶ分（CAPS の時間の項） ----
            if pairs is not None:
                caps, caps_step = self._caps_loss(*pairs)
                loss = loss + self.caps_coef * caps
                mean_caps += caps.item()
                mean_caps_step += caps_step

            # Compute the gradients for PPO
            self.optimizer.zero_grad()
            loss.backward()
            # Compute the gradients for RND
            if self.rnd:
                self.rnd.optimizer.zero_grad()
                rnd_loss.backward()

            # Collect gradients from all GPUs
            if self.is_multi_gpu:
                self.reduce_parameters()

            # Apply the gradients for PPO
            nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
            nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
            self.optimizer.step()
            # Apply the gradients for RND
            if self.rnd:
                self.rnd.optimizer.step()

            # Store the losses
            mean_value_loss += value_loss.item()
            mean_surrogate_loss += surrogate_loss.item()
            mean_entropy += entropy.mean().item()
            # RND loss
            if mean_rnd_loss is not None:
                mean_rnd_loss += rnd_loss.item()
            # Symmetry loss
            if mean_symmetry_loss is not None:
                mean_symmetry_loss += symmetry_loss.item()

        # Divide the losses by the number of updates
        num_updates = self.num_learning_epochs * self.num_mini_batches
        mean_value_loss /= num_updates
        mean_surrogate_loss /= num_updates
        mean_entropy /= num_updates
        mean_bound_loss /= num_updates  # getup-v2
        mean_mu_outside /= num_updates  # getup-v2
        mean_caps /= num_updates  # unified-0c
        mean_caps_step /= num_updates  # unified-0c
        if mean_rnd_loss is not None:
            mean_rnd_loss /= num_updates
        if mean_symmetry_loss is not None:
            mean_symmetry_loss /= num_updates

        # Construct the loss dictionary
        loss_dict = {
            "value": mean_value_loss,
            "surrogate": mean_surrogate_loss,
            "entropy": mean_entropy,
            "bound": mean_bound_loss,  # getup-v2
            "mu_outside_frac": mean_mu_outside,  # getup-v2（行動の平均が ±bound の外にある割合）
            "caps": mean_caps,  # unified-0c（係数を掛ける前）
            "caps_step_rad": mean_caps_step,  # unified-0c（方策の平均の目標角の 1 周期の変化の平均 [rad]）
        }
        if self.rnd:
            loss_dict["rnd"] = mean_rnd_loss
        if self.symmetry:
            loss_dict["symmetry"] = mean_symmetry_loss

        # Clear the storage
        self.storage.clear()

        return loss_dict
