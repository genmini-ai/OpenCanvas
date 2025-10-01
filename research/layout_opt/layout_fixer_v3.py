#!/usr/bin/env python3
"""
Layout Fixer V3 - Ensures all content is visible
Fixes text cutoff and ensures complete content visibility through smart scaling and scrolling.
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup, Comment, NavigableString
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class LayoutFixerV3:
    """
    Advanced layout fixer that ensures no content is cut off.
    """

    def __init__(self):
        self.fixes_applied = []
        self.problem_slides = []

    def process_html(self, html_content: str) -> Tuple[str, List[Dict]]:
        """
        Process HTML content with focus on preventing content cutoff.

        Args:
            html_content: Original HTML content

        Returns:
            Tuple of (fixed_html, fixes_log)
        """
        fixes_log = []

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Analyze all slides for overflow
        overflow_slides = self.detect_overflow_slides(soup)
        if overflow_slides:
            fixes_log.append({
                'type': 'overflow_detection',
                'description': f'Detected potential overflow in {len(overflow_slides)} slides',
                'slides': overflow_slides
            })
            self.problem_slides = overflow_slides

        # 2. Inject improved CSS
        css_injected = self.inject_improved_css(soup)
        if css_injected:
            fixes_log.append({'type': 'improved_css', 'description': 'Injected improved CSS with better overflow handling'})

        # 3. Add enhanced runtime JavaScript
        js_injected = self.inject_enhanced_js(soup)
        if js_injected:
            fixes_log.append({'type': 'enhanced_js', 'description': 'Added enhanced JavaScript for dynamic fixes'})

        # 4. Fix specific slide issues
        for slide_id in self.problem_slides:
            slide = soup.find('div', id=slide_id)
            if slide:
                self.fix_slide_content(slide)
                fixes_log.append({
                    'type': 'slide_fix',
                    'description': f'Applied content fixes to {slide_id}'
                })

        # 5. Ensure images are properly constrained
        images_fixed = self.fix_all_images(soup)
        if images_fixed > 0:
            fixes_log.append({
                'type': 'image_constraints',
                'description': f'Constrained {images_fixed} images'
            })

        # Return without prettifying to preserve JavaScript
        fixed_html = str(soup)

        return fixed_html, fixes_log

    def detect_overflow_slides(self, soup: BeautifulSoup) -> List[str]:
        """
        Detect slides that likely have overflow issues based on content analysis.
        """
        problem_slides = []

        slides = soup.find_all('div', class_='slide')

        for slide in slides:
            slide_id = slide.get('id', '')

            # Count content indicators
            text_length = len(slide.get_text(strip=True))
            num_images = len(slide.find_all('img'))
            num_paragraphs = len(slide.find_all('p'))
            num_lists = len(slide.find_all(['ul', 'ol']))
            num_list_items = len(slide.find_all('li'))

            # Check for specific problem indicators
            has_figure = bool(slide.find_all(string=re.compile(r'Figure \d+:')))
            has_math = bool(slide.find_all(class_='mathjax-enabled'))
            has_table = bool(slide.find('table'))

            # Calculate risk score
            risk_score = 0

            # Text-based risk
            if text_length > 2000:
                risk_score += 3
            elif text_length > 1500:
                risk_score += 2
            elif text_length > 1000:
                risk_score += 1

            # Structure-based risk
            if num_images > 1:
                risk_score += 2
            if num_list_items > 8:
                risk_score += 2
            if num_paragraphs > 5:
                risk_score += 1
            if has_figure:
                risk_score += 1
            if has_math:
                risk_score += 1
            if has_table:
                risk_score += 1

            # Mark as problematic if risk is high
            if risk_score >= 3:
                problem_slides.append(slide_id)
                logger.info(f"Slide {slide_id}: High overflow risk (score: {risk_score}, text: {text_length} chars)")

        return problem_slides

    def fix_slide_content(self, slide):
        """
        Apply specific fixes to a slide with overflow issues.
        """
        # Add class to mark this slide needs special handling
        existing_classes = slide.get('class', [])
        if 'overflow-risk' not in existing_classes:
            slide['class'] = existing_classes + ['overflow-risk']

        # Make slide-content scrollable
        slide_content = slide.find('div', class_='slide-content')
        if slide_content:
            current_style = slide_content.get('style', '')
            if 'overflow-y' not in current_style:
                slide_content['style'] = current_style + '; overflow-y: auto; max-height: 640px;'

        # Reduce padding on dense slides
        slide_body = slide.find('div', class_='slide-body')
        if slide_body:
            current_style = slide_body.get('style', '')
            if 'gap' not in current_style:
                slide_body['style'] = current_style + '; gap: 20px;'

    def fix_all_images(self, soup: BeautifulSoup) -> int:
        """
        Ensure all images are properly constrained.
        """
        images = soup.find_all('img')
        fixed_count = 0

        for img in images:
            style = img.get('style', '')

            # Add max dimensions if not present
            if 'max-height' not in style:
                new_style = style
                if new_style and not new_style.endswith(';'):
                    new_style += '; '
                new_style += 'max-width: 100%; max-height: 400px; height: auto; object-fit: contain;'
                img['style'] = new_style
                fixed_count += 1

        return fixed_count

    def inject_improved_css(self, soup: BeautifulSoup) -> bool:
        """Inject improved CSS that ensures content visibility."""

        improved_css = """
