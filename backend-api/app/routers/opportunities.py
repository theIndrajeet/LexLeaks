from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import JobOpportunity
from app.job_engine import job_engine
from app.smart_automation import smart_automation
from app.schemas import JobOpportunityResponse, JobSearchResponse, MarketTrendsResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/opportunities/search", response_model=JobSearchResponse)
async def search_opportunities(
    query: str = Query("", description="Search query for job titles, companies, or keywords"),
    location: str = Query("", description="Location filter"),
    work_type: str = Query("", description="Work type: remote, hybrid, office, flexible"),
    practice_area: str = Query("", description="Legal practice area"),
    experience_level: str = Query("", description="Experience level: entry, mid, senior"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """Search job opportunities with advanced filtering"""
    try:
        # Build query filters
        filters = []
        
        if query:
            filters.append(
                or_(
                    JobOpportunity.title.ilike(f"%{query}%"),
                    JobOpportunity.company.ilike(f"%{query}%"),
                    JobOpportunity.description.ilike(f"%{query}%")
                )
            )
        
        if location:
            filters.append(JobOpportunity.location.ilike(f"%{location}%"))
        
        if work_type:
            filters.append(JobOpportunity.work_type == work_type)
        
        if practice_area:
            filters.append(JobOpportunity.practice_area.ilike(f"%{practice_area}%"))
        
        if experience_level:
            filters.append(JobOpportunity.experience_level == experience_level)
        
        if salary_min is not None:
            filters.append(JobOpportunity.salary_min >= salary_min)
        
        if salary_max is not None:
            filters.append(JobOpportunity.salary_max <= salary_max)
        
        # Execute query
        query_obj = db.query(JobOpportunity)
        if filters:
            query_obj = query_obj.filter(and_(*filters))
        
        # Get total count
        total_count = query_obj.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        jobs = query_obj.order_by(JobOpportunity.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        job_responses = []
        for job in jobs:
            job_responses.append(JobOpportunityResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                work_type=job.work_type,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                job_type=job.job_type,
                experience_level=job.experience_level,
                practice_area=job.practice_area,
                firm_size=job.firm_size,
                practice_type=job.practice_type,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                application_url=job.application_url,
                source=job.source,
                source_url=job.source_url,
                posted_date=job.posted_date,
                expires_date=job.expires_date,
                quality_score=job.quality_score,
                is_remote=job.is_remote,
                is_hybrid=job.is_hybrid,
                is_office=job.is_office,
                gemini_enhanced=job.gemini_enhanced,
                created_at=job.created_at,
                updated_at=job.updated_at
            ))
        
        return JobSearchResponse(
            jobs=job_responses,
            total_count=total_count,
            page=page,
            limit=limit,
            total_pages=(total_count + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error searching opportunities: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/opportunities/trends", response_model=MarketTrendsResponse)
async def get_market_trends(db: Session = Depends(get_db)):
    """Get market intelligence and trends"""
    try:
        # Get recent job data for analysis
        recent_jobs = db.query(JobOpportunity).filter(
            JobOpportunity.created_at >= datetime.now() - timedelta(days=30)
        ).all()
        
        # Convert to dict format for AI analysis
        job_data = []
        for job in recent_jobs:
            job_data.append({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_type": job.work_type,
                "practice_area": job.practice_area,
                "experience_level": job.experience_level,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "quality_score": job.quality_score,
                "is_remote": job.is_remote,
                "is_hybrid": job.is_hybrid,
                "is_office": job.is_office
            })
        
        # Get AI-powered market insights
        market_insights = await job_engine.get_market_trends(job_data)
        
        return MarketTrendsResponse(
            insights=market_insights,
            data_period="30 days",
            total_jobs_analyzed=len(job_data),
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/opportunities/refresh")
async def refresh_job_data(
    sources: List[str] = Query(["indeed", "linkedin", "glassdoor"], description="Job sources to refresh"),
    db: Session = Depends(get_db)
):
    """Trigger manual job data refresh"""
    try:
        # Search parameters for scraping
        search_params = {
            "keywords": ["legal", "lawyer", "attorney", "paralegal", "legal assistant"],
            "locations": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "limit": 50
        }
        
        # Scrape and enhance job data
        enhanced_jobs = await job_engine.scrape_and_enhance(sources, search_params)
        
        # Save to database
        saved_count = 0
        for job_data in enhanced_jobs:
            try:
                # Check if job already exists
                existing_job = db.query(JobOpportunity).filter(
                    and_(
                        JobOpportunity.title == job_data.get("title"),
                        JobOpportunity.company == job_data.get("company"),
                        JobOpportunity.source == job_data.get("source")
                    )
                ).first()
                
                if not existing_job:
                    # Create new job opportunity
                    job_opportunity = JobOpportunity(
                        title=job_data.get("title", ""),
                        company=job_data.get("company", ""),
                        location=job_data.get("location"),
                        work_type=job_data.get("work_type"),
                        salary_min=job_data.get("salary_min"),
                        salary_max=job_data.get("salary_max"),
                        salary_currency=job_data.get("salary_currency", "USD"),
                        job_type=job_data.get("job_type"),
                        experience_level=job_data.get("experience_level"),
                        practice_area=job_data.get("practice_area"),
                        firm_size=job_data.get("firm_size"),
                        practice_type=job_data.get("practice_type"),
                        description=job_data.get("description"),
                        requirements=job_data.get("requirements"),
                        benefits=job_data.get("benefits"),
                        application_url=job_data.get("application_url"),
                        source=job_data.get("source", ""),
                        source_url=job_data.get("source_url"),
                        posted_date=datetime.fromisoformat(job_data.get("posted_date")) if job_data.get("posted_date") else None,
                        quality_score=job_data.get("quality_score"),
                        is_remote=job_data.get("is_remote", False),
                        is_hybrid=job_data.get("is_hybrid", False),
                        is_office=job_data.get("is_office", False),
                        gemini_enhanced=job_data.get("gemini_enhanced", False)
                    )
                    
                    db.add(job_opportunity)
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving job opportunity: {e}")
                continue
        
        db.commit()
        
        return {
            "message": f"Successfully refreshed job data",
            "sources": sources,
            "jobs_scraped": len(enhanced_jobs),
            "jobs_saved": saved_count,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing job data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/opportunities/{job_id}", response_model=JobOpportunityResponse)
async def get_job_opportunity(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job opportunity by ID"""
    try:
        job = db.query(JobOpportunity).filter(JobOpportunity.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job opportunity not found")
        
        return JobOpportunityResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            work_type=job.work_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            job_type=job.job_type,
            experience_level=job.experience_level,
            practice_area=job.practice_area,
            firm_size=job.firm_size,
            practice_type=job.practice_type,
            description=job.description,
            requirements=job.requirements,
            benefits=job.benefits,
            application_url=job.application_url,
            source=job.source,
            source_url=job.source_url,
            posted_date=job.posted_date,
            expires_date=job.expires_date,
            quality_score=job.quality_score,
            is_remote=job.is_remote,
            is_hybrid=job.is_hybrid,
            is_office=job.is_office,
            gemini_enhanced=job.gemini_enhanced,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job opportunity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/opportunities/stats/summary")
async def get_opportunities_summary(db: Session = Depends(get_db)):
    """Get summary statistics for job opportunities"""
    try:
        total_jobs = db.query(JobOpportunity).count()
        
        # Work type distribution
        from sqlalchemy import func
        work_type_stats = db.query(
            JobOpportunity.work_type,
            func.count(JobOpportunity.id)
        ).group_by(JobOpportunity.work_type).all()
        
        # Practice area distribution
        practice_area_stats = db.query(
            JobOpportunity.practice_area,
            func.count(JobOpportunity.id)
        ).group_by(JobOpportunity.practice_area).all()
        
        # Remote work stats
        remote_stats = {
            "total_remote": db.query(JobOpportunity).filter(JobOpportunity.is_remote == True).count(),
            "total_hybrid": db.query(JobOpportunity).filter(JobOpportunity.is_hybrid == True).count(),
            "total_office": db.query(JobOpportunity).filter(JobOpportunity.is_office == True).count()
        }
        
        # Quality score average
        avg_quality = db.query(func.avg(JobOpportunity.quality_score)).scalar() or 0
        
        return {
            "total_jobs": total_jobs,
            "work_type_distribution": dict(work_type_stats),
            "practice_area_distribution": dict(practice_area_stats),
            "remote_work_stats": remote_stats,
            "average_quality_score": round(avg_quality, 2),
            "last_updated": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting opportunities summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/opportunities/smart-scrape")
async def smart_scrape_opportunities(
    query: Optional[str] = None,
    location: Optional[str] = None,
    work_type: Optional[str] = None,
    practice_area: Optional[str] = None,
    experience_level: Optional[str] = None
):
    """Trigger smart scraping for specific search criteria"""
    try:
        search_params = {
            'query': query,
            'location': location,
            'work_type': work_type,
            'practice_area': practice_area,
            'experience_level': experience_level,
            'keywords': [query] if query else ['legal', 'lawyer', 'attorney'],
            'limit': 30
        }
        
        # Force fresh scraping
        fresh_jobs = await smart_automation.scrape_fresh_jobs(search_params)
        
        return {
            "message": f"Smart scraping completed. Found {len(fresh_jobs)} fresh jobs.",
            "jobs_found": len(fresh_jobs),
            "search_params": search_params
        }
        
    except Exception as e:
        logger.error(f"Error in smart scraping: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/opportunities/cleanup-expired")
async def cleanup_expired_jobs():
    """Manually trigger cleanup of expired jobs"""
    try:
        await smart_automation.cleanup_expired_jobs()
        
        return {
            "message": "Expired jobs cleanup completed successfully",
            "last_cleanup": smart_automation.last_cleanup
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/opportunities/daily-update")
async def trigger_daily_update():
    """Manually trigger daily job update"""
    try:
        await smart_automation.daily_job_update()
        
        return {
            "message": "Daily job update completed successfully",
            "last_update": smart_automation.last_update
        }
        
    except Exception as e:
        logger.error(f"Error in daily update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
