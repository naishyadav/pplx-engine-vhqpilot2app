import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_echarts import st_echarts
import datetime

# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="Startup Ecosystem Dashboard")

# Custom CSS to improve UI
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stSelectbox>div>div>div {
        background-color: #f0f2f6;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to generate mock data
def generate_mock_data(n_startups=1000):
    np.random.seed(42)
    dates = pd.date_range(start='1/1/2020', end='12/31/2023', freq='D')
    
    data = pd.DataFrame({
        'date': np.random.choice(dates, n_startups),
        'startup': [f"Startup {i}" for i in range(1, n_startups + 1)],
        'industry': np.random.choice(['Tech', 'Biotech', 'Fintech', 'E-commerce', 'AI', 'Cleantech'], n_startups),
        'funding_round': np.random.choice(['Seed', 'Series A', 'Series B', 'Series C', 'Series D'], n_startups),
        'amount': np.random.lognormal(mean=16, sigma=1.5, size=n_startups).astype(int),
        'valuation': np.random.lognormal(mean=18, sigma=2, size=n_startups).astype(int),
        'employees': np.random.randint(1, 1000, n_startups),
        'location': np.random.choice(['USA', 'UK', 'Germany', 'France', 'India', 'China', 'Japan'], n_startups)
    })
    
    return data

# Generate mock data
df = generate_mock_data()

# Sidebar for filtering
st.sidebar.header('Filters')
selected_year = st.sidebar.selectbox('Select Year', sorted(df['date'].dt.year.unique(), reverse=True))
selected_industry = st.sidebar.multiselect('Select Industry', df['industry'].unique(), default=df['industry'].unique())

# Filter data based on sidebar selections
filtered_df = df[(df['date'].dt.year == selected_year) & (df['industry'].isin(selected_industry))]

# Main dashboard
st.title('Startup Ecosystem Dashboard')

# Key metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Funding", f"${filtered_df['amount'].sum():,.0f}")
col2.metric("Number of Deals", f"{len(filtered_df):,}")
col3.metric("Average Deal Size", f"${filtered_df['amount'].mean():,.0f}")
col4.metric("Unique Startups", f"{filtered_df['startup'].nunique():,}")

# Funding trends over time
st.subheader('Funding Trends')
monthly_funding = filtered_df.groupby(filtered_df['date'].dt.to_period("M"))['amount'].sum().reset_index()
monthly_funding['date'] = monthly_funding['date'].dt.to_timestamp()

fig = px.line(monthly_funding, x='date', y='amount', title='Monthly Funding Trend')
fig.update_layout(xaxis_title='Date', yaxis_title='Total Funding ($)')
st.plotly_chart(fig, use_container_width=True)

# Industry breakdown
st.subheader('Industry Breakdown')
industry_funding = filtered_df.groupby('industry')['amount'].sum().sort_values(ascending=False)

fig = px.pie(industry_funding, values='amount', names=industry_funding.index, title='Funding by Industry')
st.plotly_chart(fig, use_container_width=True)

# Funding rounds distribution
st.subheader('Funding Rounds Distribution')
round_dist = filtered_df['funding_round'].value_counts()

fig = px.bar(round_dist, x=round_dist.index, y=round_dist.values, title='Number of Deals by Funding Round')
fig.update_layout(xaxis_title='Funding Round', yaxis_title='Number of Deals')
st.plotly_chart(fig, use_container_width=True)

# Top startups
st.subheader('Top Startups by Funding')
top_startups = filtered_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)

fig = px.bar(top_startups, x=top_startups.index, y=top_startups.values, title='Top 10 Startups by Total Funding')
fig.update_layout(xaxis_title='Startup', yaxis_title='Total Funding ($)')
st.plotly_chart(fig, use_container_width=True)

# Geographical distribution
st.subheader('Geographical Distribution of Funding')
geo_funding = filtered_df.groupby('location')['amount'].sum().reset_index()

fig = px.choropleth(geo_funding, locations='location', locationmode='country names', color='amount', 
                    hover_name='location', color_continuous_scale=px.colors.sequential.Plasma,
                    title='Total Funding by Country')
st.plotly_chart(fig, use_container_width=True)

# Interactive startup explorer
st.subheader('Startup Explorer')
selected_startup = st.selectbox('Select a Startup', filtered_df['startup'].unique())
startup_data = filtered_df[filtered_df['startup'] == selected_startup].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Industry", startup_data['industry'])
col2.metric("Funding Round", startup_data['funding_round'])
col3.metric("Employees", f"{startup_data['employees']:,}")

# Radar chart for startup comparison
st.subheader('Startup Comparison')
radar_data = filtered_df.groupby('startup').agg({
    'amount': 'sum',
    'valuation': 'max',
    'employees': 'max'
}).reset_index()

radar_data = radar_data.sort_values('amount', ascending=False).head(5)
radar_startups = radar_data['startup'].tolist()

options = {
    "title": {"text": "Top 5 Startups Comparison"},
    "legend": {"data": radar_startups},
    "radar": {
        "indicator": [
            {"name": "Funding", "max": radar_data['amount'].max()},
            {"name": "Valuation", "max": radar_data['valuation'].max()},
            {"name": "Employees", "max": radar_data['employees'].max()}
        ]
    },
    "series": [{
        "type": "radar",
        "data": [
            {
                "value": [row['amount'], row['valuation'], row['employees']],
                "name": row['startup']
            } for _, row in radar_data.iterrows()
        ]
    }]
}
st_echarts(options=options, height="500px")

# Investor sentiment analysis (mock data)
st.subheader('Investor Sentiment Analysis')
sentiment_data = pd.DataFrame({
    'Date': pd.date_range(start='1/1/2023', end='12/31/2023', freq='M'),
    'Sentiment': np.random.uniform(0, 100, 12)
})

fig = px.line(sentiment_data, x='Date', y='Sentiment', title='Investor Sentiment Over Time')
fig.update_layout(yaxis_title='Sentiment Score')
st.plotly_chart(fig, use_container_width=True)

# Call to action
st.markdown("---")
st.header("Ready to dive deeper?")
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("Request Full Report"):
        st.success("Thank you for your interest! We'll contact you shortly with the full report.")

# Footer
st.markdown("---")
st.markdown("© 2024 Startup Ecosystem Analytics. All rights reserved.")
