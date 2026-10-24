import json
from pathlib import Path
import pandas as pd
import numpy as np
from fetch_openf1 import normalize,neutral_intervals

def test_flag_intervals_do_not_use_sector_clear_to_end_sc():
    messages=[{'date':'2024-10-20T19:00:00Z','message':'SAFETY CAR DEPLOYED','flag':None,'scope':None},
              {'date':'2024-10-20T19:01:00Z','message':'CLEAR IN TRACK SECTOR 3','flag':'CLEAR','scope':'Sector','sector':3},
              {'date':'2024-10-20T19:02:00Z','message':'SAFETY CAR IN THIS LAP','flag':None,'scope':None}]
    intervals=neutral_intervals(messages)
    assert len(intervals)==1
    assert intervals[0][1]==pd.Timestamp('2024-10-20T19:05:00Z')

def test_observed_table_integrity():
    for path in (Path(__file__).parent/'data').glob('cota_*.csv'):
        d=pd.read_csv(path)
        assert not d.duplicated(['Driver','LapNumber']).any()
        if 'Eligible' in d:
            clean=d[d.Eligible]
            assert len(clean)>0
            assert not clean.PitIn.any() and not clean.PitOut.any() and not clean.Deleted.any()
            assert np.allclose(clean[['Sector1Time','Sector2Time','Sector3Time']].sum(axis=1),clean.LapTime,atol=.015)
        meta=json.loads(path.with_suffix('.json').read_text())
        assert meta['rows']==len(d) and 'observed' in meta['kind']
