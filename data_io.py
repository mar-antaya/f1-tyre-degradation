"""Public FastF1 adapter. No fabricated fallback on a failed download."""
from pathlib import Path
import json
from datetime import datetime, timezone
import pandas as pd
ROOT=Path(__file__).parent
DATA=ROOT/'data'
def read_laps(session='R',year=2024):
    path=DATA/f'cota_{year}_{session}.csv'
    if not path.exists():
        raise FileNotFoundError(f'Run python fetch_data.py --year {year} --session {session} first.')
    return pd.read_csv(path, dtype={'TrackStatus':str})
def clean_laps(laps):
    """Strict green, accurate, undeleted, non-pit laps; first lap removed."""
    if 'Eligible' in laps: return laps.loc[laps.Eligible.fillna(False)].copy()
    return laps.loc[(laps.LapNumber>1)&(laps.TrackStatus=='1')&laps.IsAccurate.fillna(False)
        &~laps.Deleted.fillna(True)&~laps.PitIn&~laps.PitOut&laps.LapTime.notna()
        &laps.Compound.isin(['SOFT','MEDIUM','HARD'])].copy()
def fetch(year=2024,session='R',telemetry=False):
    import fastf1
    cache=ROOT/'.cache';cache.mkdir(exist_ok=True);DATA.mkdir(exist_ok=True)
    fastf1.Cache.enable_cache(str(cache))
    s=fastf1.get_session(year,'United States',session)
    s.load(laps=True,telemetry=telemetry,weather=True,messages=True)
    d=pd.DataFrame(s.laps.copy())
    for col in ['LapTime','Sector1Time','Sector2Time','Sector3Time']:
        d[col]=d[col].dt.total_seconds()
    d['PitIn']=d.PitInTime.notna();d['PitOut']=d.PitOutTime.notna()
    # Deleted/accuracy flags must exist; do not silently assume missing flags are clean.
    cols=['Driver','LapNumber','Stint','Compound','TyreLife','LapTime','Sector1Time','Sector2Time','Sector3Time','TrackStatus','IsAccurate','Deleted','PitIn','PitOut','FreshTyre']
    d[cols].to_csv(DATA/f'cota_{year}_{session}.csv',index=False)
    s.track_status.to_csv(DATA/f'track_status_{year}_{session}.csv',index=False)
    if telemetry:
        # One observed fastest valid lap per driver; no synthetic telemetry.
        for driver in s.laps.Driver.unique():
            lap=s.laps.pick_drivers(driver).pick_fastest()
            if lap is None: continue
            t=lap.get_telemetry();t['Time']=t.Time.dt.total_seconds()
            t[['Time','Distance','Speed','Throttle','Brake','X','Y']].to_csv(DATA/f'telemetry_{year}_{session}_{driver}.csv',index=False)
    meta={'kind':'observed public timing, normalized by FastF1','year':year,'event':'United States','session':session,'fetched_at':datetime.now(timezone.utc).isoformat(),'fastf1':fastf1.__version__,'rows':len(d),'telemetry':telemetry,'source':'https://docs.fastf1.dev/','note':'Timing may be revised by provider. Not an official race classification.'}
    (DATA/f'cota_{year}_{session}.json').write_text(json.dumps(meta,indent=2))
    return d
