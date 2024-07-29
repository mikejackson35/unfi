import pandas as pd
import numpy as np

import plotly.express as px

import streamlit as st
import altair as alt

st.set_page_config(layout="wide")
config = {'displayModeBar': False}
alt.themes.enable("dark")


# df = pd.read_csv('unfi_clean.csv')
df = pd.read_excel(r'unfi_clean.xlsx')
df.drop(columns=['Month','Address','Zip Code','MFG PROD CD','Brand','UNFI Published Wholesale'], inplace=True)
df = df[['MonthYear','Region','Channel','Segment','Chain Name','Customer Name','City','State','Warehouse','Prod #','Description','Pack','Size','Units','Sales','Year']]

df['Year'] = df['Year'].astype(str)
df['Prod #'] = df['Prod #'].astype(str)

ytd = df[df['Year'] > '2023']['Sales'].sum()
custs = df[df['Year'] > '2023']['Customer Name'].nunique()
chart_year = df.groupby(['Year','MonthYear'])[['Sales']].sum().reset_index()
chart_size = df.groupby(['Year','MonthYear','Size'])[['Sales']].sum().sort_values(['Year','MonthYear','Size'],ascending=[True,True,False]).reset_index()
chart_channel = df.groupby(['Year','MonthYear','Segment'])[['Sales']].sum().sort_values(['Year','MonthYear','Segment'],ascending=[True,True,False]).reset_index()


col, col1, col2, col3 = st.columns(4)

with col:
    st.markdown('<h1>UNFI</h1>',unsafe_allow_html=True)

with col1:
    st.write('#')
    st.markdown('<h5>YTD: ${:,.0f}'.format(ytd),unsafe_allow_html=True)

with col2:
    st.write('#')
    st.markdown('<h5>Customers: {:,.0f}'.format(custs),unsafe_allow_html=True)

with col3:
    st.write('#')
    st.markdown('<h5>SKUs: {:,.0f}'.format(df['Prod #'].nunique()),unsafe_allow_html=True)

st.write('#')

col1, col2, col3 = st.columns(3)

with col1:
    fig = px.bar(chart_year, x='MonthYear', y='Sales',
                color='Year', title='Month / Year', width=430, height=350,
                text_auto='.3s', labels={'Sales':'','MonthYear':''},template='presentation')
    fig.update_yaxes(showticklabels=False,showgrid=False)
    fig.update_layout(showlegend=False, title_x=0.05)
    st.plotly_chart(fig, config=config)

with col2:
    fig2 = px.bar(chart_size, x='MonthYear', y='Sales',
            color='Size', title='Bag Size', width=450, height=350,
            labels={'Sales':'','Size':'', 'MonthYear':''},template='presentation')
    fig2.update_yaxes(showgrid=False)
    fig2.update_layout(legend=dict(orientation='h', y=1.2, x=0.25), title_x=0.05)
    st.plotly_chart(fig2, config=config)

with col3:
    fig3 = px.bar(chart_channel, x='MonthYear', y='Sales',
            color='Segment', title='Segment', width=450, height=350,
            labels={'Sales':'','MonthYear':'','Channel':'','Segment':''},template='presentation')
    fig3.update_yaxes(showgrid=False)
    fig3.update_layout(legend=dict(orientation='h',y=1.6,x=.1))
    st.plotly_chart(fig3, config=config)


st.write('<small>downloadable clean data',unsafe_allow_html=True)

# with st.expander('Click to see full data'):
df_container = st.container(border=True)

with df_container:
    st.dataframe(df,use_container_width=True, height=250)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)