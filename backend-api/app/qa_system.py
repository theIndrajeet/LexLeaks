import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from .deep_research_models import Source, Extract, Claim, Section, QAMetrics, SourceKind

class QASystem:
    """Quality Assurance system for legal research reports"""
    
    def __init__(self):
        self.min_citation_density = 1.0  # 1 citation per 100 words
        self.max_stale_ratio = 0.2  # Max 20% stale citations
        self.min_primary_ratio = 0.6  # Min 60% primary sources
        self.max_contradiction_ratio = 0.1  # Max 10% contradictions
    
    def analyze_report_quality(self, sections: List[Section], sources: List[Source], extracts: List[Extract]) -> QAMetrics:
        """Analyze the overall quality of the research report"""
        
        # Calculate basic metrics
        total_words = sum(section.word_count for section in sections)
        total_citations = sum(section.citation_count for section in sections)
        
        # Citation density
        pin_density = (total_citations / total_words * 100) if total_words > 0 else 0
        
        # Primary source ratio
        primary_sources = [s for s in sources if s.kind in [SourceKind.STATUTE, SourceKind.CASE]]
        primary_source_ratio = len(primary_sources) / len(sources) if sources else 0
        
        # Stale citation ratio
        stale_sources = self._identify_stale_sources(sources)
        stale_citation_ratio = len(stale_sources) / len(sources) if sources else 0
        
        # Contradiction analysis
        contradictions = self._identify_contradictions(extracts)
        contradiction_count = len(contradictions)
        
        # Coverage analysis
        uncovered_sections = self._identify_uncovered_sections(sections)
        
        # Overall quality score
        coverage_score = self._calculate_coverage_score(sections, sources)
        trust_score = self._calculate_trust_score(sources)
        
        return QAMetrics(
            pin_density=pin_density,
            primary_source_ratio=primary_source_ratio,
            stale_citation_ratio=stale_citation_ratio,
            contradiction_count=contradiction_count,
            uncovered_sections=uncovered_sections,
            coverage_score=coverage_score,
            trust_score=trust_score
        )
    
    def validate_section_quality(self, section: Section, sources: List[Source], extracts: List[Extract]) -> Dict[str, Any]:
        """Validate the quality of a specific section"""
        
        issues = []
        recommendations = []
        
        # Check citation density
        if section.word_count > 0:
            citation_density = (section.citation_count / section.word_count * 100)
            if citation_density < self.min_citation_density:
                issues.append({
                    "type": "low_citation_density",
                    "severity": "high",
                    "description": f"Citation density is {citation_density:.1f}%, below minimum of {self.min_citation_density}%",
                    "section_id": section.id
                })
                recommendations.append("Add more citations to support claims")
        
        # Check source quality
        section_sources = self._get_section_sources(section, sources)
        if section_sources:
            primary_ratio = len([s for s in section_sources if s.kind in [SourceKind.STATUTE, SourceKind.CASE]]) / len(section_sources)
            if primary_ratio < self.min_primary_ratio:
                issues.append({
                    "type": "low_primary_sources",
                    "severity": "medium",
                    "description": f"Primary source ratio is {primary_ratio:.1%}, below minimum of {self.min_primary_ratio:.1%}",
                    "section_id": section.id
                })
                recommendations.append("Include more primary sources (statutes, cases)")
        
        # Check for stale sources
        stale_sources = self._identify_stale_sources(section_sources)
        if stale_sources:
            issues.append({
                "type": "stale_sources",
                "severity": "medium",
                "description": f"Found {len(stale_sources)} stale sources",
                "section_id": section.id
            })
            recommendations.append("Update or replace stale sources")
        
        # Check for contradictions
        section_extracts = self._get_section_extracts(section, extracts)
        contradictions = self._identify_contradictions(section_extracts)
        if contradictions:
            issues.append({
                "type": "contradictions",
                "severity": "high",
                "description": f"Found {len(contradictions)} contradictions",
                "section_id": section.id
            })
            recommendations.append("Resolve contradictions or acknowledge conflicting views")
        
        return {
            "section_id": section.id,
            "issues": issues,
            "recommendations": recommendations,
            "quality_score": self._calculate_section_quality_score(issues)
        }
    
    def validate_citation_format(self, text: str) -> Dict[str, Any]:
        """Validate citation format in text"""
        
        issues = []
        
        # Check for inline citations
        inline_citations = re.findall(r'\[(\d+)\]', text)
        if not inline_citations:
            issues.append({
                "type": "no_inline_citations",
                "severity": "high",
                "description": "No inline citations found"
            })
        
        # Check for citation list
        citation_list = re.findall(r'\[(\d+)\]:\s*(.+)', text)
        if not citation_list:
            issues.append({
                "type": "no_citation_list",
                "severity": "high",
                "description": "No citation list found"
            })
        
        # Check for proper Bluebook format
        bluebook_issues = self._check_bluebook_format(text)
        issues.extend(bluebook_issues)
        
        return {
            "issues": issues,
            "citation_count": len(inline_citations),
            "citation_list_count": len(citation_list)
        }
    
    def _identify_stale_sources(self, sources: List[Source]) -> List[Source]:
        """Identify sources that may be stale"""
        
        stale_sources = []
        cutoff_date = datetime.now() - timedelta(days=18*30)  # 18 months
        
        for source in sources:
            if source.date and source.date < cutoff_date:
                # Check if it's a source that could have changed
                if source.kind in [SourceKind.NEWS, SourceKind.GUIDANCE, SourceKind.ORDER]:
                    stale_sources.append(source)
        
        return stale_sources
    
    def _identify_contradictions(self, extracts: List[Extract]) -> List[Dict[str, str]]:
        """Identify contradictory extracts"""
        
        contradictions = []
        
        # Simple contradiction detection based on keywords
        contradiction_keywords = [
            ("prohibited", "allowed"),
            ("required", "optional"),
            ("mandatory", "discretionary"),
            ("valid", "invalid"),
            ("legal", "illegal")
        ]
        
        for i, extract1 in enumerate(extracts):
            for j, extract2 in enumerate(extracts[i+1:], i+1):
                for positive, negative in contradiction_keywords:
                    if (positive in extract1.fact.lower() and negative in extract2.fact.lower()) or \
                       (negative in extract1.fact.lower() and positive in extract2.fact.lower()):
                        contradictions.append({
                            "extract1_id": extract1.id,
                            "extract2_id": extract2.id,
                            "type": f"{positive}/{negative} contradiction"
                        })
        
        return contradictions
    
    def _identify_uncovered_sections(self, sections: List[Section]) -> List[str]:
        """Identify sections with insufficient coverage"""
        
        uncovered = []
        
        for section in sections:
            if section.citation_count < 3:  # Minimum 3 citations per section
                uncovered.append(section.id)
            elif section.word_count < 500:  # Minimum 500 words per section
                uncovered.append(section.id)
        
        return uncovered
    
    def _calculate_coverage_score(self, sections: List[Section], sources: List[Source]) -> float:
        """Calculate coverage score based on sections and sources"""
        
        if not sections:
            return 0.0
        
        # Check if each section has adequate coverage
        covered_sections = 0
        for section in sections:
            if section.citation_count >= 3 and section.word_count >= 500:
                covered_sections += 1
        
        return covered_sections / len(sections)
    
    def _calculate_trust_score(self, sources: List[Source]) -> float:
        """Calculate overall trust score based on source quality"""
        
        if not sources:
            return 0.0
        
        total_trust = sum(source.trust_score for source in sources)
        return total_trust / len(sources)
    
    def _get_section_sources(self, section: Section, sources: List[Source]) -> List[Source]:
        """Get sources relevant to a specific section"""
        
        # This would be more sophisticated in a real implementation
        # For now, return all sources
        return sources
    
    def _get_section_extracts(self, section: Section, extracts: List[Extract]) -> List[Extract]:
        """Get extracts relevant to a specific section"""
        
        # This would be more sophisticated in a real implementation
        # For now, return all extracts
        return extracts
    
    def _calculate_section_quality_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate quality score for a section based on issues"""
        
        if not issues:
            return 1.0
        
        # Weight issues by severity
        severity_weights = {"high": 0.5, "medium": 0.3, "low": 0.1}
        total_weight = sum(severity_weights.get(issue["severity"], 0.1) for issue in issues)
        
        return max(0.0, 1.0 - total_weight)
    
    def _check_bluebook_format(self, text: str) -> List[Dict[str, Any]]:
        """Check for proper Bluebook citation format"""
        
        issues = []
        
        # Check for case citations
        case_pattern = r'\b\d+\s+\w+\s+\d+\s*\(\d{4}\)'
        if not re.search(case_pattern, text):
            issues.append({
                "type": "no_case_citations",
                "severity": "medium",
                "description": "No properly formatted case citations found"
            })
        
        # Check for statute citations
        statute_pattern = r'\b\w+\s+Act,\s*\d{4}'
        if not re.search(statute_pattern, text):
            issues.append({
                "type": "no_statute_citations",
                "severity": "medium",
                "description": "No properly formatted statute citations found"
            })
        
        return issues
    
    def generate_quality_report(self, sections: List[Section], sources: List[Source], extracts: List[Extract]) -> Dict[str, Any]:
        """Generate a comprehensive quality report"""
        
        # Overall metrics
        overall_metrics = self.analyze_report_quality(sections, sources, extracts)
        
        # Section-by-section analysis
        section_analyses = []
        for section in sections:
            section_analysis = self.validate_section_quality(section, sources, extracts)
            section_analyses.append(section_analysis)
        
        # Citation format validation
        citation_issues = []
        for section in sections:
            citation_validation = self.validate_citation_format(section.draft_md)
            if citation_validation["issues"]:
                citation_issues.extend(citation_validation["issues"])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_metrics, section_analyses, citation_issues)
        
        return {
            "overall_metrics": overall_metrics.dict(),
            "section_analyses": section_analyses,
            "citation_issues": citation_issues,
            "recommendations": recommendations,
            "quality_grade": self._calculate_quality_grade(overall_metrics),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_recommendations(self, metrics: QAMetrics, section_analyses: List[Dict[str, Any]], citation_issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on quality analysis"""
        
        recommendations = []
        
        # Citation density recommendations
        if metrics.pin_density < self.min_citation_density:
            recommendations.append(f"Increase citation density from {metrics.pin_density:.1f}% to at least {self.min_citation_density}%")
        
        # Primary source recommendations
        if metrics.primary_source_ratio < self.min_primary_ratio:
            recommendations.append(f"Increase primary source ratio from {metrics.primary_source_ratio:.1%} to at least {self.min_primary_ratio:.1%}")
        
        # Stale source recommendations
        if metrics.stale_citation_ratio > self.max_stale_ratio:
            recommendations.append(f"Reduce stale citation ratio from {metrics.stale_citation_ratio:.1%} to at most {self.max_stale_ratio:.1%}")
        
        # Contradiction recommendations
        if metrics.contradiction_count > 0:
            recommendations.append(f"Resolve {metrics.contradiction_count} contradictions or acknowledge conflicting views")
        
        # Coverage recommendations
        if metrics.coverage_score < 0.8:
            recommendations.append("Improve coverage of sections with insufficient citations or content")
        
        # Section-specific recommendations
        for analysis in section_analyses:
            if analysis["quality_score"] < 0.7:
                recommendations.extend(analysis["recommendations"])
        
        # Citation format recommendations
        if citation_issues:
            recommendations.append("Fix citation format issues to comply with Bluebook standards")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_quality_grade(self, metrics: QAMetrics) -> str:
        """Calculate overall quality grade"""
        
        # Weight different metrics
        weights = {
            "pin_density": 0.25,
            "primary_source_ratio": 0.25,
            "stale_citation_ratio": 0.20,
            "coverage_score": 0.20,
            "trust_score": 0.10
        }
        
        # Calculate weighted score
        score = (
            min(metrics.pin_density / self.min_citation_density, 1.0) * weights["pin_density"] +
            min(metrics.primary_source_ratio / self.min_primary_ratio, 1.0) * weights["primary_source_ratio"] +
            max(0, 1.0 - metrics.stale_citation_ratio / self.max_stale_ratio) * weights["stale_citation_ratio"] +
            metrics.coverage_score * weights["coverage_score"] +
            metrics.trust_score * weights["trust_score"]
        )
        
        # Convert to letter grade
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
