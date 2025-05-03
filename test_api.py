import requests
import json
import time
import sys

def test_api(base_url="http://localhost:8000"):
    """Test the API endpoints"""
    print("Testing SHL Assessment Recommendation API")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
        print("   Make sure the API server is running!")
        sys.exit(1)
    
    # Test recommendation endpoint
    print("\n2. Testing recommendation endpoint...")
    
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes.",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and Java Script. Need an assessment package that can test all skills with max duration of 60 minutes.",
        "I am hiring for an analyst and wants applications to screen using Cognitive and personality tests, what options are available within 45 mins."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Test Query {i}:")
        print(f"   {query[:100]}...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/recommend",
                json={"query": query},
                timeout=30
            )
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {end_time - start_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                assessments = data.get("recommended_assessments", [])
                print(f"   Assessments Found: {len(assessments)}")
                
                if assessments:
                    print("   First Assessment:")
                    first = assessments[0]
                    print(f"     URL: {first.get('url', 'N/A')}")
                    print(f"     Duration: {first.get('duration', 'N/A')} minutes")
                    print(f"     Test Type: {', '.join(first.get('test_type', []))}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api()