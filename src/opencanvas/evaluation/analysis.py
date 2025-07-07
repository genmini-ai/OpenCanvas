"""
Evaluation Results Analysis Module

This module provides tools for parsing, comparing, and analyzing
presentation evaluation results, particularly for adversarial testing.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EvaluationResultsAnalyzer:
    """Analyzes and compares presentation evaluation results"""
    
    def __init__(self):
        self.original_results = {}
        self.attacked_results = {}
        self.comparison_data = []
    
    def load_original_results(self, base_dir: str = "test_output") -> Dict[str, Any]:
        """Load original evaluation results from topic-based tests"""
        base_path = Path(base_dir)
        results = {}
        
        # Look for evaluation results in organized folders
        for topic_dir in base_path.iterdir():
            if not topic_dir.is_dir():
                continue
            
            eval_dir = topic_dir / "evaluation"
            eval_file = eval_dir / "evaluation_results.json"
            
            if eval_file.exists():
                try:
                    with open(eval_file, 'r') as f:
                        eval_data = json.load(f)
                    
                    # Extract topic name from directory or content
                    topic_name = self._extract_topic_name(topic_dir.name)
                    results[topic_name] = eval_data
                    
                except Exception as e:
                    logger.error(f"Failed to load {eval_file}: {e}")
        
        self.original_results = results
        logger.info(f"Loaded {len(results)} original evaluation results")
        return results
    
    def load_attacked_results(self, adversarial_dir: str = "test_output/adversarial_analysis") -> Dict[str, Any]:
        """Load attacked evaluation results from adversarial testing"""
        adv_path = Path(adversarial_dir)
        results = {}
        
        # Check for consolidated results file first
        results_file = adv_path / "adversarial_evaluation_results.json"
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    data = json.load(f)
                results = data.get("attacked_evaluations", {})
            except Exception as e:
                logger.error(f"Failed to load consolidated results: {e}")
        
        # Also load individual attack evaluation files
        eval_dir = adv_path / "attacked_evaluations"
        if eval_dir.exists():
            for topic_dir in eval_dir.iterdir():
                if not topic_dir.is_dir():
                    continue
                
                topic_name = self._extract_topic_name(topic_dir.name)
                topic_results = {}
                
                for eval_file in topic_dir.glob("*_evaluation.json"):
                    attack_name = eval_file.stem.replace("_evaluation", "")
                    try:
                        with open(eval_file, 'r') as f:
                            eval_data = json.load(f)
                        topic_results[attack_name] = eval_data
                    except Exception as e:
                        logger.error(f"Failed to load {eval_file}: {e}")
                
                if topic_results:
                    if topic_name not in results:
                        results[topic_name] = {}
                    results[topic_name].update(topic_results)
        
        self.attacked_results = results
        logger.info(f"Loaded attacked results for {len(results)} topics")
        return results
    
    def _extract_topic_name(self, dir_name: str) -> str:
        """Extract readable topic name from directory name"""
        # Convert from snake_case or other formats to readable names
        name_mappings = {
            "sustainable_energy_solutions": "Sustainable Energy Solutions",
            "ai_in_healthcare": "AI in Healthcare", 
            "quantum_computing_fundamentals": "Quantum Computing Fundamentals",
            "climate_change_mitigation": "Climate Change Mitigation",
            "blockchain_technology": "Blockchain Technology"
        }
        
        return name_mappings.get(dir_name, dir_name.replace("_", " ").title())
    
    def extract_scores(self, eval_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical scores from evaluation data"""
        scores = {}
        
        # Overall scores
        overall_scores = eval_data.get("overall_scores", {})
        for key, value in overall_scores.items():
            if isinstance(value, (int, float)):
                scores[f"overall_{key}"] = float(value)
        
        # Visual scores
        visual_eval = eval_data.get("visual_evaluation", eval_data.get("visual_scores", {}))
        if isinstance(visual_eval, dict):
            overall_visual = visual_eval.get("overall_visual_score")
            if overall_visual is not None:
                scores["visual_overall"] = float(overall_visual)
            
            # Individual visual dimensions
            for dim, details in visual_eval.items():
                if isinstance(details, dict) and "score" in details:
                    scores[f"visual_{dim}"] = float(details["score"])
        
        # Content scores
        content_free = eval_data.get("content_reference_free_evaluation", eval_data.get("content_free_scores", {}))
        if isinstance(content_free, dict):
            overall_content = content_free.get("overall_content_score")
            if overall_content is not None:
                scores["content_free_overall"] = float(overall_content)
        
        content_required = eval_data.get("content_reference_required_evaluation", eval_data.get("content_required_scores", {}))
        if isinstance(content_required, dict):
            overall_accuracy = content_required.get("overall_accuracy_coverage_score")
            if overall_accuracy is not None:
                scores["content_required_overall"] = float(overall_accuracy)
        
        return scores
    
    def compare_scores(self) -> pd.DataFrame:
        """Compare original vs attacked scores"""
        comparison_data = []
        
        for topic, original_eval in self.original_results.items():
            if topic not in self.attacked_results:
                continue
            
            original_scores = self.extract_scores(original_eval)
            
            for attack_name, attack_eval in self.attacked_results[topic].items():
                if "error" in attack_eval:
                    continue
                
                attack_scores = self.extract_scores(attack_eval)
                
                # Compare each score dimension
                for score_name in original_scores.keys():
                    if score_name in attack_scores:
                        comparison_data.append({
                            "topic": topic,
                            "attack": attack_name,
                            "score_dimension": score_name,
                            "original_score": original_scores[score_name],
                            "attacked_score": attack_scores[score_name],
                            "score_drop": original_scores[score_name] - attack_scores[score_name],
                            "relative_drop": (original_scores[score_name] - attack_scores[score_name]) / original_scores[score_name] if original_scores[score_name] > 0 else 0
                        })
        
        df = pd.DataFrame(comparison_data)
        self.comparison_data = df
        return df
    
    def calculate_attack_effectiveness(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Calculate effectiveness metrics for each attack"""
        if df is None:
            df = self.comparison_data
        
        if df.empty:
            return {}
        
        effectiveness = {}
        
        # Group by attack type
        for attack in df['attack'].unique():
            attack_data = df[df['attack'] == attack]
            
            effectiveness[attack] = {
                "mean_score_drop": attack_data['score_drop'].mean(),
                "median_score_drop": attack_data['score_drop'].median(),
                "std_score_drop": attack_data['score_drop'].std(),
                "mean_relative_drop": attack_data['relative_drop'].mean(),
                "max_score_drop": attack_data['score_drop'].max(),
                "min_score_drop": attack_data['score_drop'].min(),
                "success_rate": (attack_data['score_drop'] > 0).mean(),
                "significant_impact_rate": (attack_data['score_drop'] > 0.5).mean(),
                "sample_size": len(attack_data)
            }
        
        return effectiveness
    
    def analyze_by_dimension(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Analyze attack effectiveness by evaluation dimension"""
        if df is None:
            df = self.comparison_data
        
        if df.empty:
            return {}
        
        dimension_analysis = {}
        
        for dimension in df['score_dimension'].unique():
            dim_data = df[df['score_dimension'] == dimension]
            
            dimension_analysis[dimension] = {
                "mean_vulnerability": dim_data['score_drop'].mean(),
                "most_vulnerable_to": dim_data.groupby('attack')['score_drop'].mean().idxmax(),
                "least_vulnerable_to": dim_data.groupby('attack')['score_drop'].mean().idxmin(),
                "attack_effects": dim_data.groupby('attack')['score_drop'].agg(['mean', 'std', 'count']).to_dict()
            }
        
        return dimension_analysis
    
    def generate_statistical_report(self) -> Dict[str, Any]:
        """Generate comprehensive statistical analysis report"""
        if self.comparison_data.empty:
            self.compare_scores()
        
        df = self.comparison_data
        
        report = {
            "overview": {
                "total_comparisons": len(df),
                "topics_tested": df['topic'].nunique(),
                "attacks_tested": df['attack'].nunique(),
                "dimensions_analyzed": df['score_dimension'].nunique()
            },
            "attack_effectiveness": self.calculate_attack_effectiveness(df),
            "dimension_vulnerability": self.analyze_by_dimension(df),
            "overall_statistics": {
                "mean_score_drop_all_attacks": df['score_drop'].mean(),
                "median_score_drop_all_attacks": df['score_drop'].median(),
                "std_score_drop_all_attacks": df['score_drop'].std(),
                "attack_success_rate": (df['score_drop'] > 0).mean(),
                "significant_impact_rate": (df['score_drop'] > 0.5).mean()
            }
        }
        
        # Statistical significance tests
        report["statistical_tests"] = self._perform_statistical_tests(df)
        
        return report
    
    def _perform_statistical_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical significance tests"""
        from scipy import stats
        
        tests = {}
        
        # Test if attacks significantly reduce scores
        original_scores = df['original_score'].values
        attacked_scores = df['attacked_score'].values
        
        # Paired t-test
        t_stat, p_value = stats.ttest_rel(original_scores, attacked_scores)
        tests["paired_t_test"] = {
            "statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "interpretation": "Attacks significantly reduce scores" if p_value < 0.05 else "No significant effect"
        }
        
        # ANOVA to test if different attacks have different effects
        attack_groups = [df[df['attack'] == attack]['score_drop'].values for attack in df['attack'].unique()]
        f_stat, p_value = stats.f_oneway(*attack_groups)
        tests["anova_attacks"] = {
            "statistic": float(f_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "interpretation": "Different attacks have significantly different effects" if p_value < 0.05 else "No significant difference between attacks"
        }
        
        return tests
    
    def create_visualizations(self, output_dir: str = "test_output/adversarial_analysis/plots"):
        """Create visualization plots for the analysis"""
        if self.comparison_data.empty:
            self.compare_scores()
        
        df = self.comparison_data
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Attack effectiveness comparison
        plt.figure(figsize=(12, 8))
        attack_means = df.groupby('attack')['score_drop'].mean().sort_values(ascending=True)
        attack_means.plot(kind='barh')
        plt.title('Attack Effectiveness: Mean Score Drop by Attack Type')
        plt.xlabel('Mean Score Drop')
        plt.ylabel('Attack Type')
        plt.tight_layout()
        plt.savefig(output_path / 'attack_effectiveness.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Score drops by dimension
        plt.figure(figsize=(14, 8))
        pivot_data = df.pivot_table(values='score_drop', index='score_dimension', columns='attack', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='Reds')
        plt.title('Score Drops by Evaluation Dimension and Attack Type')
        plt.ylabel('Evaluation Dimension')
        plt.xlabel('Attack Type')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(output_path / 'dimension_vulnerability_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Distribution of score drops
        plt.figure(figsize=(12, 8))
        df.boxplot(column='score_drop', by='attack', figsize=(12, 8))
        plt.title('Distribution of Score Drops by Attack Type')
        plt.xlabel('Attack Type')
        plt.ylabel('Score Drop')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path / 'score_drop_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Topic vulnerability analysis
        plt.figure(figsize=(12, 8))
        topic_vulnerability = df.groupby('topic')['score_drop'].mean().sort_values(ascending=True)
        topic_vulnerability.plot(kind='barh')
        plt.title('Topic Vulnerability: Mean Score Drop by Topic')
        plt.xlabel('Mean Score Drop')
        plt.ylabel('Topic')
        plt.tight_layout()
        plt.savefig(output_path / 'topic_vulnerability.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualizations saved to {output_path}")
    
    def save_analysis_report(self, output_file: str = "test_output/adversarial_analysis/analysis_report.json"):
        """Save comprehensive analysis report to JSON"""
        report = self.generate_statistical_report()
        
        # Add metadata
        report["metadata"] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_sources": {
                "original_results_count": len(self.original_results),
                "attacked_results_count": len(self.attacked_results)
            }
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Analysis report saved to {output_path}")
        return report
    
    def print_summary(self):
        """Print a formatted summary of the analysis"""
        if self.comparison_data.empty:
            self.compare_scores()
        
        report = self.generate_statistical_report()
        
        print("\n" + "="*80)
        print("ADVERSARIAL EVALUATION ANALYSIS SUMMARY")
        print("="*80)
        
        overview = report["overview"]
        print(f"\n📊 OVERVIEW:")
        print(f"  Total Comparisons: {overview['total_comparisons']}")
        print(f"  Topics Tested: {overview['topics_tested']}")
        print(f"  Attacks Tested: {overview['attacks_tested']}")
        print(f"  Evaluation Dimensions: {overview['dimensions_analyzed']}")
        
        overall_stats = report["overall_statistics"]
        print(f"\n📈 OVERALL IMPACT:")
        print(f"  Mean Score Drop: {overall_stats['mean_score_drop_all_attacks']:.3f}")
        print(f"  Attack Success Rate: {overall_stats['attack_success_rate']:.1%}")
        print(f"  Significant Impact Rate: {overall_stats['significant_impact_rate']:.1%}")
        
        print(f"\n🎯 ATTACK EFFECTIVENESS RANKING:")
        effectiveness = report["attack_effectiveness"]
        ranked_attacks = sorted(effectiveness.items(), key=lambda x: x[1]['mean_score_drop'], reverse=True)
        
        for i, (attack, stats) in enumerate(ranked_attacks, 1):
            print(f"  {i}. {attack.replace('_', ' ').title()}: {stats['mean_score_drop']:.3f} avg drop")
        
        print(f"\n🔍 STATISTICAL SIGNIFICANCE:")
        stat_tests = report["statistical_tests"]
        t_test = stat_tests["paired_t_test"]
        print(f"  Attacks vs Original: {t_test['interpretation']}")
        print(f"  p-value: {t_test['p_value']:.6f}")
        
        anova = stat_tests["anova_attacks"]
        print(f"  Attack Differences: {anova['interpretation']}")
        print(f"  p-value: {anova['p_value']:.6f}")


def analyze_adversarial_results(
    original_dir: str = "test_output",
    adversarial_dir: str = "test_output/adversarial_analysis",
    output_dir: str = "test_output/adversarial_analysis"
) -> Dict[str, Any]:
    """
    Complete analysis of adversarial evaluation results
    
    Args:
        original_dir: Directory containing original evaluation results
        adversarial_dir: Directory containing adversarial test results
        output_dir: Directory to save analysis outputs
    
    Returns:
        Complete analysis report
    """
    analyzer = EvaluationResultsAnalyzer()
    
    # Load data
    analyzer.load_original_results(original_dir)
    analyzer.load_attacked_results(adversarial_dir)
    
    # Perform analysis
    comparison_df = analyzer.compare_scores()
    report = analyzer.save_analysis_report(f"{output_dir}/analysis_report.json")
    
    # Create visualizations
    analyzer.create_visualizations(f"{output_dir}/plots")
    
    # Print summary
    analyzer.print_summary()
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze adversarial evaluation results")
    parser.add_argument("--original-dir", default="test_output", help="Directory with original results")
    parser.add_argument("--adversarial-dir", default="test_output/adversarial_analysis", help="Directory with adversarial results")
    parser.add_argument("--output-dir", default="test_output/adversarial_analysis", help="Output directory for analysis")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run analysis
    analyze_adversarial_results(
        original_dir=args.original_dir,
        adversarial_dir=args.adversarial_dir,
        output_dir=args.output_dir
    )