import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Literal
from dataclasses import dataclass
import base64

from anthropic import Anthropic
from openai import OpenAI
from .prompts import EvaluationPrompts

logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    """Container for evaluation results"""
    visual_scores: Optional[Dict[str, Any]] = None
    content_free_scores: Optional[Dict[str, Any]] = None
    content_required_scores: Optional[Dict[str, Any]] = None
    overall_scores: Optional[Dict[str, float]] = None

class PresentationEvaluator:
    """
    Comprehensive presentation evaluation system using three specialized prompts
    Supports both Claude and GPT models
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", provider: Literal["claude", "gpt"] = "claude"):
        """
        Initialize the evaluator
        
        Args:
            api_key: API key for the chosen provider
            model: Model name to use for evaluation
            provider: Either "claude" or "gpt"
        """
        self.provider = provider
        self.model = model
        self.prompts = EvaluationPrompts()
        
        if provider == "claude":
            self.client = Anthropic(api_key=api_key)
        elif provider == "gpt":
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError("Provider must be either 'claude' or 'gpt'")
    
    def extract_pdf_as_base64(self, pdf_path: str) -> str:
        """Extract PDF as base64 data for API calls"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_data = base64.b64encode(file.read()).decode('utf-8')
            return pdf_data
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            return ""
    
    def extract_pdf_content(self, pdf_path: str) -> str:
        """Extract PDF as base64 data for API calls"""
        return self.extract_pdf_as_base64(pdf_path)
    
    def call_claude_api_with_pdfs(self, prompt: str, presentation_pdf_data: str, source_pdf_data: Optional[str] = None) -> Dict[str, Any]:
        """Make API call to Claude with presentation PDF and optional source PDF"""
        try:
            content = [{"type": "text", "text": prompt}]
            
            # Add source PDF if available (for reference-required evaluation)
            if source_pdf_data:
                content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": source_pdf_data,
                    },
                })
                content.append({
                    "type": "text",
                    "text": "Above is the source paper. Below is the presentation to evaluate:"
                })
            
            # Add presentation PDF
            content.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": presentation_pdf_data,
                },
            })
            content.append({
                "type": "text",
                "text": "This is the presentation to evaluate. Please assess it according to the evaluation criteria."
            })
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.1,
                messages=[{"role": "user", "content": content}]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.error("No JSON found in response")
                return {"error": "No valid JSON in response", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return {"error": str(e)}
    
    def call_gpt_api_with_pdfs(self, prompt: str, presentation_pdf_data: str, source_pdf_data: Optional[str] = None) -> Dict[str, Any]:
        """Make API call to GPT with presentation PDF and optional source PDF"""
        try:
            # For GPT models, we'll use a different approach since file handling is more complex
            # We'll extract text content from PDFs and include it in the prompt
            # This is a simplified approach - for production use, you might want to use PDF text extraction
            
            # Create a comprehensive prompt that includes the PDF content
            full_prompt = prompt + "\n\n"
            
            if source_pdf_data:
                full_prompt += "SOURCE PAPER CONTENT:\n"
                full_prompt += "[PDF content would be extracted here]\n\n"
                full_prompt += "PRESENTATION CONTENT:\n"
                full_prompt += "[PDF content would be extracted here]\n\n"
            else:
                full_prompt += "PRESENTATION CONTENT:\n"
                full_prompt += "[PDF content would be extracted here]\n\n"
            
            full_prompt += "Please evaluate the presentation according to the criteria above."
            
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": full_prompt}],
                max_output_tokens=8000,
                temperature=0.1,
            )
            
            response_text = response.output[0].content[0].text
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.error("No JSON found in response")
                return {"error": "No valid JSON in response", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"GPT API call failed: {e}")
            return {"error": str(e)}
    
    def call_api_with_pdfs(self, prompt: str, presentation_pdf_data: str, source_pdf_data: Optional[str] = None) -> Dict[str, Any]:
        """Make API call using the appropriate provider"""
        if self.provider == "claude":
            return self.call_claude_api_with_pdfs(prompt, presentation_pdf_data, source_pdf_data)
        elif self.provider == "gpt":
            # Note: GPT implementation is a placeholder
            # For production use, you would need to implement proper PDF text extraction
            # and use GPT's vision capabilities or file upload features
            return self.call_gpt_api_with_pdfs(prompt, presentation_pdf_data, source_pdf_data)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def evaluate_visual(self, presentation_pdf_data: str) -> Dict[str, Any]:
        """Evaluate visual dimensions using presentation PDF"""
        logger.info("Evaluating visual dimensions...")
        return self.call_api_with_pdfs(self.prompts.visual, presentation_pdf_data)
    
    def evaluate_content_free(self, presentation_pdf_data: str) -> Dict[str, Any]:
        """Evaluate content dimensions without reference using presentation PDF"""
        logger.info("Evaluating reference-free content dimensions...")
        return self.call_api_with_pdfs(self.prompts.content_free, presentation_pdf_data)
    
    def evaluate_content_required(self, presentation_pdf_data: str, source_pdf_data: str) -> Dict[str, Any]:
        """Evaluate content dimensions requiring reference comparison using both PDFs"""
        logger.info("Evaluating reference-required content dimensions...")
        return self.call_api_with_pdfs(self.prompts.content_required, presentation_pdf_data, source_pdf_data)
    
    def evaluate_presentation(self, eval_folder: str) -> EvaluationResult:
        """
        Evaluate a presentation folder containing .html and .pdf files
        
        Args:
            eval_folder: Path to folder containing presentation files
            
        Returns:
            EvaluationResult containing all evaluation scores
        """
        eval_path = Path(eval_folder)
        
        # Look for the specific files
        presentation_pdf = eval_path / "presentation.pdf"
        source_pdf = eval_path / "paper.pdf"
        
        if not presentation_pdf.exists():
            raise FileNotFoundError(f"presentation.pdf not found in {eval_folder}")
        
        if not source_pdf.exists():
            logger.warning(f"paper.pdf not found in {eval_folder}. Reference-required evaluation will be skipped.")
            source_pdf = None
        
        logger.info(f"Evaluating presentation: {presentation_pdf.name}")
        if source_pdf:
            logger.info(f"Using source paper: {source_pdf.name}")
        
        # Extract PDF data
        presentation_pdf_data = self.extract_pdf_content(str(presentation_pdf))
        source_pdf_data = self.extract_pdf_content(str(source_pdf)) if source_pdf else None
        
        if not presentation_pdf_data:
            raise ValueError("Could not read presentation.pdf file")
        
        # Run evaluations using PDFs
        result = EvaluationResult()
        
        # Visual evaluation (always possible with presentation PDF)
        result.visual_scores = self.evaluate_visual(presentation_pdf_data)
        
        # Content evaluation - reference-free (using presentation PDF)
        result.content_free_scores = self.evaluate_content_free(presentation_pdf_data)
        
        # Content evaluation - reference-required (only if source PDF available)
        if source_pdf_data:
            result.content_required_scores = self.evaluate_content_required(presentation_pdf_data, source_pdf_data)
        
        # Calculate overall scores
        result.overall_scores = self._calculate_overall_scores(result)
        
        return result
    
    def _calculate_overall_scores(self, result: EvaluationResult) -> Dict[str, float]:
        """Calculate overall scores from individual evaluations"""
        overall = {}
        
        # Visual overall score
        if result.visual_scores and "overall_visual_score" in result.visual_scores:
            overall["visual"] = result.visual_scores["overall_visual_score"]
        
        # Content reference-free overall score
        if result.content_free_scores and "overall_content_score" in result.content_free_scores:
            overall["content_reference_free"] = result.content_free_scores["overall_content_score"]
        
        # Content reference-required overall score
        if result.content_required_scores and "overall_accuracy_coverage_score" in result.content_required_scores:
            overall["content_reference_required"] = result.content_required_scores["overall_accuracy_coverage_score"]
        
        # Combined content score (if both available)
        if "content_reference_free" in overall and "content_reference_required" in overall:
            overall["content_combined"] = (overall["content_reference_free"] + overall["content_reference_required"]) / 2
        
        # Overall presentation score
        available_scores = [score for score in overall.values() if score is not None]
        if available_scores:
            overall["presentation_overall"] = sum(available_scores) / len(available_scores)
        
        return overall
    
    def save_results(self, result: EvaluationResult, output_path: str):
        """Save evaluation results to JSON file"""
        output_data = {
            "visual_evaluation": result.visual_scores,
            "content_reference_free_evaluation": result.content_free_scores,
            "content_reference_required_evaluation": result.content_required_scores,
            "overall_scores": result.overall_scores,
            "evaluation_summary": self._generate_summary(result)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_path}")
    
    def _generate_summary(self, result: EvaluationResult) -> Dict[str, Any]:
        """Generate a human-readable summary"""
        summary = {
            "evaluation_completed": True,
            "evaluations_performed": []
        }
        
        if result.visual_scores:
            summary["evaluations_performed"].append("Visual (Reference-Free)")
        if result.content_free_scores:
            summary["evaluations_performed"].append("Content Structure & Narrative (Reference-Free)")
        if result.content_required_scores:
            summary["evaluations_performed"].append("Content Accuracy & Coverage (Reference-Required)")
        
        if result.overall_scores:
            summary["overall_scores"] = result.overall_scores
            
            # Add interpretation
            if "presentation_overall" in result.overall_scores:
                score = result.overall_scores["presentation_overall"]
                if score >= 4.5:
                    summary["interpretation"] = "Excellent presentation quality"
                elif score >= 3.5:
                    summary["interpretation"] = "Good presentation quality"
                elif score >= 2.5:
                    summary["interpretation"] = "Average presentation quality"
                elif score >= 1.5:
                    summary["interpretation"] = "Below average presentation quality"
                else:
                    summary["interpretation"] = "Poor presentation quality"
        
        return summary
    
    def print_results(self, result: EvaluationResult):
        """Print formatted results to console"""
        print("\n" + "="*60)
        print("PRESENTATION EVALUATION RESULTS")
        print("="*60)
        
        # Visual Scores
        if result.visual_scores:
            print("\n📊 VISUAL EVALUATION (Reference-Free)")
            print("-" * 40)
            for dimension, details in result.visual_scores.items():
                if dimension != "overall_visual_score" and isinstance(details, dict):
                    print(f"{dimension.replace('_', ' ').title()}: {details['score']}/5")
                    print(f"  Reasoning: {details['reasoning']}\n")
            
            if "overall_visual_score" in result.visual_scores:
                print(f"Overall Visual Score: {result.visual_scores['overall_visual_score']:.2f}/5")
        
        # Content Reference-Free Scores
        if result.content_free_scores:
            print("\n📝 CONTENT EVALUATION (Reference-Free)")
            print("-" * 40)
            for dimension, details in result.content_free_scores.items():
                if dimension != "overall_content_score" and isinstance(details, dict):
                    print(f"{dimension.replace('_', ' ').title()}: {details['score']}/5")
                    print(f"  Reasoning: {details['reasoning']}\n")
            
            if "overall_content_score" in result.content_free_scores:
                print(f"Overall Content Score: {result.content_free_scores['overall_content_score']:.2f}/5")
        
        # Content Reference-Required Scores
        if result.content_required_scores:
            print("\n🔍 CONTENT EVALUATION (Reference-Required)")
            print("-" * 40)
            for dimension, details in result.content_required_scores.items():
                if dimension != "overall_accuracy_coverage_score" and isinstance(details, dict):
                    print(f"{dimension.replace('_', ' ').title()}: {details['score']}/5")
                    print(f"  Reasoning: {details['reasoning']}\n")
            
            if "overall_accuracy_coverage_score" in result.content_required_scores:
                print(f"Overall Accuracy & Coverage Score: {result.content_required_scores['overall_accuracy_coverage_score']:.2f}/5")
        
        # Overall Scores
        if result.overall_scores:
            print("\n🎯 OVERALL SCORES")
            print("-" * 40)
            for category, score in result.overall_scores.items():
                print(f"{category.replace('_', ' ').title()}: {score:.2f}/5")