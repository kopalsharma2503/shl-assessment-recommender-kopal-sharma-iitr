import os
import sys
import subprocess
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

if __name__ == "__main__":
    subprocess.run([
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        "src/app.py",
        "--server.port", 
        os.getenv("STREAMLIT_PORT", "8501")
    ])