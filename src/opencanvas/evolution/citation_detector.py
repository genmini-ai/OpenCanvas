"""
Citation authenticity detector for identifying fake citations and fabricated names
"""

import re
import logging
from typing import List, Dict, Any, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class CitationAuthenticityDetector:
    """Detects potentially fake citations and fabricated author names"""
    
    def __init__(self):
        """Initialize with common patterns of AI-generated fake names and citations"""
        
        # Common AI-generated name patterns
        self.suspicious_name_patterns = [
            # Common AI-generated first names
            r'\b(Dr\.\s+)?(?:James|John|Michael|David|Robert|William|Richard|Charles|Joseph|Thomas|Christopher|Daniel|Paul|Mark|Donald|Steven|Andrew|Kenneth|Joshua|Kevin|Brian|George|Timothy|Ronald|Jason|Edward|Jeffrey|Ryan|Jacob|Gary|Nicholas|Eric|Jonathan|Stephen|Larry|Justin|Scott|Brandon|Benjamin|Samuel|Gregory|Alexander|Patrick|Jack|Dennis|Jerry|Tyler|Aaron|Jose|Henry|Adam|Douglas|Nathan|Peter|Kyle|Noah|Jeremy|William|Alan|Sean|Albert|Carl|Frank|Arthur|Louis|Philip|Evan|Wayne|Harold|Ralph|Roger|Eugene|Antonio|Jesse|Austin|Todd|Clinton|Manuel|Mario|Francis|Sidney|Roy|Lewis|Glenn|Jay|Edgar|Clarence|Sean)\s+(Smith|Johnson|Williams|Brown|Jones|Garcia|Miller|Davis|Rodriguez|Martinez|Hernandez|Lopez|Gonzalez|Wilson|Anderson|Thomas|Taylor|Moore|Jackson|Martin|Lee|Perez|Thompson|White|Harris|Sanchez|Clark|Ramirez|Lewis|Robinson|Walker|Young|Allen|King|Wright|Scott|Torres|Nguyen|Hill|Flores|Green|Adams|Nelson|Baker|Hall|Rivera|Campbell|Mitchell|Carter|Roberts|Gomez|Phillips|Evans|Turner|Diaz|Parker|Cruz|Edwards|Collins|Reyes|Stewart|Morris|Morales|Murphy|Cook|Rogers|Gutierrez|Ortiz|Morgan|Cooper|Peterson|Bailey|Reed|Kelly|Howard|Ramos|Kim|Cox|Ward|Richardson|Watson|Brooks|Chavez|Wood|James|Bennett|Gray|Mendoza|Ruiz|Hughes|Price|Alvarez|Castillo|Sanders|Patel|Myers|Long|Ross|Foster|Jimenez)\b',
            
            # Generic academic combinations
            r'\b(?:Dr\.\s+)?(?:Sarah|Lisa|Karen|Nancy|Betty|Helen|Sandra|Donna|Carol|Ruth|Sharon|Michelle|Laura|Sarah|Kimberly|Deborah|Dorothy|Lisa|Nancy|Karen|Betty|Helen|Sandra|Donna|Carol|Ruth|Sharon|Michelle|Laura|Sarah|Emily|Ashley|Jessica|Amanda|Stephanie|Jennifer|Elizabeth|Heather|Nicole|Amy|Angela|Brenda|Emma|Olivia|Cynthia|Marie|Janet|Frances|Christine|Samantha|Debra|Rachel|Carolyn|Janet|Maria|Heather|Diane|Julie|Joyce|Victoria|Kelly|Christina|Joan|Evelyn|Lauren|Judith|Megan|Andrea|Cheryl|Hannah|Jacqueline|Martha|Gloria|Teresa|Sara|Janice|Marie|Julia|Grace|Judy|Theresa|Madison|Beverly|Denise|Charlotte|Diana|Kayla|Alexis|Lori|Rose)\s+(Smith|Johnson|Williams|Brown|Jones|Garcia|Miller|Davis|Rodriguez|Martinez|Hernandez|Lopez|Gonzalez|Wilson|Anderson|Thomas|Taylor|Moore|Jackson|Martin|Lee|Perez|Thompson|White|Harris|Sanchez|Clark|Ramirez|Lewis|Robinson|Walker|Young|Allen|King|Wright|Scott|Torres|Nguyen|Hill|Flores|Green|Adams|Nelson|Baker|Hall|Rivera|Campbell|Mitchell|Carter|Roberts|Gomez|Phillips|Evans|Turner|Diaz|Parker|Cruz|Edwards|Collins|Reyes|Stewart|Morris|Morales|Murphy|Cook|Rogers|Gutierrez|Ortiz|Morgan|Cooper|Peterson|Bailey|Reed|Kelly|Howard|Ramos|Kim|Cox|Ward|Richardson|Watson|Brooks|Chavez|Wood|James|Bennett|Gray|Mendoza|Ruiz|Hughes|Price|Alvarez|Castillo|Sanders|Patel|Myers|Long|Ross|Foster|Jimenez)\b'
        ]
        
        # Suspicious citation patterns
        self.suspicious_citation_patterns = [
            # Generic academic journal names that don't exist
            r'\bJournal of (?:Advanced|Modern|Contemporary|Current|International|Global|Applied|Theoretical|Innovative|Future|Next-Generation|Emerging|Progressive|Strategic|Sustainable|Digital|Smart|Intelligent)\s+(?:Research|Studies|Science|Technology|Innovation|Development|Management|Analytics|Solutions|Systems|Applications|Methodologies)\b',
            
            # Too-perfect years (very recent or future)
            r'\b(?:2024|2025|2026)\b',
            
            # Generic conference names
            r'\b(?:International Conference on|Global Summit on|World Conference on|Annual Meeting of|Proceedings of the)\s+(?:Advanced|Modern|Contemporary|Current|International|Global|Applied|Theoretical|Innovative|Future|Next-Generation|Emerging|Progressive|Strategic|Sustainable|Digital|Smart|Intelligent)\s+(?:Research|Studies|Science|Technology|Innovation|Development|Management|Analytics|Solutions|Systems|Applications|Methodologies)\b',
            
            # Suspiciously round numbers or perfect percentages
            r'\b(?:99\.9|95\.0|90\.0|85\.0|80\.0|75\.0)%\b',
            r'\b(?:1000|5000|10000|50000|100000|500000|1000000)\b'
        ]
        
        # Known real institutions (partial list - could be expanded)
        self.real_institutions = {
            'MIT', 'Stanford', 'Harvard', 'Yale', 'Princeton', 'Caltech', 'Berkeley', 'UCLA',
            'Oxford', 'Cambridge', 'Imperial College', 'ETH Zurich', 'Max Planck', 'CERN',
            'Google', 'Microsoft', 'IBM', 'Apple', 'Amazon', 'Meta', 'Tesla', 'OpenAI',
            'Nature', 'Science', 'Cell', 'PNAS', 'The Lancet', 'NEJM', 'IEEE', 'ACM',
            'WHO', 'FDA', 'NIH', 'NSF', 'NASA', 'NOAA', 'UN', 'World Bank', 'IMF'
        }
    
    def analyze_presentation_citations(self, html_content: str) -> Dict[str, Any]:
        """
        Analyze presentation HTML for suspicious citations and fake names
        
        Args:
            html_content: HTML content of the presentation
            
        Returns:
            Dictionary with citation analysis results
        """
        
        results = {
            "suspicious_names": [],
            "suspicious_citations": [],
            "fake_statistics": [],
            "plausibility_issues": [],
            "authenticity_score": 5.0,  # Start with perfect score, deduct for issues
            "total_citations": 0,
            "total_names": 0,
            "recommendations": []
        }
        
        # Extract text content from HTML
        text_content = self._extract_text_from_html(html_content)
        
        # Find all potential author names
        author_names = self._extract_author_names(text_content)
        results["total_names"] = len(author_names)
        
        # Check for suspicious name patterns
        for name in author_names:
            for pattern in self.suspicious_name_patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    results["suspicious_names"].append(name)
                    results["authenticity_score"] -= 0.5
        
        # Find all potential citations
        citations = self._extract_citations(text_content)
        results["total_citations"] = len(citations)
        
        # Check for suspicious citation patterns
        for citation in citations:
            for pattern in self.suspicious_citation_patterns:
                if re.search(pattern, citation, re.IGNORECASE):
                    results["suspicious_citations"].append(citation)
                    results["authenticity_score"] -= 0.3
        
        # Check for fake statistics
        fake_stats = self._detect_fake_statistics(text_content)
        results["fake_statistics"] = fake_stats
        results["authenticity_score"] -= len(fake_stats) * 0.2
        
        # Check for plausibility issues
        plausibility_issues = self._check_plausibility(text_content)
        results["plausibility_issues"] = plausibility_issues
        results["authenticity_score"] -= len(plausibility_issues) * 0.1
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        
        # Ensure score doesn't go below 1.0
        results["authenticity_score"] = max(1.0, results["authenticity_score"])
        
        return results
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text content from HTML"""
        # Simple HTML tag removal (could use BeautifulSoup for better parsing)
        import re
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_author_names(self, text: str) -> List[str]:
        """Extract potential author names from text"""
        # Look for patterns like "Dr. FirstName LastName" or "FirstName LastName (Year)"
        name_patterns = [
            r'\b(?:Dr\.\s+|Prof\.\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s*\([0-9]{4}\))?',
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:found|showed|demonstrated|reported|concluded|argued|stated)',
            r'(?:According to|Research by|Study by|Work of)\s+(?:Dr\.\s+|Prof\.\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        names = []
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            names.extend(matches)
        
        # Remove duplicates
        return list(set(names))
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract potential citations from text"""
        citation_patterns = [
            r'\b[A-Z][a-z]+\s+et\s+al\.\s*\([0-9]{4}\)',
            r'\b[A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s*\([0-9]{4}\)',
            r'\b[A-Z][a-z]+\s*\([0-9]{4}\)',
            r'Journal of [A-Za-z\s]+\s*\([0-9]{4}\)',
            r'Proceedings of [A-Za-z\s]+\s*\([0-9]{4}\)',
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        
        return list(set(citations))
    
    def _detect_fake_statistics(self, text: str) -> List[str]:
        """Detect potentially fabricated statistics"""
        fake_stats = []
        
        # Look for suspiciously perfect numbers
        perfect_numbers = re.findall(r'\b(?:99\.9|95\.0|90\.0|85\.0|80\.0|75\.0)%', text)
        for num in perfect_numbers:
            fake_stats.append(f"Suspiciously perfect percentage: {num}")
        
        # Look for round numbers that seem fabricated
        round_numbers = re.findall(r'\b(?:exactly|precisely)\s+(?:1000|5000|10000|50000|100000|500000|1000000)\b', text, re.IGNORECASE)
        for num in round_numbers:
            fake_stats.append(f"Suspiciously round number: {num}")
        
        return fake_stats
    
    def _check_plausibility(self, text: str) -> List[str]:
        """Check for implausible claims"""
        issues = []
        
        # Check for impossible percentages
        if re.search(r'\b(?:10[0-9]|1[1-9][0-9]|[2-9][0-9][0-9])%', text):
            issues.append("Percentage over 100% found")
        
        # Check for future dates beyond reasonable projection
        current_year = 2025  # Update as needed
        future_years = re.findall(r'\b(20[3-9][0-9])\b', text)
        for year in future_years:
            if int(year) > current_year + 5:
                issues.append(f"Implausible future year: {year}")
        
        # Check for contradictory claims in same text
        if 'increased' in text.lower() and 'decreased' in text.lower():
            # This would need more sophisticated analysis
            pass
        
        return issues
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if results["suspicious_names"]:
            recommendations.append(f"Replace {len(results['suspicious_names'])} suspicious author names with generic attributions like 'Recent research shows...'")
        
        if results["suspicious_citations"]:
            recommendations.append(f"Replace {len(results['suspicious_citations'])} suspicious citations with verified sources or generic references")
        
        if results["fake_statistics"]:
            recommendations.append("Verify or replace suspiciously perfect statistical claims with more realistic ranges")
        
        if results["plausibility_issues"]:
            recommendations.append("Review and correct implausible claims or impossible values")
        
        if results["authenticity_score"] < 3.0:
            recommendations.append("CRITICAL: This presentation contains multiple authenticity issues that significantly harm credibility")
        elif results["authenticity_score"] < 4.0:
            recommendations.append("WARNING: This presentation contains several authenticity concerns that should be addressed")
        
        return recommendations
    
    def generate_citation_evaluation_prompt(self) -> str:
        """Generate enhanced evaluation prompt that includes citation authenticity checking"""
        return """
ENHANCED CITATION AUTHENTICITY EVALUATION

In addition to the standard accuracy evaluation, assess the presentation for citation authenticity:

## Citation Authenticity Criteria:

### Fabricated Names (CRITICAL ISSUE):
- Check for AI-generated fake author names (e.g., "Dr. James Mitchell", "Sarah Johnson", etc.)
- Look for suspiciously generic academic names combined with common surnames
- Flag any specific author attributions that seem fabricated
- DEDUCT HEAVILY for fake author names - this is a critical credibility issue

### Citation Plausibility:
- Verify that cited years are reasonable (not future dates beyond 2025)
- Check that journal names sound legitimate (not generic AI-generated titles)
- Look for suspiciously perfect statistics (99.9%, exactly 10,000, etc.)
- Flag round numbers that seem fabricated rather than measured

### Attribution Standards:
- Prefer generic attributions ("Recent research shows...") over specific fake names
- Accept organizational sources (WHO, MIT, etc.) over individual authors
- Flag any citations that seem too convenient or perfectly aligned with the narrative

## Authenticity Scoring Impact:
- ANY fabricated author names should result in accuracy score ≤ 2.0
- Multiple fake citations should result in accuracy score ≤ 1.0
- Perfect scores (5.0) require either verified real sources OR proper generic attribution

## Examples:
❌ FABRICATED: "Dr. James Mitchell (2024) found that 95.0% of implementations succeeded"
✅ ACCEPTABLE: "Recent studies indicate high success rates in implementations"
❌ FABRICATED: "According to Sarah Johnson et al. (2023), exactly 50,000 cases were analyzed"
✅ ACCEPTABLE: "Industry analysis shows significant case study data supports this approach"

Include this authenticity assessment in your accuracy reasoning and scoring.
"""