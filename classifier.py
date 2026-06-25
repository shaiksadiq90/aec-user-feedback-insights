import psycopg2
from psycopg2.extras import Json
from openai import OpenAI
import json
import logging
from config import DATABASE_URL, OPENAI_API_KEY, OPENAI_MODEL, CLASSIFIER_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackClassifier:
    def __init__(self):
        self.db_url = DATABASE_URL
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    def connect_db(self):
        """Connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def get_unclassified_feedback(self, conn):
        """Fetch feedback that hasn't been classified yet"""
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rf.id, rf.review_text, rf.source
                FROM raw_feedback rf
                LEFT JOIN feedback_insights fi ON rf.id = fi.raw_feedback_id
                WHERE fi.id IS NULL
                ORDER BY rf.scraped_at DESC
                LIMIT 50;
            """)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def classify_feedback(self, review_text):
        """Use GPT-4o to classify a single review"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"{CLASSIFIER_PROMPT}\n\nReview to analyze:\n\n{review_text}"
                    }
                ]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text
            print(f"DEBUG: Raw response: {response_text[:200]}")
            
            # Try to parse JSON from response
            try:
                # Look for JSON block
                if '```json' in response_text:
                    json_str = response_text.split('```json')[1].split('```')[0].strip()
                elif '{' in response_text:
                    # Extract JSON object
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    json_str = response_text[start_idx:end_idx]
                else:
                    raise ValueError("No JSON found in response")
                
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {e}")
                logger.warning(f"Raw response: {response_text}")
                return None
        
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None
    
    def insert_insight(self, conn, raw_feedback_id, classification):
        """Insert classified insight into database"""
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback_insights (
                    raw_feedback_id,
                    user_outcome,
                    friction_point,
                    sentiment,
                    sentiment_score,
                    friction_category,
                    product_mention,
                    tyto_component,
                    tyto_specific_solution,
                    adoption_barrier,
                    adoption_lever,
                    outcome_amplification,
                    raw_output
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                raw_feedback_id,
                classification.get('user_outcome'),
                classification.get('friction_point'),
                classification.get('sentiment'),
                float(classification.get('sentiment_score', 0)),
                classification.get('friction_category'),
                classification.get('product_mention'),
                classification.get('tyto_component'),
                classification.get('tyto_specific_solution'),
                classification.get('adoption_barrier'),
                classification.get('adoption_lever'),
                classification.get('outcome_amplification'),
                Json(classification)
            ))
            
            conn.commit()
            logger.info(f"Inserted insight for feedback {raw_feedback_id}")
            return True
        except Exception as e:
            logger.error(f"Insert insight failed: {e}")
            conn.rollback()
            return False
    
    def run(self):
        """Execute classification pipeline"""
        logger.info("Starting feedback classifier...")
        
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set in .env")
            return
        
        conn = self.connect_db()
        if not conn:
            logger.error("Cannot proceed without database connection")
            return
        
        try:
            # Get unclassified feedback
            unclassified = self.get_unclassified_feedback(conn)
            logger.info(f"Found {len(unclassified)} unclassified reviews")
            
            if len(unclassified) == 0:
                logger.info("No unclassified feedback to process")
                return
            
            # Classify each review
            processed = 0
            for feedback_id, review_text, source in unclassified:
                logger.info(f"Classifying feedback {feedback_id} from {source}...")
                
                classification = self.classify_feedback(review_text)
                
                if classification:
                    if self.insert_insight(conn, feedback_id, classification):
                        processed += 1
                    else:
                        logger.warning(f"Failed to insert insight for {feedback_id}")
                else:
                    logger.warning(f"Failed to classify feedback {feedback_id}")
            
            logger.info(f"Classification complete: {processed}/{len(unclassified)} processed")
        
        finally:
            conn.close()

if __name__ == '__main__':
    classifier = FeedbackClassifier()
    classifier.run()
