# Data Engineering Pipeline

## 🎯 Project Overview
This project implements an end-to-end data engineering pipeline specifically designed for collecting, processing, and annotating software engineering job descriptions to power AI recruitment models. The pipeline focuses on remote job positions sourced from reliable APIs.

## 📊 Pipeline Architecture

### 1. Data Collection Layer
**Primary Source:** RemoteOK API - providing real-time remote job listings  
**Fallback Mechanism:** Sample data generation when APIs are unavailable  

**Key Features:**
- API integration with proper error handling
- Real-time data acquisition
- Structured JSON response parsing
- Graceful degradation to ensure data availability

### 2. Data Processing Layer
**Cleaning Operations:**
- HTML tag and entity removal
- Text normalization (lowercase, whitespace handling)
- Special character cleaning
- Duplicate detection and removal

**Quality Assurance:**
- Minimum length validation (30+ words)
- Empty field filtering
- Skill keyword extraction
- Metadata enrichment

### 3. Annotation Layer
**Labeling System:**
- Experience Level: entry, mid, senior, lead
- Job Category: backend, frontend, fullstack, devops, data
- Education Requirements: none, bachelors, masters, phd
- Remote Status: yes, no, hybrid

**Annotation Method:** Rule-based keyword matching with weighted scoring

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.8+:** Primary programming language
- **Requests:** HTTP API interactions
- **Pandas:** Data manipulation and CSV export
- **JSON:** Data serialization and storage
- **Regular Expressions:** Text pattern matching

### Key Libraries
```bash
requests==2.31.0
beautifulsoup4==4.12.2
pandas==2.0.3
numpy==1.24.3
lxml==4.9.3
html5lib==1.1
