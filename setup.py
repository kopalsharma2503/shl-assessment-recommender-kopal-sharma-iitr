import os
import json
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.data_loader import DataLoader
from src.recommender.vector_db import VectorDBManager

def setup_project():
    """Setup the project with initial data"""
    print("Setting up SHL Assessment Recommender...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['GOOGLE_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required API keys.")
        return False
    
    # Create necessary directories
    os.makedirs("data/processed", exist_ok=True)
    
    # Load assessments from data files
    print("\n1. Loading assessments from data files...")
    data_loader = DataLoader()
    
    # Look for data files
    possible_files = [
        'assessments.csv',
        'shl_assessments.csv',
        'data.csv'
    ]
    
    assessments = []
    loaded_file = None
    
    for filename in possible_files:
        file_path = os.path.join('data', filename)
        if os.path.exists(file_path):
            print(f"   Found data file: {filename}")
            assessments = data_loader.load_assessments_from_file(filename)
            loaded_file = filename
            break
    
    if not assessments:
        print("\nERROR: No data file found!")
        print("Please save your assessment data as 'data/assessments.csv'")
        return False
    
    print(f"   Loaded {len(assessments)} assessments from {loaded_file}")
    
    # Save processed data
    processed_file = 'data/processed/assessments.json'
    with open(processed_file, 'w') as f:
        json.dump(assessments, f, indent=2)
    print(f"   Saved processed data to {processed_file}")
    
    # Index assessments in Pinecone
    print("\n2. Indexing assessments in vector database...")
    try:
        vector_db = VectorDBManager()
        vector_db.index_assessments(assessments)
        print("   Indexing complete!")
    except Exception as e:
        print(f"\nERROR: Failed to index assessments: {e}")
        print("Please check your Pinecone API key and environment.")
        return False
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("You can now run the application with: python quickstart.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1)