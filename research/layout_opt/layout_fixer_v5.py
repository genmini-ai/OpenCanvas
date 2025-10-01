#!/usr/bin/env python3
"""
Layout Fixer V5 - Dynamic Height Approach
Keeps width fixed at 1280px but allows height to expand based on content.
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


class LayoutFixerV5:
    """
    Dynamic height layout fixer - content determines slide height.
    """

    def __init__(self):
        self.fixes_applied = []

    def process_html(self, html_content: str) -> Tuple[str, List[Dict]]:
        """
        Process HTML to use dynamic height instead of fixed 720px.

        Args:
            html_content: Original HTML content

        Returns:
            Tuple of (fixed_html, fixes_log)
        """
        fixes_log = []

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Inject dynamic height CSS
        css_injected = self.inject_dynamic_css(soup)
        if css_injected:
            fixes_log.append({
                'type': 'dynamic_css',
                'description': 'Injected dynamic height CSS - slides expand to fit content'
            })

        # 2. Inject adaptive JavaScript
        js_injected = self.inject_adaptive_js(soup)
        if js_injected:
            fixes_log.append({
                'type': 'adaptive_js',
                'description': 'Added JavaScript for dynamic height management'
            })

        # 3. Process each slide to remove height constraints
        slides_modified = self.modify_slides(soup)
        if slides_modified > 0:
            fixes_log.append({
                'type': 'slide_modifications',
                'description': f'Modified {slides_modified} slides for dynamic height'
            })

        # 4. Constrain images appropriately
        images_fixed = self.adjust_images(soup)
        if images_fixed > 0:
            fixes_log.append({
                'type': 'image_adjustments',
                'description': f'Adjusted {images_fixed} images for dynamic layout'
            })

        # Return without prettifying
        fixed_html = str(soup)

        return fixed_html, fixes_log

    def modify_slides(self, soup: BeautifulSoup) -> int:
        """Remove fixed height constraints from slides."""
        modified_count = 0

        slides = soup.find_all('div', class_='slide')

        for slide in slides:
            # Remove inline height styles if present
            style = slide.get('style', '')
            if 'height:' in style:
                # Remove height property
                style = re.sub(r'height:\s*[^;]+;?', '', style)
                slide['style'] = style.strip()
                modified_count += 1

            # Add class for dynamic height
            classes = slide.get('class', [])
            if 'dynamic-height' not in classes:
                slide['class'] = classes + ['dynamic-height']

        return modified_count

    def adjust_images(self, soup: BeautifulSoup) -> int:
        """Adjust images for dynamic layout."""
        images = soup.find_all('img')
        adjusted = 0

        for img in images:
            style = img.get('style', '')

            # Ensure images scale properly
            if 'max-width' not in style:
                new_style = style
                if new_style and not new_style.endswith(';'):
                    new_style += '; '
                new_style += 'max-width: 100%; height: auto; display: block; margin: 0 auto;'
                img['style'] = new_style
                adjusted += 1

        return adjusted

    def inject_dynamic_css(self, soup: BeautifulSoup) -> bool:
        """Inject CSS for dynamic height layout."""

        dynamic_css = """
/* ========== LAYOUT FIXER V5 - DYNAMIC HEIGHT WITH SCROLLING ========== */

/* Body setup for scrolling */
body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scroll-behavior: smooth;
}

/* Presentation container adjustments */
.presentation-container {
    width: 1280px !important;
    height: auto !important;
    min-height: 100vh;
    margin: 0 auto;
    background: #0a1929;
    position: relative;
}

/* Dynamic height slides */
.slide {
    width: 1280px !important;
    min-height: 100vh !important; /* At least full viewport */
    height: auto !important;
    overflow: visible !important;
    position: relative !important;
    display: none;
    padding-bottom: 80px; /* Space for footer/navigation */
    scroll-margin-top: 0; /* For smooth scroll anchoring */
}

/* Active slide is visible */
.slide.active {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Visual separator between slides in V5 scroll mode */
.slide::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(87, 197, 182, 0.3), transparent);
}

/* Ensure content flows naturally */
.slide-content {
    max-width: 1200px;
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    padding: 40px;
    margin: 0 auto;
}

