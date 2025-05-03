import pandas as pd
import numpy as np

def clean_assessment_data(input_file, output_file):
    """Clean and validate the assessment data"""
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    
    # Remove exact duplicates
    df = df.drop_duplicates()
    print(f"After removing duplicates: {df.shape}")
    
    # Clean the data
    df['name'] = df['name'].str.strip()
    df['url'] = df['url'].str.strip()
    
    # Handle duration - keep as is since all are "N/A"
    df['duration'] = df['duration'].fillna('N/A')
    
    # Clean test_type - remove extra quotes and spaces
    df['test_type'] = df['test_type'].str.replace('"', '').str.strip()
    
    # Clean boolean fields
    df['remote_testing'] = df['remote_testing'].str.strip()
    df['adaptive_irt'] = df['adaptive_irt'].str.strip()
    
    # Check for any remaining duplicates based on URL (which should be unique)
    url_duplicates = df[df.duplicated(subset=['url'], keep=False)]
    if not url_duplicates.empty:
        print("\nWarning: Duplicate URLs found:")
        print(url_duplicates[['name', 'url']].sort_values('url'))
        
        # Keep first occurrence of each URL
        df = df.drop_duplicates(subset=['url'], keep='first')
        print(f"After removing URL duplicates: {df.shape}")
    
    # Sort by name for better readability
    df = df.sort_values('name')
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"\nCleaned data saved to: {output_file}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total assessments: {len(df)}")
    print(f"Remote testing available: {df['remote_testing'].value_counts().get('Yes', 0)}")
    print(f"Adaptive/IRT support: {df['adaptive_irt'].value_counts().get('Yes', 0)}")
    
    # Analyze test types
    test_types = []
    for types in df['test_type'].dropna():
        if types:
            test_types.extend([t.strip() for t in types.split(',')])
    
    if test_types:
        from collections import Counter
        type_counts = Counter(test_types)
        print("\nTest Type Distribution:")
        for test_type, count in type_counts.most_common():
            print(f"  {test_type}: {count}")
    
    return df

# If running as a script
if __name__ == "__main__":
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Input file (create this with your data)
    input_file = 'data/assessments_raw.csv'
    output_file = 'data/assessments.csv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Please create {input_file} with your assessment data.")
        print("The file should have the following columns:")
        print("name,url,duration,test_type,remote_testing,adaptive_irt")
    else:
        # Clean the data
        cleaned_df = clean_assessment_data(input_file, output_file)