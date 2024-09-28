import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import plotly.graph_objects as go
from wordcloud import WordCloud

# Mock data generation
def generate_mock_data(n_startups, n_investors):
    startups = pd.DataFrame({
        'name': [f"Startup {i}" for i in range(1, n_startups + 1)],
        'industry': np.random.choice(['Tech', 'Biotech', 'Fintech', 'E-commerce', 'AI'], n_startups),
        'funding_stage': np.random.choice(['Seed', 'Series A', 'Series B', 'Series C'], n_startups),
        'funding_sought': np.random.randint(100000, 10000000, n_startups),
        'description': [f"Innovative {np.random.choice(['platform', 'solution', 'technology'])} for {np.random.choice(['improving', 'revolutionizing', 'disrupting'])} {np.random.choice(['healthcare', 'finance', 'education', 'transportation'])}" for _ in range(n_startups)]
    })
    
    investors = pd.DataFrame({
        'name': [f"Investor {i}" for i in range(1, n_investors + 1)],
        'preferred_industries': [', '.join(np.random.choice(['Tech', 'Biotech', 'Fintech', 'E-commerce', 'AI'], size=np.random.randint(1, 4), replace=False)) for _ in range(n_investors)],
        'preferred_stages': [', '.join(np.random.choice(['Seed', 'Series A', 'Series B', 'Series C'], size=np.random.randint(1, 4), replace=False)) for _ in range(n_investors)],
        'min_investment': np.random.randint(50000, 1000000, n_investors),
        'max_investment': np.random.randint(1000000, 20000000, n_investors),
        'previous_investments': np.random.randint(1, 50, n_investors)
    })
    
    return startups, investors

# Sentiment analysis
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Matching algorithm
def match_startups_to_investors(startups, investors):
    matches = []
    
    # TF-IDF vectorization for startup descriptions
    tfidf = TfidfVectorizer()
    startup_desc_vecs = tfidf.fit_transform(startups['description'])
    
    for _, investor in investors.iterrows():
        investor_industry_vec = tfidf.transform([investor['preferred_industries']])
        
        for _, startup in startups.iterrows():
            # Industry matching
            industry_match = cosine_similarity(startup_desc_vecs[startups.index == startup.name], investor_industry_vec)[0][0]
            
            # Funding stage matching
            stage_match = int(startup['funding_stage'] in investor['preferred_stages'])
            
            # Funding amount matching
            funding_match = 1 if investor['min_investment'] <= startup['funding_sought'] <= investor['max_investment'] else 0
            
            # Sentiment matching
            sentiment_match = get_sentiment(startup['description'])
            
            # Calculate overall match score
            match_score = (industry_match * 0.4 + stage_match * 0.3 + funding_match * 0.2 + sentiment_match * 0.1) * 100
            
            matches.append({
                'startup': startup['name'],
                'investor': investor['name'],
                'match_score': match_score
            })
    
    return pd.DataFrame(matches)

# Streamlit app
def main():
    st.title("Startup Investor Matching Algorithm")
    st.write("This app demonstrates a sophisticated algorithm for matching startups with potential investors.")

    # Generate mock data
    n_startups = st.sidebar.slider("Number of Startups", 10, 100, 50)
    n_investors = st.sidebar.slider("Number of Investors", 5, 50, 20)
    startups, investors = generate_mock_data(n_startups, n_investors)

    # Run matching algorithm
    if st.button("Run Matching Algorithm"):
        matches = match_startups_to_investors(startups, investors)

        # Display top matches
        st.subheader("Top Matches")
        top_matches = matches.sort_values('match_score', ascending=False).head(10)
        st.table(top_matches)

        # Interactive heatmap of match scores
        st.subheader("Match Score Heatmap")
        pivot_matches = matches.pivot(index='startup', columns='investor', values='match_score')
        fig = go.Figure(data=go.Heatmap(z=pivot_matches.values, x=pivot_matches.columns, y=pivot_matches.index, colorscale='Viridis'))
        fig.update_layout(title='Startup-Investor Match Scores', xaxis_title='Investors', yaxis_title='Startups')
        st.plotly_chart(fig)

        # Startup industry distribution
        st.subheader("Startup Industry Distribution")
        industry_counts = startups['industry'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(industry_counts.values, labels=industry_counts.index, autopct='%1.1f%%')
        st.pyplot(fig)

        # Word cloud of startup descriptions
        st.subheader("Startup Description Word Cloud")
        text = ' '.join(startups['description'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        # Investor preference analysis
        st.subheader("Investor Preferences")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        investors['preferred_industries'].str.split(', ', expand=True).stack().value_counts().plot(kind='bar', ax=ax1)
        ax1.set_title('Preferred Industries')
        ax1.set_xlabel('Industry')
        ax1.set_ylabel('Count')
        
        investors['preferred_stages'].str.split(', ', expand=True).stack().value_counts().plot(kind='bar', ax=ax2)
        ax2.set_title('Preferred Funding Stages')
        ax2.set_xlabel('Stage')
        ax2.set_ylabel('Count')
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()