/* Remove height constraints from body */
.slide-body {
    height: auto !important;
    min-height: 400px;
    overflow: visible !important;
}

/* Footer positioning for dynamic height */
.slide-footer {
    position: relative !important;
    margin-top: 40px;
    bottom: auto !important;
}

/* Navigation stays fixed */
.navigation {
    position: fixed !important;
    bottom: 30px;
    right: 40px;
    z-index: 1000;
}

/* Images adapt to dynamic layout */
.slide img {
    max-width: 100% !important;
    max-height: 600px !important;
    height: auto !important;
    object-fit: contain;
    display: block;
    margin: 20px auto;
}

/* Two-column layout adjustments */
.two-column {
    display: flex;
    flex-wrap: wrap;
    gap: 30px;
    min-height: auto !important;
}

.column {
    flex: 1 1 45%;
    min-width: 500px;
    height: auto !important;
}

/* Cards expand naturally */
.card {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    margin-bottom: 20px;
}

/* Tables can be full height */
.comparison-table {
    max-height: none !important;
    overflow: visible !important;
}

/* Code blocks can expand */
.code-block,
pre {
    max-height: none !important;
    overflow-x: auto;
    overflow-y: visible;
}

/* Feature lists flow naturally */
.feature-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    height: auto !important;
}

/* Ensure backgrounds extend */
.bg-pattern,
.bg-gradient,
.bg-gradient-2 {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100% !important;
    min-height: 720px;
}

/* Progress bar adjustments */
.progress-bar {
    position: fixed !important;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4px;
    z-index: 999;
}

/* Smooth transitions */
.slide {
    transition: opacity 0.5s ease;
}

/* Handle very tall slides */
@media screen and (max-height: 900px) {
    .slide {
        padding-top: 30px;
        padding-bottom: 30px;
    }
}

/* Print-friendly */
@media print {
    .slide {
        page-break-after: always;
        height: auto !important;
        min-height: 0 !important;
    }

    .navigation {
        display: none;
    }
}

/* Scroll indicator for current position */
.scroll-progress {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: rgba(255, 255, 255, 0.1);
    z-index: 1000;
}

.scroll-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--secondary), var(--accent));
    width: 0%;
    transition: width 0.2s ease;
}

/* Vertical scroll indicator */
.scroll-indicator {
    position: fixed;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 150px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    z-index: 100;
}

.scroll-indicator-thumb {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 30px;
    background: rgba(87, 197, 182, 0.8);
    border-radius: 2px;
    transition: transform 0.2s ease;
}

/* Scroll hint for tall slides */
.scroll-hint {
    position: fixed;
    bottom: 60px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    z-index: 500;
    animation: bounce 2s infinite;
    display: none;
}

.scroll-hint.visible {
    display: block;
}

@keyframes bounce {
    0%, 100% { transform: translateX(-50%) translateY(0); }
    50% { transform: translateX(-50%) translateY(-10px); }
}

/* ========== END V5 DYNAMIC HEIGHT CSS ========== */
"""

        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)

        # Check if already present
        existing = soup.find(string=re.compile('LAYOUT FIXER V5'))
        if existing:
            return False

        # Add style tag
        style_tag = soup.new_tag('style')
        style_tag.string = dynamic_css

        # Insert after existing styles
        existing_styles = head.find_all('style')
        if existing_styles:
            existing_styles[-1].insert_after(style_tag)
        else:
            head.append(style_tag)

        return True

    def inject_adaptive_js(self, soup: BeautifulSoup) -> bool:
        """Inject JavaScript for dynamic height management."""

        adaptive_js = """
