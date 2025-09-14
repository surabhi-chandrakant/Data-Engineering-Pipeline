import json
import pandas as pd
import re
from typing import List, Dict
import random

class JobDescriptionAnnotator:
    def __init__(self):
        # Define annotation schema
        self.annotation_schema = {
            'experience_level': ['entry', 'mid', 'senior', 'lead'],
            'job_category': ['backend', 'frontend', 'fullstack', 'devops', 'data', 'mobile', 'qa'],
            'education_required': ['none', 'bachelors', 'masters', 'phd'],
            'remote_possible': ['yes', 'no', 'hybrid']
        }
    
    def load_cleaned_data(self, filename: str) -> List[Dict]:
        """Load cleaned JSON data"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Cleaned data file not found. Please run cleaner.py first.")
            return []
    
    def predict_experience_level(self, description: str, title: str) -> str:
        """Predict experience level based on content"""
        text = (title + ' ' + description).lower()
        
        # Strong indicators for senior level
        senior_indicators = [
            r'senior', r'sr\.', r'lead', r'principal', r'architect',
            r'5\+ years', r'8\+ years', r'10\+ years', r'experienced',
            r'mentor', r'guide', r'strateg', r'expert'
        ]
        
        # Indicators for entry level
        entry_indicators = [
            r'entry', r'junior', r'jr\.', r'graduate', r'0-2 years',
            r'1\+ years', r'2\+ years', r'fresher', r'beginner'
        ]
        
        # Check for senior indicators
        for pattern in senior_indicators:
            if re.search(pattern, text):
                return 'senior'
        
        # Check for entry indicators
        for pattern in entry_indicators:
            if re.search(pattern, text):
                return 'entry'
        
        # Default to mid-level
        return 'mid'
    
    def predict_job_category(self, description: str, skills: List[str]) -> str:
        """Predict job category based on skills and description"""
        text = description.lower()
        
        # Category keywords with weights
        category_keywords = {
            'backend': ['backend', 'server', 'api', 'microservices', 'java', 'python', 'c#', 'go', 'ruby'],
            'frontend': ['frontend', 'react', 'angular', 'vue', 'javascript', 'css', 'html', 'ui/ux'],
            'devops': ['devops', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'infrastructure'],
            'data': ['data', 'database', 'sql', 'nosql', 'etl', 'warehouse', 'analytics', 'big data'],
            'mobile': ['mobile', 'ios', 'android', 'swift', 'kotlin', 'react native', 'flutter'],
            'qa': ['qa', 'quality', 'test', 'selenium', 'automation', 'testing']
        }
        
        # Count matches for each category
        category_scores = {category: 0 for category in category_keywords}
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text):
                    category_scores[category] += 1
        
        # Also consider skills
        for skill in skills:
            for category, keywords in category_keywords.items():
                if skill in keywords:
                    category_scores[category] += 2  # Higher weight for explicit skills
        
        # Find category with highest score
        max_score = max(category_scores.values())
        if max_score == 0:
            return 'fullstack'  # Default if no clear category
        
        best_category = max(category_scores, key=category_scores.get)
        
        # If multiple categories have high scores, it's probably fullstack
        high_score_categories = [cat for cat, score in category_scores.items() if score >= max_score * 0.7]
        if len(high_score_categories) > 1:
            return 'fullstack'
        
        return best_category
    
    def predict_education(self, description: str) -> str:
        """Predict education requirement"""
        text = description.lower()
        
        if re.search(r'\bph\.?d\b|\bdoctorate\b', text):
            return 'phd'
        elif re.search(r'\bmaster\'?s\b|\bms\b|\bm\.?s\b|\bma\b', text):
            return 'masters'
        elif re.search(r'\bbachelor\'?s\b|\bbs\b|\bb\.?s\b|\bba\b|\bdegree\b', text):
            return 'bachelors'
        else:
            return 'none'
    
    def predict_remote(self, description: str, location: str) -> str:
        """Predict if remote work is possible"""
        text = (description + ' ' + location).lower()
        
        if re.search(r'\bremote\b|\bwork from home\b|\bwfh\b', text):
            return 'yes'
        elif re.search(r'\bhybrid\b|\bflexible\b|\bpartial\b', text):
            return 'hybrid'
        elif re.search(r'\bon.?site\b|\boffice\b|\bin.?person\b', text):
            return 'no'
        else:
            return 'unknown'
    
    def annotate_dataset(self, cleaned_data: List[Dict]) -> List[Dict]:
        """Annotate the dataset with predicted labels"""
        annotated_data = []
        
        for item in cleaned_data:
            description = item['description']
            title = item['title']
            skills = item['skills']
            location = item['location']
            
            annotations = {
                'experience_level': self.predict_experience_level(description, title),
                'job_category': self.predict_job_category(description, skills),
                'education_required': self.predict_education(description),
                'remote_possible': self.predict_remote(description, location),
                'annotation_method': 'rule_based'
            }
            
            # Create annotated item
            annotated_item = {**item, **annotations}
            annotated_data.append(annotated_item)
        
        return annotated_data
    
    def save_annotated_data(self, data: List[Dict], filename: str):
        """Save annotated data to JSON and CSV"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create simplified CSV for viewing
        csv_data = []
        for item in data:
            csv_item = {
                'title': item['title'],
                'company': item['company'],
                'experience_level': item['experience_level'],
                'job_category': item['job_category'],
                'education_required': item['education_required'],
                'remote_possible': item['remote_possible'],
                'skills': ', '.join(item['skills'][:5]),
                'source': item['source']
            }
            csv_data.append(csv_item)
        
        df = pd.DataFrame(csv_data)
        csv_filename = filename.replace('.json', '.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"Saved {len(data)} annotated job descriptions to {filename}")

def main():
    annotator = JobDescriptionAnnotator()
    
    print("Loading cleaned data...")
    cleaned_data = annotator.load_cleaned_data('data/cleaned_job_descriptions.json')
    
    if not cleaned_data:
        print("No cleaned data found. Exiting.")
        return
    
    print(f"Loaded {len(cleaned_data)} cleaned job descriptions")
    
    print("Annotating data...")
    annotated_data = annotator.annotate_dataset(cleaned_data)
    
    print("Saving annotated data...")
    annotator.save_annotated_data(annotated_data, 'data/annotated_job_descriptions.json')
    
    # Show annotation statistics
    print("\nAnnotation Statistics:")
    experience_counts = {}
    category_counts = {}
    education_counts = {}
    
    for item in annotated_data:
        exp = item['experience_level']
        cat = item['job_category']
        edu = item['education_required']
        
        experience_counts[exp] = experience_counts.get(exp, 0) + 1
        category_counts[cat] = category_counts.get(cat, 0) + 1
        education_counts[edu] = education_counts.get(edu, 0) + 1
    
    print(f"Experience Levels: {experience_counts}")
    print(f"Job Categories: {category_counts}")
    print(f"Education Requirements: {education_counts}")
    
    # Show sample annotations
    print("\nSample Annotations:")
    for i, item in enumerate(annotated_data[:3]):
        print(f"\n{i+1}. {item['title'].title()} at {item['company'].title()}")
        print(f"   Experience: {item['experience_level']}")
        print(f"   Category: {item['job_category']}")
        print(f"   Education: {item['education_required']}")
        print(f"   Remote: {item['remote_possible']}")
        print(f"   Skills: {', '.join(item['skills'][:3])}...")

if __name__ == "__main__":
    main()