import numpy as np
import pandas as pd
import pytest
from model import fit_stint

def test_recover_known_wear_and_fuel_identifiability():
    age=np.arange(1,21);laps=np.arange(21,41)
    d=pd.DataFrame({'TyreLife':age,'LapNumber':laps,'LapTime':100+.08*(age-1)-.04*(laps-1)})
    a=fit_stint(d,.04);b=fit_stint(d,.08)
    assert a['slope']==pytest.approx(.08)
    assert b['slope']-a['slope']==pytest.approx(.04)
    assert a['mae']<1e-10
    with pytest.raises(ValueError):fit_stint(d.head(3))
