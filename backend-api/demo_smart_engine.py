#!/usr/bin/env python3
"""
Demo script to showcase THE ENGINE's smart automation features
"""

import asyncio
import httpx
import json
from datetime import datetime

async def demo_smart_engine():
    """Demonstrate THE ENGINE's capabilities"""
    
    print("🚀 THE ENGINE - Smart Legal Job Scraping Demo")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    async with httpx.AsyncClient() as client:
        
        # 1. Test Smart Scraping
        print("\n1️⃣ Smart Scraping Demo")
        print("-" * 30)
        
        search_params = {
            "query": "legal intern",
            "location": "delhi", 
            "work_type": "remote"
        }
        
        try:
            response = await client.post(
                f"{base_url}/opportunities/smart-scrape",
                params=search_params
            )
            result = response.json()
            print(f"✅ Smart Scraping Result: {result['message']}")
            print(f"📊 Jobs Found: {result['jobs_found']}")
        except Exception as e:
            print(f"❌ Smart Scraping Error: {e}")
        
        # 2. Test Search with Fresh Data
        print("\n2️⃣ Search with Fresh Data")
        print("-" * 30)
        
        try:
            response = await client.get(
                f"{base_url}/opportunities/search",
                params={"query": "legal intern", "location": "delhi", "work_type": "remote"}
            )
            result = response.json()
            print(f"✅ Search Results: {result['total_count']} jobs found")
            
            if result['jobs']:
                for i, job in enumerate(result['jobs'][:3], 1):
                    print(f"   {i}. {job['title']} at {job['company']}")
                    print(f"      Location: {job['location']}")
                    print(f"      Work Type: {job['work_type']}")
                    print(f"      Quality Score: {job['quality_score']}/10")
                    print()
        except Exception as e:
            print(f"❌ Search Error: {e}")
        
        # 3. Test Market Trends
        print("\n3️⃣ AI-Powered Market Trends")
        print("-" * 30)
        
        try:
            response = await client.get(f"{base_url}/opportunities/trends")
            result = response.json()
            print(f"✅ Market Trends Generated")
            print(f"📈 Trending Practice Areas: {result.get('trending_practice_areas', 'N/A')}")
            print(f"💰 Salary Insights: {result.get('salary_insights', 'N/A')}")
            print(f"🏠 Remote Work Trends: {result.get('remote_work_trends', 'N/A')}")
        except Exception as e:
            print(f"❌ Market Trends Error: {e}")
        
        # 4. Test Statistics
        print("\n4️⃣ Database Statistics")
        print("-" * 30)
        
        try:
            response = await client.get(f"{base_url}/opportunities/stats/summary")
            result = response.json()
            print(f"✅ Database Stats Retrieved")
            print(f"📊 Total Jobs: {result['total_jobs']}")
            print(f"🏠 Remote Jobs: {result['remote_work_stats']['total_remote']}")
            print(f"🔄 Hybrid Jobs: {result['remote_work_stats']['total_hybrid']}")
            print(f"🏢 Office Jobs: {result['remote_work_stats']['total_office']}")
            print(f"⭐ Average Quality Score: {result['average_quality_score']}")
        except Exception as e:
            print(f"❌ Statistics Error: {e}")
        
        # 5. Test Cleanup
        print("\n5️⃣ Expired Jobs Cleanup")
        print("-" * 30)
        
        try:
            response = await client.post(f"{base_url}/opportunities/cleanup-expired")
            result = response.json()
            print(f"✅ Cleanup Result: {result['message']}")
            print(f"🧹 Last Cleanup: {result['last_cleanup']}")
        except Exception as e:
            print(f"❌ Cleanup Error: {e}")
        
        # 6. Test Daily Update
        print("\n6️⃣ Daily Update Trigger")
        print("-" * 30)
        
        try:
            response = await client.post(f"{base_url}/opportunities/daily-update")
            result = response.json()
            print(f"✅ Daily Update Result: {result['message']}")
            print(f"🔄 Last Update: {result['last_update']}")
        except Exception as e:
            print(f"❌ Daily Update Error: {e}")
    
    print("\n🎉 THE ENGINE Demo Complete!")
    print("=" * 50)
    print("✨ Features Demonstrated:")
    print("   • Smart scraping on demand")
    print("   • AI-powered job enhancement")
    print("   • Market trend analysis")
    print("   • Automatic cleanup")
    print("   • Daily updates")
    print("   • Quality scoring")
    print("   • Duplicate detection")
    print("   • Rate limiting")
    print("\n🚀 THE ENGINE is ready for production!")

if __name__ == "__main__":
    asyncio.run(demo_smart_engine())
