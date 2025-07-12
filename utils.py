"""
Utility functions for PMC Chatbot
"""
import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pmc_chatbot.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
    
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def save_data(data: List[Dict[str, Any]], filename: str):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(filename: str) -> List[Dict[str, Any]]:
    """Load data from JSON file"""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'model_name': os.getenv('MODEL_NAME', 'gpt-3.5-turbo'),
        'temperature': float(os.getenv('TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
        'base_url': os.getenv('BASE_URL', 'https://www.pmc.gov.in'),
        'max_pages': int(os.getenv('MAX_PAGES', '50')),
        'request_delay': float(os.getenv('REQUEST_DELAY', '1')),
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', './models/chroma_db'),
        'embedding_model_name': os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
    }

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration"""
    if not config['openai_api_key']:
        print("ERROR: OPENAI_API_KEY is required. Please set it in your .env file.")
        return False
    
    if not config['base_url']:
        print("ERROR: BASE_URL is required.")
        return False
    
    return True

def format_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def extract_metadata(url: str, title: str = "") -> Dict[str, str]:
    """Extract metadata from URL and title"""
    return {
        'url': url,
        'title': title,
        'domain': 'pmc.gov.in',
        'timestamp': format_timestamp()
    } 
