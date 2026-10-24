"""Explicit alternate provider. Downloaded facts + derived eligibility, never FastF1 flags."""
from pathlib import Path
from datetime import datetime,timezone
import json,re,time,argparse
import requests
import numpy as np
import pandas as pd
ROOT=Path(__file__).parent;DATA=ROOT/'data';BASE='https://api.openf1.org/v1/'
def get(endpoint,**params):
    for i in range(4):
        r=requests.get(BASE+endpoint,params=params,timeout=60)
        if r.status_code==429 and i<3:time.sleep(3*(i+1));continue
        r.raise_for_status();return r.json()
def session_key(year,session):
    sessions=get('sessions',year=year,country_name='United States',session_name={'R':'Race','Q':'Qualifying'}[session])
    found=[s for s in sessions if s['circuit_short_name']=='Austin']
    if len(found)!=1:raise ValueError('Expected exactly one COTA session.')
    return found[0]['session_key']
def neutral_intervals(messages):
    opened={};out=[]
    for m in sorted(messages,key=lambda m:m['date']):
        stamp=pd.Timestamp(m['date']);msg=m['message'];flag=m.get('flag');key=m.get('sector') if m.get('scope')=='Sector' else 'track'
        if flag in ['YELLOW','DOUBLE YELLOW','RED']:opened.setdefault(key,stamp)
        if 'SAFETY CAR DEPLOYED' in msg:opened.setdefault('sc',stamp)
        if flag=='CLEAR' and key in opened:out.append((opened.pop(key),stamp))
        if flag=='GREEN' or msg=='TRACK CLEAR':
            if key=='track':
                for k in list(opened):out.append((opened.pop(k),stamp))
        if 'VSC ENDING' in msg and 'sc' in opened:out.append((opened.pop('sc'),stamp+pd.Timedelta(seconds=90)))
        if 'SAFETY CAR IN THIS LAP' in msg and 'sc' in opened:out.append((opened.pop('sc'),stamp+pd.Timedelta(seconds=180)))
    for stamp in opened.values():out.append((stamp,pd.Timestamp.max.tz_localize('UTC')))
    return out

def normalize(laps,stints,drivers,pits,messages):
    d=pd.DataFrame(laps).rename(columns={'lap_number':'LapNumber','lap_duration':'LapTime','duration_sector_1':'Sector1Time','duration_sector_2':'Sector2Time','duration_sector_3':'Sector3Time','is_pit_out_lap':'PitOut'})
    names={x['driver_number']:x['name_acronym'] for x in drivers};d['Driver']=d.driver_number.map(names)
    d['Stint']=np.nan;d['Compound']='UNKNOWN';d['TyreLife']=np.nan
    for s in stints:
        mask=(d.driver_number==s['driver_number'])&d.LapNumber.between(s['lap_start'],s['lap_end'])
        d.loc[mask,'Stint']=s['stint_number'];d.loc[mask,'Compound']=s['compound']
        d.loc[mask,'TyreLife']=d.loc[mask,'LapNumber']-s['lap_start']+1+s['tyre_age_at_start']
    pitset={(x['driver_number'],x['lap_number']) for x in pits}
    d['PitIn']=[(r.driver_number,r.LapNumber) in pitset for r in d.itertuples()]
    # Also remove the lap immediately before a reported outlap.
    prev={(r.driver_number,r.LapNumber-1) for r in d.itertuples() if r.PitOut}
    d['PitIn']|=np.array([(r.driver_number,r.LapNumber) in prev for r in d.itertuples()])
    d['Deleted']=False
    for m in messages:
        msg=m['message']
        if 'DELETED' not in msg:continue
        car=re.search(r'CAR (\d+)',msg);duration=re.search(r'TIME (\d+):(\d+\.\d+)',msg)
        if car and duration:
            sec=int(duration[1])*60+float(duration[2])
            d.loc[(d.driver_number==int(car[1]))&np.isclose(d.LapTime,sec,atol=.002),'Deleted']=True
        elif car:
            # Unparsed deletion: exclude that driver's laps instead of silently retaining them.
            d.loc[d.driver_number==int(car[1]),'Deleted']=True
        else:raise ValueError('Cannot attribute a deleted lap; review race-control feed.')
    start=pd.to_datetime(d.date_start,utc=True,format="ISO8601");end=start+pd.to_timedelta(d.LapTime,unit='s')
    neutral=pd.Series(False,index=d.index)
    for lo,hi in neutral_intervals(messages):neutral|=(start<=hi)&(end>=lo)
    # Blue flags can contaminate pace too; remove overlapping laps for the driver.
    for m in messages:
        if m.get('flag')=='BLUE':
            stamp=pd.Timestamp(m['date']);neutral|=(d.driver_number==m['driver_number'])&(start<=stamp)&(end>=stamp)
    sec=['Sector1Time','Sector2Time','Sector3Time']
    consistent=d[sec].notna().all(axis=1)&np.isclose(d[sec].sum(axis=1),d.LapTime,atol=.015)&(d[sec]>0).all(axis=1)
    d['Eligible']=consistent&~neutral&start.notna()&~d.Deleted&~d.PitIn&~d.PitOut&(d.LapNumber>1)&d.Compound.isin(['SOFT','MEDIUM','HARD'])
    d['QualityMethod']='OpenF1 derived eligibility; not FastF1 IsAccurate'
    return d[['Driver','LapNumber','Stint','Compound','TyreLife','LapTime']+sec+['PitIn','PitOut','Deleted','Eligible','QualityMethod']]
