"""rsl-rl 5.4.0 の PPO に「行動の平均が ±bound を超えた分の 2 乗」の罰（bound loss）を足したもの（getup-v2 の候補 1、2026-10-14）。

getup-v1 では行動の平均が 9 割の時間 ±1 の外にあり（行動は ±1 で切るので、外に出すと探索のゆらぎが効かない）、
エントロピーの項で std が 0.30 → 0.92 と増え続け、決定的な方策がゆらぎつきより 7 pt 低かった（getup/DIARY.md）。
三宅さんの設定（rl_games の bounds_loss_coef 0.001）と同じ考え方で、平均を ±1 の内側に戻す。

update() は rsl-rl 5.4.0 の PPO.update をそのまま写し、「# getup-v2」の印の行だけを足した
（rsl-rl の update には損失に項を足す口がないため）。版が違うと写した中身と食い違うので、5.4.0 以外では止める。
TensorBoard の Loss/bound・Loss/mu_outside_frac に記録される。

使い方（学習の設定）: "algorithm": {"class_name": "getup.ppo_bound:PPOBound", "bound_loss_coef": 0.01, "bound": 1.0, ...}
"""

from __future__ import annotations

from importlib import metadata

import torch
import torch.nn as nn

from rsl_rl.algorithms.ppo import PPO

_RSL_RL_VERSION = "5.4.0"
if metadata.version("rsl-rl-lib") != _RSL_RL_VERSION:
    raise ImportError(f"getup.ppo_bound は rsl-rl-lib {_RSL_RL_VERSION} の PPO.update を写している（今は {metadata.version('rsl-rl-lib')}）。写し直すこと")


class PPOBound(PPO):
    def __init__(self, *args, bound_loss_coef: float = 0.01, bound: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.bound_loss_coef = float(bound_loss_coef)
        self.bound = float(bound)

    def update(self) -> dict[str, float]:
        """Run optimization epochs over stored batches and return mean losses."""
        mean_value_loss = 0
        mean_surrogate_loss = 0
        mean_entropy = 0
        mean_bound_loss = 0.0  # getup-v2
        mean_mu_outside = 0.0  # getup-v2
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
        }
        if self.rnd:
            loss_dict["rnd"] = mean_rnd_loss
        if self.symmetry:
            loss_dict["symmetry"] = mean_symmetry_loss

        # Clear the storage
        self.storage.clear()

        return loss_dict
