import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import atoma
import re
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class LegalNewsScraper:
    def __init__(self):
        self.session = None
        self.legal_sources = [
            # RSS Feeds
            {
                'name': 'Supreme Court of India',
                'url': 'https://main.sci.gov.in/rss/rss.xml',
                'type': 'rss',
                'category': 'judicial'
            },
            {
                'name': 'Legal News India',
                'url': 'https://www.legalnewsindia.com/feed/',
                'type': 'rss',
                'category': 'general'
            },
            {
                'name': 'Bar and Bench',
                'url': 'https://www.barandbench.com/feed',
                'type': 'rss',
                'category': 'legal_news'
            },
            {
                'name': 'Live Law',
                'url': 'https://www.livelaw.in/feed/',
                'type': 'rss',
                'category': 'legal_news'
            },
            {
                'name': 'SCC Online',
                'url': 'https://www.scconline.com/blog/feed/',
                'type': 'rss',
                'category': 'case_law'
            },
            # Web Scraping Targets
            {
                'name': 'Law.com India',
                'url': 'https://www.law.com/international-edition/india/',
                'type': 'scrape',
                'category': 'corporate_law',
                'selectors': {
                    'articles': 'article, .article-item, .news-item',
                    'title': 'h1, h2, h3, .title, .headline',
                    'content': '.content, .article-content, .summary, p'
                }
            },
            {
                'name': 'Legal Era',
                'url': 'https://www.legalera.com/',
                'type': 'scrape',
                'category': 'legal_news',
                'selectors': {
                    'articles': '.news-item, .article, .post',
                    'title': 'h1, h2, h3, .title',
                    'content': '.content, .excerpt, .summary'
                }
            }
        ]
        
        self.scraped_data = []
        self.last_scrape_time = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all legal news sources and return collected data"""
        logger.info(" Starting legal news scraping...")
        
        all_articles = []
        
        # Process RSS feeds and web scraping in parallel
        tasks = []
        for source in self.legal_sources:
            if source['type'] == 'rss':
                tasks.append(self._scrape_rss_feed(source))
            elif source['type'] == 'scrape':
                tasks.append(self._scrape_website(source))
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all articles
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
        
        # Filter and clean articles
        filtered_articles = self._filter_and_clean_articles(all_articles)
        
        self.scraped_data = filtered_articles
        self.last_scrape_time = datetime.now()
        
        logger.info(f" Scraping completed. Found {len(filtered_articles)} relevant legal articles")
        return filtered_articles

    async def _scrape_rss_feed(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape RSS feed for legal news"""
        try:
            logger.info(f"📡 Scraping RSS: {source['name']}")
            
            async with self.session.get(source['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = atoma.parse_rss_bytes(content.encode('utf-8'))
                    
                    articles = []
                    for entry in feed.items[:10]:  # Limit to 10 most recent
                        article = {
                            'title': entry.title or '',
                            'summary': entry.description or '',
                            'link': entry.link or '',
                            'published': entry.pub_date,
                            'source': source['name'],
                            'category': source['category'],
                            'type': 'rss'
                        }
                        
                        # Parse published date
                        if article['published']:
                            try:
                                article['published'] = article['published'].replace(tzinfo=None)
                            except:
                                article['published'] = datetime.now()
                        else:
                            article['published'] = datetime.now()
                        
                        articles.append(article)
                    
                    logger.info(f" RSS {source['name']}: Found {len(articles)} articles")
                    return articles
                else:
                    logger.warning(f"❌ RSS {source['name']}: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ RSS {source['name']} error: {e}")
            return []

    async def _scrape_website(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape website for legal news articles"""
        try:
            logger.info(f"🌐 Scraping website: {source['name']}")
            
            async with self.session.get(source['url']) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    articles = []
                    selectors = source.get('selectors', {})
                    
                    # Find article containers
                    article_elements = soup.select(selectors.get('articles', 'article'))
                    
                    for element in article_elements[:15]:  # Limit to 15 articles
                        try:
                            # Extract title
                            title_elem = element.select_one(selectors.get('title', 'h1, h2, h3'))
                            title = title_elem.get_text(strip=True) if title_elem else ''
                            
                            # Extract content/summary
                            content_elem = element.select_one(selectors.get('content', 'p'))
                            content = content_elem.get_text(strip=True) if content_elem else ''
                            
                            # Extract link
                            link_elem = element.find('a', href=True)
                            link = urljoin(source['url'], link_elem['href']) if link_elem else source['url']
                            
                            if title and len(title) > 10:  # Basic quality filter
                                article = {
                                    'title': title,
                                    'summary': content[:500] if content else '',  # Limit summary length
                                    'link': link,
                                    'published': datetime.now(),  # Approximate time
                                    'source': source['name'],
                                    'category': source['category'],
                                    'type': 'scraped'
                                }
                                articles.append(article)
                                
                        except Exception as e:
                            logger.debug(f"Error parsing article element: {e}")
                            continue
                    
                    logger.info(f" Website {source['name']}: Found {len(articles)} articles")
                    return articles
                else:
                    logger.warning(f"❌ Website {source['name']}: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Website {source['name']} error: {e}")
            return []

    def _filter_and_clean_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and clean scraped articles for relevance and quality"""
        legal_keywords = [
            'law', 'legal', 'court', 'judge', 'judgment', 'ruling', 'case', 'litigation',
            'supreme court', 'high court', 'district court', 'tribunal', 'commission',
            'constitution', 'amendment', 'bill', 'act', 'regulation', 'policy',
            'criminal', 'civil', 'corporate', 'contract', 'property', 'family',
            'cyber', 'data protection', 'privacy', 'intellectual property', 'patent',
            'trademark', 'copyright', 'merger', 'acquisition', 'insolvency',
            'sebi', 'rbi', 'gst', 'tax', 'compliance', 'governance',
            'bail', 'anticipatory bail', 'arrest', 'custody', 'evidence',
            'fundamental rights', 'human rights', 'constitutional', 'judicial review'
        ]
        
        filtered_articles = []
        seen_titles = set()
        
        for article in articles:
            # Basic quality checks
            if not article.get('title') or len(article['title']) < 10:
                continue
                
            # Check for legal relevance
            title_lower = article['title'].lower()
            summary_lower = article.get('summary', '').lower()
            
            is_legal_relevant = any(
                keyword in title_lower or keyword in summary_lower 
                for keyword in legal_keywords
            )
            
            if not is_legal_relevant:
                continue
            
            # Remove duplicates
            title_hash = hash(article['title'].lower().strip())
            if title_hash in seen_titles:
                continue
            seen_titles.add(title_hash)
            
            # Clean and format
            article['title'] = article['title'].strip()
            article['summary'] = article.get('summary', '').strip()
            article['relevance_score'] = self._calculate_relevance_score(article, legal_keywords)
            
            filtered_articles.append(article)
        
        # Sort by relevance score and recency
        filtered_articles.sort(
            key=lambda x: (x['relevance_score'], x['published']), 
            reverse=True
        )
        
        return filtered_articles[:50]  # Return top 50 most relevant

    def _calculate_relevance_score(self, article: Dict[str, Any], keywords: List[str]) -> int:
        """Calculate relevance score based on keyword matches"""
        title_lower = article['title'].lower()
        summary_lower = article.get('summary', '').lower()
        
        score = 0
        
        # Title matches are worth more
        for keyword in keywords:
            if keyword in title_lower:
                score += 3
            if keyword in summary_lower:
                score += 1
        
        # Boost for recent articles
        if article['published']:
            hours_ago = (datetime.now() - article['published']).total_seconds() / 3600
            if hours_ago < 24:
                score += 5
            elif hours_ago < 72:
                score += 2
        
        return score

    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get statistics about the last scraping run"""
        return {
            'last_scrape_time': self.last_scrape_time.isoformat() if self.last_scrape_time else None,
            'total_articles_found': len(self.scraped_data),
            'sources_scraped': len(self.legal_sources),
            'articles_by_category': self._get_articles_by_category(),
            'top_sources': self._get_top_sources()
        }

    def _get_articles_by_category(self) -> Dict[str, int]:
        """Get count of articles by category"""
        categories = {}
        for article in self.scraped_data:
            category = article.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _get_top_sources(self) -> List[Dict[str, Any]]:
        """Get top sources by article count"""
        sources = {}
        for article in self.scraped_data:
            source = article.get('source', 'unknown')
            if source not in sources:
                sources[source] = {'name': source, 'count': 0, 'avg_score': 0}
            sources[source]['count'] += 1
            sources[source]['avg_score'] += article.get('relevance_score', 0)
        
        # Calculate average scores
        for source in sources.values():
            if source['count'] > 0:
                source['avg_score'] = round(source['avg_score'] / source['count'], 2)
        
        return sorted(sources.values(), key=lambda x: x['count'], reverse=True)[:5]

# Global scraper instance
legal_scraper = LegalNewsScraper()
