import pandas as pd
import numpy as np

import plotly.express as px

import streamlit as st
import altair as alt

st.set_page_config(layout="wide")
config = {'displayModeBar': False}
alt.themes.enable("dark")

with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

# get data from unfi_sbo.xlsx and clean
df = pd.read_excel(r'C:\Users\mikej\Desktop\unfi\unfi_sbo.xlsx',sheetname='unfi_clean')
df.drop(columns=['Month','Address','Zip Code','MFG PROD CD','UNFI Published Wholesale', 'Grand Total'], inplace=True)
df = df[['MonthYear','Region','Channel','Segment','Chain Name','Customer Name','City','State','Warehouse','Prod #','Description','Pack','Size','Units','Sales','Year']]

df['Year'] = df['Year'].astype(str)
df['Prod #'] = df['Prod #'].astype(str)

# summary stats
ytd = df[df['Year'] > '2023']['Sales'].sum()
custs = df[df['Year'] > '2023']['Customer Name'].nunique()

# dataframes for bar charts
chart_year = df[df['Year'] > '2023'].groupby(['Year','MonthYear'])[['Sales']].sum().reset_index()
chart_size = df[df['Year'] > '2023'].groupby(['Year','MonthYear','Size'])[['Sales']].sum().sort_values(['Year','MonthYear','Size'],ascending=[True,True,False]).reset_index()
chart_channel = df[(df['Year'] > '2023') & (df['Segment']!='All Others')].groupby(['MonthYear','Segment'],as_index=False)[['Sales']].sum().sort_values(['MonthYear', 'Sales'],ascending=[True,False])



st.write('#')

# TOP ROW
# with col:
col, blank, col1 = st.columns([1,.5,5])
with col:
      st.markdown('<h1>UNFI<br><br></h1>',unsafe_allow_html=True)
      st.markdown('<h5>YTD: ${:,.0f}'.format(ytd),unsafe_allow_html=True)
      st.markdown('<h5>Customers: {:,.0f}'.format(custs),unsafe_allow_html=True)
      st.markdown('<h5>SKUs: {:,.0f}'.format(df['Prod #'].nunique()),unsafe_allow_html=True)

with col1:
        fig = px.bar(chart_year, x='MonthYear', y='Sales',
                    color='Year', title='Month / Year', height=350,
                    text_auto='.3s', labels={'Sales':'','MonthYear':''},template='presentation')
        fig.update_yaxes(showgrid=False)
        fig.update_layout(showlegend=False, title_x=0.5, title_y=.88)
        #     st.plotly_chart(fig, config=config,use_container_width=True)

        # with col2:
        fig2 = px.bar(chart_size, x='MonthYear', y='Sales',
                color='Size', title='Bag Size', height=350,
                labels={'Sales':'','Size':'', 'MonthYear':''},template='plotly_dark')
        fig2.update_yaxes(showgrid=False)
        fig2.update_layout(legend=dict(orientation='h', y=1.85,x=.39), title_x=0.5, title_y=.88)
        #     st.plotly_chart(fig2, config=config,use_container_width=True)

        # with col3:
        fig3 = px.bar(chart_channel, x='MonthYear', y='Sales',
                color='Segment', title='Segment', height=350,
                labels={'Sales':'','MonthYear':'','Channel':'','Segment':''},template='presentation',
                hover_name='Segment')
        fig3.update_yaxes(showgrid=False)
        fig3.update_layout(legend=dict(orientation='h',y=1.85), title_x=0.5, title_y=.88)
#     st.plotly_chart(fig3, config=config, use_container_width=True)

        tab1, tab2, tab3 = st.tabs(['by Month', 'by Product', "by Segment"])
        with tab1:
            st.plotly_chart(fig,use_container_width=True,config = config)
        with tab2:
            st.plotly_chart(fig2,use_container_width=True,config = config)
        with tab3:
            st.plotly_chart(fig3,use_container_width=True,config = config) 
        "#"

# SECOND ROW
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