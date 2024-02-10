import streamlit as st
import pandas as pd
import numpy as np
from typing import List
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px
import subprocess
import sys
import os

icon_path = 'https://aiesec.lk/data/dist/images/favicon.png'
st.set_page_config(
    layout="wide",
    page_title="OD Dashboard - AIESEC in Sri Lanka",
    page_icon= icon_path,
)

# Load data outside of Streamlit app initialization
@st.cache_data
def load_data(data_url):
    try:
        data = pd.read_csv(data_url)

        # Check if 'month_name' column exists
        if 'month_name' not in data.columns:
            st.error("Error: 'month_name' column not found in the CSV file.")
            return None

        data['month_name'] = pd.to_datetime(data['month_name'], format='%Y %B', errors='coerce').dt.strftime('%B %Y')
        return data
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return None

# Main Data Source
data_url1 = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRifHGM_iqkAo_9yWFckhtQOu7J-ybWSTJppU_JBhYq-cQegFDqgezIB6X5c3dHAODXDvKJ__AUZzvC/pub?gid=0&single=true&output=csv'
data = load_data(data_url1)

# Sub Data Source
data_url2 = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4p6YJ0XKwY0AmS37dz_j7cuUG4uZYoZeFyCuWP0MBbjBgV7XXf2nqGompdTW-o-2x1CAxmIExoHXy/pub?gid=1230705189&single=true&output=csv'
data_core = load_data(data_url2)

# Ranks of Main Data Source
data_url3 = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTfr0Ohkx_-2hHXFzlztMkQKioFUpeMrehZKSoFgcNniHYUp5evKerCHR2TfSU7ASTmjAhKMVOqObWV/pub?gid=1230705189&single=true&output=csv'
data_rank = load_data(data_url3)

# Set up Streamlit app title
st.title('OD Dashboard - AIESEC in Sri Lanka')

# Get unique entity and month lists
unique_entities = data['entity'].unique()
entity_list = list(unique_entities)

unique_month = data['month_name'].unique()
month_list = list(unique_month)

function_list = ["FnL", "BD", "ER", "TM", "Brand", "EM", "IM", "iGV", "oGV", "iGTa", "iGTe", "oGTa", "oGTe", "DXP"]

# Sidebar for user selection
selected_entity = st.sidebar.selectbox('Select Entity', entity_list)
selected_month = st.sidebar.selectbox('Select Month', month_list)


# Filter data based on user selection
filtered_data = data[(data['entity'] == selected_entity) & (data['month_name'] == selected_month)]
filtered_data_entity = data[(data['entity'] == selected_entity)]
filtered_data2 = filtered_data_month = data[(data['month_name'] == selected_month)]

#defined colors
xdi_col="#f85c44"
hdi_col="#38c49c"
odi_col="#086cb4"
gen="#cccccc"


def plot_bubble_chart(filtered_data2):
    # Bubble plot using Plotly
    fig = px.scatter(filtered_data2, x='HDI', y='XDI', size='ODI', color='entity',
                     title='Bubble Plot', labels={'HDI': 'HDI', 'XDI': 'XDI', 'ODI': 'ODI'},
                     )

    # Customize the layout
    fig.update_layout(
        showlegend=True,
        legend_title_text='Entity',
        xaxis_title='HDI',
        yaxis_title='XDI',
        xaxis=dict(range=[0, 1]), # Set x-axis range to [0, 1]
        yaxis=dict(range=[0, 1]), # Set y-axis range to [0, 1]
        paper_bgcolor='rgba(0,0,0,0)' # Set background color to transparent
    )

    # Display the plot using Streamlit
    st.plotly_chart(fig, use_container_width=True)

def plot_score_line_chart(filtered_data, score_column, color):
    # Melt the DataFrame to long format
    melted_data = filtered_data.melt(id_vars=['month_name'], var_name='Entity', value_name='Score')

    # Select the specified score column
    score_data = melted_data[melted_data['Entity'] == score_column]

    # Create a line chart using Altair
    chart = alt.Chart(score_data).mark_line(color=color).encode(
        x=alt.X('month_name:N', title='Month'),
        y=alt.Y('Score:Q', title=f'{score_column} Score'),
        tooltip=['month_name:N', 'Score:Q']  # Include Month and the selected score in the tooltip
    ).properties(
        width=600,
        height=400,
        title=f'{score_column} Scores Over Time'
    )

    # Display the chart using Streamlit
    st.altair_chart(chart, use_container_width=True)

