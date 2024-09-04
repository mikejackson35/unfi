import streamlit as st

import numpy as np
import pandas as pd

import plotly.express as px

#### CONFIGS - streamlit, css, plotly  ####
st.set_page_config(page_title='Unfi Cleaner', layout="wide", initial_sidebar_state="expanded")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

# clean Size column
def clean_size(size):
    size = size.replace(' ', '').upper()  # Remove spaces and standardize case
    if '2.25' in size:
        return '2.25 OZ'
    elif '1.34' in size:
        return '1.34 OZ'
    else:
        return '4 OZ'  # Return the size as is if it doesn't match any condition
    
# map categories to Grocery, Away From Home, Other
def categorize(channel):

    grocery_categories = ['Independents', 'SuperMarket Independent', 'SuperMarket Chain', 
                          'Natural - Chain', 'SuperMarket']
    away_from_home_categories = ['Food Service', 'Alternative Channel']

    if channel in grocery_categories:
        return 'Grocery'
    elif channel in away_from_home_categories:
        return 'Away From Home'
    else:
        return 'Other'
    
def get_month_num(month):
    if month == 'January':
        return 1
    elif month == 'February':
        return 2
    elif month == 'March':
        return 3
    elif month == 'April':
        return 4
    elif month == 'May':
        return 5
    elif month == 'June':
        return 6
    elif month == 'July':
        return 7
    elif month == 'August':
        return 8
    elif month == 'September':
        return 9
    elif month == 'October':
        return 10
    elif month == 'November':
        return 11
    else:
        return 12

use_cols = ['Region', 'Channel', 'Chain Name','Customer Name', 'Address', 'City', 'State',
       'Zip Code', 'Warehouse', 'MFG PROD CD', 'Prod #', 'Description', 'Pack', 'Size',
       'UNFI Published Wholesale','Sales', 'Units']

st.sidebar.title('UNFI SBO Report Cleaner')
st.sidebar.write('#')

month = st.sidebar.selectbox(
    'Choose the Month',(
    'January','February','March','April',
    'May','June','July','August','September',
    'October','November','December'
    ))

st.sidebar.write('#')
sales_path = st.sidebar.file_uploader('...then drop your file')                     # File uploader

st.write('#')
if sales_path is not None:                                                          # If file is uploaded

    raw_sbo_report = pd.read_excel(sales_path)
    with st.expander('Click to see original data'):
        st.dataframe(raw_sbo_report, height=500, use_container_width=True)          # Display original data

    df = pd.read_excel(sales_path,skiprows=12, usecols=use_cols)                    # Get original data without blank headers, filter columns   

    # CLEAN UNFI SBO REPORT
    df.dropna(subset=['Customer Name'], inplace=True)                               # Drop rows with missing Customer Name
    df['Chain Name'].fillna(df['Customer Name'], inplace=True)                      # Fill missing Chain Name with Customer Name
    df.rename(columns = {'Channel':'Segment','MFG PROD CD':'MFG #',
                         'UNFI Published Wholesale':'UNFI Whlesle'}, inplace = True)  # Rename columns
    
    df['Prod #'] = df['Prod #'].astype(int).astype(str)                             # Convert Prod # to string
    
    df['Size'] = df['Size'].apply(clean_size).convert_dtypes()                      # Clean Size column
    df['Channel'] = df['Segment'].apply(categorize)                                 # Categorize Channel column                           

    df['Chain Name'] = df['Chain Name'].str.title()                                 # Title case for Chain Name
    df['Customer Name'] = df['Customer Name'].str.title()                           # Title case for Customer Name 
    df['Address'] = df['Address'].str.title()                                       # Title case for Address
    df['City'] = df['City'].str.title()                                             # Title case for City
    df['Description'] = df['Description'].str.title()                               # Title case for Description

    df['Month'] = month                                                             # Add Month column
    df['MonthNum'] =  df['Month'].apply(get_month_num)                              # Add MonthNum column
    df['Year'] = str(2024)                                                          # Add Year column
    df['MonthYear'] = df['MonthNum'] \
        .astype(str).str.zfill(2) + '-' + df['Year'].astype(str)                    # Finish MonthYear column

    st.write('#')

    df = df[['Month','MonthNum','Year','Region','Segment','Chain Name','Customer Name',
            'Address','City','State','Zip Code','Warehouse','MFG #','Prod #','Description','Pack',
            'Size','UNFI Whlesle','Sales','Units','MonthYear','Channel']]                                 # Reorder columns


    ## DOWNLOAD CSV BUTTON ###
    @st.cache_data
    def convert_df(df):
        # df = df[['Month','Year','Region','Channel','Segment','Chain Name','Customer Name',
        #             'City','State','Warehouse','MFG #','Prod #','Description','Pack',
        #             'Size','UNFI Whlesle','Sales','Units']]                        
        
        return df.to_csv(index=False).encode('utf-8')
    csv = convert_df(df)                                                            # convert to CSV for download

    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name='Clean SBO Report.csv',
        mime='text/csv',
    )                                                                               # Download button
    
    st.dataframe(df, height=400)                                                    # Display cleaned data

    st.write('#')
    st.write('Insights...')

    template = 'presentation'
    tab1, tab2, tab3 = st.tabs(['Customer','Segment','SKU / Size'])                 # Tabs for bar charts           
    
    with tab1:                                                                      # Bar chart by Chain Name
        chart_df = df.groupby(['Chain Name','Segment']).agg({'Sales':'sum','Units':'sum'}).reset_index().sort_values('Sales',ascending=False)[:15]
        st.plotly_chart(px.bar(chart_df, x='Chain Name', y='Sales', title='Sales by Chain Name',
                            text_auto='.2s', labels={'Sales':'Total Sales ($)'},
                            height=400, color='Segment',template=template).update_yaxes(showgrid=False).update_layout(legend=dict(title='', orientation='h', x = .4, y=1.1)),
                            use_container_width=True)
    with tab2:                                                                      # Bar chart by Segment
        chart_df = df.groupby('Segment').agg({'Sales':'sum','Units':'sum'}).reset_index().sort_values('Sales',ascending=False)[:10]
        st.plotly_chart(px.bar(chart_df, x='Segment', y='Sales', title='Sales by Segment',
                            text_auto='.2s', labels={'Sales':'Total Sales ($)'},
                            height=400,template=template).update_yaxes(showgrid=False),
                            use_container_width=True)
        
    with tab3:                                                                      # Bar chart by Product
        chart_df = df.groupby(['Prod #','Size'])[['Sales']].sum().reset_index().sort_values('Sales',ascending=False)[:15]
        st.plotly_chart(px.bar(chart_df, x='Prod #', y='Sales', title='Sales by Product',
                            text_auto='.2s', color='Size', labels={'Sales':'Total Sales ($)'},
                            height=400,template=template).update_yaxes(showgrid=False).update_xaxes(type='category').update_layout(legend=dict(title='', orientation='h', x = .4, y=1.1)),
                            use_container_width=True)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)                                  # Hide Streamlit footer