# gemini_api.py (simplified version)
import os
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize models
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

def generate_content(prompt, temperature=0.7):
    """Generate content using Gemini Flash 2.0"""
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

def create_embeddings(texts):
    """
    Create simple embeddings using Gemini or fallback to hash-based embeddings
    """
    embeddings = []
    
    for text in texts:
        try:
            # Use Gemini to generate a semantic representation
            prompt = f"""
            Create a 384-dimensional embedding vector for this text. 
            Return ONLY a Python list of 384 float numbers between -1 and 1.
            Text: "{text[:500]}"
            """
            
            response = generate_content(prompt, temperature=0.1)
            
            # Try to parse the response as a list
            if response:
                try:
                    import ast
                    embedding = ast.literal_eval(response)
                    if isinstance(embedding, list) and len(embedding) == 384:
                        embeddings.append(embedding)
                        continue
                except:
                    pass
            
            # Fallback to hash-based embedding
            embeddings.append(hash_based_embedding(text))
            
        except Exception as e:
            print(f"Error creating embedding: {e}")
            embeddings.append(hash_based_embedding(text))
    
    return embeddings

def hash_based_embedding(text, dim=384):
    """Create a deterministic embedding based on text hash"""
    # Create a hash of the text
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    
    # Convert hash to a list of floats
    embedding = []
    for i in range(0, len(text_hash), 2):
        # Convert hex pairs to float between -1 and 1
        value = int(text_hash[i:i+2], 16) / 127.5 - 1
        embedding.append(value)
    
    # Pad or truncate to desired dimension
    if len(embedding) < dim:
        # Repeat the pattern to reach desired dimension
        while len(embedding) < dim:
            embedding.extend(embedding[:dim - len(embedding)])
    else:
        embedding = embedding[:dim]
    
    return embedding