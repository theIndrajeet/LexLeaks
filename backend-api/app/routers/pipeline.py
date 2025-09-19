from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from sqlalchemy.orm import Session

from ..database import get_db
from ..web_scraper import legal_scraper
from ..gemini_topic_agent import gemini_topic_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.get("/scrape-legal-news")
async def scrape_legal_news():
    """Manually trigger legal news scraping"""
    try:
        logger.info(" Manual legal news scraping triggered")
        
        async with legal_scraper as scraper:
            articles = await scraper.scrape_all_sources()
        
        stats = scraper.get_scraping_stats()
        
        return {
            "success": True,
            "message": f"Scraped {len(articles)} legal articles",
            "articles_count": len(articles),
            "stats": stats,
            "articles": articles if articles else []
        }
        
    except Exception as e:
        logger.error(f"Error in manual scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/generate-topics")
async def generate_topics_from_scraped_data():
    """Generate trending topics from scraped data using Gemini AI"""
    try:
        logger.info("🤖 Manual topic generation triggered")
        
        # First scrape fresh data
        async with legal_scraper as scraper:
            articles = await scraper.scrape_all_sources()
        
        if not articles:
            return {
                "success": False,
                "message": "No articles found to generate topics from",
                "topics": []
            }
        
        # Generate topics using Gemini AI
        topics = await gemini_topic_agent.generate_trending_topics(articles, num_topics=5)
        
        return {
            "success": True,
            "message": f"Generated {len(topics)} trending topics",
            "topics": topics,
            "source_articles_count": len(articles)
        }
        
    except Exception as e:
        logger.error(f"Error in topic generation: {e}")
        raise HTTPException(status_code=500, detail=f"Topic generation failed: {str(e)}")

@router.get("/test-full-pipeline")
async def test_full_pipeline():
    """Test the complete pipeline: Scraping → Gemini AI → Topic Generation"""
    try:
        logger.info(" Testing full pipeline...")
        
        # Step 1: Scrape legal news
        logger.info("Step 1: Scraping legal news...")
        async with legal_scraper as scraper:
            articles = await scraper.scrape_all_sources()
        
        scraping_stats = scraper.get_scraping_stats()
        
        # Step 2: Generate topics with Gemini AI
        logger.info("Step 2: Generating topics with Gemini AI...")
        topics = await gemini_topic_agent.generate_trending_topics(articles, num_topics=3)
        
        agent_stats = gemini_topic_agent.get_agent_stats()
        
        return {
            "success": True,
            "message": "Full pipeline test completed",
            "pipeline_results": {
                "scraping": {
                    "articles_found": len(articles),
                    "stats": scraping_stats
                },
                "topic_generation": {
                    "topics_generated": len(topics),
                    "topics": topics,
                    "agent_stats": agent_stats
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error in full pipeline test: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline test failed: {str(e)}")

@router.get("/scraper-stats")
async def get_scraper_stats():
    """Get statistics about the web scraper"""
    try:
        stats = legal_scraper.get_scraping_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting scraper stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scraper stats: {str(e)}")

@router.get("/gemini-stats")
async def get_gemini_stats():
    """Get statistics about the Gemini topic agent"""
    try:
        stats = gemini_topic_agent.get_agent_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting Gemini stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Gemini stats: {str(e)}")

@router.get("/test-gemini-api")
async def test_gemini_api():
    """Test Gemini API connectivity and configuration"""
    try:
        import os
        import google.generativeai as genai
        
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        api_key_status = "Found" if api_key else "NOT FOUND"
        
        # Test API call if key is available
        test_result = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Test connection - respond with 'OK'")
                test_result = {
                    "status": "success",
                    "response": response.text[:100] if response.text else "No response"
                }
            except Exception as e:
                test_result = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "success": True,
            "api_key_status": api_key_status,
            "api_key_length": len(api_key) if api_key else 0,
            "gemini_available": gemini_topic_agent.gemini_available,
            "test_result": test_result,
            "environment": "production" if os.getenv("K_SERVICE") else "development"
        }
    except Exception as e:
        logger.error(f"Error testing Gemini API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test Gemini API: {str(e)}")

@router.get("/test-simple-gemini")
async def test_simple_gemini():
    """Test simple Gemini API call"""
    try:
        import os
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "No Gemini API key found",
                "api_key_status": "NOT FOUND"
            }
        
        # Test simple API call
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Hello from Gemini'")
        
        return {
            "success": True,
            "api_key_status": "FOUND",
            "api_key_length": len(api_key),
            "response": response.text if response.text else "No response",
            "environment": "production" if os.getenv("K_SERVICE") else "development"
        }
        
    except Exception as e:
        logger.error(f"Simple Gemini test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "api_key_status": "FOUND" if os.getenv("GEMINI_API_KEY") else "NOT FOUND"
        }

@router.post("/manual-pipeline-run")
async def manual_pipeline_run():
    """Manually run the complete pipeline (same as scheduler would do)"""
    try:
        logger.info(" Manual pipeline run triggered")
        
        # This replicates what the scheduler does at 6 AM
        from ..scheduler_service import scheduler_service
        await scheduler_service._generate_trending_articles()
        
        return {
            "success": True,
            "message": "Manual pipeline run completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in manual pipeline run: {e}")
        raise HTTPException(status_code=500, detail=f"Manual pipeline run failed: {str(e)}")
