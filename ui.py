import json
from pathlib import Path
import streamlit as st
import plotly.express as px
COLORS=['#00E5C0','#D8D8D8','#008F83','#A3A3A3','#42B7E9','#7FBA00','#F4B400','#F36B42']
FONT='Segoe UI Variable, Segoe UI, Arial, sans-serif'
px.defaults.color_discrete_sequence=COLORS
px.defaults.color_continuous_scale=['#333333','#008F83','#00E5C0']
def header(number,title,question):
    st.set_page_config(page_title=title+' • COTA Lab',page_icon='🏁',layout='wide')
    st.markdown("""<style>
    html,body,[data-testid="stApp"] {font-family:'Segoe UI Variable','Segoe UI',Arial,sans-serif!important;}
    [data-testid="stAppViewContainer"] {background:#fff;padding:18px;}
    [data-testid="stMain"] {background:#030303;border-radius:0 0 76px 0;}
    [data-testid="stHeader"] {background:transparent;}
    .block-container {max-width:1450px;padding:2.8rem 3.5rem 3rem;}
    h1,h2,h3 {font-family:'Segoe UI Variable','Segoe UI',Arial,sans-serif!important;color:#fff;}
    h1 {letter-spacing:-.05em;font-weight:750!important;font-size:3.35rem!important;line-height:1.05!important;margin:.3rem 0 1rem!important;}
    h2 {letter-spacing:-.025em;font-weight:700!important;}
    [data-testid="stMetric"] {background:#101010;border:1px solid #454545;border-top:2px solid #00bfa5;border-radius:0 0 18px 0;padding:16px;}
    [data-testid="stMetricValue"] {font-size:clamp(1.1rem,2.1vw,2.4rem)!important;white-space:normal!important;font-family:'Segoe UI Variable','Segoe UI',Arial,sans-serif!important;}
    [data-testid="stSidebar"] {background:#626262!important;border:0;border-radius:0 0 0 58px;}
    [data-testid="stSidebar"] p,[data-testid="stSidebar"] label {color:#fff!important;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#ededed!important;}
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:#c1c1c1!important;}
    [data-testid="stMetricValue"] div,[data-testid="stMetricLabel"] p {white-space:normal!important;overflow:visible!important;text-overflow:clip!important;}
    [data-testid="stAlertContainer"] {background:#161c1a!important;color:#d7eae5!important;}
    [data-testid="stAlertContentInfo"] p {color:#d7eae5!important;}
    [data-testid="stAlert"] {background:#151a19;border:1px solid #39534e;border-radius:2px;}
    .eyebrow {color:#b9b9b9;letter-spacing:.19em;font-size:11px;font-weight:700;display:flex;align-items:center;gap:12px;}
    .number {width:29px;height:29px;border:1px solid #aaa;border-radius:50%;display:inline-grid;place-items:center;background:#525252;color:white;letter-spacing:0;}
    .legend-strip {background:#555;padding:9px 14px;display:flex;gap:20px;flex-wrap:wrap;color:white;font-size:11px;margin:15px 0 20px;}
    .legend-strip i {display:inline-block;width:28px;height:3px;background:#00e5c0;vertical-align:middle;margin-right:7px;}
    .brand-ticks {margin-left:auto;display:flex;gap:4px;}
    .brand-ticks b {width:7px;height:7px;display:block;}
    @media (max-width:700px) {.block-container{padding:2rem 1rem;}h1{font-size:2.4rem!important;}[data-testid="stAppViewContainer"]{padding:7px;}[data-testid="stMain"]{border-radius:0 0 38px 0;}}
    @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;}}
    </style>""",unsafe_allow_html=True)
    st.markdown(f'<div class="eyebrow"><span class="number">{number}</span>COTA / ENGINEERING LAB <span class="brand-ticks" aria-hidden="true"><b style="background:#f25022"></b><b style="background:#7fba00"></b><b style="background:#00a4ef"></b><b style="background:#ffb900"></b></span></div>',unsafe_allow_html=True)
    st.title(title);st.write(question)
    st.markdown('<div class="legend-strip"><span><i></i>Interactive analysis</span><span><i style="background:#c4c4c4"></i>Observed / estimated / simulated — labeled below</span></div>',unsafe_allow_html=True)
def chart(fig):
    fig.update_layout(template='plotly_dark',paper_bgcolor='#030303',plot_bgcolor='#030303',font=dict(color='#ededed',family=FONT),colorway=COLORS,margin=dict(l=15,r=15,t=48,b=15),legend=dict(title_text='',bgcolor='#4b4b4b',orientation='h',y=-.2,x=0),coloraxis_colorscale=['#333','#008f83','#00e5c0'])
    fig.update_xaxes(gridcolor='#282828',zerolinecolor='#555');fig.update_yaxes(gridcolor='#282828',zerolinecolor='#555')
    for i,tr in enumerate(fig.data):
        if tr.type in ('scatter','bar','histogram','box'):
            if hasattr(tr,'line'):tr.line.color=COLORS[i%len(COLORS)]
            if hasattr(tr,'marker') and not getattr(tr.marker,'coloraxis',None) and not isinstance(tr.marker.color,(list,tuple)):
                try:tr.marker.color=COLORS[i%len(COLORS)]
                except (ValueError,TypeError):pass
    st.plotly_chart(fig,width='stretch')
def motion(title,labels,series,unit,kind):
    """A deterministic data replay, paused by default. Never generates new observations."""
    from motion import render
    render(title,labels,series,unit,kind)
def footer():
    for path in sorted((Path(__file__).parent/'data').glob('cota_*.json')):
        meta=json.loads(path.read_text())
        st.caption(f"Data provenance: {meta['kind']} • {meta.get('year')} {meta.get('session')} • retrieved {meta['fetched_at']}")
    with st.expander('COTA context, sources & model boundaries'):
        st.markdown((Path(__file__).parent/'CONTEXT.md').read_text())
    st.caption('Reference-inspired black / silver / turquoise styling. Segoe UI-style system font stack; exact reference font not identified. Unofficial educational project.')
