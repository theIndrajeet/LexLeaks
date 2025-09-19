"""
AI Creative Agent for LexLeaks Notifications
Generates engaging, creative notifications using Gemini AI
"""

import os
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

class NotificationAIAgent:
    """AI agent that creates creative, engaging notifications"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found. Notification AI agent will use fallback templates.")
            self.gemini_available = False
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_available = True
                logger.info("✅ Notification AI Agent initialized with Gemini")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini for notifications: {e}")
                self.gemini_available = False
        
        # Define notification styles and templates
        self.styles = {
            "breaking": {
                "name": "Breaking News",
                "emoji_set": ["🚨", "⚡", "🔥", "💥"],
                "tone": "urgent",
                "template": "🚨 BREAKING: {title}\n{content}\nThis is BIG news 🔥\nRead now →"
            },
            "mystery": {
                "name": "Mystery/Teaser",
                "emoji_set": ["🤔", "🔍", "💡", "🎭"],
                "tone": "curious",
                "template": "🤔 What's {company} hiding?\nWe just uncovered something...\nSpoiler: {teaser}\nFind out →"
            },
            "urgent": {
                "name": "Urgent Action",
                "emoji_set": ["⚡", "🚨", "⏰", "🎯"],
                "tone": "urgent",
                "template": "⚡ URGENT: {title}\n{content}\nTime-sensitive information\nAct now →"
            },
            "community": {
                "name": "Community Update",
                "emoji_set": ["👥", "📰", "💬", "🎉"],
                "tone": "friendly",
                "template": "👥 LexLeaks Community Update\n{content}\nJoin the discussion\nView & Comment →"
            }
        }
    
    def analyze_content(self, post_data: Dict) -> Dict:
        """Analyze post content to determine notification strategy"""
        try:
            title = post_data.get("title", "")
            content = post_data.get("content", "")
            category = post_data.get("category", "")
            verification_status = post_data.get("verification_status", "unverified")
            
            # Determine impact level
            impact_keywords = ["scandal", "corruption", "fraud", "bribery", "lawsuit", "settlement", "resignation"]
            high_impact = any(keyword in title.lower() or keyword in content.lower() for keyword in impact_keywords)
            
            # Determine urgency
            urgent_keywords = ["breaking", "urgent", "immediate", "emergency", "crisis"]
            is_urgent = any(keyword in title.lower() for keyword in urgent_keywords)
            
            # Determine style
            if is_urgent or high_impact:
                style = "breaking"
            elif verification_status == "verified" and high_impact:
                style = "mystery"
            elif "update" in title.lower() or "new" in title.lower():
                style = "community"
            else:
                style = "urgent"
            
            return {
                "style": style,
                "impact_level": "high" if high_impact else "medium",
                "urgency": "high" if is_urgent else "medium",
                "category": category,
                "verification_status": verification_status
            }
        except Exception as e:
            logger.error(f"❌ Error analyzing content: {e}")
            return {"style": "community", "impact_level": "medium", "urgency": "medium"}
    
    def generate_creative_notification(self, post_data: Dict, style: str = None) -> Dict:
        """Generate creative notification using AI"""
        try:
            # Analyze content if style not provided
            if not style:
                analysis = self.analyze_content(post_data)
                style = analysis["style"]
            
            # Get style configuration
            style_config = self.styles.get(style, self.styles["community"])
            
            if self.gemini_available:
                # Use AI to generate creative content
                return self._generate_with_ai(post_data, style, style_config)
            else:
                # Use template-based fallback
                return self._generate_with_template(post_data, style, style_config)
                
        except Exception as e:
            logger.error(f"❌ Error generating notification: {e}")
            return self._generate_fallback_notification(post_data)
    
    def _generate_with_ai(self, post_data: Dict, style: str, style_config: Dict) -> Dict:
        """Generate notification using Gemini AI"""
        try:
            title = post_data.get("title", "")
            content = post_data.get("content", "")
            category = post_data.get("category", "")
            
            # Create AI prompt
            prompt = f"""
            Create an engaging notification for LexLeaks, a legal news platform that exposes legal industry secrets.
            
            Post Title: {title}
            Post Category: {category}
            Style: {style_config['name']}
            Tone: {style_config['tone']}
            
            Requirements:
            1. Use emojis from this set: {style_config['emoji_set']}
            2. Make it engaging and attention-grabbing (like Blinkit or Zomato)
            3. Keep it under 100 characters for mobile
            4. Include a call-to-action
            5. Make it feel urgent and exciting
            6. Use legal industry terminology appropriately
            7. Don't reveal too much - create curiosity
            
            Generate a creative notification that will make users want to click and read more.
            """
            
            response = self.model.generate_content(prompt)
            ai_content = response.text.strip()
            
            return {
                "content": ai_content,
                "style": style,
                "emoji_set": style_config["emoji_set"],
                "tone": style_config["tone"],
                "generated_by": "ai",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            return self._generate_with_template(post_data, style, style_config)
    
    def _generate_with_template(self, post_data: Dict, style: str, style_config: Dict) -> Dict:
        """Generate notification using template"""
        try:
            title = post_data.get("title", "")
            content = post_data.get("content", "")
            category = post_data.get("category", "")
            
            # Extract company/entity name from title
            company = self._extract_company_name(title)
            
            # Generate teaser from content
            teaser = self._generate_teaser(content)
            
            # Use template
            template = style_config["template"]
            notification_content = template.format(
                title=title[:50] + "..." if len(title) > 50 else title,
                content=teaser,
                company=company,
                teaser=teaser
            )
            
            return {
                "content": notification_content,
                "style": style,
                "emoji_set": style_config["emoji_set"],
                "tone": style_config["tone"],
                "generated_by": "template",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Template generation failed: {e}")
            return self._generate_fallback_notification(post_data)
    
    def _extract_company_name(self, title: str) -> str:
        """Extract company/entity name from title"""
        # Simple extraction - look for capitalized words
        words = title.split()
        for word in words:
            if word.istitle() and len(word) > 2:
                return word
        return "the company"
    
    def _generate_teaser(self, content: str) -> str:
        """Generate a teaser from content"""
        # Take first sentence or first 100 characters
        sentences = content.split('.')
        if sentences:
            teaser = sentences[0].strip()
            if len(teaser) > 100:
                teaser = teaser[:97] + "..."
            return teaser
        return content[:100] + "..." if len(content) > 100 else content
    
    def _generate_fallback_notification(self, post_data: Dict) -> Dict:
        """Generate basic fallback notification"""
        title = post_data.get("title", "New Legal Leak")
        return {
            "content": f"🚨 New leak: {title[:50]}...\nRead more →",
            "style": "breaking",
            "emoji_set": ["🚨", "📰"],
            "tone": "urgent",
            "generated_by": "fallback",
            "created_at": datetime.now().isoformat()
        }
    
    def generate_ab_test_variants(self, post_data: Dict) -> Tuple[Dict, Dict]:
        """Generate two variants for A/B testing"""
        try:
            # Generate primary notification
            variant_a = self.generate_creative_notification(post_data)
            
            # Generate alternative style
            analysis = self.analyze_content(post_data)
            alternative_styles = [s for s in self.styles.keys() if s != variant_a["style"]]
            alternative_style = alternative_styles[0] if alternative_styles else "community"
            
            variant_b = self.generate_creative_notification(post_data, alternative_style)
            
            return variant_a, variant_b
            
        except Exception as e:
            logger.error(f"❌ Error generating A/B test variants: {e}")
            # Return two fallback variants
            fallback_a = self._generate_fallback_notification(post_data)
            fallback_b = {
                "content": f"📰 Legal Update: {post_data.get('title', 'New Information')[:50]}...\nView details →",
                "style": "community",
                "emoji_set": ["📰", "👥"],
                "tone": "friendly",
                "generated_by": "fallback",
                "created_at": datetime.now().isoformat()
            }
            return fallback_a, fallback_b
    
    def get_available_styles(self) -> List[Dict]:
        """Get list of available notification styles"""
        return [
            {
                "key": key,
                "name": config["name"],
                "emoji_set": config["emoji_set"],
                "tone": config["tone"]
            }
            for key, config in self.styles.items()
        ]

# Global instance
notification_ai_agent = NotificationAIAgent()
