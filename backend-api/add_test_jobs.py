#!/usr/bin/env python3
"""
Script to add test job opportunities to the database
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import JobOpportunity

def add_test_jobs():
    """Add some test job opportunities to the database"""
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if we already have test jobs
        existing_count = db.query(JobOpportunity).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} job opportunities")
            return
        
        # Test job opportunities
        test_jobs = [
            {
                "title": "Senior Corporate Attorney",
                "company": "Goldman Sachs",
                "location": "New York, NY",
                "work_type": "hybrid",
                "salary_min": 180000,
                "salary_max": 250000,
                "salary_currency": "USD",
                "job_type": "full-time",
                "experience_level": "senior",
                "practice_area": "Corporate Law",
                "firm_size": "big-law",
                "practice_type": "transactional",
                "description": "Seeking an experienced corporate attorney to join our legal team. You will work on complex M&A transactions, securities offerings, and corporate governance matters.",
                "requirements": "JD from accredited law school, 5+ years corporate law experience, admitted to NY bar",
                "benefits": "Comprehensive health insurance, 401k matching, flexible PTO, professional development budget",
                "application_url": "https://goldmansachs.com/careers/legal",
                "source": "linkedin",
                "source_url": "https://linkedin.com/jobs/view/123456",
                "posted_date": datetime.now(),
                "quality_score": 8.5,
                "is_remote": False,
                "is_hybrid": True,
                "is_office": False,
                "gemini_enhanced": True
            },
            {
                "title": "Remote Legal Research Associate",
                "company": "LegalTech Solutions",
                "location": "Remote",
                "work_type": "remote",
                "salary_min": 70000,
                "salary_max": 95000,
                "salary_currency": "USD",
                "job_type": "full-time",
                "experience_level": "entry",
                "practice_area": "Legal Technology",
                "firm_size": "mid-size",
                "practice_type": "regulatory",
                "description": "Join our innovative legal tech team as a research associate. You'll work on cutting-edge legal research projects using AI and machine learning.",
                "requirements": "JD preferred but not required, strong research skills, tech-savvy, excellent writing",
                "benefits": "Fully remote, health insurance, stock options, learning stipend",
                "application_url": "https://legaltechsolutions.com/careers",
                "source": "indeed",
                "source_url": "https://indeed.com/viewjob?jk=789012",
                "posted_date": datetime.now(),
                "quality_score": 7.8,
                "is_remote": True,
                "is_hybrid": False,
                "is_office": False,
                "gemini_enhanced": True
            },
            {
                "title": "Criminal Defense Attorney",
                "company": "Public Defender's Office",
                "location": "Los Angeles, CA",
                "work_type": "office",
                "salary_min": 65000,
                "salary_max": 85000,
                "salary_currency": "USD",
                "job_type": "full-time",
                "experience_level": "mid",
                "practice_area": "Criminal Law",
                "firm_size": "government",
                "practice_type": "litigation",
                "description": "Serve the community as a public defender. Represent indigent clients in criminal proceedings and make a difference in people's lives.",
                "requirements": "JD, CA bar admission, 2+ years criminal law experience, passion for public service",
                "benefits": "Government benefits, pension, loan forgiveness eligible, meaningful work",
                "application_url": "https://lacounty.gov/careers",
                "source": "glassdoor",
                "source_url": "https://glassdoor.com/job-listing/345678",
                "posted_date": datetime.now(),
                "quality_score": 6.5,
                "is_remote": False,
                "is_hybrid": False,
                "is_office": True,
                "gemini_enhanced": True
            },
            {
                "title": "IP Attorney - Patent Specialist",
                "company": "TechCorp Industries",
                "location": "San Francisco, CA",
                "work_type": "flexible",
                "salary_min": 150000,
                "salary_max": 200000,
                "salary_currency": "USD",
                "job_type": "full-time",
                "experience_level": "senior",
                "practice_area": "Intellectual Property",
                "firm_size": "big-law",
                "practice_type": "transactional",
                "description": "Lead our IP portfolio management and patent prosecution. Work with cutting-edge technology companies on patent strategy and IP protection.",
                "requirements": "JD, USPTO registration, 4+ years patent law, technical background preferred",
                "benefits": "Competitive salary, equity participation, flexible schedule, top-tier benefits",
                "application_url": "https://techcorp.com/careers/legal",
                "source": "linkedin",
                "source_url": "https://linkedin.com/jobs/view/456789",
                "posted_date": datetime.now(),
                "quality_score": 9.2,
                "is_remote": False,
                "is_hybrid": True,
                "is_office": True,
                "gemini_enhanced": True
            },
            {
                "title": "Family Law Associate",
                "company": "Smith & Associates",
                "location": "Chicago, IL",
                "work_type": "office",
                "salary_min": 80000,
                "salary_max": 120000,
                "salary_currency": "USD",
                "job_type": "full-time",
                "experience_level": "mid",
                "practice_area": "Family Law",
                "firm_size": "boutique",
                "practice_type": "litigation",
                "description": "Join our boutique family law practice. Handle divorce, custody, and domestic relations matters with a compassionate approach.",
                "requirements": "JD, IL bar admission, 3+ years family law experience, strong interpersonal skills",
                "benefits": "Small firm culture, mentorship opportunities, work-life balance, competitive benefits",
                "application_url": "https://smithlaw.com/careers",
                "source": "indeed",
                "source_url": "https://indeed.com/viewjob?jk=567890",
                "posted_date": datetime.now(),
                "quality_score": 7.0,
                "is_remote": False,
                "is_hybrid": False,
                "is_office": True,
                "gemini_enhanced": True
            }
        ]
        
        # Add jobs to database
        for job_data in test_jobs:
            job = JobOpportunity(**job_data)
            db.add(job)
        
        # Commit the transaction
        db.commit()
        
        print(f"Successfully added {len(test_jobs)} test job opportunities to the database")
        
        # Print summary
        total_jobs = db.query(JobOpportunity).count()
        remote_jobs = db.query(JobOpportunity).filter(JobOpportunity.is_remote == True).count()
        hybrid_jobs = db.query(JobOpportunity).filter(JobOpportunity.is_hybrid == True).count()
        office_jobs = db.query(JobOpportunity).filter(JobOpportunity.is_office == True).count()
        
        print(f"\nDatabase Summary:")
        print(f"Total jobs: {total_jobs}")
        print(f"Remote jobs: {remote_jobs}")
        print(f"Hybrid jobs: {hybrid_jobs}")
        print(f"Office jobs: {office_jobs}")
        
    except Exception as e:
        print(f"Error adding test jobs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_jobs()
