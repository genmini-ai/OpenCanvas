# Prompts Registry
Updated: 2025-08-17

**Long-term memory for prompt evolution. Tracks successful and failed prompt modifications across evolution runs.**

## Successful Prompt Edits

```yaml
name: anti_hallucination_rules
improvement: 2.0
dimension: content_reference_required
edit_type: add_section
change: "Added CRITICAL_ACCURACY_REQUIREMENTS section that overrides all other instructions"
specific_text: "NEVER add numerical data, statistics, or percentages not explicitly stated in the source"
lesson: "Explicit prohibition more effective than positive guidance for preventing fabrication"
```

```yaml
name: opacity_transition_fix
improvement: 0.75
dimension: visual
edit_type: replace
change: "Replace vague transition method with specific opacity-only approach"
old_text: "using ONE consistent method (opacity OR transform)"
new_text: "using ONLY opacity-based methods (opacity: 0 to opacity: 1)"
lesson: "Specific technical parameters eliminate ambiguity and bugs"
```

```yaml
name: grid_system_specification
improvement: 0.5
dimension: visual
edit_type: enhance_specificity
change: "Add concrete column numbers to grid system requirement"
old_text: "follow a visual grid system"
new_text: "follow a visual grid system (6 or 12 column)"
lesson: "Concrete specifications improve layout consistency"
```

```yaml
name: no_fabrication_constraint
improvement: 1.5
dimension: content_reference_required
edit_type: add_rule
change: "Add explicit constraint against inventing percentages"
specific_text: "If source says 'improved' or 'increased' without numbers, DO NOT invent percentages"
lesson: "Must explicitly handle common hallucination triggers"
```

```yaml
name: glass_effect_parameters
improvement: 0.3
dimension: visual
edit_type: add_technical_spec
change: "Specify exact blur value for frosted glass effect"
specific_text: "backdrop-filter: blur(8px)"
lesson: "Exact CSS values create consistent visual effects"
```

```yaml
name: content_verification_checklist
improvement: 1.0
dimension: content_reference_required
edit_type: add_section
change: "Add 8-point verification checklist before finalizing slides"
specific_text: "All numerical data comes directly from source (no invented statistics)"
lesson: "Checklists enforce systematic validation"
```

```yaml
name: variable_opacity_hierarchy
improvement: 0.4
dimension: visual
edit_type: add_specification
change: "Define specific opacity levels for visual hierarchy"
specific_text: "Use variable opacity levels (20%, 40%, 60%, 80%, 100%)"
lesson: "Predefined opacity scale creates consistent depth"
```

## Failed Prompt Edits

```yaml
name: visual_requirement_overload
improvement: -0.66
dimension: all
edit_type: excessive_addition
change: "Added 30+ visual requirements in single prompt"
problem: "Too many requirements caused confusion and competing instructions"
lesson: "Keep visual requirements under 20 items to maintain coherence"
```

```yaml
name: vague_quality_descriptors
improvement: -0.2
dimension: all
edit_type: add_subjective
change: "Added subjective quality terms without criteria"
problem_text: "Make it stunning and professional"
lesson: "Vague terms interpreted inconsistently; always define specific criteria"
```

```yaml
name: missing_hallucination_prevention
improvement: -2.5
dimension: content_reference_required
edit_type: omission
change: "No explicit anti-fabrication rules in baseline"
problem: "LLM invented statistics like '60% Faster Diagnosis', '19 Species Monitored'"
lesson: "Anti-hallucination rules must be in base prompt, not evolved later"
```

```yaml
name: competing_animation_systems
improvement: -0.4
dimension: visual
edit_type: conflicting_addition
change: "Multiple animation approaches without clear priority"
problem: "Physics-based animations conflicted with CSS transitions"
lesson: "Choose single animation approach and stick to it"
```

```yaml
name: reorganization_freedom
improvement: -0.5
dimension: content_reference_required
edit_type: missing_constraint
change: "No requirement to preserve source structure"
problem: "Examples elevated to main categories, changing meaning"
lesson: "Must explicitly require preservation of source hierarchy"
```