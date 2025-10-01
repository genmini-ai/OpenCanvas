#!/usr/bin/env python3
"""
Layout Fixer for AI-Generated HTML Presentations
Implements post-processing strategies to fix overflow, overlap, and sizing issues.
Based on research from Claude, Gemini, and GPT reports.
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class LayoutAnalyzer:
    """Analyzes HTML slides for potential layout issues."""

    def __init__(self, slide_width: int = 1280, slide_height: int = 720):
        self.slide_width = slide_width
        self.slide_height = slide_height
        self.issues = []

    def analyze_html(self, soup: BeautifulSoup) -> Dict:
        """Analyze the entire HTML document for layout issues."""
        results = {
            'total_slides': 0,
            'issues_by_slide': {},
            'global_issues': [],
            'statistics': {}
        }

        # Find all slides
        slides = soup.find_all('div', class_='slide')
        results['total_slides'] = len(slides)

        # Analyze each slide
        for i, slide in enumerate(slides, 1):
            slide_id = slide.get('id', f'slide-{i}')
            slide_issues = self.analyze_slide(slide, slide_id)
            if slide_issues:
                results['issues_by_slide'][slide_id] = slide_issues

        # Check global issues
        results['global_issues'] = self.check_global_issues(soup)

        # Calculate statistics
        results['statistics'] = self.calculate_statistics(results)

        return results

    def analyze_slide(self, slide, slide_id: str) -> List[Dict]:
        """Analyze a single slide for layout issues."""
        issues = []

        # Check for overflow risk based on content density
        overflow_risk = self.check_overflow_risk(slide)
        if overflow_risk['risk_level'] > 0.7:
            issues.append({
                'type': 'overflow_risk',
                'severity': 'high' if overflow_risk['risk_level'] > 0.85 else 'medium',
                'details': overflow_risk,
                'element': slide_id
            })

        # Check images
        images = slide.find_all('img')
        for img in images:
            img_issues = self.check_image_issues(img)
            if img_issues:
                issues.extend(img_issues)

        # Check text density
        text_density = self.calculate_text_density(slide)
        if text_density > 0.8:
            issues.append({
                'type': 'high_text_density',
                'severity': 'medium',
                'details': {'density': text_density},
                'element': slide_id
            })

        # Check for two-column layout issues
        two_column = slide.find('div', class_='two-column')
        if two_column:
            column_issues = self.check_column_layout(two_column)
            if column_issues:
                issues.extend(column_issues)

        # Check for long lists
        lists = slide.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            if len(items) > 6:
                issues.append({
                    'type': 'long_list',
                    'severity': 'low',
                    'details': {'item_count': len(items)},
                    'element': slide_id
                })

        # Check for math formula overflow
        math_elements = slide.find_all(class_='mathjax-enabled')
        if math_elements:
            issues.append({
                'type': 'math_formula_risk',
                'severity': 'low',
                'details': {'count': len(math_elements)},
                'element': slide_id
            })

        return issues

    def check_overflow_risk(self, slide) -> Dict:
        """Estimate overflow risk based on content volume."""
        # Count various elements
        text_length = len(slide.get_text(strip=True))
        num_images = len(slide.find_all('img'))
        num_cards = len(slide.find_all(class_='card'))
        num_features = len(slide.find_all(class_='feature-item'))

        # Calculate risk score (0-1)
        risk_score = 0

        # Text length risk
        if text_length > 1500:
            risk_score += 0.3
        elif text_length > 1000:
            risk_score += 0.2
        elif text_length > 500:
            risk_score += 0.1

        # Multiple images risk
        if num_images > 2:
            risk_score += 0.3
        elif num_images > 1:
            risk_score += 0.15

        # Multiple cards risk
        if num_cards > 2:
            risk_score += 0.2
        elif num_cards > 1:
            risk_score += 0.1

        # Features risk
        if num_features > 4:
            risk_score += 0.2
        elif num_features > 2:
            risk_score += 0.1

        return {
            'risk_level': min(risk_score, 1.0),
            'text_length': text_length,
            'num_images': num_images,
            'num_cards': num_cards,
            'num_features': num_features
        }

    def check_image_issues(self, img) -> List[Dict]:
        """Check for potential image-related issues."""
        issues = []

        # Check for missing max-width constraint
        style = img.get('style', '')
        if 'max-width' not in style and not img.parent.name == 'div':
            issues.append({
                'type': 'unconstrained_image',
                'severity': 'medium',
                'details': {'src': img.get('src', 'unknown')},
                'element': 'image'
            })

        return issues

    def calculate_text_density(self, element) -> float:
        """Calculate text density score (0-1)."""
        text = element.get_text(strip=True)
        # Rough estimate: assume average 80 chars per line, 20 lines per slide
        max_comfortable_chars = 1600
        density = min(len(text) / max_comfortable_chars, 1.0)
        return density

    def check_column_layout(self, two_column) -> List[Dict]:
        """Check for issues in two-column layouts."""
        issues = []
        columns = two_column.find_all(class_='column')

        if len(columns) == 2:
            # Check if columns have unbalanced content
            col1_text = len(columns[0].get_text(strip=True))
            col2_text = len(columns[1].get_text(strip=True))

            if abs(col1_text - col2_text) > 500:
                issues.append({
                    'type': 'unbalanced_columns',
                    'severity': 'low',
                    'details': {'col1_chars': col1_text, 'col2_chars': col2_text},
                    'element': 'two-column'
                })

        return issues

    def check_global_issues(self, soup) -> List[Dict]:
        """Check for document-wide issues."""
        issues = []

        # Check if defensive CSS is missing
        styles = soup.find_all('style')
        has_overflow_protection = False
        for style in styles:
            if style.string and 'overflow:' in style.string:
                has_overflow_protection = True
                break

        if not has_overflow_protection:
            issues.append({
                'type': 'missing_overflow_protection',
                'severity': 'high',
                'details': 'No overflow CSS rules found'
            })

        return issues

    def calculate_statistics(self, results: Dict) -> Dict:
        """Calculate statistics about issues found."""
        total_issues = sum(len(issues) for issues in results['issues_by_slide'].values())
        total_issues += len(results['global_issues'])

        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        type_counts = {}

        for slide_issues in results['issues_by_slide'].values():
            for issue in slide_issues:
                severity_counts[issue['severity']] += 1
                issue_type = issue['type']
                type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

        for issue in results['global_issues']:
            severity_counts[issue['severity']] += 1
            type_counts[issue['type']] = type_counts.get(issue['type'], 0) + 1

        return {
            'total_issues': total_issues,
            'affected_slides': len(results['issues_by_slide']),
            'severity_distribution': severity_counts,
            'issue_types': type_counts
        }


class LayoutFixer:
    """Applies fixes to resolve layout issues."""

    def __init__(self):
        self.fixes_applied = []
        self.defensive_css = self.generate_defensive_css()
        self.runtime_js = self.generate_runtime_js()

    def fix_html(self, soup: BeautifulSoup, issues: Dict) -> Tuple[BeautifulSoup, List[Dict]]:
        """Apply fixes based on detected issues."""
        fixes_log = []

        # Apply global fixes first
        logger.info("Applying global fixes...")
        self.inject_defensive_css(soup)
        fixes_log.append({'type': 'defensive_css', 'description': 'Injected defensive CSS rules'})

        self.inject_runtime_js(soup)
        fixes_log.append({'type': 'runtime_js', 'description': 'Added runtime JavaScript fixes'})

        # Fix issues by slide
        for slide_id, slide_issues in issues['issues_by_slide'].items():
            logger.info(f"Fixing issues in {slide_id}...")
            slide = soup.find('div', id=slide_id)
            if not slide:
                slide = soup.find('div', class_='slide')  # Fallback to first slide

            for issue in slide_issues:
                fix_result = self.apply_fix(soup, slide, issue)
                if fix_result:
                    fixes_log.append(fix_result)

        # Apply additional preventive measures
        self.apply_preventive_measures(soup)
        fixes_log.append({'type': 'preventive_measures', 'description': 'Applied additional preventive CSS'})

        return soup, fixes_log

    def apply_fix(self, soup: BeautifulSoup, slide, issue: Dict) -> Optional[Dict]:
        """Apply appropriate fix based on issue type."""
        issue_type = issue['type']

        if issue_type == 'overflow_risk':
            return self.fix_overflow_risk(slide, issue)
        elif issue_type == 'unconstrained_image':
            return self.fix_unconstrained_image(slide, issue)
        elif issue_type == 'high_text_density':
            return self.fix_text_density(slide, issue)
        elif issue_type == 'unbalanced_columns':
            return self.fix_unbalanced_columns(slide, issue)
        elif issue_type == 'long_list':
            return self.fix_long_list(slide, issue)
        elif issue_type == 'math_formula_risk':
            return self.fix_math_overflow(slide, issue)

        return None

    def fix_overflow_risk(self, slide, issue: Dict) -> Dict:
        """Fix potential overflow issues."""
        severity = issue['severity']

        # Add overflow protection
        slide['style'] = slide.get('style', '') + ' overflow: hidden;'

        # If high risk, add scrolling to content
        if severity == 'high':
            content = slide.find('div', class_='slide-content')
            if content:
                content['style'] = content.get('style', '') + ' overflow-y: auto; max-height: 650px;'

        # Reduce spacing for high-risk slides
        if issue['details']['risk_level'] > 0.85:
            slide['class'] = slide.get('class', []) + ['compact-spacing']

        return {
            'type': 'overflow_fix',
            'slide': slide.get('id'),
            'actions': ['Added overflow protection', 'Enabled scrolling' if severity == 'high' else 'Added compact spacing']
        }

    def fix_unconstrained_image(self, slide, issue: Dict) -> Dict:
        """Add constraints to images."""
        images = slide.find_all('img')
        for img in images:
            # Add inline style for max dimensions
            current_style = img.get('style', '')
            if 'max-width' not in current_style:
                img['style'] = current_style + ' max-width: 100%; height: auto;'

            # Wrap in container if not already
            if img.parent.name != 'div' or 'image-container' not in img.parent.get('class', []):
                wrapper = slide.new_tag('div', class_='image-wrapper')
                wrapper['style'] = 'max-width: 100%; overflow: hidden;'
                img.wrap(wrapper)

        return {
            'type': 'image_constraint_fix',
            'slide': slide.get('id'),
            'actions': ['Added max-width constraints', 'Wrapped in container']
        }

    def fix_text_density(self, slide, issue: Dict) -> Dict:
        """Fix high text density issues."""
        # Reduce font size slightly
        slide['class'] = slide.get('class', []) + ['reduced-font']

        # Adjust line height for better readability
        paragraphs = slide.find_all('p')
        for p in paragraphs:
            p['style'] = p.get('style', '') + ' line-height: 1.5;'

        return {
            'type': 'text_density_fix',
            'slide': slide.get('id'),
            'actions': ['Reduced font size', 'Adjusted line height']
        }

    def fix_unbalanced_columns(self, slide, issue: Dict) -> Dict:
        """Fix unbalanced column layouts."""
        two_column = slide.find('div', class_='two-column')
        if two_column:
            # Add flexbox properties to allow wrapping
            two_column['style'] = two_column.get('style', '') + ' flex-wrap: wrap;'

        return {
            'type': 'column_balance_fix',
            'slide': slide.get('id'),
            'actions': ['Added flex-wrap for responsive columns']
        }

    def fix_long_list(self, slide, issue: Dict) -> Dict:
        """Fix long list issues."""
        lists = slide.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            if len(items) > 6:
                # Add compact class
                lst['class'] = lst.get('class', []) + ['compact-list']
                # Reduce margin between items
                for li in items:
                    li['style'] = li.get('style', '') + ' margin-bottom: 0.5em;'

        return {
            'type': 'list_compaction_fix',
            'slide': slide.get('id'),
            'actions': ['Compacted list spacing']
        }

    def fix_math_overflow(self, slide, issue: Dict) -> Dict:
        """Fix potential math formula overflow."""
        math_elements = slide.find_all(class_='mathjax-enabled')
        for elem in math_elements:
            elem['style'] = elem.get('style', '') + ' overflow-x: auto; max-width: 100%;'

        return {
            'type': 'math_overflow_fix',
            'slide': slide.get('id'),
            'actions': ['Added horizontal scroll for math formulas']
        }

    def inject_defensive_css(self, soup: BeautifulSoup):
        """Inject defensive CSS rules."""
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            soup.insert(0, head)

        style_tag = soup.new_tag('style')
        style_tag.string = self.defensive_css

        # Add comment
        comment = Comment(' Defensive CSS injected by Layout Fixer ')
        head.append(comment)
        head.append(style_tag)

    def inject_runtime_js(self, soup: BeautifulSoup):
        """Inject runtime JavaScript for dynamic fixes."""
        body = soup.find('body')
        if not body:
            return

        script_tag = soup.new_tag('script')
        script_tag.string = self.runtime_js

        # Add comment
        comment = Comment(' Runtime JS fixes by Layout Fixer ')
        body.append(comment)
        body.append(script_tag)

    def apply_preventive_measures(self, soup: BeautifulSoup):
        """Apply additional preventive CSS classes."""
        # Add viewport meta tag if missing
        head = soup.find('head')
        if head and not head.find('meta', attrs={'name': 'viewport'}):
            viewport = soup.new_tag('meta')
            viewport.attrs['name'] = 'viewport'
            viewport.attrs['content'] = 'width=device-width, initial-scale=1.0'
            head.append(viewport)

        # Ensure all slides have proper classes
        slides = soup.find_all('div', class_='slide')
        for slide in slides:
            if 'layout-fixed' not in slide.get('class', []):
                slide['class'] = slide.get('class', []) + ['layout-fixed']

    def generate_defensive_css(self) -> str:
        """Generate defensive CSS rules."""
        return """