def plot_score_bar_chart(filtered_data, score_column, color):
    # Melt the DataFrame to long format
    melted_data = filtered_data.melt(id_vars=['entity'], var_name='Function', value_name='Score')

    # Select the specified score column
    score_data = melted_data[melted_data['Function'] == score_column]

    # Create a bar chart using Altair
    chart = alt.Chart(score_data).mark_bar(opacity=0.7).encode(
        x=alt.X('entity:N', title='Entity'),
        y=alt.Y('Score:Q', title=f'{score_column} Score'),
        color=alt.value(color),  # Use the specified color
        tooltip=['entity:N', 'Score:Q']  # Include Entity and the selected score in the tooltip
    ).properties(
        width=600,
        height=400,
        title=f'{score_column} Scores by Entity'
    )

    # Display the chart using Streamlit
    st.altair_chart(chart, use_container_width=True)

def gen_bar_chart(selected_entity, selected_month, data):
    filtered_data = data[(data['month_name'] == selected_month) & (data['entity'] == selected_entity)]
    melted_data = filtered_data.melt(id_vars=['entity'], var_name='Function', value_name='Score')
    melted_data['Score'] = pd.to_numeric(melted_data['Score'], errors='coerce')
    chart = alt.Chart(melted_data).mark_bar(opacity=0.7).encode(
        x=alt.X('Function:N', title='Function'),
        y=alt.Y('Score:Q', title='Score'),
        tooltip=['Function:N', 'Score:Q'],  # Include Function and Score in the tooltip
        # color=alt.value('blue')  # You can change the color if needed
    ).properties(
        title=f'Scores vs Functions - {selected_entity} - {selected_month}'
    )

    # Calculate the average scores
    filtered_data2 = data[data['month_name'] == selected_month]
    pivot_data = filtered_data2.set_index('entity').T.drop('month_name')
    pivot_data['Average'] = pivot_data.mean(axis=1)
    function_average_data = pivot_data[['Average']].reset_index()

    # Create a line chart for average scores
    line_chart = alt.Chart(function_average_data.reset_index()).mark_line(strokeDash=[5, 5]).encode(
        x=alt.X('index:N', title='Function'),
        y=alt.Y('Average:Q', title='Average Score', axis=alt.Axis(titleColor='red', format=".2f")),  # Format to two decimal places
        tooltip=['index:N', alt.Tooltip('Average:Q', title='Average Score', format=".2f")],  # Include Function and Average Score in the tooltip
    )

    # Add data points to the line chart
    point_chart = alt.Chart(function_average_data.reset_index()).mark_point(color='red').encode(
        x=alt.X('index:N'),
        y=alt.Y('Average:Q', axis=alt.Axis(titleColor='red', format=".2f")),  # Format to two decimal places
        tooltip=['index:N', alt.Tooltip('Average:Q', title='Average Score', format=".2f")],  # Include Function and Average Score in the tooltip
    )

    # Combine bar, line, and point charts
    combined_chart = chart + line_chart + point_chart
    st.altair_chart(combined_chart, use_container_width=True)

