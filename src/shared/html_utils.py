"""
HTML utilities for presentation generation
"""

import re
from pathlib import Path
from datetime import datetime

class HTMLUtils:
    """Utility functions for HTML manipulation and processing"""
    
    @staticmethod
    def clean_html_content(html_content: str) -> str:
        """Clean up HTML content if wrapped in code blocks"""
        if not html_content:
            return ""
        
        content = html_content.strip()
        
        # Remove markdown code block markers
        if content.startswith("```html"):
            content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
        elif content.startswith("```"):
            content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
        
        return content.strip()
    
    @staticmethod
    def validate_html_structure(html_content: str) -> tuple[bool, str]:
        """Validate basic HTML structure"""
        if not html_content:
            return False, "Empty HTML content"
        
        html_content = html_content.strip()
        
        # Check for DOCTYPE
        if not html_content.startswith('<!DOCTYPE html>'):
            return False, "Missing DOCTYPE declaration"
        
        # Check for basic HTML tags
        required_tags = ['<html', '</html>', '<head', '</head>', '<body', '</body>']
        for tag in required_tags:
            if tag not in html_content:
                return False, f"Missing required tag: {tag}"
        
        return True, "Valid HTML structure"
    
    @staticmethod
    def extract_slide_count(html_content: str) -> int:
        """Extract approximate slide count from HTML content"""
        if not html_content:
            return 0
        
        # Try different slide patterns
        patterns = [
            r'<div[^>]*class="slide"',
            r'<section[^>]*class="slide"',
            r'<div[^>]*class="[^"]*slide[^"]*"',
            r'<section[^>]*class="[^"]*slide[^"]*"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                return len(matches)
        
        return 0
    
    @staticmethod
    def add_meta_tags(html_content: str, title: str = "Presentation", 
                     description: str = "Generated presentation") -> str:
        """Add meta tags to HTML content"""
        meta_tags = f'''
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="generator" content="Presentation Toolkit">
    <meta name="created" content="{datetime.now().isoformat()}">
    <title>{title}</title>'''
        
        # Insert after <head> tag
        head_pattern = r'(<head[^>]*>)'
        replacement = r'\1' + meta_tags
        
        return re.sub(head_pattern, replacement, html_content, count=1)
    
    @staticmethod
    def minify_html(html_content: str) -> str:
        """Basic HTML minification"""
        if not html_content:
            return ""
        
        # Remove extra whitespace between tags
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Remove extra newlines
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        # Remove leading/trailing whitespace on lines
        lines = [line.strip() for line in html_content.split('\n')]
        
        return '\n'.join(line for line in lines if line)
    
    @staticmethod
    def inject_analytics(html_content: str, analytics_code: str) -> str:
        """Inject analytics code before closing body tag"""
        if not analytics_code:
            return html_content
        
        pattern = r'(</body>)'
        replacement = f'{analytics_code}\n\\1'
        
        return re.sub(pattern, replacement, html_content, count=1)
    
    @staticmethod
    def extract_title(html_content: str) -> str:
        """Extract title from HTML content"""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # Try to find h1 tag as fallback
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()
        
        return "Presentation"