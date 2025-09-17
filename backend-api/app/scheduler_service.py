import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import pytz

from .database import get_db
from .models import Post, User
from .web_scraper import legal_scraper
from .gemini_topic_agent import gemini_topic_agent
from .ai_service import ai_generator
from .config import FRONTEND_URL

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.is_running = False
        self.automation_enabled = True
        self.generation_time = "06:00"  # 6 AM IST
        self.publish_time = "07:00"    # 7 AM IST
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.task = None
        
    async def start_scheduler(self):
        """Start the scheduler service"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        self.is_running = True
        logger.info(" Starting Article Scheduler Service")
        
        # Start the main scheduler loop
        self.task = asyncio.create_task(self._scheduler_loop())
        
    async def stop_scheduler(self):
        """Stop the scheduler service"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
            
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Stopped Article Scheduler Service")
        
    async def run_automation_now(self, mode: str = 'generate') -> Dict[str, Any]:
        """Run the automation immediately.

        mode options:
        - 'generate': run generation pipeline now (default)
        - 'generate_and_publish': run generation, then attempt publish now
        """
        start_time = datetime.now(self.timezone)
        try:
            generated = False
            published = False

            # Always run generation first
            await self._generate_trending_articles()
            generated = True

            if mode == 'generate_and_publish':
                await self._publish_scheduled_articles()
                published = True

            end_time = datetime.now(self.timezone)
            duration = (end_time - start_time).total_seconds()

            return {
                'success': True,
                'message': 'Automation run completed',
                'actions': {
                    'generated': generated,
                    'published': published,
                },
                'duration_seconds': duration,
                'ran_at': start_time.isoformat()
            }
        except Exception as e:
            logger.error(f"Error running automation now: {e}")
            return {
                'success': False,
                'message': f'Error running automation: {str(e)}'
            }
        
    async def _scheduler_loop(self):
        """Main scheduler loop that runs every minute"""
        while self.is_running:
            try:
                current_time = datetime.now(self.timezone)
                current_time_str = current_time.strftime("%H:%M")
                
                # Check if it's time to generate articles (6 AM IST)
                if current_time_str == self.generation_time and self.automation_enabled:
                    logger.info(f"  It's {self.generation_time} IST - Time to generate trending articles!")
                    await self._generate_trending_articles()
                
                # Check if it's time to publish articles (7 AM IST)
                if current_time_str == self.publish_time and self.automation_enabled:
                    logger.info(f"  It's {self.publish_time} IST - Time to publish scheduled articles!")
                    await self._publish_scheduled_articles()
                
                # Sleep for 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Continue running even if there's an error
                
    async def _generate_trending_articles(self):
        """Generate articles using the new pipeline: Scraping → Gemini AI → Article Generation"""
        try:
            logger.info(" Starting new article generation pipeline...")
            
            # Step 1: Scrape legal news sources
            logger.info(" Step 1: Scraping legal news sources...")
            async with legal_scraper as scraper:
                scraped_articles = await scraper.scrape_all_sources()
            
            if not scraped_articles:
                logger.warning("No legal articles found from scraping. Using fallback topics.")
                # Use fallback topics if scraping fails
                fallback_topics = [
                    {
                        'title': 'Latest Legal Developments in India',
                        'category': 'General Legal',
                        'suggested_article_type': 'standard',
                        'suggested_template': 'legal_explainer'
                    }
                ]
                trending_topics = fallback_topics
            else:
                # Step 2: Generate trending topics using Gemini AI
                logger.info("🤖 Step 2: Generating trending topics with Gemini AI...")
                trending_topics = await gemini_topic_agent.generate_trending_topics(
                    scraped_articles, num_topics=3
                )
            
            if not trending_topics:
                logger.warning("No trending topics generated. Skipping article generation.")
                return
                
            logger.info(f"Found {len(trending_topics)} trending topics")
            
            # Step 3: Generate articles for top trending topics
            logger.info(" Step 3: Generating articles from trending topics...")
            for i, topic in enumerate(trending_topics[:3]):
                try:
                    logger.info(f"🤖 Generating article {i+1}/3: {topic['title']}")
                    
                    # Step 3a: Filter relevant research data for this topic
                    relevant_research_data = self._filter_relevant_research_data(
                        scraped_articles, topic['title']
                    ) if scraped_articles else []
                    
                    logger.info(f"📊 Using {len(relevant_research_data)} relevant research sources")
                    
                    # Generate article using AI with research data
                    article_data = await ai_generator.generate_article(
                        topic=topic['title'],
                        article_type=topic.get('suggested_article_type', 'standard'),
                        template=topic.get('suggested_template', 'legal_explainer'),
                        research_data=relevant_research_data,  # Pass filtered research data
                        category='ai-generated',
                        publish_option='schedule',  # Schedule for 7 AM
                        scheduled_for=self._get_next_publish_time()
                    )
                    
                    if article_data and 'post_id' in article_data:
                        logger.info(f" Article generated successfully: {article_data['post_id']}")
                    else:
                        logger.error(f"❌ Failed to generate article for topic: {topic['title']}")
                        
                except Exception as e:
                    logger.error(f"Error generating article for topic {topic['title']}: {e}")
                    
            logger.info(" Article generation pipeline completed successfully.")
                    
        except Exception as e:
            logger.error(f"❌ Critical error in article generation pipeline: {e}")
            # Try fallback generation
            try:
                logger.info(" Attempting fallback article generation...")
                fallback_topic = {
                    'title': 'Daily Legal Update - ' + datetime.now().strftime('%B %d, %Y'),
                    'category': 'General Legal',
                    'suggested_article_type': 'standard',
                    'suggested_template': 'legal_explainer'
                }
                
                article_data = await ai_generator.generate_article(
                    topic=fallback_topic['title'],
                    article_type=fallback_topic['suggested_article_type'],
                    template=fallback_topic['suggested_template'],
                    research_data=None,  # No research data for fallback
                    category='ai-generated',
                    publish_option='schedule',
                    scheduled_for=self._get_next_publish_time()
                )
                
                if article_data and 'post_id' in article_data:
                    logger.info(f" Fallback article generated: {article_data['post_id']}")
                else:
                    logger.error("❌ Fallback generation also failed")
                    
            except Exception as fallback_error:
                logger.error(f"❌ Fallback generation also failed: {fallback_error}")
            
    async def _publish_scheduled_articles(self):
        """Publish articles that are scheduled for this time"""
        try:
            db = next(get_db())
            
            # Find articles scheduled for publishing
            current_time = datetime.now(self.timezone)
            scheduled_posts = db.query(Post).filter(
                and_(
                    Post.status == 'draft',
                    Post.published_at.isnot(None),
                    Post.published_at <= current_time,
                    Post.category == 'ai-generated'
                )
            ).all()
            
            if not scheduled_posts:
                logger.info("No articles scheduled for publishing")
                return
                
            logger.info(f" Publishing {len(scheduled_posts)} scheduled articles")
            
            for post in scheduled_posts:
                try:
                    # Update post status to published
                    post.status = 'published'
                    post.published_at = current_time
                    db.commit()
                    
                    logger.info(f" Published article: {post.title}")
                    
                except Exception as e:
                    logger.error(f"Error publishing article {post.id}: {e}")
                    db.rollback()
                    
        except Exception as e:
            logger.error(f"Error in _publish_scheduled_articles: {e}")
        finally:
            db.close()
            
    def _get_next_publish_time(self) -> datetime:
        """Get the next publish time (7 AM IST)"""
        now = datetime.now(self.timezone)
        publish_time = now.replace(
            hour=7, 
            minute=0, 
            second=0, 
            microsecond=0
        )
        
        # If it's already past 7 AM today, schedule for tomorrow
        if now >= publish_time:
            publish_time += timedelta(days=1)
            
        return publish_time
        
    async def manual_generate_article(self, topic: str, article_type: str = 'standard', 
                                    template: str = 'legal_explainer', publish_option: str = 'draft') -> Dict[str, Any]:
        """Manually generate an article"""
        try:
            logger.info(f"🤖 Manual article generation: {topic} (publish_option: {publish_option})")
            
            # Generate article content
            article_data = await ai_generator.generate_article(
                topic=topic,
                article_type=article_type,
                template=template,
                research_data=None,  # Manual generation without research data
                category='ai-generated',
                publish_option=publish_option
            )
            
            if not article_data or article_data.get('error'):
                return {
                    'success': False,
                    'message': f'Failed to generate article: {article_data.get("error", "Unknown error")}',
                    'data': None
                }
            
            # Save article to database
            db = next(get_db())
            try:
                # Determine status and published_at based on publish_option
                if publish_option == 'live':
                    status = 'published'
                    published_at = datetime.now()
                else:  # draft
                    status = 'draft'
                    published_at = None
                
                # Create new post
                new_post = Post(
                    title=article_data['title'],
                    slug=article_data['slug'],
                    content=article_data['content'],
                    excerpt=article_data['excerpt'],
                    status=status,
                    verification_status='unverified',
                    category='ai-generated',
                    author_id=1,  # Default admin user ID
                    published_at=published_at,
                    ai_generated=True,
                    ai_prompt=topic
                )
                
                db.add(new_post)
                db.commit()
                db.refresh(new_post)
                
                logger.info(f" Article saved to database: {new_post.title} (ID: {new_post.id})")
                
                return {
                    'success': True,
                    'message': f'Article generated successfully and saved as {publish_option}',
                    'data': {
                        **article_data,
                        'post_id': new_post.id,
                        'database_id': new_post.id
                    },
                    'publish_option': publish_option
                }
                
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                db.rollback()
                return {
                    'success': False,
                    'message': f'Failed to save article to database: {str(db_error)}',
                    'data': None
                }
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Error in manual_generate_article: {e}")
            return {
                'success': False,
                'message': f'Error generating article: {str(e)}',
                'data': None
            }
            
    async def manual_publish_scheduled(self) -> Dict[str, Any]:
        """Manually publish all scheduled articles"""
        try:
            logger.info(" Manual publish of scheduled articles")
            await self._publish_scheduled_articles()
            
            return {
                'success': True,
                'message': 'Scheduled articles published successfully'
            }
            
        except Exception as e:
            logger.error(f"Error in manual_publish_scheduled: {e}")
            return {
                'success': False,
                'message': f'Error publishing articles: {str(e)}'
            }
            
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'automation_enabled': self.automation_enabled,
            'generation_time': self.generation_time,
            'publish_time': self.publish_time,
            'timezone': str(self.timezone),
            'next_generation': self._get_next_generation_time().isoformat(),
            'next_publish': self._get_next_publish_time().isoformat()
        }
        
    def _get_next_generation_time(self) -> datetime:
        """Get the next generation time (6 AM IST)"""
        now = datetime.now(self.timezone)
        generation_time = now.replace(
            hour=6, 
            minute=0, 
            second=0, 
            microsecond=0
        )
        
        # If it's already past 6 AM today, schedule for tomorrow
        if now >= generation_time:
            generation_time += timedelta(days=1)
            
        return generation_time
        
    def toggle_automation(self, enabled: bool) -> Dict[str, Any]:
        """Toggle automation on/off"""
        self.automation_enabled = enabled
        status = "enabled" if enabled else "disabled"
        logger.info(f" Automation {status}")
        
        return {
            'success': True,
            'message': f'Automation {status}',
            'automation_enabled': self.automation_enabled
        }
        
    def update_schedule(self, generation_time: str, publish_time: str) -> Dict[str, Any]:
        """Update the schedule times"""
        try:
            # Validate time format
            datetime.strptime(generation_time, "%H:%M")
            datetime.strptime(publish_time, "%H:%M")
            
            self.generation_time = generation_time
            self.publish_time = publish_time
            
            logger.info(f"  Schedule updated: Generate at {generation_time}, Publish at {publish_time}")
            
            return {
                'success': True,
                'message': 'Schedule updated successfully',
                'generation_time': self.generation_time,
                'publish_time': self.publish_time
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': f'Invalid time format: {str(e)}'
            }
    
    def _filter_relevant_research_data(self, scraped_articles: List[Dict[str, Any]], topic_title: str) -> List[Dict[str, Any]]:
        """Filter and clean research data relevant to the topic"""
        try:
            if not scraped_articles:
                return []
            
            logger.info(f" Filtering research data for topic: {topic_title}")
            
            # Convert topic to lowercase for matching
            topic_lower = topic_title.lower()
            topic_keywords = set(topic_lower.split())
            
            relevant_articles = []
            seen_titles = set()  # To remove duplicates
            
            for article in scraped_articles:
                try:
                    title = article.get('title', '').lower()
                    content = article.get('content', article.get('summary', '')).lower()
                    
                    # Skip if we've seen this title before (duplicate removal)
                    if title in seen_titles:
                        continue
                    
                    # Calculate relevance score based on keyword matches
                    relevance_score = 0
                    
                    # Check title matches (higher weight)
                    title_matches = sum(1 for keyword in topic_keywords if keyword in title)
                    relevance_score += title_matches * 3
                    
                    # Check content matches
                    content_matches = sum(1 for keyword in topic_keywords if keyword in content)
                    relevance_score += content_matches
                    
                    # Only include articles with some relevance
                    if relevance_score > 0:
                        article_copy = article.copy()
                        article_copy['relevance_score'] = relevance_score
                        relevant_articles.append(article_copy)
                        seen_titles.add(title)
                        
                except Exception as e:
                    logger.warning(f"Error processing article: {e}")
                    continue
            
            # Sort by relevance score (highest first) and limit to top 10
            relevant_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            filtered_articles = relevant_articles[:10]
            
            logger.info(f"📊 Filtered {len(scraped_articles)} articles down to {len(filtered_articles)} relevant sources")
            
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Error filtering research data: {e}")
            return scraped_articles[:10] if scraped_articles else []  # Fallback to first 10

# Global scheduler instance
scheduler_service = SchedulerService()
