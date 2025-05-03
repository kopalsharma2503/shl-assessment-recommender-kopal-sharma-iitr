from fastapi import FastAPI, Query, Body, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
from dotenv import load_dotenv
import os
import uvicorn
from scrape_shl2 import scrape_shl_catalog, save_to_csv
import time
import numpy as np
from gemini_api import generate_content, create_embeddings
import re
import pickle
import json
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Global variables
assessments_df = None
embedding_cache = {}
EMBEDDINGS_FILE = "embeddings.pkl"

# Test type mapping
TEST_TYPE_MAPPING = {
    'A': 'Ability',
    'B': 'Behavioral', 
    'C': 'Competency',
    'D': 'Development',
    'K': 'Knowledge',
    'P': 'Personality',
    'S': 'Skills'
}

def load_or_scrape_data():
    """Load data from CSV or scrape if not available"""
    global assessments_df
    
    filename = "shl_assessments.csv"
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        if not df.empty:
            # Ensure duration column has proper values
            df = enhance_duration_data(df)
            return df
    
    print("Initial data load: Scraping SHL catalog...")
    df = scrape_shl_catalog()
    save_to_csv(df, filename)
    df = enhance_duration_data(df)
    
    return df

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global assessments_df
    try:
        assessments_df = load_or_scrape_data()
        print(f"Loaded {len(assessments_df)} assessments")
    except Exception as e:
        print(f"Error loading assessment data: {e}")
    
    yield
    
    # Shutdown (if needed)
    pass

app = FastAPI(
    title="SHL Assessment Recommender API",
    description="API for recommending SHL assessments based on job descriptions and queries",
    version="1.0.0",
    lifespan=lifespan
)

# Data models
class Assessment(BaseModel):
    url: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

class RecommendationRequest(BaseModel):
    query: str = Field(..., description="Natural language query or job description")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return", ge=1, le=20)
    test_types: Optional[List[str]] = Field(None, description="Filter by specific test types")
    max_duration: Optional[int] = Field(None, description="Maximum duration in minutes", ge=0)

class RecommendationResponse(BaseModel):
    recommended_assessments: List[Assessment]

def enhance_duration_data(df):
    """Add estimated durations based on test types"""
    default_durations = {
        'A': 30,  # Ability tests
        'B': 45,  # Behavioral tests
        'C': 60,  # Competency tests
        'D': 30,  # Development tests
        'K': 20,  # Knowledge tests
        'P': 45,  # Personality tests
        'S': 30   # Skills tests
    }
    
    for idx, row in df.iterrows():
        if pd.isna(row['duration']) or row['duration'] == 'N/A':
            test_types = str(row['test_type']).split(',')
            durations = []
            
            for test_type in test_types:
                test_type = test_type.strip()
                if test_type in default_durations:
                    durations.append(default_durations[test_type])
            
            if durations:
                df.at[idx, 'duration'] = int(np.mean(durations))
            else:
                df.at[idx, 'duration'] = 30  # Default duration
                
    return df

def save_embeddings(embeddings, filename=EMBEDDINGS_FILE):
    """Save embeddings to disk"""
    with open(filename, 'wb') as f:
        pickle.dump(embeddings, f)

def load_embeddings(filename=EMBEDDINGS_FILE):
    """Load embeddings from disk"""
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None

def create_embeddings_for_api(texts):
    """Generate embeddings for texts using sentence-transformers"""
    embeddings = []
    for text in texts:
        if text in embedding_cache:
            embeddings.append(embedding_cache[text])
            continue
            
        try:
            embedding = create_embeddings([text])[0]
            embedding_cache[text] = embedding
            embeddings.append(embedding)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            embeddings.append([0.0] * 384)  # all-MiniLM-L6-v2 has 384 dimensions
    return embeddings

def extract_requirements(query):
    """Extract structured requirements from query"""
    prompt = f"""
    Analyze this query and extract requirements for assessment selection:
    Query: "{query}"
    
    Return a JSON object with the following structure:
    {{
        "duration_limit": null or integer (maximum duration in minutes),
        "test_types": [] (list of test type codes: A, B, C, D, K, P, S),
        "skills_required": [] (list of specific skills mentioned),
        "remote_required": boolean,
        "adaptive_required": boolean
    }}
    
    Test type codes:
    A: Ability, B: Behavioral, C: Competency, D: Development, K: Knowledge, P: Personality, S: Skills
    
    Only include test types if explicitly mentioned or clearly implied.
    """
    
    try:
        response = generate_content(prompt)
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            # Fallback to regex-based extraction
            return extract_requirements_fallback(query)
    except Exception as e:
        print(f"Error extracting requirements: {e}")
        return extract_requirements_fallback(query)

def extract_requirements_fallback(query):
    """Fallback method to extract requirements using regex"""
    requirements = {
        "duration_limit": None,
        "test_types": [],
        "skills_required": [],
        "remote_required": False,
        "adaptive_required": False
    }
    
    # Extract duration
    duration_match = re.search(r'(\d+)\s*(?:min|minute|minutes)', query.lower())
    if duration_match:
        requirements["duration_limit"] = int(duration_match.group(1))
    
    # Extract test types based on keywords
    query_lower = query.lower()
    if any(word in query_lower for word in ['cognitive', 'ability', 'aptitude']):
        requirements["test_types"].append('A')
    if any(word in query_lower for word in ['behavioral', 'behavior']):
        requirements["test_types"].append('B')
    if any(word in query_lower for word in ['personality', 'traits']):
        requirements["test_types"].append('P')
    if any(word in query_lower for word in ['skill', 'technical']):
        requirements["test_types"].append('S')
    if 'knowledge' in query_lower:
        requirements["test_types"].append('K')
    
    # Check for remote/adaptive requirements
    requirements["remote_required"] = 'remote' in query_lower
    requirements["adaptive_required"] = 'adaptive' in query_lower
    
    return requirements