/* ========== DEFENSIVE CSS BY LAYOUT FIXER ========== */

/* Container Protection */
.slide.layout-fixed {
    width: 1280px !important;
    height: 720px !important;
    overflow: hidden !important;
    contain: layout paint;
    position: relative;
}

.slide-content {
    max-height: 650px !important;
    overflow-y: auto;
    overflow-x: hidden;
    scroll-behavior: smooth;
}

/* Image Constraints */
.image-container img,
.image-wrapper img,
.slide img {
    max-width: 100% !important;
    max-height: 500px !important;
    height: auto !important;
    object-fit: contain !important;
}

/* Text Overflow Protection */
.slide p,
.slide li,
.card-content,
.feature-description {
    overflow-wrap: break-word !important;
    word-break: break-word !important;
    hyphens: auto;
}

/* Responsive Font Sizing */
.slide.reduced-font {
    font-size: 0.95em !important;
}

.slide.reduced-font .slide-title {
    font-size: 2.2rem !important;
}

.slide.reduced-font .card-title {
    font-size: 1.3rem !important;
}

/* Compact Spacing */
.slide.compact-spacing {
    padding: 30px !important;
}

.slide.compact-spacing .slide-body {
    gap: 20px !important;
}

.slide.compact-spacing .card {
    padding: 20px !important;
}

