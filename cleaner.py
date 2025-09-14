import json
import re
import pandas as pd
from typing import List, Dict
import html

class DataCleaner:
    def __init__(self):
        self.tech_skills = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'spring', 'sql', 'nosql', 'mongodb',
            'postgresql', 'mysql', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 
            'git', 'jenkins', 'agile', 'scrum', 'rest', 'api', 'microservices',
            'tensorflow', 'pytorch', 'machine learning', 'ai', 'ci/cd', 'linux',
            'html', 'css', 'bootstrap', 'tailwind', 'redis', 'kafka', 'rabbitmq'
        }
    
    def load_raw_data(self, filename: str) -> List[Dict]:
        """Load raw JSON data"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Raw data file not found. Please run scraper.py first.")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text or not isinstance(text, str):
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert to lowercase
        text = text.lower()
        
        return text
    
    def remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicate job descriptions"""
        seen = set()
        unique_data = []
        
        for item in data:
            # Create fingerprint based on title and first 100 chars of description
            desc_preview = item.get('description', '')[:100].lower()
            fingerprint = f"{item.get('title', '').lower()}_{desc_preview}"
            
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique_data.append(item)
        
        return unique_data
    
    def extract_skills(self, description: str) -> List[str]:
        """Extract technical skills from job description"""
        found_skills = []
        description_lower = description.lower()
        
        for skill in self.tech_skills:
            if re.search(rf'\b{re.escape(skill)}\b', description_lower):
                found_skills.append(skill)
        
        # Remove duplicates and sort
        return sorted(list(set(found_skills)))
    
    def clean_dataset(self, raw_data: List[Dict]) -> List[Dict]:
        """Main cleaning pipeline"""
        cleaned_data = []
        
        for item in raw_data:
            # Clean all text fields
            cleaned_item = {
                'title': self.clean_text(item.get('title', '')),
                'company': self.clean_text(item.get('company', '')),
                'location': self.clean_text(item.get('location', '')),
                'description': self.clean_text(item.get('description', '')),
                'source': item.get('source', ''),
                'url': item.get('url', '')
            }
            
            # Skip if essential fields are missing or too short
            if (not cleaned_item['title'] or 
                not cleaned_item['description'] or 
                len(cleaned_item['description'].split()) < 30):
                continue
            
            # Extract skills and add metadata
            cleaned_item['skills'] = self.extract_skills(cleaned_item['description'])
            cleaned_item['word_count'] = len(cleaned_item['description'].split())
            cleaned_item['char_count'] = len(cleaned_item['description'])
            
            cleaned_data.append(cleaned_item)
        
        # Remove duplicates
        cleaned_data = self.remove_duplicates(cleaned_data)
        
        return cleaned_data
    
    def save_cleaned_data(self, data: List[Dict], filename: str):
        """Save cleaned data to JSON and CSV"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create CSV version
        csv_data = []
        for item in data:
            csv_item = {
                'title': item['title'],
                'company': item['company'],
                'location': item['location'],
                'description': item['description'][:200] + '...' if len(item['description']) > 200 else item['description'],
                'skills': ', '.join(item['skills']),
                'word_count': item['word_count'],
                'source': item['source']
            }
            csv_data.append(csv_item)
        
        df = pd.DataFrame(csv_data)
        csv_filename = filename.replace('.json', '.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"Saved {len(data)} cleaned job descriptions to {filename}")

def main():
    cleaner = DataCleaner()
    
    print("Loading raw data...")
    raw_data = cleaner.load_raw_data('data/raw_job_descriptions.json')
    
    if not raw_data:
        print("No raw data found. Exiting.")
        return
    
    print(f"Loaded {len(raw_data)} raw job descriptions")
    
    print("Cleaning data...")
    cleaned_data = cleaner.clean_dataset(raw_data)
    print(f"After cleaning: {len(cleaned_data)} job descriptions")
    
    print("Saving cleaned data...")
    cleaner.save_cleaned_data(cleaned_data, 'data/cleaned_job_descriptions.json')
    
    # Show statistics
    total_words = sum(item['word_count'] for item in cleaned_data)
    avg_words = total_words / len(cleaned_data) if cleaned_data else 0
    
    print(f"\nCleaning Statistics:")
    print(f"Average description length: {avg_words:.1f} words")
    print(f"Total skills identified: {sum(len(item['skills']) for item in cleaned_data)}")

if __name__ == "__main__":
    main()