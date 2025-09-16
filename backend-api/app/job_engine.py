import asyncio
import logging
import httpx
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import google.generativeai as genai
from app.config import GEMINI_API_KEY
from bs4 import BeautifulSoup
import random
import time
import json

logger = logging.getLogger(__name__)

class GeminiJobEnhancer:
    """AI-powered job enhancement using Gemini"""
    
    def __init__(self):
        self.genai = genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def enhance_job_posting(self, raw_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw job data into intelligent, structured information"""
        try:
            prompt = f"""
            Analyze this legal job posting and enhance it with:
            
            1. WORK LOCATION CLASSIFICATION:
               - Remote (100% work from home)
               - Hybrid (2-3 days remote)
               - Office (on-site required)
               - Flexible (mix of options)
            
            2. SALARY INTELLIGENCE:
               - Extract salary range if provided
               - Estimate market rate if missing
               - Identify if competitive for location
            
            3. LEGAL SPECIALIZATION:
               - Practice area (Corporate, Criminal, IP, etc.)
               - Experience level (Entry/Mid/Senior)
               - Firm size (Boutique/Mid-size/Big Law)
               - Practice type (Litigation/Transactional/Regulatory)
            
            4. QUALITY SCORING (1-10):
               - Completeness of information
               - Professional presentation
               - Clear requirements
               - Competitive benefits
            
            5. CAREER INSIGHTS:
               - Growth potential
               - Learning opportunities
               - Company culture indicators
               - Work-life balance signals
            
            Raw job data: {raw_job_data}
            
            Return the analysis in JSON format with these fields:
            - work_type: "remote" | "hybrid" | "office" | "flexible"
            - salary_min: number or null
            - salary_max: number or null
            - practice_area: string
            - experience_level: "entry" | "mid" | "senior"
            - firm_size: "boutique" | "mid-size" | "big-law"
            - practice_type: "litigation" | "transactional" | "regulatory"
            - quality_score: number (1-10)
            - career_insights: string
            - is_remote: boolean
            - is_hybrid: boolean
            - is_office: boolean
            """
            
            response = await self.model.generate_content_async(prompt)
            return self.parse_enhanced_data(response.text)
            
        except Exception as e:
            logger.error(f"Error enhancing job posting: {e}")
            return self.get_default_enhancement(raw_job_data)
    
    def parse_enhanced_data(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""
        try:
            # Simple parsing - in production, use proper JSON parsing
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self.get_default_enhancement({})
                
        except Exception as e:
            logger.error(f"Error parsing enhanced data: {e}")
            return self.get_default_enhancement({})
    
    def get_default_enhancement(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback enhancement when AI fails"""
        return {
            "work_type": "office",
            "salary_min": None,
            "salary_max": None,
            "practice_area": "General Legal",
            "experience_level": "mid",
            "firm_size": "mid-size",
            "practice_type": "litigation",
            "quality_score": 5.0,
            "career_insights": "Standard legal position",
            "is_remote": False,
            "is_hybrid": False,
            "is_office": True
        }

class SmartRateLimiter:
    """Intelligent rate limiting for different job sources"""
    
    def __init__(self):
        self.rate_limits = {
            'indeed': {'requests_per_minute': 30, 'requests_per_hour': 1000},
            'linkedin': {'requests_per_minute': 20, 'requests_per_hour': 500},
            'glassdoor': {'requests_per_minute': 15, 'requests_per_hour': 300},
            'lawcrossing': {'requests_per_minute': 25, 'requests_per_hour': 800},
            'usajobs': {'requests_per_minute': 10, 'requests_per_hour': 200},
            'law_firms': {'requests_per_minute': 20, 'requests_per_hour': 600},
            'legal_tech': {'requests_per_minute': 30, 'requests_per_hour': 1000},
            'internships': {'requests_per_minute': 25, 'requests_per_hour': 800},
            'fellowships': {'requests_per_minute': 15, 'requests_per_hour': 300},
            'clerkships': {'requests_per_minute': 20, 'requests_per_hour': 500},
            'gemini': {'requests_per_minute': 60, 'requests_per_hour': 2000}  # Add Gemini rate limits
        }
        self.request_counts = {}
    
    def can_make_request(self, source: str) -> bool:
        """Check if we can make a request to the source"""
        now = datetime.now()
        minute_key = f"{source}_{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"{source}_{now.strftime('%Y%m%d%H')}"
        
        # Check minute limit
        minute_count = self.request_counts.get(minute_key, 0)
        if minute_count >= self.rate_limits[source]['requests_per_minute']:
            return False
        
        # Check hour limit
        hour_count = self.request_counts.get(hour_key, 0)
        if hour_count >= self.rate_limits[source]['requests_per_hour']:
            return False
        
        return True
    
    def record_request(self, source: str):
        """Record a request for rate limiting"""
        now = datetime.now()
        minute_key = f"{source}_{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"{source}_{now.strftime('%Y%m%d%H')}"
        
        self.request_counts[minute_key] = self.request_counts.get(minute_key, 0) + 1
        self.request_counts[hour_key] = self.request_counts.get(hour_key, 0) + 1

class DuplicateDetector:
    """AI-powered duplicate detection"""
    
    def __init__(self):
        self.gemini_enhancer = GeminiJobEnhancer()
    
    async def detect_duplicates(self, job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use Gemini to identify duplicate postings across sources"""
        try:
            prompt = f"""
            Analyze these job listings and identify duplicates:
            - Same company, same position
            - Similar job descriptions
            - Different sources, same job
            
            Jobs: {job_listings}
            
            Return a list of unique jobs, removing duplicates.
            """
            
            response = await self.gemini_enhancer.model.generate_content_async(prompt)
            return self.parse_duplicate_analysis(response.text, job_listings)
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            return job_listings
    
    def parse_duplicate_analysis(self, response_text: str, original_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse duplicate analysis and return unique jobs"""
        # For now, return original jobs - implement proper parsing later
        return original_jobs

class QualityScorer:
    """AI-powered job quality scoring"""
    
    def __init__(self):
        self.gemini_enhancer = GeminiJobEnhancer()
    
    async def score_job_quality(self, job_posting: Dict[str, Any]) -> float:
        """Score job quality using multiple criteria"""
        try:
            prompt = f"""
            Score this job posting quality from 1-10 based on:
            - Completeness of information
            - Professional presentation
            - Clear requirements
            - Competitive benefits
            - Career growth potential
            
            Job: {job_posting}
            
            Return only a number between 1-10.
            """
            
            response = await self.gemini_enhancer.model.generate_content_async(prompt)
            return self.parse_quality_score(response.text)
            
        except Exception as e:
            logger.error(f"Error scoring job quality: {e}")
            return 5.0
    
    def parse_quality_score(self, response_text: str) -> float:
        """Parse quality score from response"""
        try:
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)', response_text)
            if score_match:
                score = float(score_match.group(1))
                return max(1.0, min(10.0, score))  # Clamp between 1-10
            return 5.0
        except:
            return 5.0

class LexLeaksJobEngine:
    """The main job scraping engine"""
    
    def __init__(self):
        self.gemini_enhancer = GeminiJobEnhancer()
        self.rate_limiter = SmartRateLimiter()
        self.duplicate_detector = DuplicateDetector()
        self.quality_scorer = QualityScorer()
        self.scrapers = {}  # Will be populated with specific scrapers
    
    async def scrape_and_enhance(self, job_sources: List[str], search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main method to scrape and enhance job data"""
        all_jobs = []
        
        for source in job_sources:
            if not self.rate_limiter.can_make_request(source):
                logger.warning(f"Rate limit exceeded for {source}, skipping")
                continue
            
            try:
                # Scrape raw data (placeholder for now)
                raw_jobs = await self.scrape_source(source, search_params)
                
                # Enhance with Gemini
                enhanced_jobs = []
                for job in raw_jobs:
                    if self.rate_limiter.can_make_request('gemini'):
                        enhanced = await self.gemini_enhancer.enhance_job_posting(job)
                        job.update(enhanced)
                        enhanced_jobs.append(job)
                        self.rate_limiter.record_request('gemini')
                    else:
                        enhanced_jobs.append(job)
                
                all_jobs.extend(enhanced_jobs)
                self.rate_limiter.record_request(source)
                
            except Exception as e:
                logger.error(f"Error scraping {source}: {e}")
                continue
        
        # Remove duplicates
        unique_jobs = await self.duplicate_detector.detect_duplicates(all_jobs)
        
        # Score quality
        for job in unique_jobs:
            if self.rate_limiter.can_make_request('gemini'):
                quality_score = await self.quality_scorer.score_job_quality(job)
                job['quality_score'] = quality_score
                self.rate_limiter.record_request('gemini')
        
        return unique_jobs
    
    async def scrape_source(self, source: str, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Placeholder for source-specific scraping"""
        # This will be implemented with specific scrapers
        logger.info(f"Scraping {source} with params: {search_params}")
        
        # TODO: Implement real job scraping
        return [
            {
                "title": f"Legal Associate - {source}",
                "company": "Unknown",
                "location": "New York, NY",
                "description": "Seeking a legal associate with 2-3 years experience...",
                "source": source,
                "source_url": f"https://{source}.com/job/123",
                "posted_date": datetime.now().isoformat()
            }
        ]
    
    async def get_market_trends(self, job_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market intelligence and trends"""
        try:
            prompt = f"""
            Analyze this legal job market data and provide insights:
            - Trending practice areas
            - Salary trends by location
            - Remote work adoption
            - Skills in demand
            - Market predictions
            
            Data: {job_data[:10]}  # Limit for token efficiency
            
            Return insights in JSON format.
            """
            
            response = await self.gemini_enhancer.model.generate_content_async(prompt)
            return self.parse_market_insights(response.text)
            
        except Exception as e:
            logger.error(f"Error generating market trends: {e}")
            return {"error": "Failed to generate market insights"}
    
    def parse_market_insights(self, response_text: str) -> Dict[str, Any]:
        """Parse market insights from response"""
        try:
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse market insights"}
                
        except Exception as e:
            logger.error(f"Error parsing market insights: {e}")
            return {"error": "Failed to parse market insights"}

# Global engine instance
job_engine = LexLeaksJobEngine()
