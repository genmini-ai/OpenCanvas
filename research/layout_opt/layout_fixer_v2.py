#!/usr/bin/env python3
"""
Layout Fixer V2 - Preserves multi-slide functionality
Fixes layout issues without breaking JavaScript or slide navigation.
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


class LayoutFixerV2:
    """
    Improved layout fixer that preserves JavaScript and HTML structure.
    """

    def __init__(self):
        self.fixes_applied = []

    def process_html(self, html_content: str) -> Tuple[str, List[Dict]]:
        """
        Process HTML content and inject fixes without breaking structure.

        Args:
            html_content: Original HTML content

        Returns:
            Tuple of (fixed_html, fixes_log)
        """
        fixes_log = []

        # Parse with BeautifulSoup - but we'll be careful with output
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Inject defensive CSS
        css_injected = self.inject_defensive_css(soup)
        if css_injected:
            fixes_log.append({'type': 'defensive_css', 'description': 'Injected defensive CSS rules'})

        # 2. Inject runtime JavaScript (after existing scripts)
        js_injected = self.inject_runtime_js(soup)
        if js_injected:
            fixes_log.append({'type': 'runtime_js', 'description': 'Added runtime JavaScript fixes'})

        # 3. Add protective classes to slides (without breaking existing classes)
        slides_fixed = self.add_protective_classes(soup)
        if slides_fixed > 0:
            fixes_log.append({
                'type': 'protective_classes',
                'description': f'Added protective classes to {slides_fixed} slides'
            })

        # 4. Fix image constraints
        images_fixed = self.fix_image_constraints(soup)
        if images_fixed > 0:
            fixes_log.append({
                'type': 'image_constraints',
                'description': f'Fixed constraints on {images_fixed} images'
            })

        # CRITICAL: Use str() instead of prettify() to preserve JavaScript
        fixed_html = str(soup)

        return fixed_html, fixes_log

    def inject_defensive_css(self, soup: BeautifulSoup) -> bool:
        """Inject defensive CSS without breaking existing styles."""

        defensive_css = """
/* ========== LAYOUT FIXER V2 DEFENSIVE CSS ========== */
/* Carefully crafted to not break slide navigation */

/* Slide overflow protection - don't break opacity transitions */
.slide {
    overflow: hidden !important;
    contain: layout style; /* Not paint - that can break opacity */
}

/* Content area constraints */
.slide-content {
    max-height: 650px;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

/* Webkit scrollbar styling */
.slide-content::-webkit-scrollbar {
    width: 6px;
}

.slide-content::-webkit-scrollbar-track {
    background: transparent;
}

.slide-content::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
}

/* Image constraints - preserve aspect ratios */
.image-container img,
.slide img {
    max-width: 100% !important;
    max-height: 450px !important;
    height: auto;
    object-fit: contain;
}

/* Prevent text overflow */
.slide p,
.slide li,
.card-content,
.feature-description,
.method-description {
    overflow-wrap: break-word;
    word-break: break-word;
    hyphens: auto;
}

/* Two-column responsive without breaking layout */
@media screen and (max-width: 1280px) {
    .two-column {
        flex-wrap: wrap;
    }
}

/* Math formula overflow protection */
.mathjax-enabled,
.MathJax_Display {
    overflow-x: auto !important;
    max-width: 100% !important;
}

/* Card height limits with scroll */
.card {
    max-height: calc(100vh - 200px);
    overflow-y: auto;
    scrollbar-width: thin;
}

/* Table responsiveness */
.comparison-table {
    display: block;
    overflow-x: auto;
    max-width: 100%;
}

/* Code block constraints */
.code-block,
pre {
    max-height: 400px !important;
    overflow: auto !important;
    font-size: 0.9em;
}

/* Feature list responsive grid */
.feature-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}

/* Long list compaction */
ul li, ol li {
    margin-bottom: 0.75em;
}

/* Reduce spacing on dense slides */
.dense-content .slide-body {
    gap: 20px;
}

.dense-content .card {
    padding: 20px;
}

