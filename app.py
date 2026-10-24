import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ui import header,chart,footer,motion
from data_io import read_laps,clean_laps
from model import fit_stint
header('03','How long can we stay out?','Estimate within-stint tire degradation, then test how much the fuel assumption changes the answer.')
st.info('FITTED ESTIMATE • Observed 2024 COTA race laps. A fitted slope is not a tire-only causal effect or a transferable 2026 coefficient.')
try:raw=read_laps();clean=clean_laps(raw)
except FileNotFoundError as e:st.error(str(e));st.stop()
with st.sidebar:
    driver=st.selectbox('Driver',sorted(clean.Driver.unique()),index=sorted(clean.Driver.unique()).index('LEC') if 'LEC' in clean.Driver.values else 0)
    choices=clean[clean.Driver==driver].groupby('Stint').filter(lambda x:len(x)>=6)
    if choices.empty:st.warning('No sufficiently long clean stint');st.stop()
    stint=st.selectbox('Stint',sorted(choices.Stint.unique()))
    fuel=st.slider('Fuel gain per race lap (s)',0.,.12,.04,.005)
    trim=st.slider('Exclude first tire ages',0,5,2)
d=choices[(choices.Stint==stint)&(choices.TyreLife>trim)]
try:result=fit_stint(d,fuel)
except ValueError as e:st.error(str(e));st.stop()
a,b,c=st.columns(3);a.metric('Estimated wear',f'{result["slope"]:.3f} s/lap');b.metric('95% conditional interval',f'{result["low"]:.3f} to {result["high"]:.3f}');c.metric('Held-out tail MAE',f'{result["mae"]:.3f} s')
f=result['frame'];fig=px.scatter(f,x='TyreLife',y='fuel_corrected',hover_data=['LapNumber','Compound'],title=f'{driver} • stint {stint:g} • {f.Compound.iloc[0]}')
fig.add_trace(go.Scatter(x=f.TyreLife,y=f.fitted,name='OLS fit',mode='lines'));chart(fig)
st.caption('Interval assumes independent errors and the chosen fuel correction. Serial correlation, traffic and track evolution can make it too narrow. Tail MAE uses only earlier laps to fit.')
chart(px.bar(f,x='LapNumber',y='residual',title='Residuals: what the line cannot explain',labels={'residual':'Observed − fitted (s)'}))
partial=[fit_stint(d.sort_values('LapNumber').iloc[:n],fuel) for n in range(6,len(d)+1)]
motion('Watch the estimate develop',[f'{x["n"]} laps fitted' for x in partial],{'Wear estimate':[x['slope'] for x in partial],'Lower 95%':[x['low'] for x in partial],'Upper 95%':[x['high'] for x in partial]},'s/lap','FITTED • expanding-window estimates from observed laps')
st.subheader('Fuel sensitivity')
import pandas as pd
sensitivity=pd.DataFrame([{'fuel_gain':g,'wear':fit_stint(d,g)['slope']} for g in [0,.02,.04,.06,.08,.10,.12]])
chart(px.line(sensitivity,x='fuel_gain',y='wear',markers=True,labels={'fuel_gain':'Assumed fuel gain (s/race lap)','wear':'Estimated tire degradation (s/tire lap)'}))
st.write(f'{len(raw)} raw laps → {len(clean)} clean laps → {len(f)} selected observations. No cross-year pooling.')
st.download_button('Download fitted stint',f.to_csv(index=False),'fitted_stint.csv','text/csv')
footer()
