#!/usr/bin/env python3
"""Create demo impacts for existing posts"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend-api'))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def create_demo_impacts():
    """Create sample impacts for demonstration"""
    db = SessionLocal()
    
    try:
        # Get some posts to associate impacts with
        posts = db.query(models.Post).filter(models.Post.status == "published").limit(5).all()
        
        if not posts:
            print("No published posts found. Please create some posts first.")
            return
        
        # Sample impacts data
        impacts_data = [
            {
                "post": posts[0] if len(posts) > 0 else None,
                "impacts": [
                    {
                        "title": "Internal Investigation Launched",
                        "description": "Following our exposé, the law firm initiated a comprehensive internal investigation into the alleged misconduct, hiring an independent third-party investigator.",
                        "date": datetime.now() - timedelta(days=30),
                        "type": "investigation",
                        "status": "in_progress"
                    },
                    {
                        "title": "State Bar Ethics Review",
                        "description": "The State Bar Association announced a formal ethics review of the attorneys named in our report, potentially leading to disciplinary action.",
                        "date": datetime.now() - timedelta(days=25),
                        "type": "investigation",
                        "status": "pending"
                    }
                ]
            },
            {
                "post": posts[1] if len(posts) > 1 else None,
                "impacts": [
                    {
                        "title": "Managing Partner Resignation",
                        "description": "The managing partner implicated in the financial misconduct scandal resigned from their position, citing 'personal reasons' in their departure statement.",
                        "date": datetime.now() - timedelta(days=15),
                        "type": "resignation",
                        "status": "completed"
                    },
                    {
                        "title": "Client Compensation Program Established",
                        "description": "The firm announced a $5 million compensation fund for affected clients, acknowledging the harm caused by the fraudulent billing practices.",
                        "date": datetime.now() - timedelta(days=10),
                        "type": "reform",
                        "status": "in_progress"
                    }
                ]
            },
            {
                "post": posts[2] if len(posts) > 2 else None,
                "impacts": [
                    {
                        "title": "Federal Investigation Opened",
                        "description": "The Department of Justice opened a formal investigation into potential criminal charges related to the systematic overbilling scheme exposed in our report.",
                        "date": datetime.now() - timedelta(days=20),
                        "type": "legal_action",
                        "status": "in_progress"
                    }
                ]
            },
            {
                "post": posts[3] if len(posts) > 3 else None,
                "impacts": [
                    {
                        "title": "New Ethics Training Mandated",
                        "description": "The state's Supreme Court mandated new ethics training requirements for all practicing attorneys, directly referencing our investigation in the ruling.",
                        "date": datetime.now() - timedelta(days=45),
                        "type": "policy_change",
                        "status": "completed"
                    },
                    {
                        "title": "Legislative Hearing Scheduled",
                        "description": "State legislators announced hearings on legal industry reform, inviting our reporters to testify about their findings.",
                        "date": datetime.now() - timedelta(days=5),
                        "type": "policy_change",
                        "status": "pending"
                    }
                ]
            }
        ]
        
        # Create impacts
        created_count = 0
        for impact_group in impacts_data:
            if impact_group["post"]:
                for impact_data in impact_group["impacts"]:
                    # Check if impact already exists
                    existing = db.query(models.Impact).filter(
                        models.Impact.title == impact_data["title"],
                        models.Impact.post_id == impact_group["post"].id
                    ).first()
                    
                    if not existing:
                        impact = models.Impact(
                            title=impact_data["title"],
                            description=impact_data["description"],
                            date=impact_data["date"],
                            type=impact_data["type"],
                            status=impact_data["status"],
                            post_id=impact_group["post"].id
                        )
                        db.add(impact)
                        created_count += 1
                        print(f"Created impact: {impact_data['title']} for post: {impact_group['post'].title}")
        
        db.commit()
        print(f"\nSuccessfully created {created_count} demo impacts!")
        
    except Exception as e:
        print(f"Error creating demo impacts: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_impacts() 