/* ========== LAYOUT FIXER V3 - COMPLETE CONTENT VISIBILITY ========== */

/* Global slide constraints with better overflow */
.slide {
    width: 1280px !important;
    height: 720px !important;
    overflow: hidden; /* Hide outer overflow */
    position: relative;
}

/* Content area with smart scrolling */
.slide-content {
    max-height: 640px !important; /* Leave room for footer */
    overflow-y: auto !important; /* Always allow scrolling */
    overflow-x: hidden !important;
    padding-right: 10px; /* Space for scrollbar */
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 0, 0, 0.3) transparent;
}

/* Prettier scrollbars */
.slide-content::-webkit-scrollbar {
    width: 8px;
}

.slide-content::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
}

.slide-content::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
}

.slide-content::-webkit-scrollbar-thumb:hover {
    background-color: rgba(0, 0, 0, 0.5);
}

/* Scroll indicator for overflow content */
.slide.has-overflow .slide-content::after {
    content: "↓ Scroll for more ↓";
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    pointer-events: none;
    z-index: 100;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.8; }
    50% { opacity: 1; }
}

/* Aggressive image constraints */
.slide img {
    max-width: 100% !important;
    max-height: 380px !important; /* Reduced from 400px */
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
    display: block;
    margin: 0 auto;
}

