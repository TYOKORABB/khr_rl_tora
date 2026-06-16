# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Reinforcement-learning code that trains a **bipedal walking policy for the Kondo KHR-3HV
humanoid** (12-DOF, legs only) in the **Genesis** physics simulator using **PPO** from
**rsl-rl-lib (>= 5.0.0)**. The `khr_*` scripts were adapted from the Genesis Unitree Go2
locomotion example.

This is a university graduation thesis. It builds on a senior lab member's prior work, which
already implemented both the Genesis sim-RL pipeline and **real-robot walking on the physical
KHR-3HV**. The real-robot path communicates with the hardware via **Meridian Console** (not
part of this repo). The specific thesis contribution is still being refined — ask the user
before assuming the end goal.

## Repository layout caveat

The git repository is **this directory (`khr_rl_tora/`)**, remote
`github.com/TYOKORABB/khr_rl_tora.git`. Its parent (the Claude Code launch directory,
`KajitaLab/`) is **not** version-controlled — make changes and run git inside `khr_rl_tora/`.

## Environment & prerequisites

- **Training needs a CUDA GPU machine.** `khr_train.py` calls `gs.init(backend=gs.gpu)`. The
  development Mac here (Apple Silicon, no CUDA) is for **editing and CPU eval only** — it
  cannot run training.
- The robot assets `../assets/khr3hv/urdf/*.urdf` (e.g. `khr3hv_12dof.urdf`) are referenced
  relative to the script's working dir but are **kept on the GPU machine, intentionally not in
  this repo**. Nothing here runs without them present at `../assets/khr3hv/`.
- `urdf/plane/plane_light.urdf` and `urdf/plane/plane.urdf` are Genesis built-in assets.

## Commands

Run from inside `khr_rl_tora/` (use `python` / `python3` as appropriate for the GPU machine):

```bash
# Train (headless, GPU). Writes checkpoints + TensorBoard to logs/<exp_name>/.
python khr_train.py -e khr-walking -B 4096 -I 101 --seed 1
python khr_train.py --view          # same, but opens the Genesis viewer to watch env 0

# Evaluate / play a checkpoint in the viewer (CPU). Loads logs/<exp>/model_<ckpt>.pt.
python khr_eval.py -e khr-walking --ckpt 100

# PD-control sanity check of the URDF (standalone; plots joint angle & torque).
python pd_test.py

# Watch training curves.
tensorboard --logdir logs
```

CLI flags: `khr_train.py` → `-e/--exp_name -B/--num_envs -I/--max_iterations --seed --view`;
`khr_eval.py` → `-e/--exp_name --ckpt/-I`.

Note: `khr_train.py` **deletes and recreates** `logs/<exp_name>/` on every run — copy out any
checkpoints you want to keep before re-training with the same `exp_name`.

## Architecture

- **`khr_env.py`** — `KHREnv`, the core Genesis environment. Builds the scene, loads the KHR
  URDF, runs **PD position control** (`kp=25, kd=0.5`, `action_scale=0.25`, control dt=0.02 /
  50 Hz). Produces a **71-dim observation** (`num_obs=71`) for the actor plus a separate
  **privileged observation** for the critic (asymmetric actor-critic). Computes gait-phase
  signals (`sin/cos_phase`, `leg_phase`), applies **domain randomization** (base mass,
  friction, COM shift, optional kp), and defines all reward terms.
- **`khr_train.py`** — training entry point and the single source of hyperparameters:
  `get_cfgs()` returns the four config dicts; `get_train_cfg()` returns the PPO + network
  config (MLP `[128,64,32]`, `elu`, `obs_groups` mapping actor→`policy`, critic→
  `policy`+`privileged`). Pickles all configs to `logs/<exp>/cfgs.pkl`; logs to TensorBoard.
- **`khr_eval.py`** — loads `logs/<exp>/cfgs.pkl` and `model_<ckpt>.pt`, then runs the
  inference policy in the viewer (CPU backend), reward scales zeroed.
- **`pd_test.py`** — standalone PD-control test of the URDF; not part of the RL loop.
- **`go2_env.py` / `go2_train.py` / `go2_eval.py`** — the upstream Genesis Go2 example, kept as
  a reference baseline. **Not imported** by the `khr_*` scripts; edit the `khr_*` files.

### Config flow

Four dicts — `env_cfg`, `obs_cfg`, `reward_cfg`, `command_cfg` — are threaded through the env
and are the main tuning surface. They are created in `khr_train.py:get_cfgs()`, **pickled** to
`logs/<exp>/cfgs.pkl` at train time, and **unpickled** by `khr_eval.py` so eval matches
training exactly. Change hyperparameters in `get_cfgs()` / `get_train_cfg()`, not in the env.

## Conventions when editing

- **Add a reward** by defining `KHREnv._reward_<name>(self) -> Tensor[num_envs]` and adding
  `"<name>": <scale>` to `reward_cfg["reward_scales"]`. Reward functions are auto-discovered
  by name (`getattr(self, "_reward_" + name)`); a scale entry with no matching method (or vice
  versa) will break. Scales are multiplied by `dt` once at init.
- **Observation layout is order- and size-sensitive.** If you change `_update_observation()`,
  keep it consistent with `num_obs=71`, with `commands_scale`, and with the indices in
  `_prepare_obs_noise()` (which hard-codes obs slice positions for noise injection).
- `logs/` and `*.mp4` are gitignored (see `.gitignore` bottom) — checkpoints and recordings
  are not tracked.

## GitHub workflow

This repo is actively managed on GitHub. **Commit and push changes frequently** with concise,
descriptive messages so progress is recorded. The history is **direct-to-`main`** (no PR
flow); follow that pattern unless the user asks otherwise.
