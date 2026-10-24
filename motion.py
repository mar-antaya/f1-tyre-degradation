"""Accessible local replay of supplied numerical series; no network or autoplay."""
from pathlib import Path
import json
import math
import streamlit as st

def payload(title,labels,series,unit,kind):
    labels=[str(x) for x in labels]
    if not labels or any(len(v)!=len(labels) for v in series.values()):
        raise ValueError('Every replay series must match the nonempty label sequence.')
    values={str(k):[float(x) for x in v] for k,v in series.items()}
    if not all(math.isfinite(x) for v in values.values() for x in v):raise ValueError('Replay requires finite numbers.')
    return {'title':title,'labels':labels,'series':values,'unit':unit,'kind':kind}
def render(title,labels,series,unit,kind):
    data=payload(title,labels,series,unit,kind)
    encoded=json.dumps(data).replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')
    html=(Path(__file__).parent/'motion.html').read_text().replace('__DATA__',encoded)
    st.iframe(html,height="content",alt=title+" — controllable data replay")