/* Specific constraints for image containers */
.image-container {
    max-height: 420px !important;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.image-container img {
    max-height: 360px !important;
}

.image-caption {
    font-size: 0.85rem !important;
    margin-top: 8px !important;
    line-height: 1.3 !important;
}

/* Dense content handling */
.slide.overflow-risk {
    font-size: 0.95em;
}

.slide.overflow-risk .slide-body {
    gap: 15px !important;
}

.slide.overflow-risk .card {
    padding: 15px !important;
}

.slide.overflow-risk p,
.slide.overflow-risk li {
    line-height: 1.5 !important;
    margin-bottom: 0.6em !important;
}

/* Title size constraints */
.slide-title {
    font-size: clamp(1.8rem, 3vw, 2.3rem) !important;
    line-height: 1.2 !important;
    margin-bottom: 15px !important;
}

.slide-subtitle {
    font-size: clamp(1.2rem, 2vw, 1.4rem) !important;
    margin-bottom: 20px !important;
}

/* List compaction */
.slide ul,
.slide ol {
    margin: 10px 0 !important;
    padding-left: 25px !important;
}

.slide li {
    margin-bottom: 0.5em !important;
    line-height: 1.5 !important;
}

/* Two-column responsive layout */
.two-column {
    gap: 30px !important;
}

.two-column .column {
    overflow: hidden;
}

/* Card constraints */
.card {
    max-height: 500px;
    overflow-y: auto;
    scrollbar-width: thin;
}

/* Table overflow handling */
.comparison-table {
    display: block !important;
    overflow-x: auto !important;
    max-width: 100% !important;
    max-height: 400px !important;
    overflow-y: auto !important;
}

/* Code block constraints */
.code-block,
pre {
    max-height: 300px !important;
    overflow: auto !important;
    font-size: 0.85em !important;
    line-height: 1.4 !important;
}

/* Math formula handling */
.mathjax-enabled {
    overflow-x: auto !important;
    max-width: 100% !important;
    font-size: 0.9em;
}

/* Feature list responsive */
.feature-list {
    gap: 15px !important;
}

.feature-item {
    margin-bottom: 10px !important;
}

.feature-description {
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
}

/* Method comparison cards */
.method-card {
    max-height: 300px;
    overflow-y: auto;
}

/* Result cards compaction */
.result-card {
    padding: 15px !important;
}

.result-value {
    font-size: 2rem !important;
}

/* Footer positioning fix */
.slide-footer {
    position: absolute;
    bottom: 20px !important;
    z-index: 10;
    background: rgba(255, 255, 255, 0.9);
    padding: 5px 40px;
}

/* Navigation stays on top */
.navigation {
    z-index: 1000 !important;
    position: fixed !important;
}

/* ========== END LAYOUT FIXER V3 CSS ========== */
"""

        head = soup.find('head')
        if not head:
            logger.warning("No <head> tag found, creating one")
            head = soup.new_tag('head')
            soup.html.insert(0, head)

        # Check if already injected
        existing = soup.find(string=re.compile('LAYOUT FIXER V3'))
        if existing:
            logger.info("V3 CSS already present, skipping")
            return False

        # Create and append style tag
        style_tag = soup.new_tag('style')
        style_tag.string = improved_css
        head.append(style_tag)

        return True

    def inject_enhanced_js(self, soup: BeautifulSoup) -> bool:
        """Inject enhanced JavaScript for dynamic overflow handling."""

        enhanced_js = """
// ========== LAYOUT FIXER V3 - ENHANCED OVERFLOW HANDLING ==========
(function() {
    'use strict';

    console.log('Layout Fixer V3 initializing...');

    // Initialize after DOM and existing scripts
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        setTimeout(initialize, 100);
    }

    function initialize() {
        const slides = document.querySelectorAll('.slide');
        console.log(`Processing ${slides.length} slides for overflow...`);

        // Process all slides
        slides.forEach((slide, index) => {
            checkAndFixSlide(slide, index + 1);
        });

        // Watch for slide changes
        setupSlideObserver();

        // Handle dynamic content loading
        setupDynamicContentHandler();

        console.log('Layout Fixer V3 initialized successfully');
    }

    function checkAndFixSlide(slide, slideNum) {
        const content = slide.querySelector('.slide-content');
        if (!content) return;

        // Check for actual overflow
        const hasOverflow = content.scrollHeight > content.clientHeight;

        if (hasOverflow) {
            console.log(`Slide ${slideNum}: Overflow detected (${content.scrollHeight}px > ${content.clientHeight}px)`);

            // Mark slide as having overflow
            slide.classList.add('has-overflow');

            // Try to reduce content size first
            reduceContentSize(slide);

            // Recheck after reduction
            if (content.scrollHeight > content.clientHeight) {
                console.log(`Slide ${slideNum}: Still has overflow after reduction, enabling scroll`);
                content.style.overflowY = 'auto';

                // Add scroll hint
                addScrollHint(slide);
            } else {
                slide.classList.remove('has-overflow');
            }
        }

        // Check images
        const images = slide.querySelectorAll('img');
        images.forEach(img => {
            constrainImage(img);
        });

        // Check tables
        const tables = slide.querySelectorAll('table');
        tables.forEach(table => {
            if (table.offsetWidth > content.offsetWidth) {
                table.style.fontSize = '0.85em';
                console.log(`Slide ${slideNum}: Reduced table font size`);
            }
        });
    }

    function reduceContentSize(slide) {
        // Add overflow-risk class for CSS rules
        slide.classList.add('overflow-risk');

        // Reduce font sizes programmatically
        const elements = slide.querySelectorAll('p, li, .card-content');
        elements.forEach(el => {
            const currentSize = parseFloat(window.getComputedStyle(el).fontSize);
            if (currentSize > 14) {
                el.style.fontSize = (currentSize * 0.9) + 'px';
            }
        });

        // Reduce spacing
        const cards = slide.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.padding = '15px';
        });

        // Compact lists
        const lists = slide.querySelectorAll('ul, ol');
        lists.forEach(list => {
            list.style.marginTop = '8px';
            list.style.marginBottom = '8px';
        });
    }

    function constrainImage(img) {
        // Ensure image doesn't break layout
        if (!img.style.maxHeight || parseInt(img.style.maxHeight) > 380) {
            img.style.maxHeight = '380px';
            img.style.width = 'auto';
            img.style.objectFit = 'contain';
        }

        // Handle load event
        if (!img.complete) {
            img.addEventListener('load', function() {
                if (this.naturalHeight > 380) {
                    this.style.maxHeight = '380px';
                    console.log('Constrained large image:', this.src);
                }
            });
        }
    }

    function addScrollHint(slide) {
        // Visual indicator that content is scrollable
        const content = slide.querySelector('.slide-content');
        if (!content) return;

        // Remove existing hint
        const existingHint = slide.querySelector('.scroll-hint');
        if (existingHint) {
            existingHint.remove();
        }

        // Check if actually scrollable
        if (content.scrollHeight > content.clientHeight) {
            content.addEventListener('scroll', function() {
                // Hide hint when user starts scrolling
                if (this.scrollTop > 10) {
                    slide.classList.remove('has-overflow');
                } else {
                    slide.classList.add('has-overflow');
                }
            });
        }
    }

    function setupSlideObserver() {
        // Watch for active slide changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' &&
                    mutation.attributeName === 'class' &&
                    mutation.target.classList.contains('active')) {

                    // Recheck active slide
                    const slideNum = Array.from(document.querySelectorAll('.slide')).indexOf(mutation.target) + 1;
                    setTimeout(() => {
                        checkAndFixSlide(mutation.target, slideNum);
                    }, 100);
                }
            });
        });

        document.querySelectorAll('.slide').forEach(slide => {
            observer.observe(slide, { attributes: true });
        });
    }

    function setupDynamicContentHandler() {
        // Handle MathJax rendering
        if (window.MathJax && window.MathJax.startup) {
            window.MathJax.startup.promise.then(() => {
                console.log('MathJax rendered, rechecking slides...');
                document.querySelectorAll('.slide.active').forEach((slide, i) => {
                    checkAndFixSlide(slide, i + 1);
                });
            });
        }

        // Handle image loading
        document.querySelectorAll('img').forEach(img => {
            if (!img.complete) {
                img.addEventListener('load', function() {
                    const slide = this.closest('.slide');
                    if (slide && slide.classList.contains('active')) {
                        const slideNum = Array.from(document.querySelectorAll('.slide')).indexOf(slide) + 1;
                        setTimeout(() => checkAndFixSlide(slide, slideNum), 100);
                    }
                });
            }
        });
    }

    // Add keyboard shortcut for scrolling within slides
    document.addEventListener('keydown', function(e) {
        const activeSlide = document.querySelector('.slide.active');
        if (!activeSlide) return;

        const content = activeSlide.querySelector('.slide-content');
        if (!content) return;

        // Page Up/Down for scrolling within slide
        if (e.key === 'PageDown') {
            e.preventDefault();
            content.scrollBy({ top: 200, behavior: 'smooth' });
        } else if (e.key === 'PageUp') {
            e.preventDefault();
            content.scrollBy({ top: -200, behavior: 'smooth' });
        }
    });

})();
// ========== END LAYOUT FIXER V3 ==========
"""

        body = soup.find('body')
        if not body:
            logger.warning("No <body> tag found")
            return False

        # Check if already injected
        existing = soup.find(string=re.compile('LAYOUT FIXER V3 - ENHANCED'))
        if existing:
            logger.info("V3 JS already present, skipping")
            return False

        # Create and append script tag
        script_tag = soup.new_tag('script')
        script_tag.string = enhanced_js
        body.append(script_tag)

        return True


def process_file(input_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict]:
    """
    Process an HTML file with V3 fixer focusing on content visibility.

    Args:
        input_path: Path to input HTML
        output_path: Optional output path

    Returns:
        Tuple of (output_path, report)
    """
    logger.info(f"Processing: {input_path}")

    # Read the HTML file
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Count slides
    slide_count = html_content.count('class="slide"')
    logger.info(f"Found {slide_count} slides")

    # Process with V3 fixer
    fixer = LayoutFixerV3()
    fixed_html, fixes_log = fixer.process_html(html_content)

    # Generate output path
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_fixed_v3{input_path_obj.suffix}"

    # Write fixed HTML
    logger.info(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_html)

    # Create report
    report = {
        'input_file': input_path,
        'output_file': str(output_path),
        'slide_count': slide_count,
        'problem_slides': fixer.problem_slides,
        'fixes_applied': fixes_log,
        'file_size': {
            'original': len(html_content),
            'fixed': len(fixed_html),
            'difference': len(fixed_html) - len(html_content)
        }
    }

    # Save JSON report
    report_path = Path(output_path).parent / f"{Path(output_path).stem}_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Report saved to: {report_path}")

    return str(output_path), report


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Layout Fixer V3 - Ensures all content is visible'
    )
    parser.add_argument('input', help='Input HTML file path')
    parser.add_argument('-o', '--output', help='Output HTML file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        output_path, report = process_file(args.input, args.output)

        print("\n" + "="*60)
        print("LAYOUT FIXER V3 - COMPLETE")
        print("="*60)
        print(f"Input:  {args.input}")
        print(f"Output: {output_path}")
        print(f"Slides: {report['slide_count']}")

        if report['problem_slides']:
            print(f"\nProblematic slides detected: {', '.join(report['problem_slides'])}")

        print(f"\nFixes applied: {len(report['fixes_applied'])}")
        for fix in report['fixes_applied']:
            print(f"  ✓ {fix['description']}")

        size_diff = report['file_size']['difference']
        print(f"\nFile size change: {size_diff:+,} bytes")

        print("\n✅ Success! The fixed HTML should now:")
        print("   • Show all content (scrollable where needed)")
        print("   • Have visual scroll indicators")
        print("   • Preserve slide navigation")
        print("   • Scale content appropriately")
        print("\nTip: Use PageUp/PageDown to scroll within slides")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())