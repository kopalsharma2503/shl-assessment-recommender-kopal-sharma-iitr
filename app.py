import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import time

# Set page config
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🧪",
    layout="wide"
)

# Load environment variables
load_dotenv()

# API endpoint
API_ENDPOINT = "https://shl-assessment-recommender-kopal-sharma.onrender.com"  

def check_api_health():
    """Check if the API is available"""
    try:
        response = requests.get(f"{API_ENDPOINT}/health")
        return response.status_code == 200
    except:
        return False

def get_recommendations_from_api(query, max_results=10):
    """Get assessment recommendations from the FastAPI backend"""
    try:
        response = requests.post(
            f"{API_ENDPOINT}/recommend",
            json={"query": query, "max_results": max_results}
        )
        
        if response.status_code == 200:
            return response.json()["recommended_assessments"]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

def scrape_job_description(url):
    """Scrape job description from a provided URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Generic approach to extract job description
            text_elements = soup.find_all(['p', 'div', 'li'])
            job_description = " ".join([elem.text.strip() for elem in text_elements])
            return job_description[:2000]  # Limit length
        else:
            return f"Failed to fetch URL: {response.status_code}"
    except Exception as e:
        return f"Error processing URL: {str(e)}"

def main():
    st.title("🧪 SHL Assessment Recommender")
    st.markdown("""
    Find the perfect SHL assessments for your hiring needs. Enter a job description 
    or requirements to get personalized recommendations.
    """)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API service is not available. Please make sure the API server is running.")
        st.stop()
    else:
        st.success("✅ Connected to API service")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Enter Query", "Import Job Description URL"])
    
    with tab1:
        query = st.text_area(
            "Enter your requirements:",
            height=150,
            placeholder="Example: I need assessments for a Java developer role that include problem-solving skills, completed within 45 minutes."
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_button = st.button("Get Recommendations", key="search_button", type="primary")
        with col2:
            max_results = st.number_input("Max results", min_value=1, max_value=20, value=10)
    
    with tab2:
        url = st.text_input(
            "Enter job description URL:",
            placeholder="https://example.com/job-posting"
        )
        url_button = st.button("Fetch & Analyze", key="url_button", type="primary")
    
    # Process query
    if search_button and query:
        with st.spinner("Finding the best assessments for you..."):
            recommendations = get_recommendations_from_api(query, max_results)
            
            if recommendations:
                display_recommendations(recommendations)
            else:
                st.warning("No assessments found matching your query.")
    
    # Process URL
    elif url_button and url:
        with st.spinner("Fetching job description..."):
            job_description = scrape_job_description(url)
            
            if not job_description.startswith("Failed") and not job_description.startswith("Error"):
                st.text_area("Extracted Job Description", job_description, height=200)
                
                with st.spinner("Finding assessments..."):
                    recommendations = get_recommendations_from_api(job_description, max_results)
                    
                    if recommendations:
                        display_recommendations(recommendations)
                    else:
                        st.warning("No assessments found matching the job description.")
            else:
                st.error(job_description)

def display_recommendations(recommendations):
    """Display recommendations in a structured format"""
    st.subheader("📊 Recommended Assessments")
    
    # Display cards for each recommendation
    for i, assessment in enumerate(recommendations, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                assessment_name = assessment['description'].split('.')[0]
                st.markdown(f"### {i}. [{assessment_name}]({assessment['url']})")
                
                test_types = assessment['test_type']
                st.markdown(f"**Test Types:** {', '.join(test_types)}")
                
                relevance = assessment['description'].split('.', 1)[1] if '.' in assessment['description'] else ""
                if relevance:
                    st.markdown(f"**Relevance:** {relevance.strip()}")
            
            with col2:
                st.markdown(f"**Duration:** {assessment['duration']} minutes")
                st.markdown(f"**Remote:** {assessment['remote_support']}")
                st.markdown(f"**Adaptive:** {assessment['adaptive_support']}")
            
            st.markdown("---")
    
    # Visualization
    if recommendations:
        st.subheader("📈 Test Type Distribution")
        
        # Collect test types
        all_test_types = []
        for assessment in recommendations:
            all_test_types.extend(assessment['test_type'])
        
        # Create frequency dataframe
        type_counts = pd.Series(all_test_types).value_counts().reset_index()
        type_counts.columns = ['Test Type', 'Count']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        type_counts.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Distribution of Test Types in Recommendations')
        ax.set_xlabel('Test Type')
        ax.set_ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()