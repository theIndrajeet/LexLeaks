#!/usr/bin/env python3
"""
Script to add Indian legal job opportunities to the database
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import JobOpportunity

def add_indian_legal_jobs():
    """Add Indian legal job opportunities to the database"""
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Indian legal job opportunities
        indian_jobs = [
            {
                "title": "Legal Intern - Corporate Law",
                "company": "Khaitan & Co",
                "location": "Delhi, India",
                "work_type": "remote",
                "salary_min": 15000,
                "salary_max": 25000,
                "salary_currency": "INR",
                "job_type": "internship",
                "experience_level": "entry",
                "practice_area": "Corporate Law",
                "firm_size": "big-law",
                "practice_type": "transactional",
                "description": "Join our prestigious corporate law team as a legal intern. Work on high-profile M&A transactions, corporate governance, and regulatory compliance matters.",
                "requirements": "LLB from recognized university, strong research skills, excellent English communication",
                "benefits": "Stipend, mentorship, certificate, flexible hours",
                "application_url": "https://khaitanco.com/careers/internships",
                "source": "linkedin",
                "source_url": "https://linkedin.com/jobs/view/indian-legal-intern-1",
                "posted_date": datetime.now(),
                "quality_score": 8.0,
                "is_remote": True,
                "is_hybrid": False,
                "is_office": False,
                "gemini_enhanced": True
            },
            {
                "title": "Legal Research Associate - Remote",
                "company": "AZB & Partners",
                "location": "Mumbai, India",
                "work_type": "remote",
                "salary_min": 20000,
                "salary_max": 35000,
                "salary_currency": "INR",
                "job_type": "full-time",
                "experience_level": "entry",
                "practice_area": "Legal Research",
                "firm_size": "big-law",
                "practice_type": "regulatory",
                "description": "Remote legal research position focusing on Indian corporate law, securities regulations, and compliance matters.",
                "requirements": "LLB, 0-2 years experience, strong research and writing skills",
                "benefits": "Remote work, competitive salary, professional development",
                "application_url": "https://azbpartners.com/careers",
                "source": "indeed",
                "source_url": "https://indeed.com/viewjob?jk=indian-legal-2",
                "posted_date": datetime.now(),
                "quality_score": 7.5,
                "is_remote": True,
                "is_hybrid": False,
                "is_office": False,
                "gemini_enhanced": True
            },
            {
                "title": "Legal Intern - Criminal Law",
                "company": "Delhi Legal Aid Society",
                "location": "Delhi, India",
                "work_type": "office",
                "salary_min": 10000,
                "salary_max": 15000,
                "salary_currency": "INR",
                "job_type": "internship",
                "experience_level": "entry",
                "practice_area": "Criminal Law",
                "firm_size": "non-profit",
                "practice_type": "litigation",
                "description": "Legal internship focusing on criminal defense, legal aid, and social justice. Work with experienced criminal lawyers on real cases.",
                "requirements": "LLB student or recent graduate, passion for social justice, Hindi and English proficiency",
                "benefits": "Hands-on experience, mentorship, social impact",
                "application_url": "https://delhilegalaid.org/internships",
                "source": "glassdoor",
                "source_url": "https://glassdoor.com/job-listing/indian-legal-3",
                "posted_date": datetime.now(),
                "quality_score": 6.8,
                "is_remote": False,
                "is_hybrid": False,
                "is_office": True,
                "gemini_enhanced": True
            },
            {
                "title": "Legal Assistant - IP Law",
                "company": "Remfry & Sagar",
                "location": "Delhi, India",
                "work_type": "hybrid",
                "salary_min": 25000,
                "salary_max": 40000,
                "salary_currency": "INR",
                "job_type": "full-time",
                "experience_level": "entry",
                "practice_area": "Intellectual Property",
                "firm_size": "mid-size",
                "practice_type": "transactional",
                "description": "Support our IP team with patent and trademark applications, IP research, and client communications.",
                "requirements": "LLB, interest in IP law, good communication skills, attention to detail",
                "benefits": "Hybrid work, learning opportunities, competitive package",
                "application_url": "https://remfry.com/careers",
                "source": "linkedin",
                "source_url": "https://linkedin.com/jobs/view/indian-legal-4",
                "posted_date": datetime.now(),
                "quality_score": 7.2,
                "is_remote": False,
                "is_hybrid": True,
                "is_office": False,
                "gemini_enhanced": True
            },
            {
                "title": "Legal Intern - Family Law",
                "company": "Singh & Associates",
                "location": "Delhi, India",
                "work_type": "office",
                "salary_min": 12000,
                "salary_max": 18000,
                "salary_currency": "INR",
                "job_type": "internship",
                "experience_level": "entry",
                "practice_area": "Family Law",
                "firm_size": "boutique",
                "practice_type": "litigation",
                "description": "Internship in family law practice covering divorce, custody, and domestic relations matters in Delhi courts.",
                "requirements": "LLB student, good interpersonal skills, knowledge of family law",
                "benefits": "Court experience, client interaction, practical learning",
                "application_url": "https://singhassociates.com/internships",
                "source": "indeed",
                "source_url": "https://indeed.com/viewjob?jk=indian-legal-5",
                "posted_date": datetime.now(),
                "quality_score": 6.5,
                "is_remote": False,
                "is_hybrid": False,
                "is_office": True,
                "gemini_enhanced": True
            }
        ]
        
        # Add jobs to database
        for job_data in indian_jobs:
            job = JobOpportunity(**job_data)
            db.add(job)
        
        # Commit the transaction
        db.commit()
        
        print(f"Successfully added {len(indian_jobs)} Indian legal job opportunities to the database")
        
        # Print summary
        total_jobs = db.query(JobOpportunity).count()
        remote_jobs = db.query(JobOpportunity).filter(JobOpportunity.is_remote == True).count()
        hybrid_jobs = db.query(JobOpportunity).filter(JobOpportunity.is_hybrid == True).count()
        office_jobs = db.query(JobOpportunity).filter(JobOpportunity.is_office == True).count()
        entry_level_jobs = db.query(JobOpportunity).filter(JobOpportunity.experience_level == "entry").count()
        
        print(f"\nDatabase Summary:")
        print(f"Total jobs: {total_jobs}")
        print(f"Remote jobs: {remote_jobs}")
        print(f"Hybrid jobs: {hybrid_jobs}")
        print(f"Office jobs: {office_jobs}")
        print(f"Entry level jobs: {entry_level_jobs}")
        
    except Exception as e:
        print(f"Error adding Indian legal jobs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_indian_legal_jobs()