def semantic_search(query, df, top_k=10):
    """Perform semantic search using embeddings"""
    if df is None or df.empty:
        raise ValueError("Assessment dataframe is empty or None")
    
    # Generate embedding for the query
    query_embedding = create_embeddings_for_api([query])[0]
    
    # Check if embeddings exist
    embeddings_file = "assessment_embeddings.pkl"
    
    if 'embedding' not in df.columns:
        saved_embeddings = load_embeddings(embeddings_file)
        
        if saved_embeddings is not None:
            df['embedding'] = saved_embeddings
        else:
            print("Generating embeddings for assessments...")
            assessment_texts = []
            for _, row in df.iterrows():
                # Create rich text representation
                test_types = [TEST_TYPE_MAPPING.get(t.strip(), t.strip()) 
                            for t in str(row['test_type']).split(',')]
                text = f"{row['name']}. Test types: {', '.join(test_types)}. "
                if row.get('duration') != 'N/A':
                    text += f"Duration: {row['duration']} minutes. "
                assessment_texts.append(text)
            
            embeddings = create_embeddings_for_api(assessment_texts)
            df['embedding'] = embeddings
            save_embeddings(embeddings, embeddings_file)
    
    # Calculate cosine similarity
    similarities = []
    for _, row in df.iterrows():
        embedding = row['embedding']
        dot_product = np.dot(query_embedding, embedding)
        norm_query = np.linalg.norm(query_embedding)
        norm_doc = np.linalg.norm(embedding)
        
        if norm_query > 0 and norm_doc > 0:
            similarity = dot_product / (norm_query * norm_doc)
        else:
            similarity = 0
            
        similarities.append(similarity)
    
    df['similarity'] = similarities
    results = df.sort_values('similarity', ascending=False).head(top_k).copy()
    
    if 'embedding' in results.columns:
        results = results.drop('embedding', axis=1)
    
    return results

def enhance_recommendations(results, query):
    """Add relevance explanations to recommendations"""
    explanations = []
    
    for _, row in results.iterrows():
        test_types = [TEST_TYPE_MAPPING.get(t.strip(), t.strip()) 
                     for t in str(row['test_type']).split(',')]
        
        prompt = f"""
        Explain why this SHL assessment is relevant to the query in 1-2 concise sentences.
        
        Query: "{query}"
        Assessment: "{row['name']}"
        Test types: {', '.join(test_types)}
        Remote testing: {row['remote_testing']}
        Adaptive/IRT: {row['adaptive_irt']}
        Duration: {row.get('duration', 'N/A')} minutes
        
        Focus on specific skills and competencies measured by this assessment that match the query.
        """
        
        try:
            explanation = generate_content(prompt)
            if explanation:
                explanations.append(explanation.strip())
            else:
                explanations.append("Relevant assessment based on query requirements.")
        except Exception:
            explanations.append("Relevant assessment based on query requirements.")
    
    results['relevance'] = explanations
    return results

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SHL Assessment Recommender API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)",
            "documentation": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global assessments_df
    
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "data_loaded": assessments_df is not None and not assessments_df.empty,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoints": ["/", "/recommend", "/health", "/docs"]
    }

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest = Body(...)):
    global assessments_df
    
    # Validate input
    if not request.query or len(request.query.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 3 characters long"
        )
    
    try:
        # Ensure data is loaded
        if assessments_df is None:
            assessments_df = load_or_scrape_data()
        
        # Extract requirements
        requirements = extract_requirements(request.query)
        
        # Get initial recommendations
        results = semantic_search(request.query, assessments_df, top_k=request.max_results * 2)
        
        # Apply filters
        if requirements["duration_limit"]:
            filtered_df = results[results['duration'] <= requirements["duration_limit"]]
            if not filtered_df.empty:
                results = filtered_df
        
        if requirements["test_types"]:
            def has_required_types(row):
                row_types = [t.strip() for t in str(row['test_type']).split(',')]
                return any(req_type in row_types for req_type in requirements["test_types"])
            
            filtered_df = results[results.apply(has_required_types, axis=1)]
            if not filtered_df.empty:
                results = filtered_df
        
        if requirements["remote_required"]:
            filtered_df = results[results['remote_testing'].str.lower() == 'yes']
            if not filtered_df.empty:
                results = filtered_df
        
        if requirements["adaptive_required"]:
            filtered_df = results[results['adaptive_irt'].str.lower() == 'yes']
            if not filtered_df.empty:
                results = filtered_df
        
        # Limit to requested number of results
        results = results.head(request.max_results)
        
        # Add relevance explanations
        results = enhance_recommendations(results, request.query)
        
        # Convert to response format
        recommended_assessments = []
        for _, row in results.iterrows():
            test_types = [t.strip() for t in str(row['test_type']).split(',') if t.strip()]
            
            assessment = Assessment(
                url=row['url'],
                test_type=test_types,
                remote_support=row['remote_testing'],
                adaptive_support=row['adaptive_irt'],
                duration=int(row.get('duration', 30)),
                description=f"{row['name']}. {row.get('relevance', '')}"
            )
            recommended_assessments.append(assessment)
        
        return RecommendationResponse(recommended_assessments=recommended_assessments)
    
    except Exception as e:
        print(f"Error processing recommendation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)