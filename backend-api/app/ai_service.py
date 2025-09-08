import os
import httpx
import google.generativeai as genai
from typing import Optional, Dict, Any, Literal
import re
from datetime import datetime

class AIContentGenerator:
    def __init__(self):
        # Initialize Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
    
    async def generate_article(
        self, 
        topic: str, 
        article_type: Literal["quick", "standard", "deep"] = "standard",
        ai_provider: Literal["gemini", "perplexity", "both"] = "gemini"
    ) -> Dict[str, Any]:
        """Generate article using specified AI provider"""
        
        try:
            # For now, always use Gemini as it's more reliable
            # TODO: Fix Perplexity integration later
            result = await self._generate_with_gemini(topic, article_type)
            if not result.get("error"):
                return result
            
            # If Gemini fails, return the error
            return result
            
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}
    
    async def _generate_with_gemini(self, topic: str, article_type: str) -> Dict[str, Any]:
        """Generate content using Google Gemini"""
        if not self.gemini_api_key:
            return {"error": "Gemini API key not configured"}
        
        try:
            prompt = self._create_prompt(topic, article_type)
            response = self.gemini_model.generate_content(prompt)
            
            if not response.text:
                return {"error": "Gemini returned empty response"}
            
            return self._parse_response(response.text, "gemini", topic)
            
        except Exception as e:
            return {"error": f"Gemini error: {str(e)}"}
    
    async def _generate_with_perplexity(self, topic: str, article_type: str) -> Dict[str, Any]:
        """Generate content using Perplexity AI"""
        if not self.perplexity_api_key:
            return {"error": "Perplexity API key not configured"}
        
        try:
            prompt = self._create_prompt(topic, article_type)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.perplexity_url,
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an investigative journalist writing for LexLeaks, a platform exposing legal industry misconduct. Write detailed, well-researched articles with a vintage newspaper style."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    return self._parse_response(content, "perplexity", topic)
                else:
                    return {"error": f"Perplexity API error: {response.status_code}"}
                    
        except Exception as e:
            return {"error": f"Perplexity error: {str(e)}"}
    
    def _create_prompt(self, topic: str, article_type: str) -> str:
        """Create article generation prompt based on type"""
        
        word_counts = {
            "quick": "300-500 words",
            "standard": "800-1200 words", 
            "deep": "1500-2000 words"
        }
        
        base_prompt = f"""
Write a compelling investigative article for LexLeaks about: {topic}

Requirements:
- Length: {word_counts[article_type]}
- Style: Investigative journalism with vintage newspaper tone
- Format: HTML with proper tags (<h1>, <p>, <blockquote>, etc.)
- Structure: Headline, introduction, main points with evidence, conclusion
- Include recent facts and context where relevant
- Use professional, authoritative tone
- Start with an engaging <h1> headline
- Add <blockquote> for important quotes or key points

Make it engaging and informative for readers interested in legal industry transparency.
"""
        
        return base_prompt
    
    def _parse_response(self, content: str, provider: str, topic: str) -> Dict[str, Any]:
        """Parse AI response and extract components"""
        
        # Extract title
        title = self._extract_title(content)
        if not title:
            title = f"Investigation: {topic}"
        
        # Create excerpt
        excerpt = self._create_excerpt(content)
        
        # Generate slug
        slug = self._generate_slug(title)
        
        return {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "slug": slug,
            "provider": provider,
            "generated_at": datetime.utcnow().isoformat(),
            "word_count": len(content.split()),
            "topic": topic
        }
    
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
