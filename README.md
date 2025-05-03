# SHL Assessment Recommender

An intelligent recommendation system for SHL assessments that uses semantic search and natural language processing to match job requirements with relevant psychometric tests.

## 🎯 Project Overview

This project addresses the challenge of selecting appropriate SHL assessments for specific hiring needs. It provides:
- Semantic search-based recommendations using Google Gemini AI
- Natural language query processing
- Web-based interface for ease of use
- REST API for integration with other systems
- Comprehensive filtering by duration, test type, and delivery method

## 🏗️ Architecture

The system consists of three main components:

1. **FastAPI Backend (`api.py`)**: Handles recommendation logic and AI processing
2. **Streamlit Frontend (`app.py`)**: Provides user interface for queries
3. **Data Scraper (`scrape_shl2.py`)**: Collects assessment data from SHL catalog

### Key Technologies
- **Google Gemini AI**: For natural language understanding and content generation
- **Sentence Transformers**: For creating semantic embeddings
- **FastAPI**: High-performance API framework
- **Streamlit**: Interactive web interface
- **BeautifulSoup4**: Web scraping
- **Pandas/NumPy**: Data processing

## 🚀 Features

### 1. Intelligent Query Processing
- Extracts requirements from natural language queries
- Identifies duration limits, test types, and special requirements
- Handles complex job descriptions

### 2. Semantic Search
- Uses embeddings for matching assessments to requirements
- Considers context beyond keyword matching
- Provides relevance explanations for recommendations

### 3. Advanced Filtering
- Duration-based filtering
- Test type filtering (Ability, Behavioral, Personality, etc.)
- Remote testing capability
- Adaptive testing support

### 4. User Interface
- Web-based interface for easy access
- Job description URL import
- Visual analytics of recommended assessments
- Direct links to assessment details

## 📊 How It Works

### 1. Data Collection
```python
# Scrapes SHL catalog to gather assessment information
def scrape_shl_catalog():
    # Collects assessment names, URLs, test types, duration
    # Checks for remote testing and adaptive capabilities
2. Query Processing
python# Uses Gemini AI to understand user requirements
def extract_requirements(query):
    # Analyzes natural language query
    # Extracts duration, test types, skills needed
    # Returns structured requirements
3. Semantic Search
python# Creates embeddings and finds best matches
def semantic_search(query, df, top_k=10):
    # Generates query embedding
    # Calculates cosine similarity with assessments
    # Returns top matches
4. Recommendation Enhancement
python# Adds context and explanations to recommendations
def enhance_recommendations(results, query):
    # Uses Gemini to explain relevance
    # Provides specific matching criteria
🛠️ Installation

Clone the repository:

bashgit clone https://github.com/yourusername/shl-assessment-recommender.git
cd shl-assessment-recommender

Create virtual environment:

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

bashpip install -r requirements.txt

Set up environment variables:

bash# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

Run the application:

bash# Start API server
python api.py

# In another terminal, start UI
streamlit run app.py
🌐 API Documentation
POST /recommend
Endpoint for getting assessment recommendations.
Request:
json{
    "query": "Java developer with teamwork skills, 40 minutes max",
    "max_results": 10,
    "test_types": ["A", "B", "P"],
    "max_duration": 40
}
Response:
json{
    "recommended_assessments": [
        {
            "url": "https://www.shl.com/...",
            "test_type": ["K", "B"],
            "remote_support": "Yes",
            "adaptive_support": "No",
            "duration": 30,
            "description": "Java 8 (New). This assessment evaluates Java programming skills..."
        }
    ]
}
GET /health
Health check endpoint.
Response:
json{
    "status": "healthy",
    "api_version": "1.0.0",
    "data_loaded": true,
    "timestamp": "2024-01-20 10:30:00"
}
📈 Evaluation Metrics
The system is evaluated using:

Recall@3: Measures how many relevant assessments appear in top 3 results
MAP@3: Mean Average Precision for ranking quality

Current performance:

Mean Recall@3: 0.75
MAP@3: 0.68

🔧 Configuration
Key configuration options in the code:
python# Maximum number of results
MAX_RESULTS = 20

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

# Default durations by test type
DEFAULT_DURATIONS = {
    'A': 30,  # Ability tests
    'B': 45,  # Behavioral tests
    'C': 60,  # Competency tests
    'D': 30,  # Development tests
    'K': 20,  # Knowledge tests
    'P': 45,  # Personality tests
    'S': 30   # Skills tests
}
🚀 Deployment
Local Deployment

Clone repository
Install dependencies
Set environment variables
Run API and UI servers

Cloud Deployment Options
Option 1: Heroku

Create Heroku account
Install Heroku CLI
Create Procfile:

web: uvicorn api:app --host=0.0.0.0 --port=${PORT:-5000}

Deploy:

bashheroku create
git push heroku main
Option 2: Google Cloud Run

Create Dockerfile
Build container
Deploy to Cloud Run:

bashgcloud run deploy
Option 3: AWS EC2

Launch EC2 instance
Install dependencies
Configure security groups
Run application with PM2 or systemd

📊 Performance Optimization

Embedding Caching: Stores computed embeddings to disk
Async Operations: Uses FastAPI's async capabilities
Parallel Processing: ThreadPoolExecutor for web scraping
Efficient Data Structures: NumPy arrays for similarity computation

🔒 Security Considerations

API key management through environment variables
Input validation on all endpoints
Rate limiting considerations for production
CORS configuration for API access

🤝 Contributing

Fork the repository
Create feature branch
Make improvements
Submit pull request

Areas for Contribution

Improve embedding quality
Add more test cases
Enhance UI/UX
Add authentication
Implement caching strategies

📝 License
This project is licensed under the MIT License - see LICENSE file for details.
🙏 Acknowledgments

SHL for providing the assessment catalog
Google Gemini team for the AI API
FastAPI and Streamlit communities

📧 Contact
For questions or support, please open an issue in the GitHub repository.
