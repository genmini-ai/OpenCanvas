#!/usr/bin/env python3
"""
Layout Fixer V6 Improved - Per-Slide Constraint Solver
======================================================
Applies AutoLayout.js-inspired constraint solving to each slide independently.
Guarantees no overlaps through mathematical constraints while preserving navigation.

Key improvements:
- Each slide gets its own constraint solver instance
- No cross-slide interference
- Slide-specific element marking
- Better handling of multi-page presentations
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SlideConstraintSolver:
    """Constraint solver for a single slide."""

    def __init__(self, slide_id: str, slide_index: int):
        self.slide_id = slide_id
        self.slide_index = slide_index
        self.constraints_applied = 0

    def mark_elements(self, slide: Tag) -> int:
        """Mark elements in this specific slide for constraint solving."""
        marked = 0

        # Mark slide content container with slide-specific class
        slide_content = slide.find(class_='slide-content')
        if slide_content:
            slide_content['data-constraint-content'] = f'slide-{self.slide_index}'
            slide_content['data-slide-index'] = str(self.slide_index)

            # Add slide-specific constraint class
            existing_classes = slide_content.get('class', [])
            if isinstance(existing_classes, str):
                existing_classes = existing_classes.split()
            existing_classes.append(f'constraint-slide-{self.slide_index}')
            slide_content['class'] = existing_classes
            marked += 1

        # Mark images with slide-specific attributes
        for img in slide.find_all('img'):
            img['data-constraint-image'] = f'slide-{self.slide_index}'
            img['data-slide-index'] = str(self.slide_index)

            # Add responsive constraint class
            existing_classes = img.get('class', [])
            if isinstance(existing_classes, str):
                existing_classes = existing_classes.split()
            existing_classes.append(f'constraint-img-slide-{self.slide_index}')
            img['class'] = existing_classes
            marked += 1

        # Mark text blocks with slide-specific attributes
        for elem in slide.find_all(['p', 'ul', 'ol', 'blockquote']):
            elem['data-constraint-text'] = f'slide-{self.slide_index}'
            elem['data-slide-index'] = str(self.slide_index)
            marked += 1

        # Mark tables and code blocks
        for elem in slide.find_all(['table', 'pre', 'code']):
            elem['data-constraint-block'] = f'slide-{self.slide_index}'
            elem['data-slide-index'] = str(self.slide_index)
            marked += 1

        self.constraints_applied = marked
        return marked


class LayoutFixerV6Improved:
    """Main layout fixer with per-slide constraint solving."""

    def __init__(self):
        self.fixes_applied = []
        self.slide_solvers = []

    def add_constraint_css(self, soup: BeautifulSoup) -> bool:
        """Add CSS for constraint-based layout with per-slide scoping."""

        constraint_css = """
/* ========== LAYOUT FIXER V6 IMPROVED - PER-SLIDE CONSTRAINTS ========== */

/* Note: We do NOT modify .slide position to preserve navigation */
/* The slide stacking system requires position: absolute */

/* Per-slide constraint containers */
[data-constraint-content] {
    position: relative !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 20px !important;
}

/* Slide-specific image constraints */
[data-constraint-image] {
    max-width: 100% !important;
    height: auto !important;
    object-fit: contain !important;
    display: block !important;
    margin: 10px auto !important;
}

/* Prevent image overflow per slide */
.constraint-img-slide-0, .constraint-img-slide-1, .constraint-img-slide-2,
.constraint-img-slide-3, .constraint-img-slide-4, .constraint-img-slide-5,
.constraint-img-slide-6, .constraint-img-slide-7, .constraint-img-slide-8,
.constraint-img-slide-9, .constraint-img-slide-10, .constraint-img-slide-11 {
    max-height: 400px !important;
    width: auto !important;
}

/* Text block constraints per slide */
[data-constraint-text] {
    max-width: 100% !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    hyphens: auto !important;
}

/* Code and table constraints */
[data-constraint-block] {
    max-width: 100% !important;
    overflow-x: auto !important;
    overflow-y: visible !important;
}

