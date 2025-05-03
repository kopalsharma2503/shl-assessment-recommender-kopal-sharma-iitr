import requests
import numpy as np
import pandas as pd
import json
from typing import List, Dict

# Test dataset based on the PDF
TEST_DATA = [
    {
        "query": "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes.",
        "relevant_assessments": [
            "Automata - Fix (New)",
            "Core Java (Entry Level) (New)",
            "Java 8 (New)",
            "Core Java (Advanced Level) (New)",
            "Agile Software Development"
        ],
        "relevant_urls": [
            "https://www.shl.com/solutions/products/product-catalog/view/automata-fix-new/",
            "https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/",
            "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/",
            "https://www.shl.com/solutions/products/product-catalog/view/core-java-advanced-level-new/",
            "https://www.shl.com/solutions/products/product-catalog/view/agile-software-development/"
        ]
    },
    # Add more test cases from the PDF here
]

API_ENDPOINT = "http://localhost:8000"

def calculate_recall_at_k(predicted: List[str], actual: List[str], k: int = 3) -> float:
    """Calculate Recall@K metric"""
    predicted_k = predicted[:k]
    relevant_found = len([item for item in predicted_k if item in actual])
    return relevant_found / len(actual) if actual else 0

def calculate_map_at_k(predicted: List[str], actual: List[str], k: int = 3) -> float:
    """Calculate Mean Average Precision@K"""
    if not actual:
        return 0
    
    score = 0.0
    num_hits = 0.0
    
    for i, p in enumerate(predicted[:k]):
        if p in actual and p not in predicted[:i]:
            num_hits += 1.0
            score += num_hits / (i + 1.0)
    
    return score / min(len(actual), k)

def evaluate_system():
    """Evaluate the recommendation system"""
    recalls = []
    maps = []
    
    for test_case in TEST_DATA:
        try:
            # Call the API
            response = requests.post(
                f"{API_ENDPOINT}/recommend",
                json={"query": test_case["query"], "max_results": 10}
            )
            
            if response.status_code == 200:
                recommendations = response.json()["recommended_assessments"]
                
                # Extract assessment names from descriptions
                predicted_names = []
                predicted_urls = []
                
                for rec in recommendations:
                    # Extract name from description (before first period)
                    name = rec["description"].split(".")[0].strip()
                    predicted_names.append(name)
                    predicted_urls.append(rec["url"])
                
                # Calculate metrics using names
                recall = calculate_recall_at_k(predicted_names, test_case["relevant_assessments"])
                map_score = calculate_map_at_k(predicted_names, test_case["relevant_assessments"])
                
                recalls.append(recall)
                maps.append(map_score)
                
                print(f"Query: {test_case['query'][:50]}...")
                print(f"Recall@3: {recall:.3f}, MAP@3: {map_score:.3f}")
                print(f"Predicted: {predicted_names[:3]}")
                print("---")
            else:
                print(f"API Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error evaluating test case: {e}")
    
    if recalls and maps:
        print(f"\nOverall Results:")
        print(f"Mean Recall@3: {np.mean(recalls):.3f}")
        print(f"Mean MAP@3: {np.mean(maps):.3f}")
    else:
        print("No successful evaluations completed")

if __name__ == "__main__":
    evaluate_system()