/* List Compaction */
.compact-list {
    margin: 10px 0 !important;
    padding-left: 20px !important;
}

.compact-list li {
    margin-bottom: 0.5em !important;
    line-height: 1.4 !important;
}

/* Two Column Responsive */
.two-column {
    flex-wrap: wrap !important;
}

@media (max-aspect-ratio: 16/9) {
    .two-column {
        flex-direction: column !important;
    }

    .column {
        width: 100% !important;
        max-width: 100% !important;
    }
}

/* Math Formula Protection */
.mathjax-enabled {
    overflow-x: auto !important;
    max-width: 100% !important;
    padding: 10px !important;
}

/* Feature Grid Responsive */
.feature-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
}

/* Card Height Limits */
.card {
    max-height: calc(100% - 40px);
    overflow-y: auto;
}

/* Table Overflow */
.comparison-table {
    display: block;
    overflow-x: auto;
    max-width: 100%;
}

/* Code Block Constraints */
.code-block {
    max-height: 300px !important;
    overflow: auto !important;
}

/* Progressive Font Scaling */
.slide-title {
    font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
}

.card-title {
    font-size: clamp(1.2rem, 2.5vw, 1.5rem) !important;
}

.slide p,
.slide li {
    font-size: clamp(0.85rem, 1.5vw, 1rem) !important;
}