// ========== LAYOUT FIXER V5 - ADAPTIVE HEIGHT ==========
(function() {
    'use strict';

    console.log('Layout Fixer V5 - Dynamic Height initializing...');

    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const container = document.querySelector('.presentation-container');

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        setTimeout(initialize, 100);
    }

    function initialize() {
        console.log(`V5: Initializing ${slides.length} dynamic height slides`);

        // Process slides
        slides.forEach((slide, index) => {
            // Ensure slide is properly configured
            slide.classList.add('dynamic-height');

            // Calculate natural height
            if (slide.classList.contains('active')) {
                adjustContainerHeight(slide);
            }
        });

        // Override or enhance existing navigation
        enhanceNavigation();

        // Add scroll progress indicator
        addScrollIndicator();

        // Handle window resize
        window.addEventListener('resize', () => {
            const activeSlide = document.querySelector('.slide.active');
            if (activeSlide) {
                adjustContainerHeight(activeSlide);
            }
        });

        console.log('V5: Dynamic height system ready');
    }

    function adjustContainerHeight(slide) {
        // Let the slide determine its natural height
        slide.style.display = 'block';
        slide.style.height = 'auto';

        // Get the actual content height
        const contentHeight = slide.scrollHeight;
        const minHeight = 720;

        const finalHeight = Math.max(contentHeight, minHeight);

        console.log(`V5: Slide ${slide.id} height: ${contentHeight}px (final: ${finalHeight}px)`);

        // If content is taller than viewport, allow scrolling
        if (finalHeight > window.innerHeight) {
            document.body.style.overflow = 'auto';
        } else {
            document.body.style.overflow = 'hidden';
        }
    }

    function enhanceNavigation() {
        // Find existing navigation functions
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (window.showSlide) {
            // Wrap the existing showSlide function
            const originalShowSlide = window.showSlide;
            window.showSlide = function(index) {
                // Call original
                originalShowSlide(index);

                // Then adjust height and scroll to slide
                setTimeout(() => {
                    const activeSlide = document.querySelector('.slide.active');
                    if (activeSlide) {
                        adjustContainerHeight(activeSlide);
                        // Smooth scroll to top of the slide
                        const slideTop = activeSlide.offsetTop;
                        window.scrollTo({
                            top: slideTop,
                            behavior: 'smooth'
                        });
                    }
                }, 50);
            };
        }

        // Auto-advance when scrolling past slide bottom
        let scrollTimer;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                const activeSlide = document.querySelector('.slide.active');
                if (!activeSlide) return;

                const slideBottom = activeSlide.offsetTop + activeSlide.offsetHeight;
                const scrollBottom = window.scrollY + window.innerHeight;

                // If we've scrolled past the slide and there's a next slide
                if (scrollBottom >= slideBottom + 50) {
                    const currentIndex = Array.from(slides).indexOf(activeSlide);
                    if (currentIndex < slides.length - 1 && window.nextSlide) {
                        console.log('Auto-advancing to next slide');
                        window.nextSlide();
                    }
                }
            }, 100);
        });

        // Add keyboard shortcuts for scrolling within tall slides
        document.addEventListener('keydown', function(e) {
            const activeSlide = document.querySelector('.slide.active');
            if (!activeSlide) return;

            // Space or Page Down - scroll down
            if (e.key === ' ' || e.key === 'PageDown') {
                if (window.innerHeight + window.scrollY < document.body.scrollHeight - 10) {
                    e.preventDefault();
                    window.scrollBy({ top: window.innerHeight * 0.8, behavior: 'smooth' });
                }
            }
            // Shift+Space or Page Up - scroll up
            else if ((e.shiftKey && e.key === ' ') || e.key === 'PageUp') {
                if (window.scrollY > 0) {
                    e.preventDefault();
                    window.scrollBy({ top: -window.innerHeight * 0.8, behavior: 'smooth' });
                }
            }
            // Home - go to top of slide
            else if (e.key === 'Home') {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
            // End - go to bottom of slide
            else if (e.key === 'End') {
                e.preventDefault();
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }
        });
    }

    function addScrollIndicator() {
        // Create horizontal progress bar
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        progressBar.innerHTML = '<div class="scroll-progress-bar"></div>';
        document.body.appendChild(progressBar);

        // Create vertical scroll indicator
        const indicator = document.createElement('div');
        indicator.className = 'scroll-indicator';
        indicator.innerHTML = '<div class="scroll-indicator-thumb"></div>';
        indicator.style.display = 'none';
        document.body.appendChild(indicator);

        // Create scroll hint
        const hint = document.createElement('div');
        hint.className = 'scroll-hint';
        hint.textContent = '↓ Scroll for more content ↓';
        document.body.appendChild(hint);

        // Update indicators on scroll
        window.addEventListener('scroll', () => {
            const activeSlide = document.querySelector('.slide.active');
            if (!activeSlide) return;

            // Calculate slide-relative scroll position
            const slideTop = activeSlide.offsetTop;
            const slideHeight = activeSlide.offsetHeight;
            const slideBottom = slideTop + slideHeight;
            const viewportTop = window.scrollY;
            const viewportBottom = viewportTop + window.innerHeight;

            // Update progress bar
            const slideScrollProgress = Math.max(0, Math.min(100,
                ((viewportTop - slideTop) / (slideHeight - window.innerHeight)) * 100
            ));
            progressBar.querySelector('.scroll-progress-bar').style.width = slideScrollProgress + '%';

            // Update vertical indicator
            if (slideHeight > window.innerHeight) {
                indicator.style.display = 'block';
                const thumbPosition = (slideScrollProgress / 100) * 120; // 120px travel
                indicator.querySelector('.scroll-indicator-thumb').style.transform =
                    `translateY(${thumbPosition}px)`;

                // Show/hide scroll hint
                if (viewportBottom < slideBottom - 100) {
                    hint.classList.add('visible');
                } else {
                    hint.classList.remove('visible');
                }
            } else {
                indicator.style.display = 'none';
                hint.classList.remove('visible');
            }
        });

        // Initial check
        setTimeout(() => {
            const activeSlide = document.querySelector('.slide.active');
            if (activeSlide && activeSlide.offsetHeight > window.innerHeight) {
                hint.classList.add('visible');
            }
        }, 500);
    }

    // Handle MathJax rendering
    if (window.MathJax && window.MathJax.startup) {
        window.MathJax.startup.promise.then(() => {
            console.log('V5: Adjusting for MathJax content');
            const activeSlide = document.querySelector('.slide.active');
            if (activeSlide) {
                setTimeout(() => adjustContainerHeight(activeSlide), 100);
            }
        });
    }

    // Handle image loading
    document.querySelectorAll('img').forEach(img => {
        if (!img.complete) {
            img.addEventListener('load', function() {
                const slide = this.closest('.slide');
                if (slide && slide.classList.contains('active')) {
                    adjustContainerHeight(slide);
                }
            });
        }
    });

})();
// ========== END V5 ADAPTIVE HEIGHT ==========
"""

        body = soup.find('body')
        if not body:
            return False

        # Check if already present
        existing = soup.find(string=re.compile('LAYOUT FIXER V5'))
        if existing:
            return False

        # Add script tag
        script_tag = soup.new_tag('script')
        script_tag.string = adaptive_js
        body.append(script_tag)

        return True


def process_file(input_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict]:
    """Process HTML file with V5 dynamic height approach."""

    logger.info(f"Processing: {input_path}")

    # Read HTML
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Count slides
    slide_count = html_content.count('class="slide"')
    logger.info(f"Found {slide_count} slides")

    # Process with V5
    fixer = LayoutFixerV5()
    fixed_html, fixes_log = fixer.process_html(html_content)

    # Output path
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_fixed_v5{input_path_obj.suffix}"

    # Write fixed HTML
    logger.info(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_html)

    # Create report
    report = {
        'input_file': input_path,
        'output_file': str(output_path),
        'slide_count': slide_count,
        'fixes_applied': fixes_log,
        'approach': 'Dynamic height - slides expand to fit content',
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
        description='Layout Fixer V5 - Dynamic height approach'
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
        print("LAYOUT FIXER V5 - DYNAMIC HEIGHT COMPLETE")
        print("="*60)
        print(f"Input:  {args.input}")
        print(f"Output: {output_path}")
        print(f"Slides: {report['slide_count']}")

        print(f"\nApproach: {report['approach']}")

        print(f"\nFixes applied: {len(report['fixes_applied'])}")
        for fix in report['fixes_applied']:
            print(f"  ✓ {fix['description']}")

        print(f"\nFile size change: {report['file_size']['difference']:+,} bytes")

        print("\n✅ Success! The fixed HTML now uses dynamic height:")
        print("   • Slides expand to fit all content")
        print("   • No content cutoff")
        print("   • Width remains fixed at 1280px")
        print("   • Smooth navigation between slides")
        print("\nTips:")
        print("   • Use Space/PageDown to scroll within tall slides")
        print("   • Arrow keys still navigate between slides")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())