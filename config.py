import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aec_feedback')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4o"

# Scraping Configuration
SCRAPER_CONFIG = {
    'g2': {
        'base_url': 'https://www.g2.com',
        'search_terms': ['revit', 'autodesk', 'bim', 'civil 3d'],
        'timeout': 10,
    },
    'reddit': {
        'subreddits': ['Autodesk', 'Revit', 'BIM', 'AEC'],
        'timeout': 10,
    },
    'appstore': {
        'app_ids': ['revit', 'autocad'],
        'timeout': 10,
    }
}

# Classifier Configuration
CLASSIFIER_PROMPT = """
You are an expert product insights analyst for Autodesk's AEC (Architecture, Engineering, Construction) product suite.

Analyze the following user review and extract structured insights:

1. **User Outcome**: What is the user fundamentally trying to achieve? (extract intent, not tool complaint)
2. **Friction Point**: What's preventing them from achieving this outcome?
3. **Sentiment**: Classify as 'positive', 'neutral', or 'negative'
4. **Sentiment Score**: 0.0-1.0 (0=very negative, 1=very positive)
5. **Friction Category**: Primary pain point (e.g., 'onboarding', 'mep_coordination', 'collaboration', 'learning_curve', 'performance', 'integration', 'cost')
6. **Product Mention**: Which Autodesk product is referenced (revit, civil3d, autodesk_docs, navisworks, etc.)
7. **AI Solution**: Describe how AI/automation could solve this friction (e.g., "Automated clash detection and remediation suggestions")
8. **Solution Type**: What type of AI capability helps? (automation, knowledge_graph, orchestration, analytics, prediction, etc.)
9. **Adoption Barrier**: What prevents adoption? (tool_switching, learning_curve, change_management, integration_complexity, etc.)
10. **Adoption Lever**: How could this barrier be removed? (e.g., "Unified workspace eliminating tool-switching")
11. **Outcome Amplification**: How would solving this friction free users to focus on creative work instead of mechanics?

Return response as valid JSON with these exact keys: user_outcome, friction_point, sentiment, sentiment_score, friction_category, product_mention, ai_solution, solution_type, adoption_barrier, adoption_lever, outcome_amplification
"""
