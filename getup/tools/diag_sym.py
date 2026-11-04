"""sym の 3 シードの止まり方（2026-11-05、判定には使わない）: u0 < 0.5 の評価用の状態から 8 秒後に、どちらの体側で止まるかを数える。

  python getup/tools/diag_sym.py experiments/getup/eval/diag_sym.json   # GPU、約 3 分（リポジトリの根で PYTHONPATH=. をつけて実行）
"""
import json,pickle,importlib,sys
import numpy as np
from khr_common.paths import EXPERIMENT_ROOT, LOG_ROOT, chdir_repo_root
chdir_repo_root()
import genesis as gs, torch
from rsl_rl.runners import OnPolicyRunner
gs.init(backend=gs.gpu,precision="32",logging_level="warning",seed=0,performance_mode=True)
out={}
for exp in ["getup9-sym-s1","getup9-sym-s2","getup9-sym-s3"]:
    env_cfg,obs_cfg,reward_cfg,tc=pickle.load(open(LOG_ROOT/exp/"cfgs.pkl","rb"))
    if exp.endswith("s1"):
        GE=importlib.import_module(env_cfg["env_module"]).GetupEnv
        b=torch.load(env_cfg["bank"],map_location="cpu")
        idx=torch.nonzero(b["eval"]&(b["u0"]<0.5)).flatten()
        env=GE(len(idx),env_cfg,obs_cfg,reward_cfg,eval_mode=True,level=len(env_cfg["curriculum"]["levels"])-1)
    r=OnPolicyRunner(env,tc,None,device=gs.device); r.load(str(LOG_ROOT/exp/"model_2999.pt")); pol=r.get_inference_policy(device=gs.device)
    torch.manual_seed(0)
    pool=idx.to(gs.device)
    obs=env.force_reset(pool,len(env.levels)-1)
    T=env.max_episode_length-1
    umax=torch.full((len(idx),),-2.0,device=gs.device); suc=torch.zeros(len(idx),dtype=torch.bool,device=gs.device)
    with torch.no_grad():
        for t in range(T):
            obs,_,done,_=env.step(pol(obs)); umax=torch.maximum(umax,env.u); suc|=env.ep_success
    u=env.u.cpu().numpy(); gy=env.gravity[:,1].cpu().numpy(); s=suc.cpu().numpy(); u0=b["u0"][idx].numpy(); limp=b["limp"][idx].numpy()
    st=(~s)&(u<0.7)
    gy0=None
    d=dict(n=len(idx),success=float(s.mean()),stuck=float(st.mean()),stuck_left=float((st&(gy>0.3)).mean()),stuck_right=float((st&(gy<-0.3)).mean()),stuck_other=float((st&(abs(gy)<=0.3)).mean()),
           u_end_stuck_median=float(np.median(u[st])) if st.any() else None,gy_abs_stuck_median=float(np.median(abs(gy[st]))) if st.any() else None,
           success_chestup=float(s[u0<0].mean()),success_side_limp=float(s[(u0>=0)&limp].mean()))
    out[exp]=d; print(exp,{k:(round(v,3) if isinstance(v,float) else v) for k,v in d.items()},flush=True)
json.dump(out,open(sys.argv[1],"w"),ensure_ascii=False,indent=1)
print("DIAG_SYM_DONE")