/* Z-index Management */
.slide {
    z-index: 1;
}

.slide.active {
    z-index: 10;
}

.navigation {
    z-index: 100 !important;
}

/* Prevent Absolute Positioning Issues */
.slide .absolute-element {
    position: absolute;
    max-width: 100%;
    max-height: 100%;
    overflow: hidden;
}

/* ========== END DEFENSIVE CSS ========== */
"""

    def generate_runtime_js(self) -> str:
        """Generate runtime JavaScript for dynamic fixes."""
        return """
// ========== RUNTIME LAYOUT FIXES ==========
(function() {
    'use strict';

    // Configuration
    const SLIDE_HEIGHT = 720;
    const SLIDE_WIDTH = 1280;
    const MIN_FONT_SIZE = 12; // pixels
    const FONT_REDUCTION_STEP = 0.95; // 5% reduction per step

    // Fix overflow on page load and slide change
    function fixLayoutIssues() {
        const slides = document.querySelectorAll('.slide');

        slides.forEach((slide, index) => {
            if (slide.classList.contains('active') || !document.querySelector('.slide.active')) {
                checkAndFixOverflow(slide);
                checkAndFixOverlaps(slide);
            }
        });
    }

    // Check and fix overflow issues
    function checkAndFixOverflow(slide) {
        const content = slide.querySelector('.slide-content');
        if (!content) return;

        // Check if content overflows
        if (content.scrollHeight > SLIDE_HEIGHT - 80) { // 80px for padding
            console.log(`Overflow detected in slide ${slide.id}`);

            // Strategy 1: Reduce spacing
            if (!slide.classList.contains('compact-spacing')) {
                slide.classList.add('compact-spacing');
            }

            // Strategy 2: Reduce font size progressively
            if (content.scrollHeight > SLIDE_HEIGHT - 80) {
                reduceFontSize(slide);
            }

            // Strategy 3: Enable scrolling as last resort
            if (content.scrollHeight > SLIDE_HEIGHT - 80) {
                content.style.overflowY = 'auto';
                console.log(`Enabled scrolling for slide ${slide.id}`);
            }
        }
    }

    // Progressive font size reduction
    function reduceFontSize(slide) {
        const elements = slide.querySelectorAll('p, li, .card-content, .feature-description');
        let currentSize = parseFloat(window.getComputedStyle(elements[0]).fontSize);

        while (slide.scrollHeight > SLIDE_HEIGHT && currentSize > MIN_FONT_SIZE) {
            currentSize *= FONT_REDUCTION_STEP;
            elements.forEach(el => {
                el.style.fontSize = currentSize + 'px';
            });
        }
    }

    // Check and fix element overlaps
    function checkAndFixOverlaps(slide) {
        const elements = slide.querySelectorAll('.card, .image-container, .feature-item');
        const rects = [];

        elements.forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            rects.push({element: el, rect: rect, index: i});
        });

        // Check for overlaps
        for (let i = 0; i < rects.length; i++) {
            for (let j = i + 1; j < rects.length; j++) {
                if (isOverlapping(rects[i].rect, rects[j].rect)) {
                    console.log(`Overlap detected between elements ${i} and ${j}`);
                    fixOverlap(rects[i].element, rects[j].element);
                }
            }
        }
    }

    // Check if two rectangles overlap
    function isOverlapping(rect1, rect2) {
        return !(
            rect1.right < rect2.left ||
            rect1.left > rect2.right ||
            rect1.bottom < rect2.top ||
            rect1.top > rect2.bottom
        );
    }

    // Fix overlapping elements
    function fixOverlap(el1, el2) {
        // Add margin to separate elements
        el2.style.marginTop = '20px';

        // If in a flex container, ensure wrapping
        const parent = el1.parentElement;
        if (parent && window.getComputedStyle(parent).display === 'flex') {
            parent.style.flexWrap = 'wrap';
        }
    }

    // Scale images that are too large
    function scaleOversizedImages() {
        const images = document.querySelectorAll('.slide img');

        images.forEach(img => {
            img.onload = function() {
                if (this.naturalHeight > 500 || this.naturalWidth > 1000) {
                    this.style.maxHeight = '400px';
                    this.style.width = 'auto';
                    console.log(`Scaled down large image: ${this.src}`);
                }
            };

            // Trigger onload for already loaded images
            if (img.complete) {
                img.onload();
            }
        });
    }

    // Monitor slide changes
    function observeSlideChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const slide = mutation.target;
                    if (slide.classList.contains('active')) {
                        setTimeout(() => checkAndFixOverflow(slide), 100);
                    }
                }
            });
        });

        const slides = document.querySelectorAll('.slide');
        slides.forEach(slide => {
            observer.observe(slide, {attributes: true});
        });
    }

    // Initialize fixes
    function initialize() {
        // Run initial fixes
        fixLayoutIssues();
        scaleOversizedImages();

        // Set up observers
        observeSlideChanges();

        // Re-run on window resize
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(fixLayoutIssues, 250);
        });

        // Re-run after MathJax rendering
        if (window.MathJax) {
            window.MathJax.startup.document.subscribe('End', fixLayoutIssues);
        }

        console.log('Layout Fixer initialized successfully');
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
})();
// ========== END RUNTIME FIXES ==========
"""


def process_html_file(input_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict]:
    """
    Process an HTML file to fix layout issues.

    Args:
        input_path: Path to the input HTML file
        output_path: Optional path for the output file (defaults to input_path with '_fixed' suffix)

    Returns:
        Tuple of (output_path, report_dict)
    """
    logger.info(f"Processing: {input_path}")

    # Read the HTML file
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Analyze for issues
    logger.info("Analyzing HTML for layout issues...")
    analyzer = LayoutAnalyzer()
    issues = analyzer.analyze_html(soup)

    # Log analysis results
    stats = issues['statistics']
    logger.info(f"Found {stats['total_issues']} issues across {stats['affected_slides']} slides")
    logger.info(f"Severity: {stats['severity_distribution']}")

    # Apply fixes
    logger.info("Applying fixes...")
    fixer = LayoutFixer()
    fixed_soup, fixes_log = fixer.fix_html(soup, issues)

    # Generate output path if not provided
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_fixed{input_path_obj.suffix}"

    # Write fixed HTML
    logger.info(f"Writing fixed HTML to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(fixed_soup.prettify()))

    # Generate report
    report = {
        'input_file': input_path,
        'output_file': str(output_path),
        'analysis': issues,
        'fixes_applied': fixes_log,
        'summary': {
            'total_issues_found': stats['total_issues'],
            'total_fixes_applied': len(fixes_log),
            'success': True
        }
    }

    return str(output_path), report


def generate_report(report: Dict, output_path: Optional[str] = None) -> str:
    """Generate a human-readable report of the fixes applied."""
    lines = []
    lines.append("=" * 60)
    lines.append("LAYOUT FIX REPORT")
    lines.append("=" * 60)
    lines.append(f"\nInput file: {report['input_file']}")
    lines.append(f"Output file: {report['output_file']}")
    lines.append(f"\nTimestamp: {report.get('timestamp', 'N/A')}")

    # Analysis summary
    lines.append("\n" + "-" * 40)
    lines.append("ANALYSIS SUMMARY")
    lines.append("-" * 40)

    stats = report['analysis']['statistics']
    lines.append(f"Total slides analyzed: {report['analysis']['total_slides']}")
    lines.append(f"Total issues found: {stats['total_issues']}")
    lines.append(f"Affected slides: {stats['affected_slides']}")

    lines.append(f"\nSeverity distribution:")
    for severity, count in stats['severity_distribution'].items():
        lines.append(f"  - {severity.capitalize()}: {count}")

    lines.append(f"\nIssue types:")
    for issue_type, count in stats['issue_types'].items():
        lines.append(f"  - {issue_type.replace('_', ' ').title()}: {count}")

    # Issues by slide
    if report['analysis']['issues_by_slide']:
        lines.append("\n" + "-" * 40)
        lines.append("ISSUES BY SLIDE")
        lines.append("-" * 40)

        for slide_id, issues in report['analysis']['issues_by_slide'].items():
            lines.append(f"\n{slide_id}:")
            for issue in issues:
                lines.append(f"  - [{issue['severity']}] {issue['type'].replace('_', ' ').title()}")
                if 'details' in issue:
                    for key, value in issue['details'].items():
                        if isinstance(value, (int, float)):
                            lines.append(f"    • {key}: {value:.2f}" if isinstance(value, float) else f"    • {key}: {value}")

    # Fixes applied
    lines.append("\n" + "-" * 40)
    lines.append("FIXES APPLIED")
    lines.append("-" * 40)
    lines.append(f"Total fixes: {len(report['fixes_applied'])}\n")

    for fix in report['fixes_applied']:
        lines.append(f"• {fix.get('type', 'unknown').replace('_', ' ').title()}")
        if 'description' in fix:
            lines.append(f"  {fix['description']}")
        if 'actions' in fix:
            for action in fix['actions']:
                lines.append(f"  - {action}")

    # Summary
    lines.append("\n" + "-" * 40)
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"✓ Successfully processed HTML file")
    lines.append(f"✓ Found and addressed {stats['total_issues']} layout issues")
    lines.append(f"✓ Applied {len(report['fixes_applied'])} fixes")
    lines.append(f"✓ Added defensive CSS and runtime JavaScript")
    lines.append(f"\nThe fixed HTML file has been saved to:")
    lines.append(f"  {report['output_file']}")

    report_text = "\n".join(lines)

    # Save report to file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        logger.info(f"Report saved to: {output_path}")

    return report_text


def main():
    """Main entry point for command-line usage."""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description='Fix layout issues in AI-generated HTML presentations')
    parser.add_argument('input', help='Path to input HTML file')
    parser.add_argument('-o', '--output', help='Path to output HTML file (optional)')
    parser.add_argument('-r', '--report', help='Path to save report file (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Process the HTML file
    try:
        output_path, report = process_html_file(args.input, args.output)
        report['timestamp'] = datetime.now().isoformat()

        # Generate and display report
        report_text = generate_report(report, args.report)
        print("\n" + report_text)

        # Save JSON report
        json_report_path = Path(output_path).parent / f"{Path(output_path).stem}_report.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logger.info(f"JSON report saved to: {json_report_path}")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())