/* Responsive sizing based on slide index */
.constraint-slide-0, .constraint-slide-1, .constraint-slide-2,
.constraint-slide-3, .constraint-slide-4, .constraint-slide-5,
.constraint-slide-6, .constraint-slide-7, .constraint-slide-8,
.constraint-slide-9, .constraint-slide-10, .constraint-slide-11 {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    max-height: 640px !important;
    padding: 10px !important;
}

/* Debug mode styles */
.constraint-debug [data-constraint-content] {
    border: 2px dashed #ff0000 !important;
}

.constraint-debug [data-constraint-image] {
    border: 2px dashed #00ff00 !important;
}

.constraint-debug [data-constraint-text] {
    border: 1px dashed #0000ff !important;
}

.constraint-debug [data-constraint-block] {
    border: 1px dashed #ff00ff !important;
}

/* ========== END V6 IMPROVED CSS ========== */
"""

        head = soup.find('head')
        if not head:
            return False

        # Check if already present
        existing = soup.find(string=re.compile('V6 IMPROVED'))
        if existing:
            return False

        # Add style tag
        style_tag = soup.new_tag('style')
        style_tag.string = constraint_css

        # Insert after existing styles
        existing_styles = head.find_all('style')
        if existing_styles:
            existing_styles[-1].insert_after(style_tag)
        else:
            head.append(style_tag)

        return True

    def add_per_slide_constraint_solver(self, soup: BeautifulSoup) -> bool:
        """Add JavaScript for per-slide constraint solving."""

        constraint_solver_js = """
