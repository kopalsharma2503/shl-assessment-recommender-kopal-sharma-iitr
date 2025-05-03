import os
import subprocess
import time
import sys
import webbrowser
from dotenv import load_dotenv

def check_requirements():
    """Check if all requirements are met"""
    load_dotenv()
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("ERROR: .env file not found!")
        print("Please create a .env file with your API keys.")
        print("You can copy .env.example to .env and fill in your keys.")
        return False
    
    # Check for required environment variables
    required_vars = ['GOOGLE_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file.")
        return False
    
    # Check for data files
    data_dir = 'data'
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print("ERROR: No data files found in the 'data' directory!")
        print("Please add your assessment data file to the 'data' directory.")
        return False
    
    return True

def main():
    print("SHL Assessment Recommendation System - Quick Start")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Run setup if needed
    if not os.path.exists('data/processed/assessments.json'):
        print("\n1. Running initial setup...")
        result = subprocess.run([sys.executable, "setup.py"])
        if result.returncode != 0:
            print("Setup failed. Please check the error messages above.")
            sys.exit(1)
    else:
        print("\n1. Setup already completed. Skipping...")
    
    # Start API server
    print("\n2. Starting API server...")
    api_process = subprocess.Popen([sys.executable, "run_api.py"])
    time.sleep(5)  # Wait for API to start
    
    # Start Streamlit app
    print("\n3. Starting web interface...")
    streamlit_process = subprocess.Popen([sys.executable, "run_app.py"])
    time.sleep(5)  # Wait for Streamlit to start
    
    print("\n" + "=" * 50)
    print("Application is running!")
    print("API: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Web Interface: http://localhost:8501")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the application")
    
    # Open browser
    webbrowser.open("http://localhost:8501")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        api_process.terminate()
        streamlit_process.terminate()
        print("Application stopped.")

if __name__ == "__main__":
    main()