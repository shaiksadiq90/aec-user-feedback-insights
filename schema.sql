-- AEC User Feedback Insights Database Schema

CREATE DATABASE aec_feedback;

\c aec_feedback;

-- Raw feedback from various sources
CREATE TABLE raw_feedback (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL, -- 'g2', 'reddit', 'appstore', 'twitter'
    source_id VARCHAR(255) UNIQUE,
    review_text TEXT NOT NULL,
    author VARCHAR(255),
    rating DECIMAL(3,1),
    url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP
);

-- Classified insights with AI analysis
CREATE TABLE feedback_insights (
    id SERIAL PRIMARY KEY,
    raw_feedback_id INTEGER NOT NULL REFERENCES raw_feedback(id) ON DELETE CASCADE,
    user_outcome TEXT,
    friction_point TEXT,
    sentiment VARCHAR(20), -- 'positive', 'neutral', 'negative'
    sentiment_score DECIMAL(3,2), -- 0.0 to 1.0
    friction_category VARCHAR(100),
    product_mention VARCHAR(100), -- 'revit', 'civil3d', 'autodesk_docs', etc.
    ai_solution TEXT,
    solution_type VARCHAR(100), -- 'automation', 'knowledge_graph', 'orchestration', 'analytics', 'prediction', etc.
    adoption_barrier VARCHAR(100),
    adoption_lever TEXT,
    outcome_amplification TEXT,
    confidence_score DECIMAL(3,2),
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_output JSONB -- Store full GPT-4o response
);

-- Aggregated friction patterns for dashboarding
CREATE TABLE friction_patterns (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100),
    description TEXT,
    mention_count INTEGER,
    sentiment_distribution JSONB, -- {positive: X, neutral: Y, negative: Z}
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TYTO-specific opportunities
CREATE TABLE tyto_opportunities (
    id SERIAL PRIMARY KEY,
    opportunity_name VARCHAR(200),
    description TEXT,
    affected_user_segment VARCHAR(100),
    potential_impact VARCHAR(100),
    supporting_feedback_count INTEGER,
    priority VARCHAR(20), -- 'high', 'medium', 'low'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_raw_feedback_source ON raw_feedback(source);
CREATE INDEX idx_raw_feedback_created_at ON raw_feedback(created_at);
CREATE INDEX idx_insights_sentiment ON feedback_insights(sentiment);
CREATE INDEX idx_insights_friction ON feedback_insights(friction_category);
CREATE INDEX idx_insights_product ON feedback_insights(product_mention);
