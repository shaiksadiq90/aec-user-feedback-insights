import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import Json
import json
from datetime import datetime
import time
import logging
from config import DATABASE_URL, SCRAPER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackScraper:
    def __init__(self):
        self.db_url = DATABASE_URL
        self.config = SCRAPER_CONFIG
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def connect_db(self):
        """Connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def insert_feedback(self, conn, source, source_id, review_text, author, rating, url, created_at):
        """Insert raw feedback into database"""
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raw_feedback (source, source_id, review_text, author, rating, url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id) DO NOTHING
                RETURNING id;
            """, (source, source_id, review_text, author, rating, url, created_at))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                logger.info(f"Inserted feedback from {source}: {source_id}")
                return result[0]
            else:
                logger.info(f"Feedback already exists: {source_id}")
                return None
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            conn.rollback()
            return None
    
    def scrape_g2_mock(self, conn):
        """
        Mock G2 scraper - returns sample AEC feedback with TYTO-relevant pain points
        In production, replace with actual BeautifulSoup scraping of g2.com
        """
        mock_reviews = [
            {
                'source_id': 'g2_revit_001',
                'text': 'Revit is powerful but onboarding is steep. New team members spend 6 weeks just learning the interface before they can contribute meaningful designs.',
                'author': 'AEC Architect',
                'rating': 3.5,
                'url': 'https://www.g2.com/products/revit',
                'created_at': datetime(2024, 6, 10)
            },
            {
                'source_id': 'g2_revit_002',
                'text': 'MEP coordination with other teams is painful. Our mechanical engineer, structural team, and architects constantly have to manually detect clashes. These meetings take 3+ hours per week.',
                'author': 'Structural Engineer',
                'rating': 2.5,
                'url': 'https://www.g2.com/products/revit',
                'created_at': datetime(2024, 6, 12)
            },
            {
                'source_id': 'g2_civil3d_001',
                'text': 'Civil 3D works great for the design, but getting data into construction documents is a nightmare. Every export requires manual tweaking across multiple tools.',
                'author': 'Infrastructure Designer',
                'rating': 3.0,
                'url': 'https://www.g2.com/products/civil-3d',
                'created_at': datetime(2024, 6, 8)
            },
            {
                'source_id': 'g2_revit_003',
                'text': 'BIM is fantastic for visualizing designs. Would love if the software could auto-generate sustainability analysis and suggest code-compliant modifications in real-time.',
                'author': 'Design Firm Lead',
                'rating': 4.0,
                'url': 'https://www.g2.com/products/revit',
                'created_at': datetime(2024, 6, 15)
            },
            {
                'source_id': 'g2_docs_001',
                'text': 'Autodesk Docs is supposed to be collaborative, but coordinating changes across distributed teams is clunky. Version control is confusing and tracking who changed what is painful.',
                'author': 'Project Manager',
                'rating': 2.0,
                'url': 'https://www.g2.com/products/autodesk-docs',
                'created_at': datetime(2024, 6, 14)
            },
            {
                'source_id': 'g2_revit_004',
                'text': 'Revit is incredibly powerful but the learning curve is the biggest barrier. Small firms like ours cant justify the training time and costs. We need something more intuitive.',
                'author': 'Small Firm Owner',
                'rating': 3.0,
                'url': 'https://www.g2.com/products/revit',
                'created_at': datetime(2024, 6, 9)
            },
            {
                'source_id': 'g2_navisworks_001',
                'text': 'Navisworks clash detection is fantastic. But once we find clashes, suggesting which discipline should move what, and why, still requires expert judgment. AI could help here.',
                'author': 'Construction Manager',
                'rating': 3.5,
                'url': 'https://www.g2.com/products/navisworks',
                'created_at': datetime(2024, 6, 11)
            },
            {
                'source_id': 'g2_civil3d_002',
                'text': 'Performance crashing on large site models. Working with 500k+ survey points is slow and unstable. We need better AI-assisted simplification and context filtering.',
                'author': 'Civil Consultant',
                'rating': 2.0,
                'url': 'https://www.g2.com/products/civil-3d',
                'created_at': datetime(2024, 6, 13)
            }
        ]
        
        logger.info(f"Scraping {len(mock_reviews)} mock G2 reviews...")
        for review in mock_reviews:
            self.insert_feedback(
                conn,
                source='g2',
                source_id=review['source_id'],
                review_text=review['text'],
                author=review['author'],
                rating=review['rating'],
                url=review['url'],
                created_at=review['created_at']
            )
            time.sleep(0.5)  # Rate limiting
        
        logger.info("Mock G2 scrape complete")
    
    def scrape_reddit_mock(self, conn):
        """Mock Reddit scraper - returns sample AEC feedback"""
        mock_posts = [
            {
                'source_id': 'reddit_revit_collab',
                'text': 'Anyone else find Revit collaboration workflows confusing? We have 4 offices using BIM Collaborate and the model updates are inconsistent.',
                'author': 'aec_designer_123',
                'rating': None,
                'url': 'https://www.reddit.com/r/Revit',
                'created_at': datetime(2024, 6, 15)
            },
            {
                'source_id': 'reddit_civil3d_perf',
                'text': 'Civil 3D is killing our productivity with large files. Any tips for optimization? The software just freezes.',
                'author': 'infrastructure_guy',
                'rating': None,
                'url': 'https://www.reddit.com/r/cad',
                'created_at': datetime(2024, 6, 14)
            }
        ]
        
        logger.info(f"Scraping {len(mock_posts)} mock Reddit posts...")
        for post in mock_posts:
            self.insert_feedback(
                conn,
                source='reddit',
                source_id=post['source_id'],
                review_text=post['text'],
                author=post['author'],
                rating=post['rating'],
                url=post['url'],
                created_at=post['created_at']
            )
            time.sleep(0.5)
        
        logger.info("Mock Reddit scrape complete")
    
    def run(self):
        """Execute scraper pipeline"""
        logger.info("Starting feedback scraper...")
        
        conn = self.connect_db()
        if not conn:
            logger.error("Cannot proceed without database connection")
            return
        
        try:
            # Run scrapers
            self.scrape_g2_mock(conn)
            self.scrape_reddit_mock(conn)
            
            logger.info("Scraper pipeline complete")
        finally:
            conn.close()

if __name__ == '__main__':
    scraper = FeedbackScraper()
    scraper.run()
