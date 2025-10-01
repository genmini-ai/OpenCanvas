"""
Visual Adversarial Attack Prompts for Claude

This module contains prompts for Claude to generate adversarial attacks
on presentation HTML files to test visual evaluation robustness.
"""

VISUAL_ATTACK_PROMPTS = {
    "font_gigantism": {
        "name": "Font Gigantism Attack",
        "description": "Makes fonts excessively large to break layouts",
        "prompt": """You are modifying an HTML presentation to test evaluation systems.

TASK: Apply EXTREME font size increases to this presentation:

REQUIREMENTS:
1. Make ALL title fonts 6rem or larger (currently they are likely 2-3rem)
2. Make ALL body text 3rem or larger (currently likely 1-1.2rem)
3. Make ALL caption/small text at least 2rem
4. The goal is to make text SO LARGE it breaks the visual layout
5. Keep all content exactly the same - only change font sizes
6. Update both inline styles and any <style> blocks

IMPORTANT: 
- This is intentionally making the design WORSE to test if evaluators can detect oversized fonts
- The slides should look broken and unprofessional after this modification
- Font sizes should be obviously too large for good design

Return the complete modified HTML."""
    },
    
    "color_chaos": {
        "name": "Color Chaos Attack",
        "description": "Adds excessive colors to create visual chaos",
        "prompt": """You are modifying an HTML presentation to test evaluation systems.

TASK: Create color chaos by adding MANY different colors:

REQUIREMENTS:
1. Use at least 8 different bright, contrasting colors throughout
2. Include these specific colors: pure red (#FF0000), pure green (#00FF00), pure blue (#0000FF), 
   bright yellow (#FFFF00), hot pink (#FF00FF), bright orange (#FFA500), purple (#800080), cyan (#00FFFF)
3. Apply different colors to:
   - Each slide's headings (different color per slide)
   - Different bullet points (alternate colors)
   - Background colors (use contrasting bright backgrounds)
   - Text colors (ensure they clash with backgrounds)
4. Create a "rainbow vomit" effect - intentionally garish
5. Keep all content the same - only change colors

IMPORTANT:
- This should look absolutely terrible and unprofessional
- The goal is maximum visual chaos through color
- Like a child got hold of all the crayons at once

Return the complete modified HTML."""
    },
    
    "information_overload": {
        "name": "Information Overload Attack", 
        "description": "Adds excessive text to overwhelm viewers",
        "prompt": """You are modifying an HTML presentation to test evaluation systems.

TASK: Create information overload by adding excessive text:

REQUIREMENTS:
1. Expand every slide to have 200+ words minimum
2. Convert simple points into verbose paragraphs
3. Add 15+ bullet points per slide where possible
4. Include unnecessary details, examples, and elaborations
5. Remove most white space - fill every available area with text
6. Make slides feel cramped and overwhelming
7. Keep the core message but bury it in excessive detail

EXAMPLE TRANSFORMATION:
- Before: "Solar power is cost-effective"
- After: "Solar power, which harnesses the radiant energy emitted by our sun through sophisticated photovoltaic cells made primarily of silicon-based semiconductors, has demonstrated remarkable cost-effectiveness across numerous implementations in various geographical regions, with studies showing decreasing costs per kilowatt-hour when analyzed over multi-decade timeframes, particularly when considering government subsidies, tax incentives, and the long-term environmental benefits that translate into reduced healthcare costs and improved agricultural yields in regions previously affected by fossil fuel pollution."

IMPORTANT:
- Make readers feel exhausted just looking at the slides
- The opposite of "less is more" - this is "more is overwhelming"
- Academic paper density on presentation slides

Return the complete modified HTML."""
    },
    
    "decoration_disaster": {
        "name": "Decoration Disaster Attack",
        "description": "Adds excessive visual decorations and effects",
        "prompt": """You are modifying an HTML presentation to test evaluation systems.

TASK: Add EXCESSIVE decorative elements and visual effects:

REQUIREMENTS:
1. Add multiple drop shadows to EVERY text element:
   - text-shadow: 2px 2px 4px red, -2px -2px 4px blue, 0px 0px 10px yellow;
2. Add thick borders to everything:
   - Every div: border: 5px solid with different colors
   - Every paragraph: border: 3px dashed
   - Every list item: border: 2px dotted
3. Add gradient backgrounds to all elements:
   - Use loud gradients like: linear-gradient(45deg, red, yellow, green, blue)
4. Add excessive margins and padding creating weird spacing
5. Add transform effects:
   - Rotate some text elements: transform: rotate(5deg)
   - Skew others: transform: skew(10deg)
6. Add glowing effects: box-shadow with multiple colors
7. Use different background patterns/textures if possible

IMPORTANT:
- This should look like someone discovered CSS effects for the first time
- Every possible decoration should be applied excessively
- The content should be hard to read due to visual noise
- "MySpace 2005" aesthetic - everything that can be decorated IS decorated

Return the complete modified HTML."""
    },
    
    "hierarchy_anarchy": {
        "name": "Hierarchy Anarchy Attack",
        "description": "Destroys visual hierarchy completely",
        "prompt": """You are modifying an HTML presentation to test evaluation systems.

TASK: Completely destroy the visual hierarchy:

REQUIREMENTS:
1. Make ALL text the same size (pick 1.5rem for everything)
2. Make EVERYTHING bold - every single piece of text
3. Randomly apply ALL CAPS to 50% of sentences/bullets
4. Remove any size-based emphasis:
   - Titles same size as body text
   - Subtitles same size as content
   - All bullets same size
5. Apply identical styling to all elements:
   - Same font weight (bold)
   - Same font family
   - Same line height
6. Add random emphasis that makes no sense:
   - Italicize random words in middle of sentences
   - Underline random phrases
   - CAPS in random places like "The solar PANELS are very EFFECTIVE in generating POWER"

IMPORTANT:
- There should be NO visual hierarchy at all
- Viewers shouldn't be able to distinguish headers from content
- Everything should compete for attention equally
- Like someone hit "SELECT ALL" then "BOLD" and called it done

Return the complete modified HTML."""
    },
    
    "white_space_elimination": {
        "name": "White Space Elimination Attack",
        "description": "Removes all white space and breathing room",
        "prompt": """You are modifying an HTML presentation to test evaluation systems.

TASK: Eliminate ALL white space and breathing room:

REQUIREMENTS:
1. Set all margins to 0 or minimal (2px max)
2. Set all padding to 0 or minimal (2px max)
3. Reduce line-height to 1.0 (text lines touching)
4. Remove any spacer divs or empty paragraphs
5. Pack elements as tightly as possible
6. Set letter-spacing to -1px (letters cramped)
7. Make slides feel claustrophobic
8. Fill any empty areas with additional content or expand existing content

CSS TO APPLY:
* { margin: 0 !important; padding: 2px !important; }
p, li, div { line-height: 1.0 !important; letter-spacing: -1px !important; }
h1, h2, h3 { margin: 2px 0 !important; }

IMPORTANT:
- The slides should feel suffocating with no room to breathe
- Text should be uncomfortably close together
- Zero elegance, maximum density
- Like trying to fit a novel on a postcard

Return the complete modified HTML."""
    }
}

def get_attack_prompt(attack_type: str) -> dict:
    """Get a specific attack prompt by type"""
    if attack_type not in VISUAL_ATTACK_PROMPTS:
        raise ValueError(f"Unknown attack type: {attack_type}. Available: {list(VISUAL_ATTACK_PROMPTS.keys())}")
    return VISUAL_ATTACK_PROMPTS[attack_type]

def get_all_attack_types() -> list:
    """Get list of all available attack types"""
    return list(VISUAL_ATTACK_PROMPTS.keys())

def get_attack_description(attack_type: str) -> str:
    """Get human-readable description of an attack"""
    attack = get_attack_prompt(attack_type)
    return f"{attack['name']}: {attack['description']}"