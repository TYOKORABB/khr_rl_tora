# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Reinforcement-learning code for the Kondo KHR-3HV humanoid in the **Genesis** physics simulator using
**PPO** from **rsl-rl-lib (>= 5.0.0)**. The thesis work is **quadruped walking** (all 22 joints, arms as
front legs; `quad/`, current best v31) and its Sim2Real over Meridian (`real/`), plus a get-up task
(`getup/`). The original **bipedal** baseline (12-DOF legs, from `khr_rl_sample`) is kept in `biped/`.

This is a university graduation thesis. It builds on a senior lab member's prior work, which
already implemented both the Genesis sim-RL pipeline and **real-robot walking on the physical
KHR-3HV**. The real-robot path communicates with the hardware via **Meridian Console** (not
part of this repo). The specific thesis contribution is still being refined — ask the user
before assuming the end goal.

## Repository layout caveat

The git repository is **this directory (`khr_rl_tora/`)**, remote
`github.com/TYOKORABB/khr_rl_tora.git`. Its parent (the Claude Code launch directory,
`KajitaLab/`) is **not** version-controlled — make changes and run git inside `khr_rl_tora/`.

## Where things are (reorganized 2026-10-14; `README.md` has the full map)

| Path | Contents |
|---|---|
| `docs/` | `DevelopmentDiary_v2.md` (rebuilt main record, 2026-10-14; read first), `DevelopmentDiary.md` (original log 07-24..10-14), `GetUpSim2RealPlan.md`, `ResearchPlan.md`, `RewardReference.md`, `RealRobotVerification.md` |
| `quad/` | Quadruped walking v16–v31: `khr_quad_env*.py`, `khr_train_quad*.py`, `khr_quad_record*.py`, measurement and URDF-fix tools. **Flat on purpose**: the files import each other by bare module name, so they must share one directory. `quad/jobs/` = cron-style shell jobs, `quad/archive_v1_v15/` = v1–v15 |
| `biped/` | Original bipedal baseline (`khr_env.py`, `khr_train.py`, `khr_eval.py`, `pd_test.py`, Eureka experiment) |
| `go2_reference/` | Upstream Genesis Go2 example (reference only, not imported) |
| `khr_common/`, `real/`, `sysid/`, `getup/` | Shared Genesis-free code / real robot / sim-vs-real / get-up (run as `python -m <pkg>.<name>`) |
| `experiments/` | Research records (git-tracked). `logs/` = checkpoints (gitignored). `media/` = plots and videos |

Always run from the repo root (`cd khr_rl_tora`): URDFs are read as `../assets/...` relative to the working directory,
so run scripts as `python quad/khr_train_quad31.py`, not from inside `quad/`. Importing `khr_common.paths` puts `quad/`
(and the v1–v15 archive) on `sys.path`, which is how `real/`, `sysid/`, `getup/` load `khr_quad_env21` etc.

## Sibling repos and push rules (2026-10-14)

The workspace map (repos, exact versions, Python setup, PC specs) is `TYOKORABB/khr-workspace` (`../khr-workspace/`).
`../Genesis`, `../Meridian_LITE`, `../Meridian_consoleS` are forked to TYOKORABB: their `origin` (s-kajita) push URL is disabled
and the fork is the remote `tora` (branches `khr-v0.4.6`, `khr-getup.4`, `khr-quad`). Push only to TYOKORABB repos; never to s-kajita.
`../assets` (s-kajita/khr3hv, private) is not uploaded anywhere.

## Environment & prerequisites

- **Training needs a CUDA GPU machine.** The training scripts call `gs.init(backend=gs.gpu)`. The
  development Mac here (Apple Silicon, no CUDA) is for **editing and CPU eval only** — it
  cannot run training.
- The robot assets `../assets/khr3hv/urdf/*.urdf` (e.g. `khr3hv_12dof.urdf`) are referenced
  relative to the script's working dir but are **kept on the GPU machine, intentionally not in
  this repo**. Nothing here runs without them present at `../assets/khr3hv/`.
