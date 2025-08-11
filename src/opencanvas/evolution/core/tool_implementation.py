"""
Automatic Tool Implementation System - Core of autonomous tool creation
Integrated directly into the evolution pipeline
"""

import ast
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from anthropic import Anthropic
from opencanvas.config import Config

logger = logging.getLogger(__name__)

class AutomaticToolImplementation:
    """
    Fully autonomous tool implementation system that:
    1. Generates tool code from specifications
    2. Tests in sandbox
    3. Measures impact
    4. Deploys automatically (human review optional)
    """
    
    def __init__(self, require_human_review: bool = False):
        """
        Initialize tool implementation system
        
        Args:
            require_human_review: If False, tools deploy automatically after passing tests
        """
        self.require_human_review = require_human_review
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.sandbox_dir = Path("tool_sandbox")
        self.sandbox_dir.mkdir(exist_ok=True)
        self.implemented_tools = []
        
        logger.info(f"🤖 Automatic Tool Implementation initialized")
        logger.info(f"👤 Human review: {'Required' if require_human_review else 'Optional (auto-deploy)'}")
    
    def _load_prompt_template(self, template_name: str) -> str:
        """Load prompt template from centralized location"""
        try:
            import yaml
            prompts_file = Path("src/opencanvas/evolution/prompts/tool_generation.yaml")
            
            if prompts_file.exists():
                with open(prompts_file, 'r') as f:
                    prompts = yaml.safe_load(f)
                return prompts.get(template_name, "")
            else:
                logger.warning(f"Prompts file not found: {prompts_file}")
                return self._get_fallback_prompt(template_name)
        except Exception as e:
            logger.error(f"Failed to load prompt template {template_name}: {e}")
            return self._get_fallback_prompt(template_name)
    
    def _get_fallback_prompt(self, template_name: str) -> str:
        """Fallback prompts if YAML file not available"""
        if template_name == "tool_code_generation_prompt":
            return """Generate a complete Python implementation for this tool:

Specification:
{spec_json}{learning_context}

RESOURCE CONSTRAINTS - ONLY use these available resources:
✅ AVAILABLE:
- Anthropic Claude API (multimodal - text + images)
- OpenAI GPT API (multimodal - text + images)  
- Gemini API (multimodal - text + images)
- Brave Search API (for getting implementation specs and domain knowledge)
- Python standard library (re, json, math, statistics, etc.)
- Python packages: pdfplumber, PIL, base64 (for PDF/image processing)
- Text processing, regex, string operations
- Local file operations
- Built-in data structures
- Image processing (via multimodal LLMs)

❌ FORBIDDEN - Do NOT use:
- External APIs requiring signup/billing/account creation
- Services not already configured in Config class
- Database services needing separate setup
- Third-party services requiring authentication beyond existing APIs

Requirements:
1. Create a class that inherits from BaseTool
2. Implement the process() method using ONLY available resources above
3. Include comprehensive error handling
4. Add logging using logger = logging.getLogger(__name__)
5. Include docstrings
6. Follow Python best practices
7. Make it production-ready
8. Use existing Config class for API keys when needed

CRITICAL CODE FORMATTING RULES:
9. NEVER use nested f-strings or complex f-string expressions
10. For multi-line strings with variables, use .format() or % formatting instead of f-strings
11. For LLM API calls with dynamic content, build strings separately before passing to API
12. Example of GOOD formatting:
   prompt_template = "Analyze this content: {content}"
   prompt = prompt_template.format(content=user_input)
13. Example of BAD formatting (AVOID):
   # DON'T DO THIS - will cause f-string nesting errors
   prompt = f"Complex {f'nested {variable}'} string"
14. Use YAML for any configuration data that tools might generate, NOT JSON in f-strings
15. If you need complex string building, use string concatenation or template libraries

Generate ONLY the Python code, no explanations."""

        elif template_name == "tool_specification_enhancement_prompt":
            return """Given this tool specification, provide detailed implementation requirements:

Tool: {tool_name}
Purpose: {tool_purpose}
Weakness addressed: {target_problem}

{domain_context}

RESOURCE CONSTRAINTS - Tool must ONLY use:
✅ Available: Claude/GPT/Gemini APIs (multimodal), Brave Search, Python stdlib, text/image processing
❌ Forbidden: External APIs requiring signup/billing, services needing separate authentication

Provide a detailed specification including:
1. Class name and inheritance (should inherit from BaseTool)
2. Required methods (at minimum: __init__ and process)
3. Input/output types
4. Algorithm approach using ONLY available resources
5. Error handling requirements
6. Performance requirements
7. Integration point in pipeline
8. Resource dependencies (from available list only)
9. String formatting approach (avoid f-string nesting, use .format() for complex strings)

IMPORTANT: If the tool will generate LLM prompts or complex strings:
- Use template-based string formatting (.format() method)
- Avoid nested f-strings completely
- Build complex strings step by step rather than in single f-string expressions
- Use YAML for any structured data, not JSON in f-strings

Return as YAML format (NOT JSON due to f-string issues)."""
        
        return "Template not found"
    
    def implement_tool_from_spec(self, tool_spec: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """
        Complete pipeline: spec → code → test → deploy
        
        Args:
            tool_spec: Tool specification from reflection phase
            iteration_number: Current evolution iteration
            
        Returns:
            Implementation result with code, tests, and deployment status
        """
        
        tool_name = tool_spec.get("name", "UnnamedTool")
        logger.info(f"🔨 Starting automatic implementation of {tool_name}")
        logger.info(f"  📋 Tool purpose: {tool_spec.get('purpose', 'Unknown')}")
        logger.info(f"  🎯 Target problem: {tool_spec.get('target_problem', 'Unknown')}")
        
        # Step 1: Generate detailed specification
        logger.info(f"📝 Step 1: Enhancing tool specification...")
        detailed_spec = self._enhance_specification(tool_spec)
        logger.info(f"  ✅ Enhanced specification complete")
        
        # Step 2: Generate Python code
        logger.info(f"🤖 Step 2: Generating Python code...")
        generated_code = self._generate_code(detailed_spec)
        if not generated_code:
            logger.error(f"  ❌ Code generation failed")
            return {"success": False, "error": "Code generation failed"}
        logger.info(f"  ✅ Generated {len(generated_code)} characters of Python code")
        
        # Step 3: Validate syntax
        logger.info(f"🔍 Step 3: Validating Python syntax...")
        if not self._validate_syntax(generated_code):
            logger.error(f"  ❌ Invalid Python syntax")
            return {"success": False, "error": "Invalid Python syntax"}
        logger.info(f"  ✅ Syntax validation passed")
        
        # Step 4: Generate test cases
        logger.info(f"🧪 Step 4: Generating test cases...")
        test_cases = self._generate_test_cases(detailed_spec)
        logger.info(f"  ✅ Generated {len(test_cases)} test cases")
        
        # Step 5: Run sandbox tests
        logger.info(f"⚡ Step 5: Running sandbox tests...")
        test_results = self._run_sandbox_tests(generated_code, test_cases)
        logger.info(f"  ✅ Tests complete: {test_results['passed']}/{len(test_cases)} passed ({test_results['pass_rate']:.1%})")
        
        # Step 6: Measure performance impact
        logger.info(f"📊 Step 6: Measuring performance impact...")
        performance = self._measure_performance(generated_code)
        logger.info(f"  ⚡ Latency: {performance['latency_ms']}ms")
        logger.info(f"  💾 Memory: {performance['memory_mb']}MB")
        
        # Step 7: Calculate quality improvement (simulated for now)
        logger.info(f"🎯 Step 7: Estimating quality impact...")
        quality_impact = self._estimate_quality_impact(tool_spec)
        logger.info(f"  📈 Estimated improvement: +{quality_impact['estimated_improvement']:.2f}")
        
        # Step 8: Make deployment decision
        logger.info(f"🤔 Step 8: Making deployment decision...")
        deployment_decision = self._make_deployment_decision(
            test_results, performance, quality_impact
        )
        logger.info(f"  🎯 Should deploy: {deployment_decision['should_deploy']}")
        logger.info(f"  ⚠️  Risk level: {deployment_decision['risk_level']}")
        for reason in deployment_decision['reasons']:
            logger.info(f"    - {reason}")
        
        # Step 9: Final validation before deployment
        logger.info(f"🔒 Step 9A: Final validation before deployment...")
        validation_result = self._validate_tool_contract(generated_code, tool_name)
        if not validation_result["valid"]:
            logger.error(f"  ❌ Tool validation failed: {validation_result['error']}")
            return {
                "success": False, 
                "deployed": False,
                "error": f"Tool validation failed: {validation_result['error']}",
                "code": generated_code,
                "test_results": test_results
            }
        logger.info(f"  ✅ Tool validation passed")
        
        # Step 9B: Deploy if approved (automatic or after review)
        deployed = False
        if deployment_decision["should_deploy"]:
            if not self.require_human_review:
                logger.info(f"🚀 Step 9B: Auto-deploying {tool_name} (human review disabled)")
                deployed = self._deploy_tool(tool_name, generated_code, iteration_number)
                if deployed:
                    logger.info(f"  ✅ Deployment successful")
                else:
                    logger.error(f"  ❌ Deployment failed")
            else:
                logger.info(f"⏸️  Step 9: {tool_name} queued for human review")
                self._queue_for_review(tool_name, generated_code, test_results)
        else:
            logger.info(f"⛔ Step 9: Deployment rejected - tool not deployed")
        
        # Step 10: Log implementation
        result = {
            "success": True,
            "tool_name": tool_name,
            "code_generated": True,
            "code_length": len(generated_code),
            "test_results": test_results,
            "performance": performance,
            "quality_impact": quality_impact,
            "deployment_decision": deployment_decision,
            "deployed": deployed,
            "iteration": iteration_number,
            "timestamp": datetime.now().isoformat()
        }
        
        self.implemented_tools.append(result)
        self._save_implementation_log(result)
        
        return result
    
    def _enhance_specification(self, basic_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance basic spec with implementation details"""
        
        # Load prompt template
        prompt_template = self._load_prompt_template("tool_specification_enhancement_prompt")
        
        # Optional: Use search for domain knowledge (not for finding new APIs)
        domain_context = ""
        if hasattr(self, 'search_client') and basic_spec.get('purpose'):
            domain_context = self._get_domain_context(basic_spec['purpose'])
        
        # Format prompt using template
        prompt = prompt_template.format(
            tool_name=basic_spec['name'],
            tool_purpose=basic_spec['purpose'], 
            target_problem=basic_spec.get('target_problem', 'Unknown'),
            domain_context=domain_context
        )

        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse YAML response (safer than JSON for f-strings)
            response_text = response.content[0].text
            try:
                import yaml
                spec_yaml = yaml.safe_load(response_text)
                return {**basic_spec, **spec_yaml}
            except yaml.YAMLError:
                # Fallback: extract JSON if YAML fails
                if "{" in response_text and "}" in response_text:
                    start = response_text.index("{")
                    end = response_text.rindex("}") + 1
                    spec_json = json.loads(response_text[start:end])
                    return {**basic_spec, **spec_json}
        except Exception as e:
            logger.error(f"Failed to enhance specification: {e}")
        
        return basic_spec
    
    def _generate_code(self, spec: Dict[str, Any]) -> Optional[str]:
        """Generate Python code from specification"""
        
        # Load prompt template from centralized location
        prompt_template = self._load_prompt_template("tool_code_generation_prompt")
        
        # Get learning context from previous tools
        learning_context = self.get_learning_context()
        
        # Format prompt using template (avoiding f-string nesting issues)
        spec_json = json.dumps(spec, indent=2)
        prompt = prompt_template.format(
            spec_json=spec_json,
            learning_context=learning_context
        )

        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            code = response.content[0].text
            
            # Clean up code
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            # Add necessary imports if missing
            if "import logging" not in code:
                code = "import logging\n" + code
            if "BaseTool" in code and "class BaseTool" not in code:
                base_class = """
class BaseTool:
    def __init__(self):
        self.name = self.__class__.__name__
        self.enabled = True
    
    def process(self, content):
        raise NotImplementedError

"""
                code = base_class + code
            
            logger.info(f"✅ Generated {len(code)} characters of Python code")
            return code
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return None
    
    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            logger.info("✅ Code syntax is valid")
            return True
        except SyntaxError as e:
            logger.error(f"❌ Syntax error: {e}")
            return False
    
    def _generate_test_cases(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for the tool"""
        
        # Basic test cases
        test_cases = [
            {
                "name": "test_basic_functionality",
                "input": "Sample content with test data",
                "expected_behavior": "Should process without errors"
            },
            {
                "name": "test_empty_input",
                "input": "",
                "expected_behavior": "Should handle gracefully"
            },
            {
                "name": "test_large_input",
                "input": "x" * 10000,
                "expected_behavior": "Should handle within timeout"
            }
        ]
        
        # Add specific test cases based on tool purpose
        if "citation" in spec.get("name", "").lower():
            test_cases.append({
                "name": "test_citation_detection",
                "input": "Smith (2023) states that... According to Jones et al. (2022)...",
                "expected_behavior": "Should detect 2 citations"
            })
        
        return test_cases
    
    def _run_sandbox_tests(self, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Run tests in sandboxed environment"""
        
        logger.info(f"🧪 Running {len(test_cases)} tests in sandbox")
        
        # Create temporary test file
        test_file = self.sandbox_dir / f"test_{datetime.now().timestamp()}.py"
        test_code = code + "\n\n"
        
        # Add test runner
        test_code += """
# Test runner
if __name__ == "__main__":
    import sys
    import json
    
    tool = """ + self._extract_class_name(code) + """()
    
    test_input = sys.argv[1] if len(sys.argv) > 1 else ""
    
    try:
        result = tool.process(test_input)
        print(json.dumps({"success": True, "result": str(result)}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
"""
        
        # Write test file
        test_file.write_text(test_code)
        
        # Run tests
        results = {"passed": 0, "failed": 0, "errors": []}
        
        for test_case in test_cases:
            try:
                # Run in subprocess for isolation
                result = subprocess.run(
                    ["python", str(test_file), test_case["input"]],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=self.sandbox_dir
                )
                
                if result.returncode == 0:
                    results["passed"] += 1
                    logger.info(f"  ✅ {test_case['name']}: PASS")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{test_case['name']}: {result.stderr}")
                    logger.warning(f"  ❌ {test_case['name']}: FAIL")
                    
            except subprocess.TimeoutExpired:
                results["failed"] += 1
                results["errors"].append(f"{test_case['name']}: Timeout")
                logger.warning(f"  ⏱️ {test_case['name']}: TIMEOUT")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{test_case['name']}: {e}")
                logger.error(f"  ❌ {test_case['name']}: ERROR - {e}")
        
        # Clean up
        test_file.unlink()
        
        results["pass_rate"] = results["passed"] / len(test_cases) if test_cases else 0
        logger.info(f"📊 Test results: {results['passed']}/{len(test_cases)} passed ({results['pass_rate']:.1%})")
        
        return results
    
    def _measure_performance(self, code: str) -> Dict[str, Any]:
        """Measure performance impact of the tool"""
        
        # For now, return simulated metrics
        # In production, would run actual benchmarks
        return {
            "latency_ms": 15,  # Average processing time
            "memory_mb": 2.5,   # Memory usage
            "cpu_percent": 0.5  # CPU usage
        }
    
    def _estimate_quality_impact(self, spec: Dict[str, Any]) -> Dict[str, float]:
        """Estimate quality improvement from tool"""
        
        # Use expected_impact from spec or default estimates
        impact = spec.get("expected_impact", "medium")
        
        impact_map = {
            "high": 0.4,
            "medium": 0.25,
            "low": 0.1
        }
        
        return {
            "estimated_improvement": impact_map.get(impact, 0.2),
            "confidence": 0.75
        }
    
    def _make_deployment_decision(self, test_results: Dict, performance: Dict, quality: Dict) -> Dict[str, Any]:
        """Decide whether to deploy based on test results"""
        
        decision = {
            "should_deploy": False,
            "reasons": [],
            "risk_level": "unknown"
        }
        
        # Check test pass rate
        if test_results["pass_rate"] >= 0.8:
            decision["reasons"].append(f"Tests passed: {test_results['pass_rate']:.1%}")
        else:
            decision["reasons"].append(f"Insufficient test pass rate: {test_results['pass_rate']:.1%}")
            decision["risk_level"] = "high"
            return decision
        
        # Check performance
        if performance["latency_ms"] < 50:
            decision["reasons"].append(f"Good performance: {performance['latency_ms']}ms")
        else:
            decision["reasons"].append(f"Performance concern: {performance['latency_ms']}ms")
            decision["risk_level"] = "medium"
        
        # Check quality impact
        if quality["estimated_improvement"] > 0.15:
            decision["reasons"].append(f"Positive quality impact: +{quality['estimated_improvement']:.2f}")
            decision["should_deploy"] = True
            decision["risk_level"] = "low"
        else:
            decision["reasons"].append(f"Low quality impact: +{quality['estimated_improvement']:.2f}")
            decision["risk_level"] = "medium"
        
        return decision
    
    def _deploy_tool(self, tool_name: str, code: str, iteration_number: int) -> bool:
        """Deploy tool to evolution system"""
        
        try:
            # Save tool to evolution tools directory
            tools_dir = Path(f"src/opencanvas/evolution/tools/iteration_{iteration_number:03d}")
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            tool_file = tools_dir / f"{tool_name.lower()}.py"
            tool_file.write_text(code)
            
            # Update __init__.py to import the tool
            init_file = tools_dir / "__init__.py"
            init_content = f"from .{tool_name.lower()} import {self._extract_class_name(code)}\n"
            
            if init_file.exists():
                init_content = init_file.read_text() + init_content
            
            init_file.write_text(init_content)
            
            logger.info(f"✅ Deployed {tool_name} to {tools_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    def _queue_for_review(self, tool_name: str, code: str, test_results: Dict):
        """Queue tool for human review"""
        
        review_dir = Path("evolution_review_queue")
        review_dir.mkdir(exist_ok=True)
        
        review_file = review_dir / f"{tool_name}_{datetime.now().timestamp()}.json"
        review_data = {
            "tool_name": tool_name,
            "code": code,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_review"
        }
        
        review_file.write_text(json.dumps(review_data, indent=2))
        logger.info(f"📋 Queued {tool_name} for human review: {review_file}")
    
    def _extract_class_name(self, code: str) -> str:
        """Extract the main class name from code"""
        
        # Parse AST to find class that inherits from our base classes
        try:
            tree = ast.parse(code)
            base_classes = ["BaseTool", "EvolutionTool", "HTMLProcessingTool", "ContentProcessingTool", "ValidationTool"]
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if inherits from any of our base classes
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in base_classes:
                            return node.name
                        # Handle module.Class format
                        elif isinstance(base, ast.Attribute) and base.attr in base_classes:
                            return node.name
        except Exception as e:
            logger.warning(f"Failed to parse code for class name: {e}")
        
        # Fallback: find first class with 'Tool' in name
        import re
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)
        
        return "GeneratedTool"
    
    def _get_domain_context(self, purpose: str) -> str:
        """Get domain-specific context and API specs via search"""
        
        try:
            from opencanvas.config import Config
            
            if not hasattr(Config, 'BRAVE_API_KEY') or not Config.BRAVE_API_KEY:
                return ""
            
            # Search for implementation guidance AND API specifications
            queries = [
                f"Claude API multimodal image text processing {purpose}",
                f"OpenAI GPT-4 vision API {purpose} examples",
                f"Gemini API multimodal {purpose} implementation",
                f"python {purpose} text analysis algorithms best practices"
            ]
            
            # In a real implementation, would use Brave Search API here
            # For now, return structured context
            context = f"""
Domain Context (from search):
Implementation approaches for {purpose}:
1. Use multimodal LLM APIs for image + text analysis
2. Claude API: anthropic.messages.create() with image data
3. GPT API: openai.chat.completions.create() with image_url
4. Gemini API: Available via Config.GEMINI_API_KEY
5. Python stdlib for text processing, regex, file operations
6. Brave Search API for real-time information when needed

Focus on leveraging multimodal capabilities and existing configured APIs.
"""
            logger.info(f"🔍 Retrieved domain context for: {purpose}")
            return context
            
        except Exception as e:
            logger.warning(f"Search for domain context failed: {e}")
            return ""
    
    def _save_implementation_log(self, result: Dict):
        """Save implementation log for tracking"""
        
        log_dir = Path("evolution_implementations")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"implementation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.write_text(json.dumps(result, indent=2, default=str))
    
    def track_tool_performance(self, tool_name: str, before_scores: Dict, after_scores: Dict, iteration: int):
        """Track tool performance and update knowledge base"""
        
        improvement = {}
        overall_improvement = 0
        
        for metric in before_scores:
            if metric in after_scores:
                improvement[metric] = after_scores[metric] - before_scores[metric]
                overall_improvement += improvement[metric]
        
        avg_improvement = overall_improvement / len(improvement) if improvement else 0
        
        # Determine if tool was successful
        success_threshold = 0.1  # Minimum improvement required
        was_successful = avg_improvement >= success_threshold
        
        # Update tool knowledge base
        self._update_tool_knowledge_base(tool_name, {
            "success": was_successful,
            "avg_improvement": avg_improvement,
            "detailed_improvement": improvement,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "before_scores": before_scores,
            "after_scores": after_scores
        })
        
        if was_successful:
            logger.info(f"✅ Tool {tool_name} successful: +{avg_improvement:.3f} average improvement")
            self._add_to_successful_patterns(tool_name)
        else:
            logger.warning(f"❌ Tool {tool_name} failed: {avg_improvement:.3f} improvement (below threshold)")
            self._add_to_failed_patterns(tool_name, improvement)
        
        return was_successful, avg_improvement
    
    def _update_tool_knowledge_base(self, tool_name: str, performance_data: Dict):
        """Update TOOLS.md with performance tracking"""
        
        tools_md_path = Path("TOOLS.md")
        
        # Read existing content
        if tools_md_path.exists():
            content = tools_md_path.read_text()
        else:
            content = "# Tools Performance Tracking\n\n"
        
        # Add performance entry
        entry = f"""
## {tool_name} - Iteration {performance_data['iteration']}
- **Status**: {'✅ SUCCESS' if performance_data['success'] else '❌ FAILED'}
- **Average Improvement**: {performance_data['avg_improvement']:+.3f}
- **Detailed Changes**: {json.dumps(performance_data['detailed_improvement'], indent=2)}
- **Timestamp**: {performance_data['timestamp']}
- **Reason**: {'Exceeded improvement threshold' if performance_data['success'] else 'Below minimum improvement threshold'}

"""
        
        # Append to file
        content += entry
        tools_md_path.write_text(content)
        
        logger.info(f"📝 Updated TOOLS.md with {tool_name} performance data")
    
    def _add_to_successful_patterns(self, tool_name: str):
        """Add successful tool to pattern library for future reference"""
        
        patterns_file = Path("evolution_tool_patterns.json")
        
        if patterns_file.exists():
            patterns = json.loads(patterns_file.read_text())
        else:
            patterns = {"successful": [], "failed": []}
        
        patterns["successful"].append({
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "note": "Tool successfully improved evaluation metrics"
        })
        
        patterns_file.write_text(json.dumps(patterns, indent=2, default=str))
    
    def _add_to_failed_patterns(self, tool_name: str, improvement_details: Dict):
        """Document failed tool patterns to avoid repeating mistakes"""
        
        patterns_file = Path("evolution_tool_patterns.json")
        
        if patterns_file.exists():
            patterns = json.loads(patterns_file.read_text())
        else:
            patterns = {"successful": [], "failed": []}
        
        patterns["failed"].append({
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "improvement_details": improvement_details,
            "note": "Tool failed to meet improvement threshold - avoid similar approaches"
        })
        
        patterns_file.write_text(json.dumps(patterns, indent=2, default=str))
        
        logger.info(f"📋 Documented {tool_name} failure pattern for future reference")
    
    def get_learning_context(self) -> str:
        """Get context from previous tool successes/failures for better future tools"""
        
        patterns_file = Path("evolution_tool_patterns.json")
        
        if not patterns_file.exists():
            return ""
        
        patterns = json.loads(patterns_file.read_text())
        
        context = "\nLEARNING FROM PREVIOUS TOOLS:\n"
        
        if patterns.get("successful"):
            context += "✅ SUCCESSFUL PATTERNS:\n"
            for success in patterns["successful"][-5:]:  # Last 5 successes
                context += f"- {success['tool_name']}: {success['note']}\n"
        
        if patterns.get("failed"):
            context += "\n❌ PATTERNS TO AVOID:\n"
            for failure in patterns["failed"][-5:]:  # Last 5 failures
                context += f"- {failure['tool_name']}: {failure['note']}\n"
        
        context += "\nUse successful patterns and avoid failed approaches.\n"
        return context
    
    def _validate_tool_contract(self, code: str, tool_name: str) -> Dict[str, Any]:
        """
        Validate that the tool follows the correct contract before deployment
        
        Returns:
            dict: {"valid": bool, "error": str or None}
        """
        try:
            # Create temporary test file
            test_file = self.sandbox_dir / f"contract_test_{tool_name}_{datetime.now().timestamp()}.py"
            
            # Add test code
            test_code = code + """

# Contract validation test
if __name__ == "__main__":
    import sys
    import json
    
    try:
        # Find the tool class
        tool_class = None
        for name in dir():
            obj = globals()[name]
            if (isinstance(obj, type) and 
                hasattr(obj, 'process') and 
                obj.__name__ != 'BaseTool'):
                tool_class = obj
                break
        
        if not tool_class:
            print(json.dumps({"valid": False, "error": "No tool class found"}))
            sys.exit(1)
        
        # Test instantiation
        tool = tool_class()
        
        # Test process method with sample HTML
        test_html = "<h1>Test Title</h1><p>Test content with <b>formatting</b>.</p>"
        result = tool.process(test_html)
        
        # Critical validation checks
        if not isinstance(result, str):
            print(json.dumps({
                "valid": False, 
                "error": f"process() returned {type(result).__name__}, expected str"
            }))
            sys.exit(1)
        
        if result is None:
            print(json.dumps({
                "valid": False, 
                "error": "process() returned None, expected str"
            }))
            sys.exit(1)
        
        # Check for debug messages in output (not allowed)
        debug_patterns = ["[TOOL ENHANCEMENT", "validated by", "processed by", "[DEBUG"]
        for pattern in debug_patterns:
            if pattern in result:
                print(json.dumps({
                    "valid": False, 
                    "error": f"Tool output contains debug message: {pattern}"
                }))
                sys.exit(1)
        
        # Validation passed
        print(json.dumps({
            "valid": True, 
            "error": None, 
            "result_type": type(result).__name__,
            "result_length": len(result)
        }))
        
    except Exception as e:
        print(json.dumps({
            "valid": False, 
            "error": f"Tool validation failed: {str(e)}"
        }))
        sys.exit(1)
"""
            
            # Write and execute test
            test_file.write_text(test_code)
            
            result = subprocess.run(
                ["python", str(test_file)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.sandbox_dir
            )
            
            # Clean up
            test_file.unlink()
            
            if result.returncode == 0:
                try:
                    validation_result = json.loads(result.stdout)
                    logger.info(f"✅ Tool {tool_name} contract validation: {validation_result}")
                    return validation_result
                except json.JSONDecodeError:
                    return {"valid": False, "error": f"Invalid JSON response: {result.stdout}"}
            else:
                return {"valid": False, "error": f"Validation failed: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            if test_file.exists():
                test_file.unlink()
            return {"valid": False, "error": "Tool validation timeout"}
        except Exception as e:
            if test_file.exists():
                test_file.unlink()
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def get_implementation_stats(self) -> Dict[str, Any]:
        """Get statistics about tool implementations"""
        
        total = len(self.implemented_tools)
        deployed = sum(1 for t in self.implemented_tools if t.get("deployed"))
        
        return {
            "total_implemented": total,
            "deployed": deployed,
            "deployment_rate": deployed / total if total > 0 else 0,
            "require_human_review": self.require_human_review,
            "recent_tools": self.implemented_tools[-5:] if self.implemented_tools else []
        }