/* Font size clamps for responsive text */
.slide-title {
    font-size: clamp(2rem, 3.5vw, 2.5rem) !important;
}

.card-title {
    font-size: clamp(1.2rem, 2vw, 1.5rem) !important;
}

.slide-body p,
.slide-body li {
    font-size: clamp(0.9rem, 1.4vw, 1rem);
    line-height: 1.6;
}

/* Ensure navigation stays on top */
.navigation {
    z-index: 1000 !important;
    position: fixed !important;
}

/* Prevent absolute positioning issues */
.slide .absolute {
    position: absolute;
    max-width: 100%;
    max-height: 100%;
}

/* ========== END DEFENSIVE CSS ========== */
"""

        head = soup.find('head')
        if not head:
            logger.warning("No <head> tag found, creating one")
            head = soup.new_tag('head')
            soup.html.insert(0, head)

        # Check if we already injected CSS
        existing = soup.find(string=re.compile('LAYOUT FIXER V2 DEFENSIVE CSS'))
        if existing:
            logger.info("Defensive CSS already present, skipping")
            return False

        # Create style tag
        style_tag = soup.new_tag('style')
        style_tag.string = defensive_css

        # Add at the end of head to override other styles
        head.append(style_tag)

        return True

    def inject_runtime_js(self, soup: BeautifulSoup) -> bool:
        """Inject runtime JavaScript that doesn't interfere with slide navigation."""

        runtime_js = """
// ========== LAYOUT FIXER V2 RUNTIME ==========
(function() {
    'use strict';

    // Wait for existing slide system to initialize
    let initTimer = setTimeout(initLayoutFixer, 500);

    function initLayoutFixer() {
        console.log('Layout Fixer V2 initializing...');

        // Don't interfere with slide navigation
        const slides = document.querySelectorAll('.slide');
        if (!slides.length) {
            console.warn('No slides found');
            return;
        }

        // Process each slide
        slides.forEach((slide, index) => {
            processSlide(slide, index);
        });

        // Watch for slide changes
        observeSlideChanges();

        // Handle image loading
        handleImages();

        console.log('Layout Fixer V2 initialized');
    }

    function processSlide(slide, index) {
        const content = slide.querySelector('.slide-content');
        if (!content) return;

        // Check for text density
        const textLength = (content.textContent || '').length;
        if (textLength > 1500) {
            slide.classList.add('dense-content');
            console.log(`Slide ${index + 1}: Dense content detected (${textLength} chars)`);
        }

        // Check for overflow
        if (content.scrollHeight > content.clientHeight + 10) {
            console.log(`Slide ${index + 1}: Vertical overflow detected`);
            content.style.overflowY = 'auto';
        }

        // Process images in this slide
        const images = slide.querySelectorAll('img');
        images.forEach(img => {
            if (!img.style.maxWidth) {
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
            }
        });

        // Fix two-column layouts
        const twoCol = slide.querySelector('.two-column');
        if (twoCol) {
            const columns = twoCol.querySelectorAll('.column');
            if (columns.length === 2) {
                // Check if columns have images
                columns.forEach(col => {
                    if (col.querySelector('img')) {
                        col.style.minWidth = '0'; // Allow shrinking
                        col.style.overflow = 'hidden';
                    }
                });
            }
        }
    }

    function observeSlideChanges() {
        // Watch for class changes on slides (active/inactive)
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' &&
                    mutation.attributeName === 'class' &&
                    mutation.target.classList.contains('active')) {

                    // Process newly active slide
                    setTimeout(() => {
                        processSlide(mutation.target, 0);
                    }, 100);
                }
            });
        });

        document.querySelectorAll('.slide').forEach(slide => {
            observer.observe(slide, { attributes: true });
        });
    }

    function handleImages() {
        // Ensure images don't break layout when loaded
        document.querySelectorAll('.slide img').forEach(img => {
            if (img.complete) {
                checkImageSize(img);
            } else {
                img.addEventListener('load', function() {
                    checkImageSize(this);
                });
            }

            // Add error handling
            img.addEventListener('error', function() {
                console.warn('Image failed to load:', this.src);
                this.style.display = 'none';
            });
        });
    }

    function checkImageSize(img) {
        const maxHeight = 450;
        const maxWidth = 1000;

        if (img.naturalHeight > maxHeight || img.naturalWidth > maxWidth) {
            img.style.maxHeight = maxHeight + 'px';
            img.style.maxWidth = maxWidth + 'px';
            img.style.objectFit = 'contain';
            console.log('Large image constrained:', img.src);
        }
    }

    // Handle MathJax if present
    if (window.MathJax) {
        // Wait for MathJax to finish rendering
        if (window.MathJax.startup) {
            window.MathJax.startup.promise.then(() => {
                console.log('MathJax rendered, checking for overflow...');
                document.querySelectorAll('.mathjax-enabled').forEach(elem => {
                    if (elem.scrollWidth > elem.clientWidth) {
                        elem.style.overflowX = 'auto';
                    }
                });
            });
        }
    }
})();
// ========== END LAYOUT FIXER V2 ==========
"""

        body = soup.find('body')
        if not body:
            logger.warning("No <body> tag found")
            return False

        # Check if we already injected JS
        existing = soup.find(string=re.compile('LAYOUT FIXER V2 RUNTIME'))
        if existing:
            logger.info("Runtime JS already present, skipping")
            return False

        # Create script tag
        script_tag = soup.new_tag('script')
        script_tag.string = runtime_js

        # Add after all other scripts to not interfere
        body.append(script_tag)

        return True

    def add_protective_classes(self, soup: BeautifulSoup) -> int:
        """Add protective classes without breaking existing ones."""

        slides = soup.find_all('div', class_='slide')
        fixed_count = 0

        for slide in slides:
            # Check content density
            content = slide.get_text(strip=True)
            if len(content) > 1500:
                # Add class without removing existing ones
                existing_classes = slide.get('class', [])
                if 'dense-content' not in existing_classes:
                    slide['class'] = existing_classes + ['dense-content']
                    fixed_count += 1

        return fixed_count

    def fix_image_constraints(self, soup: BeautifulSoup) -> int:
        """Add image constraints via inline styles."""

        images = soup.find_all('img')
        fixed_count = 0

        for img in images:
            style = img.get('style', '')

            # Only add if not already constrained
            if 'max-width' not in style:
                new_style = style
                if new_style and not new_style.endswith(';'):
                    new_style += '; '
                new_style += 'max-width: 100%; height: auto;'
                img['style'] = new_style
                fixed_count += 1

        return fixed_count


