"""
Personal Brand Supertool
========================

Compresses the loop between "what is winning in my niche" and "what I make next".

Pipeline (first-principles layers):
    1. Ingestion        -> brand_supertool.ingestion
    2. Intelligence     -> brand_supertool.intelligence  (fuzzy scoring + falsify eval)
    3. Brand filter     -> brand_supertool.brand
    4. Reporting        -> brand_supertool.reporting

Runs end-to-end on bundled sample data with ZERO API keys.
Add YOUTUBE_API_KEY / ANTHROPIC_API_KEY to .env to go live.
"""

__version__ = "0.1.0"
