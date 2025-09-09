#!/usr/bin/env python3
"""
Smart Automation for THE ENGINE
- Daily job updates
- Expired job cleanup
- Smart scraping on demand
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import SessionLocal
from app.models import JobOpportunity
from app.job_engine import job_engine

logger = logging.getLogger(__name__)

class SmartAutomation:
    """Smart automation for THE ENGINE"""
    
    def __init__(self):
        self.job_engine = job_engine
        self.last_cleanup = None
        self.last_update = None
    
    async def smart_scrape_on_search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape fresh data when user searches for specific criteria"""
        try:
            # Check if we have recent data for this search
            db = SessionLocal()
            try:
                # Look for jobs matching search criteria in last 2 hours
                recent_cutoff = datetime.now() - timedelta(hours=2)
                
                # Build query based on search params
                query = db.query(JobOpportunity).filter(
                    JobOpportunity.created_at >= recent_cutoff
                )
                
                if search_params.get('query'):
                    search_term = f"%{search_params['query']}%"
                    query = query.filter(
                        or_(
                            JobOpportunity.title.ilike(search_term),
                            JobOpportunity.description.ilike(search_term),
                            JobOpportunity.company.ilike(search_term)
                        )
                    )
                
                if search_params.get('location'):
                    location_term = f"%{search_params['location']}%"
                    query = query.filter(JobOpportunity.location.ilike(location_term))
                
                if search_params.get('work_type'):
                    if search_params['work_type'] == 'remote':
                        query = query.filter(JobOpportunity.is_remote == True)
                    elif search_params['work_type'] == 'hybrid':
                        query = query.filter(JobOpportunity.is_hybrid == True)
                    elif search_params['work_type'] == 'office':
                        query = query.filter(JobOpportunity.is_office == True)
                
                if search_params.get('experience_level'):
                    query = query.filter(JobOpportunity.experience_level == search_params['experience_level'])
                
                recent_jobs = query.limit(10).all()
                
                # If we have recent data, return it
                if recent_jobs:
                    logger.info(f"Found {len(recent_jobs)} recent jobs for search criteria")
                    return [self.job_to_dict(job) for job in recent_jobs]
                
                # No recent data, scrape fresh
                logger.info("No recent data found, scraping fresh jobs")
                return await self.scrape_fresh_jobs(search_params)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in smart scrape on search: {e}")
            return []
    
    async def scrape_fresh_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape fresh jobs based on search parameters"""
        try:
            # Determine which sources to scrape based on search criteria
            sources = self.select_sources_for_search(search_params)
            
            # Scrape from selected sources
            fresh_jobs = await self.job_engine.scrape_and_enhance(sources, search_params)
            
            # Save to database
            await self.save_fresh_jobs(fresh_jobs)
            
            return fresh_jobs
            
        except Exception as e:
            logger.error(f"Error scraping fresh jobs: {e}")
            return []
    
    def select_sources_for_search(self, search_params: Dict[str, Any]) -> List[str]:
        """Select appropriate sources based on search criteria"""
        sources = []
        
        # Always include general sources
        sources.extend(['indeed', 'linkedin', 'glassdoor'])
        
        # Add specialized sources based on criteria
        if 'government' in search_params.get('query', '').lower():
            sources.append('usajobs')
        
        # Add legal-specific sources
        sources.append('lawcrossing')
        
        return sources
    
    async def save_fresh_jobs(self, jobs: List[Dict[str, Any]]):
        """Save fresh jobs to database"""
        db = SessionLocal()
        try:
            for job_data in jobs:
                # Check if job already exists
                existing = db.query(JobOpportunity).filter(
                    and_(
                        JobOpportunity.title == job_data.get('title'),
                        JobOpportunity.company == job_data.get('company'),
                        JobOpportunity.source_url == job_data.get('source_url')
                    )
                ).first()
                
                if not existing:
                    # Create new job
                    job = JobOpportunity(
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        location=job_data.get('location', ''),
                        work_type=job_data.get('work_type', 'office'),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        salary_currency=job_data.get('salary_currency', 'USD'),
                        job_type=job_data.get('job_type', 'full-time'),
                        experience_level=job_data.get('experience_level', 'mid'),
                        practice_area=job_data.get('practice_area', 'General Legal'),
                        firm_size=job_data.get('firm_size', 'mid-size'),
                        practice_type=job_data.get('practice_type', 'litigation'),
                        description=job_data.get('description', ''),
                        requirements=job_data.get('requirements', ''),
                        benefits=job_data.get('benefits', ''),
                        application_url=job_data.get('application_url', ''),
                        source=job_data.get('source', 'unknown'),
                        source_url=job_data.get('source_url', ''),
                        posted_date=datetime.now(),
                        quality_score=job_data.get('quality_score', 5.0),
                        is_remote=job_data.get('is_remote', False),
                        is_hybrid=job_data.get('is_hybrid', False),
                        is_office=job_data.get('is_office', True),
                        gemini_enhanced=job_data.get('gemini_enhanced', False)
                    )
                    db.add(job)
            
            db.commit()
            logger.info(f"Saved {len(jobs)} fresh jobs to database")
            
        except Exception as e:
            logger.error(f"Error saving fresh jobs: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def daily_job_update(self):
        """Daily job update - runs automatically"""
        try:
            logger.info("Starting daily job update")
            
            # Update all major sources
            sources = ['indeed', 'linkedin', 'glassdoor', 'lawcrossing', 'usajobs']
            
            # Default search parameters for broad update
            search_params = {
                'keywords': ['legal', 'lawyer', 'attorney', 'paralegal', 'legal assistant'],
                'locations': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Delhi', 'Mumbai', 'Bangalore'],
                'limit': 50
            }
            
            # Scrape and save fresh jobs
            fresh_jobs = await self.job_engine.scrape_and_enhance(sources, search_params)
            await self.save_fresh_jobs(fresh_jobs)
            
            # Clean up expired jobs
            await self.cleanup_expired_jobs()
            
            # Update last update time
            self.last_update = datetime.now()
            
            logger.info(f"Daily job update completed. Added {len(fresh_jobs)} new jobs")
            
        except Exception as e:
            logger.error(f"Error in daily job update: {e}")
    
    async def cleanup_expired_jobs(self):
        """Remove jobs that are no longer relevant"""
        try:
            db = SessionLocal()
            try:
                # Remove jobs older than 30 days
                cutoff_date = datetime.now() - timedelta(days=30)
                
                expired_jobs = db.query(JobOpportunity).filter(
                    JobOpportunity.posted_date < cutoff_date
                ).all()
                
                for job in expired_jobs:
                    db.delete(job)
                
                db.commit()
                
                logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")
                self.last_cleanup = datetime.now()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error cleaning up expired jobs: {e}")
    
    async def smart_refresh_jobs(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Smart refresh - only scrape if needed"""
        try:
            # Check if we need to refresh
            if self.should_refresh(search_params):
                logger.info("Smart refresh triggered - scraping fresh data")
                fresh_jobs = await self.scrape_fresh_jobs(search_params)
                return {
                    'status': 'refreshed',
                    'jobs_added': len(fresh_jobs),
                    'message': f'Added {len(fresh_jobs)} fresh jobs'
                }
            else:
                logger.info("Smart refresh skipped - recent data available")
                return {
                    'status': 'skipped',
                    'jobs_added': 0,
                    'message': 'Recent data available, no refresh needed'
                }
                
        except Exception as e:
            logger.error(f"Error in smart refresh: {e}")
            return {
                'status': 'error',
                'jobs_added': 0,
                'message': f'Error: {str(e)}'
            }
    
    def should_refresh(self, search_params: Dict[str, Any]) -> bool:
        """Determine if we should refresh data"""
        # Always refresh if last update was more than 6 hours ago
        if not self.last_update or (datetime.now() - self.last_update).total_seconds() > 21600:
            return True
        
        # Refresh if specific criteria suggest fresh data needed
        if search_params.get('query') and 'urgent' in search_params['query'].lower():
            return True
        
        if search_params.get('work_type') == 'remote':
            # Remote jobs change frequently
            return True
        
        return False
    
    def job_to_dict(self, job: JobOpportunity) -> Dict[str, Any]:
        """Convert JobOpportunity model to dictionary"""
        return {
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'work_type': job.work_type,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'salary_currency': job.salary_currency,
            'job_type': job.job_type,
            'experience_level': job.experience_level,
            'practice_area': job.practice_area,
            'firm_size': job.firm_size,
            'practice_type': job.practice_type,
            'description': job.description,
            'requirements': job.requirements,
            'benefits': job.benefits,
            'application_url': job.application_url,
            'source': job.source,
            'source_url': job.source_url,
            'posted_date': job.posted_date.isoformat() if job.posted_date else None,
            'expires_date': job.expires_date.isoformat() if job.expires_date else None,
            'quality_score': job.quality_score,
            'is_remote': job.is_remote,
            'is_hybrid': job.is_hybrid,
            'is_office': job.is_office,
            'gemini_enhanced': job.gemini_enhanced,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None
        }

# Global automation instance
smart_automation = SmartAutomation()

# Background task for daily updates
async def daily_update_task():
    """Background task that runs daily updates"""
    while True:
        try:
            await smart_automation.daily_job_update()
            # Wait 24 hours
            await asyncio.sleep(86400)  # 24 hours in seconds
        except Exception as e:
            logger.error(f"Error in daily update task: {e}")
            # Wait 1 hour before retrying
            await asyncio.sleep(3600)

# Start background task
async def start_automation():
    """Start the automation background tasks"""
    asyncio.create_task(daily_update_task())
    logger.info("Smart automation started")