def display_kpi_metrics(selected_entity, selected_month, kpis, title, data):
    # st.markdown(
    #     f"<h7 style='color: white;'>{title}</h7>", 
    #     unsafe_allow_html=True
    # )

    # Filter data based on the selected entity and month
    data = data[(data['entity'] == selected_entity) & (data['month_name'] == selected_month)]

    # Get KPI values and names from the filtered data
    kpi_values = data[kpis].values[0]
    kpi_names = kpis

    num_cols = 7  # Number of columns to display KPIs
    num_kpis = len(kpi_values)
    
    # Calculate the number of rows needed based on the number of KPIs and columns
    num_rows = (num_kpis + num_cols - 1) // num_cols

    # Iterate over the rows to display KPIs in rows of 7
    for i in range(num_rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < num_kpis:
                cols[j].markdown(
                    f"""
                    <div style="
                        background-color: #0076b6;
                        border-radius: 10px;
                        padding: 5px;
                        margin: 5px;
                        text-align: center; /* Center align text */
                    ">
                        <p style="margin: 0;">{kpi_names[idx]}</p> <!-- Add margin: 0; to remove default margin -->
                        <h3 style="margin: 0;">{kpi_values[idx]}</h3> <!-- Add margin: 0; to remove default margin -->
                    </div>
                    """
                , unsafe_allow_html=True)

def display_kpi_metrics2(selected_entity, selected_month, kpis, title, data):
    # st.markdown(
    #     f"<h7 style='color: white;'>{title}</h7>", 
    #     unsafe_allow_html=True
    # )

    # Filter data based on the selected entity and month
    data = data[(data['entity'] == selected_entity) & (data['month_name'] == selected_month)]

    # Get KPI values and names from the filtered data
    kpi_values = data[kpis].values[0]
    kpi_names = kpis

    num_cols = 3  # Number of columns to display KPIs
    num_kpis = len(kpi_values)
    
    # Calculate the number of rows needed based on the number of KPIs and columns
    num_rows = (num_kpis + num_cols - 1) // num_cols

    # Iterate over the rows to display KPIs in rows of 7
    for i in range(num_rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < num_kpis:
                cols[j].markdown(
                    f"""
                    <div style="
                        background-color: #0076b6;
                        border-radius: 10px;
                        padding: 5px;
                        margin: 5px;
                        height: 215px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                    ">
                        <p style="margin: 0;">{kpi_names[idx]}</p> <!-- Add margin: 0; to remove default margin -->
                        <h3 style="margin: 0;">{kpi_values[idx]}</h3> <!-- Add margin: 0; to remove default margin -->
                    </div>
                    """
                , unsafe_allow_html=True)

def display_kpi_metrics3(selected_entity, selected_month, kpis, title, data):

    # Filter data based on the selected entity and month
    data = data[(data['entity'] == selected_entity) & (data['month_name'] == selected_month)]

    # Get KPI values and names from the filtered data
    kpi_values = data[kpis].values[0]
    kpi_names = kpis

    num_cols = 1  # Number of columns to display KPIs
    num_kpis = len(kpi_values)
    
    # Calculate the number of rows needed based on the number of KPIs and columns
    num_rows = (num_kpis + num_cols - 1) // num_cols

    # Iterate over the rows to display KPIs in rows of 7
    for i in range(num_rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < num_kpis:
                cols[j].markdown(
                    f"""
                    <div style="
                        background-color: #0076b6;
                        border-radius: 10px;
                        padding: 5px;
                        margin: 5px;
                        height: 120px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                    ">
                        <p style="margin: 0;">{kpi_names[idx]}</p> <!-- Add margin: 0; to remove default margin -->
                        <h3 style="margin: 0;">{kpi_values[idx]}</h3> <!-- Add margin: 0; to remove default margin -->
                    </div>
                    """
                , unsafe_allow_html=True)

def display_kpi_metrics4(selected_entity, selected_month, kpis, title, data):

    # Filter data based on the selected entity and month
    data = data[(data['entity'] == selected_entity) & (data['month_name'] == selected_month)]

    # Get KPI values and names from the filtered data
    kpi_values = data[kpis].values[0]
    kpi_names = kpis

    num_cols = 1  # Number of columns to display KPIs
    num_kpis = len(kpi_values)
    
    # Calculate the number of rows needed based on the number of KPIs and columns
    num_rows = (num_kpis + num_cols - 1) // num_cols

    # Iterate over the rows to display KPIs in rows of 7
    for i in range(num_rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < num_kpis:
                cols[j].markdown(
                    f"""
                    <div style="
                        background-color: #0076b6;
                        border-radius: 10px;
                        padding: 5px;
                        margin: 5px;
                        height: 265px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                    ">
                        <p style="margin: 0;">{kpi_names[idx]}</p> <!-- Add margin: 0; to remove default margin -->
                        <h3 style="margin: 0;">{kpi_values[idx]}</h3> <!-- Add margin: 0; to remove default margin -->
                    </div>
                    """
                , unsafe_allow_html=True)

# SECTION 1 - KPIs
# Define 2 Columns
col1, col2 = st.columns([7, 3])
# Applying custom CSS to adjust column widths
st.markdown(
    """
    <style>
    .css-1ikpi7r {
        width: 60%;
        padding: 0px;
        margin: 0px;
    }
    .css-o5mxxx {
        width: 40%;
        padding: 0px;
        margin: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# KPIs
with col1:
    xdi_kpis = ['DXP', 'iGTa', 'iGTe', 'iGV', 'oGTa', 'oGTe', 'oGV']
    display_kpi_metrics(selected_entity, selected_month, xdi_kpis, "XDI Scores",data)

    """

    """
    # Display HDI Scores
    hdi_kpis = ['BD', 'Brand', 'EM', 'ER', 'FnL', 'IM', 'TM']
    display_kpi_metrics(selected_entity, selected_month, hdi_kpis, "HDI Scores",data)

    """

    """
with col2:
    odi_kpis = ['XDI', 'HDI', 'ODI']

    display_kpi_metrics2(selected_entity, selected_month, odi_kpis, "ODI Scores", data)
    

# SECTION 2  
# Define the columns with specified widths
col1, col2, col3 = st.columns([8, 1, 1])  # 70%, 15%, 15%
# Applying custom CSS to adjust column widths
st.markdown(
    """
    <style>
    .css-1ikpi7r { /* CSS class for the first column */
        width: 80%; /* Set width to 70% */
        padding: 0px; /* Remove padding */
        margin: 0px; /* Remove margin */
    }
    .css-o5mxxx { /* CSS class for the second and third columns */
        width: 10%; /* Set width to 15% */
        padding: 0px; /* Remove padding */
        margin: 0px; /* Remove margin */
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Bar chart Column
with col1:
    # Generate bar chart
    gen_bar_chart(selected_entity, selected_month, data)
# KPI Column1
with col2:
    XDI_kpi = ['XDI Rank']
    display_kpi_metrics3(selected_entity, selected_month,XDI_kpi, "XDI Rank", data_rank)
    """

    """
    HDI_kpi = ['HDI Rank']
    display_kpi_metrics3(selected_entity, selected_month, HDI_kpi, "HDI Rank", data_rank)
# KPI Column2
with col3:
    ODI_kpi = ['ODI Rank']
    display_kpi_metrics4(selected_entity, selected_month, ODI_kpi, "ODI Rank", data_rank)



# SECTION 3
# Create three columns for line charts
col1, col2, col3 = st.columns(3)
# Plot each chart in a separate column
with col1:
    plot_score_line_chart(filtered_data_entity, 'XDI', xdi_col)

with col2:
    plot_score_line_chart(filtered_data_entity, 'HDI', hdi_col)

with col3:
    plot_score_line_chart(filtered_data_entity, 'ODI', odi_col)

# Create three columns for bar charts
col1, col2, col3 = st.columns(3)

# Plot each chart in a separate column
with col1:
    plot_score_bar_chart(filtered_data2, 'XDI', xdi_col)

with col2:
    plot_score_bar_chart(filtered_data2, 'HDI', hdi_col)

with col3:
    plot_score_bar_chart(filtered_data2, 'ODI', odi_col)

# Display the DataFrame with functions in one column and selected entities
filtered_data2 = data[data['month_name'] == selected_month]
pivot_data = filtered_data2.set_index('entity').T.drop('month_name')

# Create three columns for line charts
col1, col2= st.columns(2)

# Plot each chart in a separate column
with col1:
    st.markdown(
        f"<h7 style='color: white;'>{f'Entity vs Functions Score Summary for {selected_month}'}</h7>", 
        unsafe_allow_html=True
    )
    st.dataframe(pivot_data, use_container_width=True)

with col2:
    st.markdown(
        f"<h7 style='color: white;'>{f'XDI - HDI - ODI Comparisions {selected_month}'}</h7>", 
        unsafe_allow_html=True
    )
    plot_bubble_chart(filtered_data2)

# Create three columns for bar charts
col1, col2 = st.columns(2)

selected_function = st.selectbox('Select Function', function_list)

st.subheader('Functional Analysis')

# Display the relevant function data based on the selected function
function_data = pivot_data.loc[[selected_function]].reset_index(drop=True)
st.dataframe(function_data, use_container_width=True, hide_index=True)


# Create three columns for line charts
col1, col2= st.columns(2)

# Plot each chart in a separate column
with col1:
    plot_score_bar_chart(filtered_data2, selected_function, gen)

with col2:
    plot_score_line_chart(filtered_data_entity, selected_function, gen)

# Create three columns for bar charts
col1, col2 = st.columns(2)


data_core_filtered = data_core[(data_core['Function'] == selected_function) & (data_core['month_name'] == selected_month)]
columns_to_display = [col for col in data_core_filtered.columns if col not in ['month_name', 'Function']]

# Remove index column
data_core_filtered_display = data_core_filtered[columns_to_display].reset_index(drop=True)

st.dataframe(data_core_filtered_display, use_container_width=True)

<br><br><br>
message = f'<p style="color: white;"><center>Made with ❤️ By &lt;/Dev.Team&gt; of AIESEC in Sri Lanka</center></p>'
st.write(message, unsafe_allow_html=True)