- `urdf/plane/plane_light.urdf` and `urdf/plane/plane.urdf` are Genesis built-in assets.

## Commands

Run from inside `khr_rl_tora/` (use `python` / `python3` as appropriate for the GPU machine):

```bash
# Quadruped (current work). Writes checkpoints + TensorBoard to logs/<exp_name>/.
python quad/khr_train_quad31.py -e khr-quadruped31-s1 -B 4096 -I 4000 --seed 1
python quad/khr_quad_eval_metrics.py -e khr-quadruped31-s1 --env khr_quad_env21 --ckpt 3999 -n 128
DISPLAY=:1 python quad/khr_quad_record21.py -e khr-quadruped31-s1 --ckpt 3999 --vx 0.3 -o walk.mp4

# Bipedal baseline (biped/).
python biped/khr_train.py -e khr-walking -B 4096 -I 101 --seed 1
python biped/khr_train.py --view    # same, but opens the Genesis viewer to watch env 0
python biped/khr_eval.py -e khr-walking --ckpt 100   # viewer (CPU)
python biped/pd_test.py             # PD-control sanity check of the URDF

# Watch training curves.
tensorboard --logdir logs
```

CLI flags: `biped/khr_train.py` → `-e/--exp_name -B/--num_envs -I/--max_iterations --seed --view`;
`biped/khr_eval.py` → `-e/--exp_name --ckpt/-I`.

Note: the training scripts **delete and recreate** `logs/<exp_name>/` on every run — copy out any
checkpoints you want to keep before re-training with the same `exp_name`.
Viewer replay: `python quad/khr_quad_eval.py -e <exp> --ckpt <n> --env <env module>` (any version; `--headless --steps N` to check without a window).
New training scripts (quad v32+) must call `save_code_state(log_dir)` (`quad/run_record.py` → `khr_common/run_record.py`) right after
creating `logs/<exp>/`; `getup/train_getup1.py` already does. Policies that ran on the robot are frozen in `real/policies/` (model, cfgs, SHA-256).

## Architecture (bipedal baseline, `biped/`)

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

## Get-up / Sim2Real work (2026-10, `docs/GetUpSim2RealPlan.md`)

Run everything from the repo root as modules (`python -m <pkg>.<name>`); paths resolve via `khr_common/paths.py`.

- `khr_common/` — Genesis-free code shared by sim and the real-robot tools (joint map, IMU gravity, action post-processing,
  height estimate by forward kinematics).
- `real/` — real-robot tools over Meridian (firmware patches, `walk_session.py` deployer, IMU/latency checks). `real/ROBOT_STATUS.md`
  is the robot checklist. Never commit `keys.h`, `board_ip.txt`, raw logs, or flash backups.
- `sysid/` — sim-vs-real comparison of recorded walks (closed-loop sweeps, segment replay E4a). Results in `experiments/sysid/`.
- `getup/` — get-up task: `precheck/`, `tools/make_getup_urdf.py` (writes a derived URDF to `../assets`, not committed),
  `gen_init_states.py` (initial-state bank, committed under `getup/data/banks/`), `envs/getup_env1.py`, `train_getup1.py`.
  Version history in `getup/DIARY.md`. After training, verify with `python -m getup.eval_getup -e <exp>` (or `getup/jobs/train_eval.sh <exp> <seed> <iter>`
  for train → verify): **the user wants a video of the motion every time a policy is verified** (eval_getup always records per-level MP4s to `media/videos/getup/`).
  The quadruped retrain queue (`quad/jobs/run_retrain_fixurdf.sh`) finished on 2026-10-14 and its cron line is commented out;
  if it is ever re-enabled, do not start other GPU training while it runs.

## GitHub workflow

This repo is actively managed on GitHub. **Commit and push changes frequently** with concise,
descriptive messages so progress is recorded. The history is **direct-to-`main`** (no PR
flow); follow that pattern unless the user asks otherwise.