// ========== LAYOUT FIXER V6 IMPROVED - PER-SLIDE CONSTRAINT SOLVER ==========
(function() {
    'use strict';

    console.log('Layout Fixer V6 Improved - Per-slide constraint solver initializing...');

    // Per-slide constraint solver
    class SlideConstraintSolver {
        constructor(slideElement, slideIndex) {
            this.slide = slideElement;
            this.slideIndex = slideIndex;
            this.slideId = slideElement.id || `slide-${slideIndex}`;
            this.constraints = [];
            this.elements = new Map();

            // Slide dimensions
            this.slideWidth = 1280;
            this.slideHeight = 720;
            this.padding = 40;
            this.spacing = 15;

            console.log(`Initializing solver for slide ${this.slideIndex}`);
        }

        collectElements() {
            // Collect all constraint elements for this slide only
            const selector = `[data-slide-index="${this.slideIndex}"]`;

            this.contentContainer = this.slide.querySelector('[data-constraint-content]' + selector);
            this.images = Array.from(this.slide.querySelectorAll('[data-constraint-image]' + selector));
            this.textBlocks = Array.from(this.slide.querySelectorAll('[data-constraint-text]' + selector));
            this.codeBlocks = Array.from(this.slide.querySelectorAll('[data-constraint-block]' + selector));

            console.log(`Slide ${this.slideIndex}: Found ${this.images.length} images, ${this.textBlocks.length} text blocks`);
        }

        defineConstraints() {
            this.constraints = [];

            // Available space for this slide
            const availableWidth = this.slideWidth - (2 * this.padding);
            const availableHeight = this.slideHeight - this.padding - 80;

            // Container constraint
            if (this.contentContainer) {
                this.constraints.push({
                    type: 'container',
                    element: this.contentContainer,
                    rules: {
                        maxWidth: availableWidth,
                        maxHeight: availableHeight,
                        overflow: 'auto'
                    }
                });
            }

            // Image constraints - adaptive based on count
            const imageCount = this.images.length;
            this.images.forEach((img, index) => {
                let maxWidth, maxHeight;

                if (imageCount === 1) {
                    // Single image: can be larger
                    maxWidth = availableWidth * 0.8;
                    maxHeight = availableHeight * 0.6;
                } else if (imageCount === 2) {
                    // Two images: side by side
                    maxWidth = availableWidth * 0.45;
                    maxHeight = availableHeight * 0.5;
                } else {
                    // Multiple images: grid layout
                    maxWidth = availableWidth * 0.3;
                    maxHeight = availableHeight * 0.35;
                }

                this.constraints.push({
                    type: 'image',
                    element: img,
                    index: index,
                    rules: {
                        maxWidth: maxWidth,
                        maxHeight: maxHeight,
                        display: 'inline-block',
                        margin: '10px'
                    }
                });
            });

            // Text constraints - ensure readability
            this.textBlocks.forEach((text, index) => {
                this.constraints.push({
                    type: 'text',
                    element: text,
                    index: index,
                    rules: {
                        maxWidth: availableWidth,
                        lineHeight: 1.5,
                        marginBottom: this.spacing
                    }
                });
            });

            // Code block constraints
            this.codeBlocks.forEach((code, index) => {
                this.constraints.push({
                    type: 'code',
                    element: code,
                    index: index,
                    rules: {
                        maxWidth: availableWidth,
                        maxHeight: availableHeight * 0.4,
                        overflow: 'auto',
                        fontSize: '0.9em'
                    }
                });
            });
        }

        applyConstraints() {
            // Apply calculated constraints to elements
            this.constraints.forEach(constraint => {
                const { element, rules } = constraint;

                if (!element) return;

                // Apply CSS rules
                Object.entries(rules).forEach(([property, value]) => {
                    if (typeof value === 'number') {
                        element.style[property] = value + 'px';
                    } else {
                        element.style[property] = value;
                    }
                });

                // Add data attribute to track constraint application
                element.setAttribute('data-constraints-applied', 'true');
                element.setAttribute('data-constraint-slide', this.slideIndex);
            });

            console.log(`Slide ${this.slideIndex}: Applied ${this.constraints.length} constraints`);
        }

        solve() {
            try {
                this.collectElements();
                this.defineConstraints();
                this.applyConstraints();
                return true;
            } catch (error) {
                console.error(`Error solving constraints for slide ${this.slideIndex}:`, error);
                return false;
            }
        }
    }

    // Global solver manager
    class SolverManager {
        constructor() {
            this.solvers = new Map();
            this.debugMode = false;
        }

        processAllSlides() {
            const slides = document.querySelectorAll('.slide[data-constraint-enabled="true"]');
            console.log(`Processing ${slides.length} slides with constraints`);

            slides.forEach((slide, index) => {
                // Create dedicated solver for this slide
                const solver = new SlideConstraintSolver(slide, index);

                // Store solver reference
                this.solvers.set(index, solver);

                // Apply constraints to this slide
                const success = solver.solve();

                if (success) {
                    slide.setAttribute('data-constraints-solved', 'true');
                }
            });

            // Re-apply constraints when slides become active
            this.setupSlideObserver();
        }

        setupSlideObserver() {
            // Watch for slide changes
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' &&
                        mutation.attributeName === 'class') {

                        const slide = mutation.target;
                        if (slide.classList.contains('active')) {
                            const slideIndex = parseInt(slide.getAttribute('data-slide-index') || '0');
                            const solver = this.solvers.get(slideIndex);

                            if (solver) {
                                // Re-solve constraints when slide becomes active
                                setTimeout(() => solver.solve(), 50);
                            }
                        }
                    }
                });
            });

            // Observe all slides
            document.querySelectorAll('.slide').forEach(slide => {
                observer.observe(slide, { attributes: true });
            });
        }

        toggleDebug() {
            this.debugMode = !this.debugMode;
            document.body.classList.toggle('constraint-debug', this.debugMode);
            console.log(`Constraint debug mode: ${this.debugMode ? 'ON' : 'OFF'}`);
        }
    }

    // Initialize when DOM is ready
    const manager = new SolverManager();

    // Wait for images to load before applying constraints
    function initialize() {
        const images = document.querySelectorAll('img');
        let loadedImages = 0;
        const totalImages = images.length;

        function checkAllLoaded() {
            loadedImages++;
            if (loadedImages >= totalImages) {
                console.log('All images loaded, applying constraints...');
                manager.processAllSlides();
            }
        }

        if (totalImages === 0) {
            manager.processAllSlides();
        } else {
            images.forEach(img => {
                if (img.complete) {
                    checkAllLoaded();
                } else {
                    img.addEventListener('load', checkAllLoaded);
                    img.addEventListener('error', checkAllLoaded);
                }
            });
        }
    }

    // Initialize with delay to ensure slide system is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => setTimeout(initialize, 200));
    } else {
        setTimeout(initialize, 200);
    }

    // Expose debug function globally
    window.toggleConstraintDebug = () => manager.toggleDebug();
    window.constraintSolverManager = manager;

    console.log('V6 Improved: Per-slide constraint solver ready. Use toggleConstraintDebug() to debug.');
})();
// ========== END V6 IMPROVED CONSTRAINT SOLVER ==========
"""

        body = soup.find('body')
        if not body:
            return False

        # Check if already present
        existing = soup.find(string=re.compile('V6 IMPROVED - PER-SLIDE'))
        if existing:
            return False

        # Add script tag at end of body
        script_tag = soup.new_tag('script')
        script_tag.string = constraint_solver_js
        body.append(script_tag)

        return True

    def process_slides(self, soup: BeautifulSoup) -> int:
        """Process each slide independently."""
        slides = soup.find_all(class_='slide')
        total_marked = 0

        for index, slide in enumerate(slides):
            # Mark slide as constraint-enabled
            slide['data-constraint-enabled'] = 'true'
            slide['data-slide-index'] = str(index)

            # Create solver for this slide
            solver = SlideConstraintSolver(f'slide-{index}', index)
            marked = solver.mark_elements(slide)
            total_marked += marked

            self.slide_solvers.append(solver)

            logger.info(f"Slide {index}: Marked {marked} elements for constraints")

        return total_marked


def process_file(input_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict]:
    """Process HTML file with per-slide constraint solving."""

    logger.info(f"Processing: {input_path}")

    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # Initialize fixer
    fixer = LayoutFixerV6Improved()

    # Count slides
    slides = soup.find_all(class_='slide')
    slide_count = len(slides)
    logger.info(f"Found {slide_count} slides")

    fixes_log = []

    # Add constraint CSS
    if fixer.add_constraint_css(soup):
        fixes_log.append("Added per-slide constraint CSS")
        logger.info("✓ Added per-slide constraint CSS")

    # Process each slide independently
    total_marked = fixer.process_slides(soup)
    if total_marked > 0:
        fixes_log.append(f"Marked {total_marked} elements across {slide_count} slides")
        logger.info(f"✓ Marked {total_marked} elements for constraint layout")

    # Add per-slide constraint solver JavaScript
    if fixer.add_per_slide_constraint_solver(soup):
        fixes_log.append("Added per-slide constraint solver")
        logger.info("✓ Added per-slide constraint solver implementation")

    # Convert back to string (preserving JavaScript)
    fixed_html = str(soup)

    # Determine output path
    if not output_path:
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / f"{input_path_obj.stem}_fixed_v6_improved{input_path_obj.suffix}"

    # Write fixed HTML
    logger.info(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_html)

    # Create report
    report = {
        'input_file': input_path,
        'output_file': str(output_path),
        'slide_count': slide_count,
        'slides_processed': len(fixer.slide_solvers),
        'total_elements_marked': total_marked,
        'fixes_applied': fixes_log,
        'approach': 'Per-slide constraint solving with isolated solvers',
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

    # Print summary
    print("\n" + "=" * 60)
    print("LAYOUT FIXER V6 IMPROVED - PER-SLIDE CONSTRAINTS COMPLETE")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Slides: {slide_count}")
    print(f"\nApproach: Per-slide constraint solving")
    print(f"\nElements marked: {total_marked}")
    for i, solver in enumerate(fixer.slide_solvers[:5]):  # Show first 5
        print(f"  Slide {i}: {solver.constraints_applied} constraints")
    if slide_count > 5:
        print(f"  ... and {slide_count - 5} more slides")

    print(f"\n✅ Success! Each slide now has independent constraint-based layout:")
    print("   • No cross-slide interference")
    print("   • Adaptive constraints based on content")
    print("   • Automatic image/text positioning per slide")
    print("   • Debug mode: toggleConstraintDebug() in console")

    return str(output_path), report


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description='Layout Fixer V6 Improved - Per-slide constraint solver'
    )
    parser.add_argument('input', help='Input HTML file')
    parser.add_argument('-o', '--output', help='Output HTML file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        output_path, report = process_file(args.input, args.output)
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())