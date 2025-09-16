import asyncio
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from .config import PERPLEXITY_API_KEY
from .deep_research_models import Source, SourceKind, ReportOutline
from .indian_kanoon_service import IndianKanoonService

class SourcingPipeline:
    """Discovers and fetches legal sources from multiple databases"""
    
    def __init__(self):
        self.perplexity_api_key = PERPLEXITY_API_KEY
        self.kanoon_service = IndianKanoonService()
        
    async def discover_sources(self, outline: ReportOutline, topic: str) -> List[Source]:
        """Discover sources for all sections in the outline"""
        
        all_sources = []
        
        # Discover sources for each section
        for section in outline.sections:
            section_sources = await self._discover_section_sources(section, topic)
            all_sources.extend(section_sources)
        
        # Deduplicate and rank sources
        ranked_sources = self._deduplicate_and_rank_sources(all_sources)
        
        return ranked_sources
    
    async def _discover_section_sources(self, section: Any, topic: str) -> List[Source]:
        """Discover sources for a specific section"""
        
        sources = []
        
        # 1. Search Indian Kanoon for case law
        case_sources = await self._search_indian_kanoon(section, topic)
        sources.extend(case_sources)
        
        # 2. Search Perplexity for current developments
        news_sources = await self._search_perplexity(section, topic)
        sources.extend(news_sources)
        
        # 3. Search government portals for statutes
        gov_sources = await self._search_gov_portals(section, topic)
        sources.extend(gov_sources)
        
        # 4. Search academic databases for papers
        academic_sources = await self._search_academic_databases(section, topic)
        sources.extend(academic_sources)
        
        return sources
    
    async def _search_indian_kanoon(self, section: Any, topic: str) -> List[Source]:
        """Search Indian Kanoon for relevant case law"""
        
        sources = []
        
        try:
            # Use the existing Indian Kanoon service
            search_queries = self._generate_kanoon_queries(section, topic)
            print(f"Searching Indian Kanoon with queries: {search_queries}")
            
            for query in search_queries:
                results = await self.kanoon_service.search_cases(query)
                print(f"Indian Kanoon results for '{query}': {len(results.get('cases', []))} cases found")
                
                for result in results.get("cases", []):
                    source = Source(
                        id=f"kanoon_{result.get('id', hash(result.get('title', '')))}",
                        url=result.get("url", ""),
                        title=result.get("title", "Untitled Case"),
                        kind=SourceKind.CASE,
                        jurisdiction="India",
                        court=result.get("court", "Unknown Court"),
                        date=self._parse_date(result.get("date", "")),
                        trust_score=self._calculate_kanoon_trust_score(result),
                        treatment=result.get("treatment", None)
                    )
                    sources.append(source)
                    print(f"Added source: {source.title[:50]}...")
        
        except Exception as e:
            print(f"Error searching Indian Kanoon: {e}")
            import traceback
            traceback.print_exc()
        
        return sources
    
    async def _search_perplexity(self, section: Any, topic: str) -> List[Source]:
        """Search Perplexity for current developments"""
        
        sources = []
        
        # Skip Perplexity for now and use more Indian Kanoon searches instead
        # Perplexity API is having issues, so we'll rely on Indian Kanoon for news cases
        try:
            # Search for recent cases and developments through Indian Kanoon
            news_queries = [
                f"{topic} 2024",
                f"{topic} recent judgment",
                f"{topic} latest case"
            ]
            
            for query in news_queries[:1]:  # Limit to 1 query to avoid duplicates
                results = await self.kanoon_service.search_cases(query)
                print(f"Indian Kanoon news search for '{query}': {len(results.get('cases', []))} cases found")
                
                for result in results.get("cases", [])[:2]:  # Limit to 2 results per query
                    source = Source(
                        id=f"kanoon_news_{hash(result.get('title', ''))}",
                        url=result.get("url", ""),
                        title=result.get("title", "Recent Case"),
                        kind=SourceKind.NEWS,
                        jurisdiction="India",
                        court=result.get("court", "Unknown Court"),
                        date=self._parse_date(result.get("date", "")),
                        trust_score=0.75,  # Lower trust score for news-type sources
                        treatment=result.get("treatment", None)
                    )
                    sources.append(source)
                    print(f"Added news source: {source.title[:50]}...")
        
        except Exception as e:
            print(f"Error searching for news through Indian Kanoon: {e}")
        
        return sources
    
    async def _search_gov_portals(self, section: Any, topic: str) -> List[Source]:
        """Search government portals for statutes and regulations"""
        
        sources = []
        
        try:
            # Use Indian Kanoon to search for acts, statutes, and sections
            statute_queries = [
                f"{topic} bare act",
                f"{topic} statute",
                f"{topic} section",
                f"{topic} regulation"
            ]
            
            for query in statute_queries[:2]:  # Limit to 2 queries
                results = await self.kanoon_service.search_cases(query)
                print(f"Indian Kanoon statute search for '{query}': {len(results.get('cases', []))} results found")
                
                for result in results.get("cases", [])[:2]:  # Limit results
                    # Check if it's actually a statute/section
                    title_lower = result.get("title", "").lower()
                    if "section" in title_lower or "act" in title_lower or "regulation" in title_lower:
                        source = Source(
                            id=f"kanoon_statute_{hash(result.get('title', ''))}",
                            url=result.get("url", ""),
                            title=result.get("title", "Legal Provision"),
                            kind=SourceKind.STATUTE,
                            jurisdiction="India",
                            date=self._parse_date(result.get("date", "")),
                            trust_score=0.9,  # High trust for actual statutes
                            treatment=None
                        )
                        sources.append(source)
                        print(f"Added statute source: {source.title[:50]}...")
        
        except Exception as e:
            print(f"Error searching for statutes through Indian Kanoon: {e}")
        
        return sources
    
    async def _search_academic_databases(self, section: Any, topic: str) -> List[Source]:
        """Search academic databases for research papers"""
        
        sources = []
        
        try:
            # Use Indian Kanoon to find academic/analytical cases and commentaries
            academic_queries = [
                f"{topic} analysis",
                f"{topic} commentary",
                f"{topic} jurisprudence",
                f"{topic} doctrine"
            ]
            
            for query in academic_queries[:2]:  # Limit to 2 queries
                results = await self.kanoon_service.search_cases(query)
                print(f"Indian Kanoon academic search for '{query}': {len(results.get('cases', []))} results found")
                
                for result in results.get("cases", [])[:1]:  # Limit to 1 result per query
                    # Create academic-style source from case law analysis
                    source = Source(
                        id=f"kanoon_academic_{hash(result.get('title', ''))}",
                        url=result.get("url", ""),
                        title=f"Legal Analysis: {result.get('title', 'Case Study')}",
                        kind=SourceKind.PAPER,
                        jurisdiction="India",
                        court=result.get("court", ""),
                        date=self._parse_date(result.get("date", "")),
                        trust_score=0.7,  # Moderate trust for academic sources
                        treatment=result.get("treatment", None)
                    )
                    sources.append(source)
                    print(f"Added academic source: {source.title[:50]}...")
        
        except Exception as e:
            print(f"Error searching for academic sources through Indian Kanoon: {e}")
        
        return sources
    
    def _generate_kanoon_queries(self, section: Any, topic: str) -> List[str]:
        """Generate search queries for Indian Kanoon"""
        
        queries = []
        
        # Base query from section title and topic
        base_query = f"{topic} {section.title}"
        queries.append(base_query)
        
        # Add specific legal terms
        legal_terms = ["act", "section", "rule", "regulation", "order", "judgment"]
        for term in legal_terms:
            queries.append(f"{base_query} {term}")
        
        return queries[:3]  # Limit to 3 queries
    
    def _generate_perplexity_queries(self, section: Any, topic: str) -> List[str]:
        """Generate search queries for Perplexity"""
        
        queries = []
        
        # Current developments
        queries.append(f"recent developments {topic} India 2024")
        queries.append(f"latest news {topic} legal India")
        queries.append(f"current status {topic} India law")
        
        return queries[:2]  # Limit to 2 queries
    
    def _generate_gov_queries(self, section: Any, topic: str) -> List[str]:
        """Generate search queries for government portals"""
        
        queries = []
        
        # Statute searches
        queries.append(f"{topic} act India")
        queries.append(f"{topic} rules India")
        queries.append(f"{topic} regulations India")
        
        return queries[:2]  # Limit to 2 queries
    
    def _generate_academic_queries(self, section: Any, topic: str) -> List[str]:
        """Generate search queries for academic databases"""
        
        queries = []
        
        # Academic searches
        queries.append(f"{topic} legal research India")
        queries.append(f"{topic} academic paper India")
        
        return queries[:2]  # Limit to 2 queries
    
    async def _call_perplexity_api(self, query: str) -> Dict[str, Any]:
        """Call Perplexity API"""
        
        if not self.perplexity_api_key:
            return {"choices": []}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Search for recent information about: {query}. Provide sources with URLs."
                            }
                        ],
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Perplexity API success for query: {query[:50]}...")
                    return result
                else:
                    print(f"Perplexity API error: {response.status_code} - {response.text}")
                    return {"choices": []}
        
        except Exception as e:
            print(f"Error calling Perplexity API: {e}")
            return {"choices": []}
    
    def _extract_sources_from_content(self, content: str, query: str) -> List[Source]:
        """Extract sources from Perplexity content"""
        
        sources = []
        
        # TODO: Implement real URL extraction from content
        sources.append(Source(
            id=f"perplexity_{hash(query)}",
            url="https://example-news.com/article",
            title=f"Recent Development: {query}",
            kind=SourceKind.NEWS,
            jurisdiction="India",
            date=datetime.now() - timedelta(days=7),
            trust_score=0.7,
            domain="example-news.com"
        ))
        
        return sources
    
    async def _search_egazette(self, query: str) -> List[Source]:
        """Search eGazette for official acts and rules"""
        # Deprecated - now handled in _search_gov_portals using Indian Kanoon
        return []
    
    async def _search_ministry_websites(self, query: str) -> List[Source]:
        """Search ministry websites for guidance and circulars"""
        # Deprecated - now handled in _search_gov_portals using Indian Kanoon
        return []
    
    async def _search_legal_journals(self, query: str) -> List[Source]:
        """Search legal journals for academic papers"""
        # Deprecated - now handled in _search_academic_databases using Indian Kanoon
        return []
    
    async def _search_research_repositories(self, query: str) -> List[Source]:
        """Search research repositories for papers"""
        # Deprecated - now handled in _search_academic_databases using Indian Kanoon
        return []
    
    def _calculate_kanoon_trust_score(self, result: Dict[str, Any]) -> float:
        """Calculate trust score for Indian Kanoon results"""
        
        score = 0.5  # Base score
        
        # Court hierarchy
        court = result.get("court", "").lower()
        if "supreme court" in court:
            score += 0.4
        elif "high court" in court:
            score += 0.3
        elif "district court" in court:
            score += 0.1
        
        # Treatment
        treatment = result.get("treatment", "").lower()
        if "followed" in treatment:
            score += 0.1
        elif "overruled" in treatment:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = [
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
        
        except Exception:
            return None
    
    def _deduplicate_and_rank_sources(self, sources: List[Source]) -> List[Source]:
        """Deduplicate sources and rank by trust score"""
        
        # Deduplicate by URL
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)
        
        # Rank by trust score
        ranked_sources = sorted(unique_sources, key=lambda x: x.trust_score, reverse=True)
        
        return ranked_sources
