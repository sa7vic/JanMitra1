import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from models.database import db, Article

class DataCollector:
    def __init__(self):
        self.sources = self.load_sources()
    
    def load_sources(self):
        """Load RSS feed sources"""
        return [
            {
                'name': 'The Times of India',
                'rss': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
                'category': 'general'
            },
            {
                'name': 'The Hindu',
                'rss': 'https://www.thehindu.com/news/national/feeder/default.rss',
                'category': 'general'
            },
            {
                'name': 'Indian Express',
                'rss': 'https://indianexpress.com/feed/',
                'category': 'general'
            },
            {
                'name': 'Economic Times',
                'rss': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
                'category': 'economy'
            },
            {
                'name': 'NDTV',
                'rss': 'https://feeds.feedburner.com/ndtvnews-top-stories',
                'category': 'general'
            },
            {
                'name': 'Business Standard',
                'rss': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
                'category': 'economy'
            },
            {
                'name': 'Hindustan Times',
                'rss': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
                'category': 'general'
            },
            {
                'name': 'Deccan Herald',
                'rss': 'https://www.deccanherald.com/rss/national.rss',
                'category': 'general'
            },
            {
                'name': 'Money Control',
                'rss': 'https://www.moneycontrol.com/rss/latestnews.xml',
                'category': 'economy'
            },
            {
                'name': 'Livemint',
                'rss': 'https://www.livemint.com/rss/news',
                'category': 'economy'
            },
            # Add more sources as needed
        ]
    
    def fetch_articles(self, max_per_source=10):
        """Fetch articles from all RSS sources"""
        articles_collected = 0
        
        for source in self.sources:
            try:
                print(f"📰 Fetching from {source['name']}...")
                feed = feedparser.parse(source['rss'])
                
                for entry in feed.entries[:max_per_source]:
                    # Check if article already exists
                    existing = Article.query.filter_by(url=entry.link).first()
                    if existing:
                        continue
                    
                    # Get full content
                    content = self.extract_content(entry)
                    
                    # Create article
                    article = Article(
                        title=entry.title,
                        content=content,
                        source=source['name'],
                        url=entry.link,
                        category=source['category'],
                        published_at=self.parse_date(entry.get('published'))
                    )
                    
                    db.session.add(article)
                    articles_collected += 1
                
                db.session.commit()
                print(f"✅ Collected {articles_collected} new articles from {source['name']}")
                
            except Exception as e:
                print(f"❌ Error fetching from {source['name']}: {e}")
                continue
        
        print(f"\n🎉 Total new articles collected: {articles_collected}")
        return articles_collected
    
    def extract_content(self, entry):
        """Extract content from RSS entry"""
        # Try different fields
        content = entry.get('summary', '')
        if not content:
            content = entry.get('description', '')
        if not content:
            content = entry.get('content', [{}])[0].get('value', '')
        
        # Clean HTML
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(separator=' ', strip=True)
        
        # Fallback to title if no content
        return content if content else entry.title
    
    def parse_date(self, date_string):
        """Parse date from RSS feed"""
        if not date_string:
            return datetime.utcnow()
        
        try:
            from dateutil import parser
            return parser.parse(date_string)
        except:
            return datetime.utcnow()
    
    def get_latest_articles(self, limit=100):
        """Get latest articles from database"""
        return Article.query.order_by(Article.created_at.desc()).limit(limit).all()


# Quick test function
if __name__ == "__main__":
    collector = DataCollector()
    collector.fetch_articles(max_per_source=5)