import pytest
from motion import payload

def test_replay_preserves_values_and_rejects_misalignment():
    d=payload('Lap replay',['Lap 1','Lap 2'],{'gap':[1.2,-.4]},'s','simulated')
    assert d['series']['gap']==[1.2,-.4]
    with pytest.raises(ValueError):payload('Bad',['one'],{'gap':[1,2]},'s','simulation')
    with pytest.raises(ValueError):payload('Bad',['one'],{'gap':[float('nan')]},'s','simulation')
