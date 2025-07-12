"""
Web scraper for PMC (Prime Minister's Office) website
"""
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
from typing import List, Dict, Any, Set
import os
from utils import (
    setup_logging, clean_text, chunk_text, save_data, 
    get_config, validate_config, extract_metadata
)

logger = setup_logging()

class PMCScraper:
    def __init__(self):
        self.config = get_config()
        if not validate_config(self.config):
            raise ValueError("Invalid configuration")
        
        self.base_url = self.config['base_url']
        self.max_pages = self.config['max_pages']
        self.request_delay = self.config['request_delay']
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict[str, Any]] = []
        
    def get_page_content(self, url: str) -> BeautifulSoup | None:
        """Fetch and parse page content"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(self.request_delay)
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        if not soup:
            return ""
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Find main content areas
        content_selectors = [
            'main', 'article', '.content', '.main-content', 
            '#content', '#main', '.post-content', '.entry-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text() for elem in elements])
                break
        
        # If no main content found, get body text
        if not content:
            content = soup.get_text()
        
        return clean_text(content)
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        if not soup:
            return ""
        
        # Try different title selectors
        title_selectors = ['h1', '.title', '.page-title', 'title']
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title:
                    return title
        
        return ""
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links from page"""
        if not soup:
            return []
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urllib.parse.urljoin(base_url, href)
            elif href.startswith('http'):
                # Only include links from the same domain
                if self.base_url in href:
                    href = href
                else:
                    continue
            else:
                continue
            
            # Clean URL
            href = urllib.parse.urljoin(base_url, href)
            if href not in self.visited_urls:
                links.append(href)
        
        return list(set(links))
    
    def scrape_page(self, url: str) -> Dict[str, Any] | None:
        """Scrape a single page"""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        soup = self.get_page_content(url)
        if not soup:
            return None
        
        title = self.extract_title(soup)
        content = self.extract_text_content(soup)
        
        if not content or len(content) < 50:  # Skip pages with minimal content
            return None
        
        # Chunk the content
        chunks = chunk_text(content, chunk_size=1000, overlap=200)
        
        page_data = {
            'url': url,
            'title': title,
            'content': content,
            'chunks': chunks,
            'metadata': extract_metadata(url, title)
        }
        
        logger.info(f"Scraped: {title} ({len(content)} characters, {len(chunks)} chunks)")
        return page_data
    
    def scrape_website(self) -> List[Dict[str, Any]]:
        """Main scraping function"""
        logger.info(f"Starting to scrape {self.base_url}")
        
        # Start with the main page
        main_page = self.scrape_page(self.base_url)
        if main_page:
            self.scraped_data.append(main_page)
        
        # Get links from main page
        soup = self.get_page_content(self.base_url)
        if soup:
            links = self.extract_links(soup, self.base_url)
            
            # Scrape linked pages
            for i, link in enumerate(links[:self.max_pages]):
                if len(self.scraped_data) >= self.max_pages:
                    break
                
                page_data = self.scrape_page(link)
                if page_data:
                    self.scraped_data.append(page_data)
                
                logger.info(f"Progress: {len(self.scraped_data)}/{self.max_pages} pages scraped")
        
        logger.info(f"Scraping completed. Total pages: {len(self.scraped_data)}")
        return self.scraped_data
    
    def save_scraped_data(self, filename: str = "data/pmc_scraped_data.json"):
        """Save scraped data to file"""
        save_data(self.scraped_data, filename)
        logger.info(f"Data saved to {filename}")
    
    def get_sample_data(self) -> List[Dict[str, Any]]:
        """Get sample data for testing (without scraping)"""
        sample_data = [
            {
                'url': 'https://www.pmc.gov.in/',
                'title': 'Prime Minister\'s Office',
                'content': 'The Prime Minister\'s Office (PMO) is the administrative office of the Prime Minister of India. It is responsible for providing secretarial assistance to the Prime Minister.',
                'chunks': ['The Prime Minister\'s Office (PMO) is the administrative office of the Prime Minister of India. It is responsible for providing secretarial assistance to the Prime Minister.'],
                'metadata': extract_metadata('https://www.pmc.gov.in/', 'Prime Minister\'s Office')
            },
            {
                'url': 'https://www.pmc.gov.in/about-pmo',
                'title': 'About PMO',
                'content': 'The Prime Minister\'s Office (PMO) consists of the immediate staff of the Prime Minister of India, as well as multiple levels of support staff reporting to the Prime Minister.',
                'chunks': ['The Prime Minister\'s Office (PMO) consists of the immediate staff of the Prime Minister of India, as well as multiple levels of support staff reporting to the Prime Minister.'],
                'metadata': extract_metadata('https://www.pmc.gov.in/about-pmo', 'About PMO')
            }
        ]
        return sample_data

def main():
    """Main function to run the scraper"""
    try:
        scraper = PMCScraper()
        
        # Check if data already exists
        if os.path.exists("data/pmc_scraped_data.json"):
            print("Scraped data already exists. Use existing data or delete to re-scrape.")
            return
        
        # Scrape the website
        scraped_data = scraper.scrape_website()
        
        if scraped_data:
            scraper.save_scraped_data()
            print(f"Successfully scraped {len(scraped_data)} pages")
        else:
            print("No data was scraped. Using sample data for testing.")
            sample_data = scraper.get_sample_data()
            scraper.scraped_data = sample_data
            scraper.save_scraped_data()
            
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 