def process_file(input_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict]:
    """
    Process an HTML file with the improved fixer.

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

    # Check if it's a multi-slide presentation
    if '<div class="slide"' in html_content:
        logger.info("Multi-slide presentation detected")

        # Count slides
        slide_count = html_content.count('class="slide"')
        logger.info(f"Found {slide_count} slides")

    # Process with V2 fixer
    fixer = LayoutFixerV2()
    fixed_html, fixes_log = fixer.process_html(html_content)

    # Generate output path
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_fixed{input_path_obj.suffix}"

    # Write fixed HTML
    logger.info(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_html)

    # Create report
    report = {
        'input_file': input_path,
        'output_file': str(output_path),
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

    parser = argparse.ArgumentParser(description='Layout Fixer V2 - Preserves JavaScript and slide navigation')
    parser.add_argument('input', help='Input HTML file path')
    parser.add_argument('-o', '--output', help='Output HTML file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        output_path, report = process_file(args.input, args.output)

        print("\n" + "="*60)
        print("LAYOUT FIXER V2 - COMPLETE")
        print("="*60)
        print(f"Input:  {args.input}")
        print(f"Output: {output_path}")
        print(f"Fixes applied: {len(report['fixes_applied'])}")

        for fix in report['fixes_applied']:
            print(f"  ✓ {fix['description']}")

        size_diff = report['file_size']['difference']
        print(f"\nFile size change: {size_diff:+,} bytes")
        print("\n✅ Success! Open the fixed HTML in a browser to verify.")
        print("   Check that slide navigation still works with arrow keys.")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())