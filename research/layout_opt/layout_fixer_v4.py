#!/usr/bin/env python3
"""
Layout Fixer V4 - Preserves navigation while fixing content visibility
Carefully applies fixes without breaking slide transitions.
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


class LayoutFixerV4:
    """
    Final layout fixer that preserves all original functionality.
    """

    def __init__(self):
        self.fixes_applied = []
        self.problem_slides = []

    def process_html(self, html_content: str) -> Tuple[str, List[Dict]]:
        """
        Process HTML with minimal invasive changes.

        Args:
            html_content: Original HTML content

        Returns:
            Tuple of (fixed_html, fixes_log)
        """
        fixes_log = []

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Detect problematic slides
        overflow_slides = self.detect_overflow_slides(soup)
        if overflow_slides:
            fixes_log.append({
                'type': 'overflow_detection',
                'description': f'Found {len(overflow_slides)} slides with potential overflow',
                'slides': overflow_slides
            })
            self.problem_slides = overflow_slides

        # 2. Inject non-invasive CSS
        css_injected = self.inject_safe_css(soup)
        if css_injected:
            fixes_log.append({
                'type': 'safe_css',
                'description': 'Injected non-invasive CSS for content visibility'
            })

        # 3. Inject helper JavaScript
        js_injected = self.inject_helper_js(soup)
        if js_injected:
            fixes_log.append({
                'type': 'helper_js',
                'description': 'Added helper JavaScript for content management'
            })

        # 4. Fix slide content areas only
        for slide_id in self.problem_slides:
            slide = soup.find('div', id=slide_id)
            if slide:
                self.fix_slide_content_only(slide)
                fixes_log.append({
                    'type': 'content_fix',
                    'description': f'Fixed content area in {slide_id}'
                })

        # 5. Constrain images safely
        images_fixed = self.safely_constrain_images(soup)
        if images_fixed > 0:
            fixes_log.append({
                'type': 'image_constraints',
                'description': f'Safely constrained {images_fixed} images'
            })

        # Return without prettifying
        fixed_html = str(soup)

        return fixed_html, fixes_log

    def detect_overflow_slides(self, soup: BeautifulSoup) -> List[str]:
        """Detect slides with likely overflow."""
        problem_slides = []

        slides = soup.find_all('div', class_='slide')

        for slide in slides:
            slide_id = slide.get('id', '')

            # Analyze content
            text_length = len(slide.get_text(strip=True))
            num_images = len(slide.find_all('img'))
            num_list_items = len(slide.find_all('li'))

            # Simple risk assessment
            risk = 0
            if text_length > 1500:
                risk += 2
            elif text_length > 1000:
                risk += 1

            if num_images > 1:
                risk += 1

            if num_list_items > 6:
                risk += 1

            if risk >= 2:
                problem_slides.append(slide_id)
                logger.info(f"{slide_id}: Overflow risk detected (text: {text_length}, images: {num_images})")

        return problem_slides

    def fix_slide_content_only(self, slide):
        """Fix only the content area, not the slide itself."""
        # Find slide-content div
        slide_content = slide.find('div', class_='slide-content')
        if slide_content:
            # Add inline style for scrolling
            current_style = slide_content.get('style', '')
            if 'overflow' not in current_style:
                new_style = current_style
                if new_style and not new_style.endswith(';'):
                    new_style += '; '
                new_style += 'overflow-y: auto; max-height: 640px; scrollbar-width: thin;'
                slide_content['style'] = new_style

            # Mark slide as having dense content for CSS
            slide_classes = slide.get('class', [])
            if 'dense-content' not in slide_classes:
                slide['class'] = slide_classes + ['dense-content']

    def safely_constrain_images(self, soup: BeautifulSoup) -> int:
        """Constrain images without breaking layout."""
        images = soup.find_all('img')
        fixed_count = 0

        for img in images:
            style = img.get('style', '')

            # Only add constraints if not present
            if 'max-height' not in style and 'max-width' not in style:
                new_style = style
                if new_style and not new_style.endswith(';'):
                    new_style += '; '
                new_style += 'max-width: 100%; max-height: 400px; height: auto; object-fit: contain;'
                img['style'] = new_style
                fixed_count += 1

        return fixed_count

    def inject_safe_css(self, soup: BeautifulSoup) -> bool:
        """Inject CSS that doesn't break navigation."""

        safe_css = """
/* ========== LAYOUT FIXER V4 - SAFE CSS ========== */
/* Carefully designed to not interfere with slide navigation */

/* Content area scrolling - doesn't touch .slide */
.slide-content {
    overflow-y: auto;
    overflow-x: hidden;
    max-height: 640px;
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

/* Webkit scrollbar styling */
.slide-content::-webkit-scrollbar {
    width: 6px;
}

.slide-content::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
}

.slide-content::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
}

.slide-content::-webkit-scrollbar-thumb:hover {
    background-color: rgba(0, 0, 0, 0.4);
}

/* Dense content adjustments */
.slide.dense-content .slide-body {
    gap: 20px;
}

.slide.dense-content .card {
    padding: 20px;
}

.slide.dense-content p,
.slide.dense-content li {
    line-height: 1.5;
    margin-bottom: 0.6em;
}

/* Image constraints */
.slide-content img {
    max-width: 100%;
    max-height: 400px;
    height: auto;
    object-fit: contain;
}

.image-container {
    max-height: 440px;
    overflow: hidden;
}

.image-container img {
    max-height: 380px;
}

/* Caption sizing */
.image-caption {
    font-size: 0.85rem;
    line-height: 1.3;
    margin-top: 8px;
}

/* List compaction for dense slides */
.dense-content ul,
.dense-content ol {
    margin: 10px 0;
}

.dense-content li {
    margin-bottom: 0.5em;
}

/* Card scrolling if needed */
.card {
    max-height: 500px;
    overflow-y: auto;
    scrollbar-width: thin;
}

/* Table scrolling */
.comparison-table {
    display: block;
    overflow-x: auto;
    max-width: 100%;
}

/* Code block constraints */
.code-block,
pre {
    max-height: 350px;
    overflow: auto;
    font-size: 0.9em;
}

/* Math overflow */
.mathjax-enabled {
    overflow-x: auto;
    max-width: 100%;
}

/* Feature list adjustments */
.dense-content .feature-list {
    gap: 15px;
}

.dense-content .feature-item {
    margin-bottom: 8px;
}

/* Text size adjustments for dense content */
.dense-content .slide-title {
    font-size: 2.2rem;
    margin-bottom: 15px;
}

.dense-content .slide-subtitle {
    font-size: 1.3rem;
    margin-bottom: 20px;
}

.dense-content p,
.dense-content li {
    font-size: 0.95em;
}

/* Scroll indicator */
.slide-content.has-scroll::after {
    content: "↓";
    position: fixed;
    bottom: 40px;
    right: 50%;
    transform: translateX(50%);
    background: rgba(0, 0, 0, 0.6);
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    opacity: 0.8;
    pointer-events: none;
    z-index: 50;
}

/* ========== END SAFE CSS ========== */
"""

        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)

        # Check if already present
        existing = soup.find(string=re.compile('LAYOUT FIXER V4'))
        if existing:
            return False

        # Add style tag
        style_tag = soup.new_tag('style')
        style_tag.string = safe_css

        # Insert AFTER existing styles to ensure proper cascading
        existing_styles = head.find_all('style')
        if existing_styles:
            existing_styles[-1].insert_after(style_tag)
        else:
            head.append(style_tag)

        return True

    def inject_helper_js(self, soup: BeautifulSoup) -> bool:
        """Inject helper JavaScript that doesn't interfere with navigation."""

        helper_js = """
// ========== LAYOUT FIXER V4 HELPER ==========
(function() {
    'use strict';

    // Wait for page and slide system to fully initialize
    function initHelper() {
        console.log('Layout Fixer V4 Helper initializing...');

        // Check slides for overflow
        checkAllSlides();

        // Watch for slide changes
        observeSlideChanges();

        // Handle images
        handleImages();

        console.log('Layout Fixer V4 Helper ready');
    }

    function checkAllSlides() {
        const slides = document.querySelectorAll('.slide');

        slides.forEach((slide, index) => {
            const content = slide.querySelector('.slide-content');
            if (!content) return;

            // Check if content overflows
            if (content.scrollHeight > content.clientHeight + 5) {
                console.log(`Slide ${index + 1}: Content scrollable (${content.scrollHeight}px)`);
                content.classList.add('has-scroll');

                // Remove scroll indicator when user scrolls
                content.addEventListener('scroll', function() {
                    if (this.scrollTop > 10) {
                        this.classList.remove('has-scroll');
                    }
                }, { once: true });
            }
        });
    }

    function observeSlideChanges() {
        // Re-check when slides become active
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' &&
                    mutation.attributeName === 'class' &&
                    mutation.target.classList.contains('active')) {

                    const content = mutation.target.querySelector('.slide-content');
                    if (content && content.scrollHeight > content.clientHeight) {
                        content.classList.add('has-scroll');
                    }
                }
            });
        });

        document.querySelectorAll('.slide').forEach(slide => {
            observer.observe(slide, { attributes: true });
        });
    }

    function handleImages() {
        // Ensure images don't break layout when loaded
        document.querySelectorAll('img').forEach(img => {
            if (!img.complete) {
                img.addEventListener('load', function() {
                    // Re-check parent slide for overflow
                    const slide = this.closest('.slide');
                    if (slide && slide.classList.contains('active')) {
                        const content = slide.querySelector('.slide-content');
                        if (content && content.scrollHeight > content.clientHeight) {
                            content.classList.add('has-scroll');
                        }
                    }
                });
            }
        });
    }

    // Initialize after a delay to ensure slide system is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => setTimeout(initHelper, 200));
    } else {
        setTimeout(initHelper, 200);
    }

    // Handle MathJax if present
    if (window.MathJax && window.MathJax.startup) {
        window.MathJax.startup.promise.then(() => {
            setTimeout(checkAllSlides, 100);
        });
    }
})();
// ========== END V4 HELPER ==========
"""

        body = soup.find('body')
        if not body:
            return False

        # Check if already present
        existing = soup.find(string=re.compile('LAYOUT FIXER V4 HELPER'))
        if existing:
            return False

        # Add script tag at the end
        script_tag = soup.new_tag('script')
        script_tag.string = helper_js
        body.append(script_tag)

        return True


