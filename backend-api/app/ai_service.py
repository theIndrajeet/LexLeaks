import os
import httpx
import google.generativeai as genai
from typing import Optional, Dict, Any, Literal, List
import re
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self):
        # Initialize Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        
        logger.info(f"🔑 AI Service - Gemini API Key: {'Found' if self.gemini_api_key else 'NOT FOUND'}")
        logger.info(f"🔑 AI Service - Perplexity API Key: {'Found' if self.perplexity_api_key else 'NOT FOUND'}")
        
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ AI Service - Gemini configured successfully")
            except Exception as e:
                logger.error(f"❌ AI Service - Failed to configure Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            logger.warning("⚠️ AI Service - No Gemini API key, article generation will use fallback")
        
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
    
    async def generate_article(
        self, 
        topic: str, 
        article_type: Literal["quick", "standard", "deep"] = "standard",
        ai_provider: Literal["gemini", "perplexity", "both"] = "gemini",
        template: Literal["internship", "legal_explainer"] = "legal_explainer",
        # NEW ENHANCED PARAMETERS
        research_data: Optional[List[Dict[str, Any]]] = None,
        category: Optional[str] = None,
        publish_option: Optional[str] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Enhanced article generation with research data support"""
        
        try:
            # For now, always use Gemini as it's more reliable
            # TODO: Fix Perplexity integration later
            result = await self._generate_with_gemini_enhanced(
                topic, article_type, template, research_data, category, publish_option, scheduled_for
            )
            if not result.get("error"):
                return result
            
            # If Gemini fails, return the error
            return result
            
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}
    
    async def _generate_with_gemini_enhanced(
        self, 
        topic: str, 
        article_type: str, 
        template: str, 
        research_data: Optional[List[Dict[str, Any]]] = None,
        category: Optional[str] = None,
        publish_option: Optional[str] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Enhanced Gemini generation with research data"""
        if not self.gemini_api_key:
            return {"error": "Gemini API key not configured"}
        
        try:
            # Create enhanced prompt with research data
            prompt = self._create_enhanced_prompt(topic, article_type, template, research_data)
            response = self.gemini_model.generate_content(prompt)
            
            if not response.text:
                return {"error": "Gemini returned empty response"}
            
            # Parse response with enhanced data
            result = self._parse_enhanced_response(
                response.text, "gemini", topic, research_data, category, publish_option, scheduled_for
            )
            
            return result
            
        except Exception as e:
            return {"error": f"Gemini error: {str(e)}"}
    
    def _create_enhanced_prompt(
        self, 
        topic: str, 
        article_type: str, 
        template: str, 
        research_data: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Create enhanced prompt with research data"""
        
        word_counts = {
            "quick": "300-500 words",
            "standard": "800-1200 words", 
            "deep": "1500-2000 words"
        }
        
        # Build research context if available
        research_context = ""
        sources = []
        
        if research_data and len(research_data) > 0:
            research_context = "\n\n RESEARCH DATA PROVIDED:\n"
            research_context += "Use the following research data to write a factual, well-researched article:\n\n"
            
            for i, article in enumerate(research_data[:10], 1):  # Limit to top 10 sources
                title = article.get('title', 'Untitled')
                content = article.get('content', article.get('summary', ''))
                source_url = article.get('url', article.get('link', ''))
                published_date = article.get('published_date', article.get('pub_date', ''))
                
                research_context += f"SOURCE {i}:\n"
                research_context += f"Title: {title}\n"
                if published_date:
                    research_context += f"Date: {published_date}\n"
                research_context += f"Content: {content[:500]}...\n"  # Limit content length
                if source_url:
                    research_context += f"URL: {source_url}\n"
                    sources.append(f"[{i}] {title} - {source_url}")
                research_context += "\n"
            
            research_context += "\n REQUIREMENTS:\n"
            research_context += "- Use the above research data to write factual content\n"
            research_context += "- Cross-reference information from multiple sources\n"
            research_context += "- Include specific facts, dates, and details from the research\n"
            research_context += "- Add a 'References' section at the end with source citations\n"
            research_context += "- Generate a title based on the research data trends\n\n"
        
        # Create template-specific prompt
        if template == "internship":
            base_prompt = self._create_internship_prompt(topic, word_counts[article_type])
        elif template == "legal_explainer":
            base_prompt = self._create_legal_explainer_prompt(topic, word_counts[article_type])
        else:
            base_prompt = self._create_investigative_prompt(topic, word_counts[article_type])
        
        # Combine research context with base prompt
        enhanced_prompt = research_context + base_prompt
        
        # Add sources instruction if we have research data
        if sources:
            enhanced_prompt += f"\n\n SOURCES TO CITE:\n"
            for source in sources:
                enhanced_prompt += f"{source}\n"
        
        return enhanced_prompt
    
    def _create_internship_prompt(self, topic: str, word_count: str) -> str:
        """Create prompt for internship and career experience articles"""
        return f"""
Write a comprehensive internship and career experience article about: {topic}

Follow this EXACT template structure:

1. TITLE
Create an engaging title like "Internship Experience at [Company/Firm]: Application Process, Tasks, and Key Takeaways"

2. INTRODUCTION (150-200 words)
- Start with why this internship/career path matters
- Share a hook about competitiveness, firm reputation, or what students can gain
- Outline what the article will cover (application, experience, learnings)

3. APPLICATION PROCESS (300-400 words)
- Detail deadlines, where to apply, eligibility criteria
- Share tips on CVs, cover letters, networking, and references
- Mention any unique aspects (tests, interviews, writing samples)

4. WORK EXPERIENCE (400-500 words)
- Daily tasks, responsibilities, and learning opportunities
- Insights into work culture, mentorship, and training
- Highlight specific assignments (research, drafting, court visits, client work)

5. CHALLENGES AND OPPORTUNITIES (300-400 words)
- Share what was difficult (workload, steep learning curve, environment)
- Balance with positives (exposure, growth, skills developed)

6. KEY TAKEAWAYS (200-300 words)
- Summarize what students can expect
- Provide actionable tips for those applying

7. CONCLUSION (150-200 words)
- Wrap up with personal reflections or advice for future applicants

8. REFERENCES (if applicable)
- Link to firm websites, job portals, or official recruitment notices

9. DISCLAIMER
Include: "Disclaimer: The views expressed in this article are for informational purposes only and do not constitute legal advice. Readers are advised to consult a qualified professional for specific guidance."

Requirements:
- Length: {word_count}
- Format: HTML with proper tags (<h1>, <h2>, <h3>, <p>, <ul>, <li>, etc.)
- Use professional, informative tone
- Include specific details and actionable advice
- Make it valuable for law students and young professionals

Generate the complete article following this exact structure.
"""

    def _create_legal_explainer_prompt(self, topic: str, word_count: str) -> str:
        """Create prompt for legal explainer and analysis articles"""
        return f"""
Write a comprehensive legal explainer and analysis article about: {topic}

Follow this EXACT template structure:

1. TITLE
Create an engaging title like "Explained: [Topic] in India (2025 Update)"

2. INTRODUCTION (150-200 words)
- Begin with a relatable scenario: why this law/policy matters in daily or professional life
- Explain the importance of the topic in simple terms
- Outline the sections to be covered

3. BACKGROUND AND CONTEXT (300-400 words)
- Provide history and origins of the law or policy
- Highlight any recent events, amendments, or landmark cases that made the topic relevant

4. LEGAL FRAMEWORK (400-500 words)
- Summarize key provisions, statutes, or rules
- Mention applicable case law
- Break down complex sections into plain English

5. PRACTICAL IMPACT (400-500 words)
- Explain how this law affects individuals, businesses, or professionals
- Use examples: workplace disputes, contracts, compliance

6. CHALLENGES, CRITICISMS, OR DEBATES (300-400 words)
- Outline gaps, conflicts, or controversies in interpretation or application
- Highlight differing views (courts, policymakers, practitioners)

7. WAY FORWARD OR RECOMMENDATIONS (200-300 words)
- Suggest reforms, best practices, or how readers can stay compliant
- Include commentary on future developments

8. CONCLUSION (150-200 words)
- Recap the main points
- End with clarity: why this law/policy matters now and what readers should remember

9. REFERENCES
- Cite statutes, judgments, government portals, and academic works
- Use authoritative and up-to-date sources

10. DISCLAIMER
Include: "Disclaimer: The views expressed in this article are for informational purposes only and do not constitute legal advice. Readers are advised to consult a qualified professional for specific guidance."

Requirements:
- Length: {word_count}
- Format: Use HTML content tags ONLY (<h1>, <h2>, <h3>, <p>, <ul>, <li>, etc.) - DO NOT include <!DOCTYPE>, <html>, <head>, or <body> tags
- Use professional, authoritative tone
- Include recent facts and context
- Make complex legal concepts accessible
- Provide practical insights and examples
- Start directly with <h1> for the title, then <h2> for sections, <p> for paragraphs

Generate ONLY the article content with HTML tags, no document structure.
"""

    def _create_investigative_prompt(self, topic: str, word_count: str) -> str:
        """Create prompt for investigative articles (original format)"""
        return f"""
Write a compelling investigative article for LexLeaks about: {topic}

Requirements:
- Length: {word_count}
- Style: Investigative journalism with vintage newspaper tone
- Format: Use HTML content tags ONLY (<h1>, <h2>, <p>, <blockquote>, etc.) - DO NOT include <!DOCTYPE>, <html>, <head>, or <body> tags
- Structure: Headline, introduction, main points with evidence, conclusion
- Include recent facts and context where relevant
- Use professional, authoritative tone
- Start directly with <h1> headline, then <h2> for sections, <p> for paragraphs
- Add <blockquote> for important quotes or key points

Generate ONLY the article content with HTML tags, no document structure.
"""
    
    def _parse_enhanced_response(
        self, 
        content: str, 
        provider: str, 
        topic: str, 
        research_data: Optional[List[Dict[str, Any]]] = None,
        category: Optional[str] = None,
        publish_option: Optional[str] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Parse AI response with enhanced metadata"""
        
        # Clean up content - remove full HTML document structure if present
        content = self._clean_html_content(content)
        
        # Extract title
        title = self._extract_title(content)
        if not title:
            title = f"Investigation: {topic}"
        
        # Create excerpt
        excerpt = self._create_excerpt(content)
        
        # Generate slug
        slug = self._generate_slug(title)
        
        # Create post_id for scheduler compatibility
        post_id = f"ai_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "slug": slug,
            "provider": provider,
            "generated_at": datetime.utcnow().isoformat(),
            "word_count": len(content.split()),
            "topic": topic,
            "post_id": post_id,  # For scheduler compatibility
            "category": category or "ai-generated",
            "publish_option": publish_option or "draft",
            "scheduled_for": scheduled_for.isoformat() if scheduled_for else None,
            "research_sources_count": len(research_data) if research_data else 0
        }
        
        return result
    
    def _clean_html_content(self, content: str) -> str:
        """Clean HTML content by removing full document structure"""
        # Remove DOCTYPE declaration
        content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
        
        # Remove html, head, and body tags but keep their content
        content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<body[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</body>', '', content, flags=re.IGNORECASE)
        
        # Remove title tag if it exists (we'll extract it separately)
        content = re.sub(r'<title[^>]*>.*?</title>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def _extract_title(self, content: str) -> str:
        """Extract title from generated content"""
        # Try to find H1 tag first
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
            return title[:200]  # Limit length
        
        # Try to find first line that looks like a title
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                # Remove any HTML tags
                clean_line = re.sub(r'<[^>]+>', '', line).strip()
                if clean_line:
                    return clean_line
        
        return "Untitled Article"
    
    def _create_excerpt(self, content: str) -> str:
        """Create excerpt from content"""
        # Remove HTML tags
        clean_text = re.sub(r'<[^<]+?>', '', content)
        
        # Get first paragraph or first 200 characters
        paragraphs = clean_text.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 50:
                excerpt = para[:200].strip()
                if len(para) > 200:
                    excerpt += "..."
                return excerpt
        
        # Fallback: first 200 characters
        excerpt = clean_text[:200].strip()
        if len(clean_text) > 200:
            excerpt += "..."
        return excerpt
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        # Convert to lowercase and replace special chars
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        return slug[:100] if slug else "article"

# Initialize the AI service
ai_generator = AIContentGenerator()