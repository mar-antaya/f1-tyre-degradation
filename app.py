import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ui import header,chart,footer,motion
from data_io import read_laps,clean_laps
from model import fit_stint
from roster import read_roster,refresh_roster
header('03','How long can we stay out?','Estimate within-stint tire degradation, then test how much the fuel assumption changes the answer.')
st.info('FITTED ESTIMATE • Observed 2024 COTA race laps. A fitted slope is not a tire-only causal effect or a transferable 2026 coefficient.')
try:raw=read_laps();clean=clean_laps(raw)
except FileNotFoundError as e:st.error(str(e));st.stop()
with st.sidebar:
    mode=st.radio('Driver list',['Current grid','Historical session'])
    st.caption('Lap dataset: 2024 Austin • Race. Updating the roster does not update the lap data.')
    if mode=='Current grid':
        if st.button('Refresh current grid'):
            try:
                refresh_roster()
                st.success('Roster refreshed from the latest completed Grand Prix.')
            except Exception:
                st.warning('Could not refresh the roster. Showing the saved, dated snapshot.')
        roster=read_roster()
        st.caption(f"Latest-race roster: {roster['season']} round {roster['round']} • {roster['race']}. Retrieved {roster['fetched_at'][:10]}. Substitutions after this race may not be reflected.")
        names={x['code']:x['name'] for x in roster['drivers']}
        codes=list(names)
        driver=st.selectbox('Driver',codes,index=codes.index('LEC') if 'LEC' in codes else 0,
                            format_func=lambda code:f'{names[code]} ({code})',key='current_driver')
    else:
        driver=st.selectbox('Driver',sorted(clean.Driver.unique()),key='historical_driver')
    choices=clean[clean.Driver==driver].groupby('Stint').filter(lambda x:len(x)>=6)
if choices.empty:
    name=names[driver] if mode=='Current grid' else driver
    st.subheader(name)
    st.warning('No measured stint available in the selected dataset: 2024 Austin race.')
    st.write('This driver has no sufficiently long clean stint in this dataset. No tire-wear estimate or another driver’s curve is shown under their name. This does not mean they have no data in other sessions.')
    st.info('Choose another driver, or switch to Historical session to explore the drivers in the bundled 2024 data.')
    footer()
    st.stop()
with st.sidebar:
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
