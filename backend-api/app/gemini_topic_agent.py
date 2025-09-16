import asyncio
import logging
from typing import List, Dict, Any, Optional
import random
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiTopicAgent:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. Using fallback topic generation.")
            self.gemini_available = False
        else:
            genai.configure(api_key=api_key)
            self.gemini_available = True
        
        self.model = genai.GenerativeModel('gemini-1.5-flash') if self.gemini_available else None
        # Add non-determinism so repeated runs over the same input vary a bit
        self.generation_config = None
        if self.gemini_available:
            try:
                self.generation_config = genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.9,
                    top_k=40
                )
            except Exception:
                # Older SDKs may not support types.GenerationConfig; fall back silently
                self.generation_config = None
        
        # Track recently returned titles to avoid immediate repetition across runs
        self._recent_titles: List[str] = []
        
        # Legal topic templates for fallback
        self.fallback_topics = [
            "Supreme Court's Latest Ruling on Digital Privacy Rights",
            "New Corporate Governance Guidelines: What Companies Need to Know",
            "Criminal Law Reforms: Impact on Bail and Evidence Procedures",
            "Data Protection Act: Compliance Challenges for Indian Businesses",
            "High Court's Decision on Property Rights and Inheritance Laws",
            "Cyber Crime Trends: Legal Implications for Digital Businesses",
            "Labour Law Amendments: Rights and Responsibilities of Employers",
            "Environmental Law: Recent Judgments on Climate Change Litigation",
            "Intellectual Property Rights: Patent Law Updates and Implications",
            "Constitutional Law: Fundamental Rights in the Digital Age"
        ]

    async def generate_trending_topics(self, scraped_articles: List[Dict[str, Any]], 
                                     num_topics: int = 5) -> List[Dict[str, Any]]:
        """Generate trending legal topics from scraped articles using Gemini AI"""
        
        if not scraped_articles:
            logger.warning("No scraped articles provided. Using fallback topics.")
            return self._get_fallback_topics(num_topics)
        
        if not self.gemini_available:
            logger.info("Gemini API not available. Using fallback topic generation.")
            return self._get_fallback_topics(num_topics)
        
        try:
            logger.info(f"Generating trending topics from {len(scraped_articles)} articles using Gemini AI")
            
            # Prepare context for Gemini
            context = self._prepare_context_for_gemini(scraped_articles)
            
            # Create prompt for topic generation
            prompt = self._create_topic_generation_prompt(context, num_topics)
            
            # Generate topics using Gemini
            response = await self._call_gemini_api(prompt)
            
            # Parse and format the response
            topics = self._parse_gemini_response(response, num_topics)
            # Attach likely source links from scraped articles for transparency
            topics = self._attach_source_links(topics, scraped_articles)
            topics = self._filter_new_topics(topics, num_topics)
            
            logger.info(f" Generated {len(topics)} trending topics using Gemini AI")
            return topics
            
        except Exception as e:
            logger.error(f"❌ Error generating topics with Gemini: {e}")
            logger.info("Falling back to rule-based topic generation")
            return self._filter_new_topics(
                self._generate_fallback_topics_from_articles(scraped_articles, num_topics),
                num_topics
            )

    def _prepare_context_for_gemini(self, articles: List[Dict[str, Any]]) -> str:
        """Prepare scraped articles context for Gemini AI"""
        context = "Recent Legal News Articles:\n\n"
        
        # Group articles by category for better context
        categories = {}
        # Shuffle to avoid feeding the exact same first-N articles each run
        shuffled = articles[:]
        random.shuffle(shuffled)
        for article in shuffled[:20]:  # Use top 20 articles in random order
            category = article.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(article)
        
        for category, cat_articles in categories.items():
            context += f"=== {category.upper()} ===\n"
            for article in cat_articles[:5]:  # Max 5 per category
                context += f"• {article['title']}\n"
                if article.get('summary'):
                    context += f"  Summary: {article['summary'][:200]}...\n"
                context += f"  Source: {article.get('source', 'Unknown')}\n\n"
        
        return context

    def _create_topic_generation_prompt(self, context: str, num_topics: int) -> str:
        """Create prompt for Gemini AI to generate trending topics"""
        prompt = f"""
You are a legal content strategist for LexLeaks, a legal news and analysis platform in India. 
Based on the recent legal news articles provided below, generate {num_topics} compelling, trending legal topics that would make excellent articles.

CONTEXT:
{context}

REQUIREMENTS:
1. Topics should be relevant to Indian legal system and current events
2. Make them eye-catching and SEO-friendly
3. Focus on trending legal issues, recent judgments, or emerging legal trends
4. Each topic should be specific enough to write a comprehensive article about
5. Prioritize topics that would interest legal professionals, law students, and general public
6. Include a mix of different legal areas (criminal, civil, corporate, constitutional, etc.)

OUTPUT FORMAT:
For each topic, provide:
- title: The main topic title (compelling and SEO-friendly)
- category: Legal area (e.g., "Criminal Law", "Corporate Law", "Constitutional Law")
- angle: The specific angle or focus for the article
- target_audience: Who would be most interested (e.g., "Legal Professionals", "General Public", "Law Students")
- trending_reason: Why this topic is trending now
- suggested_article_type: "quick", "standard", or "deep"
- suggested_template: "legal_explainer" or "case_analysis"

Generate exactly {num_topics} topics in JSON format.
"""
        return prompt

    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API to generate topics"""
        try:
            # Use asyncio to run the synchronous Gemini call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                (lambda: self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )) if self.generation_config else (lambda: self.model.generate_content(prompt))
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

    def _parse_gemini_response(self, response: str, num_topics: int) -> List[Dict[str, Any]]:
        """Parse Gemini response and extract topics"""
        topics = []
        
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                topics_data = json.loads(json_str)
                
                for topic_data in topics_data[:num_topics]:
                    topic = {
                        'title': topic_data.get('title', ''),
                        'category': topic_data.get('category', 'General Legal'),
                        'angle': topic_data.get('angle', ''),
                        'target_audience': topic_data.get('target_audience', 'General Public'),
                        'trending_reason': topic_data.get('trending_reason', ''),
                        'suggested_article_type': topic_data.get('suggested_article_type', 'standard'),
                        'suggested_template': topic_data.get('suggested_template', 'legal_explainer'),
                        'generated_by': 'gemini_ai',
                        'confidence_score': 0.9
                    }
                    # Infer a better template when the title clearly indicates a case/judgment
                    inferred = self._infer_template_from_topic(topic['title'], topic['angle'])
                    if inferred:
                        topic['suggested_template'] = inferred
                    topics.append(topic)
            else:
                # Fallback: parse text response
                topics = self._parse_text_response(response, num_topics)
                
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            topics = self._parse_text_response(response, num_topics)
        
        return topics

    def _parse_text_response(self, response: str, num_topics: int) -> List[Dict[str, Any]]:
        """Parse text response when JSON parsing fails"""
        topics = []
        lines = response.split('\n')
        
        current_topic = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Title:') or line.startswith('Topic:'):
                if current_topic:
                    topics.append(current_topic)
                current_topic = {
                    'title': line.split(':', 1)[1].strip(),
                    'category': 'General Legal',
                    'angle': '',
                    'target_audience': 'General Public',
                    'trending_reason': '',
                    'suggested_article_type': 'standard',
                    'suggested_template': 'legal_explainer',
                    'generated_by': 'gemini_ai',
                    'confidence_score': 0.7
                }
            elif line.startswith('Category:'):
                current_topic['category'] = line.split(':', 1)[1].strip()
            elif line.startswith('Angle:'):
                current_topic['angle'] = line.split(':', 1)[1].strip()
        
        if current_topic:
            topics.append(current_topic)
        
        # Infer templates for parsed topics
        for t in topics:
            inferred = self._infer_template_from_topic(t.get('title', ''), t.get('angle', ''))
            if inferred:
                t['suggested_template'] = inferred
        
        return topics[:num_topics]

    def _get_fallback_topics(self, num_topics: int) -> List[Dict[str, Any]]:
        """Get fallback topics when Gemini is not available"""
        import random
        
        selected_topics = random.sample(self.fallback_topics, min(num_topics, len(self.fallback_topics)))
        
        topics = []
        for title in selected_topics:
            topic = {
                'title': title,
                'category': self._categorize_topic(title),
                'angle': f"Analysis of {title.lower()}",
                'target_audience': 'Legal Professionals',
                'trending_reason': 'Current legal developments and public interest',
                'suggested_article_type': 'standard',
                'suggested_template': 'legal_explainer',
                'generated_by': 'fallback',
                'confidence_score': 0.5
            }
            topics.append(topic)
        
        return topics

    def _generate_fallback_topics_from_articles(self, articles: List[Dict[str, Any]], 
                                              num_topics: int) -> List[Dict[str, Any]]:
        """Generate topics from articles when Gemini fails"""
        topics = []
        
        # Group articles by category
        categories = {}
        for article in articles:
            category = article.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(article)
        
        # Create topics from top articles in each category
        for category, cat_articles in list(categories.items())[:num_topics]:
            if cat_articles:
                top_article = cat_articles[0]  # Most relevant article
                topic = {
                    'title': f"Breaking: {top_article['title']}",
                    'category': category.title(),
                    'angle': f"Comprehensive analysis of {top_article['title'].lower()}",
                    'target_audience': 'Legal Professionals',
                    'trending_reason': f"Recent developments in {category}",
                    'suggested_article_type': 'standard',
                    'suggested_template': self._infer_template_from_topic(top_article['title'], '') or 'legal_explainer',
                    'generated_by': 'rule_based',
                    'confidence_score': 0.6,
                    'source_article': top_article
                }
                topics.append(topic)
        
        # Shuffle to add variability
        random.shuffle(topics)
        return topics[:num_topics]

    def _infer_template_from_topic(self, title: str, angle: str) -> Optional[str]:
        """Infer template based on keywords indicating a court case or judgment."""
        text = f"{title} {angle}".lower()
        indicators_case = [
            'supreme court', 'high court', 'hc ', ' hc', 'judgment', 'order', 'verdict', 'cbI probe', 'bail', 'petition', 'writ', 'appeal'
        ]
        if any(k in text for k in indicators_case):
            return 'case_analysis'
        return None

    def _filter_new_topics(self, topics: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Avoid returning the exact same titles across consecutive runs."""
        seen = set(self._recent_titles)
        unique: List[Dict[str, Any]] = []
        for t in topics:
            title_key = t.get('title', '').strip().lower()
            if not title_key:
                continue
            if title_key in seen:
                continue
            unique.append(t)
        # Fallback if filtering removed everything
        if not unique:
            unique = topics[:]
        # Update recent titles window (keep last 100)
        for t in unique:
            title_key = t.get('title', '').strip().lower()
            if title_key:
                self._recent_titles.append(title_key)
        self._recent_titles = self._recent_titles[-100:]
        return unique[:limit]

    def _attach_source_links(self, topics: List[Dict[str, Any]], articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Attach top matching source links to each topic using simple keyword overlap."""
        def tokenize(text: str) -> set:
            import re
            tokens = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
            return {t for t in tokens if len(t) > 3}

        # Precompute tokens for articles
        article_tokens = []
        for a in articles:
            toks = tokenize(f"{a.get('title','')} {a.get('summary','')}")
            article_tokens.append((a, toks))

        for t in topics:
            ttoks = tokenize(f"{t.get('title','')} {t.get('angle','')}")
            scores = []
            for a, toks in article_tokens:
                if not a.get('link'):
                    continue
                overlap = len(ttoks & toks)
                if overlap > 0:
                    scores.append((overlap, a.get('link')))
            scores.sort(reverse=True, key=lambda x: x[0])
            source_links = [link for _, link in scores[:2]]
            if source_links:
                t['source_links'] = source_links
        return topics

    def _categorize_topic(self, title: str) -> str:
        """Categorize topic based on title keywords"""
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ['criminal', 'bail', 'arrest', 'evidence', 'ipc', 'crpc']):
            return 'Criminal Law'
        elif any(kw in title_lower for kw in ['corporate', 'company', 'sebi', 'merger', 'acquisition']):
            return 'Corporate Law'
        elif any(kw in title_lower for kw in ['constitutional', 'supreme court', 'fundamental rights']):
            return 'Constitutional Law'
        elif any(kw in title_lower for kw in ['cyber', 'data protection', 'privacy', 'digital']):
            return 'Technology Law'
        elif any(kw in title_lower for kw in ['property', 'contract', 'family', 'divorce']):
            return 'Civil Law'
        else:
            return 'General Legal'

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about the Gemini topic agent"""
        return {
            'gemini_available': self.gemini_available,
            'model_name': 'gemini-1.5-flash' if self.gemini_available else None,
            'fallback_topics_count': len(self.fallback_topics),
            'last_generation_time': datetime.now().isoformat()
        }

# Global Gemini topic agent instance
gemini_topic_agent = GeminiTopicAgent()
