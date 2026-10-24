"""Within-stint OLS with an explicit user-supplied fuel correction."""
import numpy as np
from scipy.stats import t

def fit_stint(df,fuel_gain=.04):
    d=df.dropna(subset=['TyreLife','LapTime','LapNumber']).sort_values('LapNumber').copy()
    if len(d)<6 or d.TyreLife.nunique()<4: raise ValueError('Need ≥6 clean laps spanning ≥4 tire ages.')
    # Fuel and tire age are collinear inside one stint. Never estimate both here.
    x=d.TyreLife.to_numpy(float)-1
    y=d.LapTime.to_numpy(float)+fuel_gain*(d.LapNumber.to_numpy(float)-1)
    X=np.column_stack([np.ones(len(x)),x])
    beta=np.linalg.lstsq(X,y,rcond=None)[0];pred=X@beta
    residual=y-pred;s2=residual@residual/(len(x)-2)
    se=np.sqrt(np.diag(s2*np.linalg.inv(X.T@X)))
    interval=t.ppf(.975,len(x)-2)*se[1]
    d['fuel_corrected']=y;d['fitted']=pred;d['residual']=residual
    # Chronological last quarter held out; re-fit only earlier observations.
    split=max(4,int(len(d)*.75));train=np.linalg.lstsq(X[:split],y[:split],rcond=None)[0]
    mae=float(np.abs(y[split:]-X[split:]@train).mean())
    return {'slope':float(beta[1]),'low':float(beta[1]-interval),'high':float(beta[1]+interval),'mae':mae,'n':len(d),'frame':d}