def process_file(input_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict]:
    """Process HTML file with V4 fixer."""

    logger.info(f"Processing: {input_path}")

    # Read HTML
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Count slides
    slide_count = html_content.count('class="slide"')
    logger.info(f"Found {slide_count} slides")

    # Process with V4
    fixer = LayoutFixerV4()
    fixed_html, fixes_log = fixer.process_html(html_content)

    # Output path
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_fixed_v4{input_path_obj.suffix}"

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

    # Save report
    report_path = Path(output_path).parent / f"{Path(output_path).stem}_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    return str(output_path), report


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Layout Fixer V4 - Safe fixes that preserve navigation'
    )
    parser.add_argument('input', help='Input HTML file')
    parser.add_argument('-o', '--output', help='Output HTML file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        output_path, report = process_file(args.input, args.output)

        print("\n" + "="*60)
        print("LAYOUT FIXER V4 - COMPLETE")
        print("="*60)
        print(f"Input:  {args.input}")
        print(f"Output: {output_path}")
        print(f"Slides: {report['slide_count']}")

        if report['problem_slides']:
            print(f"\nProblematic slides: {', '.join(report['problem_slides'])}")

        print(f"\nFixes applied: {len(report['fixes_applied'])}")
        for fix in report['fixes_applied']:
            print(f"  ✓ {fix['description']}")

        print(f"\nFile size change: {report['file_size']['difference']:+,} bytes")

        print("\n✅ Success! The fixed HTML should:")
        print("   • Preserve slide navigation completely")
        print("   • Make overflow content scrollable")
        print("   • Show scroll indicators where needed")
        print("   • NOT break any existing functionality")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())