def fetch(year=2024,session='R'):
    key=session_key(year,session);bundle={}
    for endpoint in ['laps','stints','drivers','pit','race_control']:
        bundle[endpoint]=get(endpoint,session_key=key);time.sleep(.25)
    if not all(bundle[k] for k in ['laps','stints','drivers','race_control']):raise ValueError('Incomplete historical session; refusing to infer missing facts.')
    frame=normalize(bundle['laps'],bundle['stints'],bundle['drivers'],bundle['pit'],bundle['race_control'])
    DATA.mkdir(exist_ok=True);frame.to_csv(DATA/f'cota_{year}_{session}.csv',index=False)
    (DATA/f'openf1_{year}_{session}_race_control.json').write_text(json.dumps(bundle['race_control'],indent=2))
    meta={'kind':'observed OpenF1 timing; eligibility derived locally','source':'https://openf1.org/docs/','session_key':key,'year':year,'session':session,'fetched_at':datetime.now(timezone.utc).isoformat(),'rows':len(frame),'eligible':int(frame.Eligible.sum()),'quality':'Sector sums within 0.015 s, non-pit, non-deleted, no overlap with reconstructed neutral/yellow or driver blue-flag intervals. SC-in message padded 180 s; VSC ending padded 90 s. Conservative heuristic, not official validation.'}
    (DATA/f'cota_{year}_{session}.json').write_text(json.dumps(meta,indent=2));print(meta)
    return frame

def history():
    rows=[]
    for year in [2023,2024,2025]:
        key=session_key(year,'R');messages=get('race_control',session_key=key)
        if not messages or not any(m.get('flag')=='CHEQUERED' for m in messages):raise ValueError(f'{year}: no end-of-race coverage')
        texts=[m['message'] for m in messages]
        rows.append({'year':year,'sc':int(any(m=='SAFETY CAR DEPLOYED' for m in texts)),'vsc':int(any('VIRTUAL SAFETY CAR DEPLOYED' in m for m in texts)),'red_flag':int(any(m.get('flag')=='RED' for m in messages)),'source':BASE+f'race_control?session_key={key}','kind':'observed OpenF1 messages; completeness not guaranteed'})
        DATA.mkdir(exist_ok=True);(DATA/f'openf1_{year}_R_race_control.json').write_text(json.dumps(messages,indent=2))
    pd.DataFrame(rows).to_csv(DATA/'safety_history.csv',index=False)
    print(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--year',type=int,default=2024);p.add_argument('--session',choices=['R','Q'],default='R');p.add_argument('--history',action='store_true');a=p.parse_args()
    history() if a.history else fetch(a.year,a.session)
