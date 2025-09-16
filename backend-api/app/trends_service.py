import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytrends
from pytrends.request import TrendReq
import logging

logger = logging.getLogger(__name__)

class GoogleTrendsService:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-IN', tz=330)  # India timezone
        self.legal_keywords = [
            # Corporate Law
            'corporate law', 'company law', 'sebi regulations', 'insolvency code',
            'merger acquisition', 'corporate governance', 'board meetings',
            
            # Criminal Law
            'criminal law', 'bail', 'anticipatory bail', 'criminal procedure',
            'evidence act', 'ipc', 'crpc', 'cyber crime',
            
            # Constitutional Law
            'constitutional law', 'fundamental rights', 'supreme court',
            'high court', 'judicial review', 'constitutional amendment',
            
            # Commercial Law
            'contract law', 'commercial law', 'arbitration', 'mediation',
            'consumer protection', 'competition law', 'intellectual property',
            
            # Regulatory
            'data protection', 'privacy law', 'gdpr', 'personal data protection',
            'regulatory compliance', 'environmental law', 'labor law',
            
            # Legal Tech & AI
            'legal technology', 'legal ai', 'legal automation', 'legal innovation',
            'legal startup', 'lawtech', 'legal software',
            
            # Recent Legal Developments
            'digital personal data protection act', 'new criminal laws',
            'bharatiya nyaya sanhita', 'bharatiya nagarik suraksha sanhita',
            'bharatiya sakshya bill', 'uniform civil code'
        ]
        
        self.trending_topics = []
        self.last_updated = None
    
    async def get_trending_legal_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending legal topics from Google Trends"""
        try:
            # Try to get real-time trending searches
            try:
                trending_searches = self.pytrends.trending_searches(pn='india')
                
                # Filter for legal-related topics
                legal_trends = []
                for topic in trending_searches[0].head(50):  # Check top 50
                    topic_lower = topic.lower()
                    if any(keyword in topic_lower for keyword in self.legal_keywords):
                        legal_trends.append({
                            'topic': topic,
                            'category': self._categorize_topic(topic),
                            'trend_score': self._calculate_trend_score(topic),
                            'suggested_article_type': self._suggest_article_type(topic),
                            'suggested_template': self._suggest_template(topic)
                        })
            except Exception as e:
                logger.warning(f"Google Trends API blocked or rate limited: {e}")
                legal_trends = []
            
            # Also check interest over time for our predefined keywords
            keyword_trends = await self._check_keyword_trends()
            legal_trends.extend(keyword_trends)
            
            # Sort by trend score and remove duplicates
            legal_trends = self._deduplicate_and_sort(legal_trends)
            
            # If no trends found, return empty list
            if not legal_trends:
                logger.info("No trending legal topics found")
                legal_trends = []
            
            self.trending_topics = legal_trends[:limit]
            self.last_updated = datetime.now()
            
            return self.trending_topics
            
        except Exception as e:
            logger.error(f"Error fetching trending topics: {str(e)}")
            return []
    
    async def _check_keyword_trends(self) -> List[Dict[str, Any]]:
        """Check interest over time for predefined legal keywords"""
        trends = []
        
        try:
            # Check trends for batches of keywords (pytrends has a 5 keyword limit)
            for i in range(0, len(self.legal_keywords), 5):
                batch = self.legal_keywords[i:i+5]
                
                self.pytrends.build_payload(
                    batch,
                    cat=0,  # All categories
                    timeframe='today 3-m',  # Last 3 months
                    geo='IN',  # India
                    gprop=''
                )
                
                interest_over_time = self.pytrends.interest_over_time()
                
                if not interest_over_time.empty:
                    # Get the latest interest values
                    latest_values = interest_over_time.iloc[-1]
                    
                    for keyword in batch:
                        if keyword in latest_values.index:
                            interest_value = latest_values[keyword]
                            if interest_value > 50:  # Only include if interest > 50
                                trends.append({
                                    'topic': keyword.title(),
                                    'category': self._categorize_topic(keyword),
                                    'trend_score': int(interest_value),
                                    'suggested_article_type': self._suggest_article_type(keyword),
                                    'suggested_template': self._suggest_template(keyword),
                                    'interest_value': int(interest_value)
                                })
                
                # Rate limiting - wait between requests
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error checking keyword trends: {str(e)}")
        
        return trends
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize topic into legal areas"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['corporate', 'company', 'sebi', 'insolvency', 'merger', 'acquisition']):
            return 'corporate'
        elif any(word in topic_lower for word in ['criminal', 'bail', 'ipc', 'crpc', 'evidence']):
            return 'criminal'
        elif any(word in topic_lower for word in ['constitutional', 'fundamental rights', 'supreme court', 'high court']):
            return 'judicial'
        elif any(word in topic_lower for word in ['contract', 'commercial', 'arbitration', 'consumer', 'competition']):
            return 'regulatory'
        elif any(word in topic_lower for word in ['data protection', 'privacy', 'gdpr', 'environmental', 'labor']):
            return 'regulatory'
        elif any(word in topic_lower for word in ['legal tech', 'legal ai', 'legal automation', 'legal innovation']):
            return 'legal-tech'
        else:
            return 'general'
    
    def _calculate_trend_score(self, topic: str) -> int:
        """Calculate a trend score for the topic"""
        # This is a simplified scoring system
        base_score = 50
        
        # Add points for specific high-impact keywords
        high_impact_keywords = ['supreme court', 'high court', 'sebi', 'data protection', 'criminal law']
        for keyword in high_impact_keywords:
            if keyword in topic.lower():
                base_score += 20
        
        # Add points for recent legal developments
        recent_keywords = ['bharatiya nyaya sanhita', 'digital personal data protection', 'uniform civil code']
        for keyword in recent_keywords:
            if keyword in topic.lower():
                base_score += 30
        
        return min(base_score, 100)  # Cap at 100
    
    def _suggest_article_type(self, topic: str) -> str:
        """Suggest article type based on topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['supreme court', 'high court', 'judgment', 'ruling']):
            return 'deep'  # Court judgments need deep analysis
        elif any(word in topic_lower for word in ['breaking', 'latest', 'update', 'amendment']):
            return 'quick'  # Breaking news should be quick
        else:
            return 'standard'  # Default to standard
    
    def _suggest_template(self, topic: str) -> str:
        """Suggest template based on topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['internship', 'career', 'job', 'recruitment', 'experience']):
            return 'internship'
        else:
            return 'legal_explainer'
    
    def _deduplicate_and_sort(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and sort by trend score"""
        seen = set()
        unique_trends = []
        
        for trend in trends:
            topic_key = trend['topic'].lower()
            if topic_key not in seen:
                seen.add(topic_key)
                unique_trends.append(trend)
        
        # Sort by trend score (descending)
        return sorted(unique_trends, key=lambda x: x['trend_score'], reverse=True)
    
    
# Create a singleton instance for router imports
trends_service = GoogleTrendsService()

