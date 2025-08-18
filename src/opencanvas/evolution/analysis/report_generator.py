"""
Report Generator

Creates comprehensive reports from prompt evolution analysis in multiple formats:
markdown, HTML dashboard, and JSON data exports.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .insights_extractor import EvolutionInsight

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates comprehensive reports from evolution analysis"""
    
    def __init__(self, analysis_data: Dict[str, Any], insights: List[EvolutionInsight], output_dir: Path):
        self.data = analysis_data
        self.insights = insights
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Organize insights by category for easier reporting
        self.insights_by_category = self._organize_insights_by_category()
    
    def generate_all_reports(self) -> List[Path]:
        """Generate all report formats"""
        generated_files = []
        
        try:
            # Generate each report type
            generated_files.append(self.generate_markdown_report())
            generated_files.append(self.generate_json_report())
            generated_files.append(self.generate_html_dashboard())
            generated_files.append(self.generate_executive_summary())
            
            logger.info(f"Generated {len(generated_files)} reports")
            return [f for f in generated_files if f is not None]
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            return generated_files
    
    def generate_markdown_report(self) -> Optional[Path]:
        """Generate comprehensive markdown report"""
        try:
            report_content = self._create_markdown_content()
            
            output_file = self.output_dir / "evolution_analysis_report.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Generated markdown report: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate markdown report: {e}")
            return None
    
    def generate_json_report(self) -> Optional[Path]:
        """Generate machine-readable JSON report"""
        try:
            json_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'report_version': '1.0',
                    'analysis_type': 'prompt_evolution'
                },
                'evolution_data': self.data,
                'insights': [self._insight_to_dict(insight) for insight in self.insights],
                'summary': {
                    'total_insights': len(self.insights),
                    'high_confidence_insights': len([i for i in self.insights if i.confidence >= 0.8]),
                    'actionable_recommendations': len([i for i in self.insights if i.actionable_recommendation]),
                    'categories': list(self.insights_by_category.keys())
                }
            }
            
            output_file = self.output_dir / "evolution_analysis_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, default=str)
            
            logger.info(f"Generated JSON report: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return None
    
    def generate_html_dashboard(self) -> Optional[Path]:
        """Generate interactive HTML dashboard"""
        try:
            html_content = self._create_dashboard_html()
            
            output_file = self.output_dir / "evolution_analysis_dashboard.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated HTML dashboard: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate HTML dashboard: {e}")
            return None
    
    def generate_executive_summary(self) -> Optional[Path]:
        """Generate concise executive summary"""
        try:
            summary_content = self._create_executive_summary()
            
            output_file = self.output_dir / "executive_summary.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"Generated executive summary: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")
            return None
    
    def _organize_insights_by_category(self) -> Dict[str, List[EvolutionInsight]]:
        """Organize insights by category"""
        categories = {}
        for insight in self.insights:
            if insight.category not in categories:
                categories[insight.category] = []
            categories[insight.category].append(insight)
        return categories
    
    def _insight_to_dict(self, insight: EvolutionInsight) -> Dict[str, Any]:
        """Convert insight to dictionary for JSON serialization"""
        return {
            'category': insight.category,
            'type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'confidence': insight.confidence,
            'supporting_data': insight.supporting_data,
            'recommendation': insight.actionable_recommendation
        }
    
    def _create_markdown_content(self) -> str:
        """Create comprehensive markdown report content"""
        overview = self.data.get('evolution_overview', {})
        growth = self.data.get('prompt_growth', {})
        
        content = f"""# Prompt Evolution Analysis Report
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

This report analyzes the evolution of prompts across {overview.get('total_iterations', 0)} iterations, examining performance improvements, change patterns, and optimization strategies.

### Key Metrics
- **Success Rate**: {overview.get('success_rate', 0):.1%}
- **Total Changes**: {overview.get('total_changes', 0)}
- **Successful Iterations**: {overview.get('successful_iterations', 0)}
- **Failed Iterations**: {overview.get('failed_iterations', 0)}

### Prompt Growth Summary
"""
        
        if growth:
            content += f"""- **Word Count Change**: {growth.get('word_count_change', 0):+d} words ({growth.get('relative_growth', 0):+.1f}%)
- **Instructions Added**: {growth.get('instruction_count_change', 0):+d}
- **Sections Added**: {growth.get('section_count_change', 0):+d}
"""
        else:
            content += "- No growth data available\n"
        
        # Add insights by category
        content += "\\n## Detailed Analysis\\n\\n"
        
        for category, insights in self.insights_by_category.items():
            content += f"### {category.replace('_', ' ').title()} Insights\\n\\n"
            
            for insight in insights:
                confidence_badge = self._get_confidence_badge(insight.confidence)
                content += f"#### {confidence_badge} {insight.title}\\n\\n"
                content += f"**Type**: {insight.insight_type.replace('_', ' ').title()}  \\n"
                content += f"**Confidence**: {insight.confidence:.1%}\\n\\n"
                content += f"{insight.description}\\n\\n"
                
                if insight.actionable_recommendation:
                    content += f"**💡 Recommendation**: {insight.actionable_recommendation}\\n\\n"
                
                if insight.supporting_data:
                    content += f"<details>\\n<summary>Supporting Data</summary>\\n\\n"
                    content += f"```json\\n{json.dumps(insight.supporting_data, indent=2)}\\n```\\n\\n"
                    content += f"</details>\\n\\n"
                
                content += "---\\n\\n"
        
        # Add actionable recommendations section
        recommendations = [i.actionable_recommendation for i in self.insights 
                         if i.actionable_recommendation and i.confidence >= 0.6]
        
        if recommendations:
            content += "## Actionable Recommendations\\n\\n"
            for i, rec in enumerate(recommendations[:10], 1):  # Top 10 recommendations
                content += f"{i}. {rec}\\n"
            content += "\\n"
        
        # Add methodology section
        content += self._create_methodology_section()
        
        return content
    
    def _create_executive_summary(self) -> str:
        """Create concise executive summary"""
        overview = self.data.get('evolution_overview', {})
        
        # Get top insights
        high_confidence_insights = [i for i in self.insights if i.confidence >= 0.8][:5]
        
        content = f"""# Executive Summary: Prompt Evolution Analysis
*{datetime.now().strftime('%Y-%m-%d')}*

## Key Results
- **Evolution Success Rate**: {overview.get('success_rate', 0):.1%}
- **Iterations Completed**: {overview.get('total_iterations', 0)}
- **High-Confidence Insights**: {len(high_confidence_insights)}

## Top Insights
"""
        
        for i, insight in enumerate(high_confidence_insights, 1):
            content += f"{i}. **{insight.title}** ({insight.confidence:.0%} confidence)\\n   {insight.description}\\n\\n"
        
        # Get top recommendations
        recommendations = [i.actionable_recommendation for i in self.insights 
                         if i.actionable_recommendation and i.confidence >= 0.7][:3]
        
        if recommendations:
            content += "## Priority Actions\\n\\n"
            for i, rec in enumerate(recommendations, 1):
                content += f"{i}. {rec}\\n"
            content += "\\n"
        
        content += f"""## Next Steps
1. Review detailed analysis report for complete findings
2. Implement priority recommendations
3. Continue evolution with identified successful patterns
4. Monitor performance using established metrics

*For full analysis, see the complete evolution analysis report.*
"""
        
        return content
    
    def _create_dashboard_html(self) -> str:
        """Create interactive HTML dashboard"""
        overview = self.data.get('evolution_overview', {})
        insights_data = []
        
        for insight in self.insights[:20]:  # Top 20 insights
            insights_data.append({
                'category': insight.category,
                'type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence,
                'recommendation': insight.actionable_recommendation or ''
            })
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Evolution Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        .dashboard {{
            max-width: 1600px;
            margin: 0 auto;
            display: grid;
            gap: 20px;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }}
        .header {{
            grid-column: 1 / -1;
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
        }}
        .card-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}
        .card-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }}
        .metric-item {{
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 10px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
            font-weight: 500;
        }}
        .insights-container {{
            grid-column: 1 / -1;
            max-height: 600px;
            overflow-y: auto;
        }}
        .insight-item {{
            background: white;
            margin: 15px 0;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }}
        .insight-item:hover {{
            transform: translateX(5px);
        }}
        .insight-item.success {{ border-left-color: #27ae60; }}
        .insight-item.failure {{ border-left-color: #e74c3c; }}
        .insight-item.recommendation {{ border-left-color: #3498db; }}
        .insight-item.observation {{ border-left-color: #f39c12; }}
        .insight-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        .insight-title {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }}
        .confidence-badge {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .insight-description {{
            color: #7f8c8d;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        .insight-recommendation {{
            background: #e8f5e8;
            padding: 12px;
            border-radius: 8px;
            color: #27ae60;
            font-weight: 500;
            border-left: 3px solid #27ae60;
        }}
        .category-filter {{
            margin: 20px 0;
            text-align: center;
        }}
        .filter-btn {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 8px 16px;
            margin: 0 5px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: white;
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 Prompt Evolution Dashboard</h1>
            <p class="subtitle">Comprehensive analysis of evolution performance and insights</p>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <div class="card-title">Evolution Metrics</div>
            </div>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-value">{overview.get('success_rate', 0):.0%}</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">{overview.get('total_iterations', 0)}</div>
                    <div class="metric-label">Iterations</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">{len(self.insights)}</div>
                    <div class="metric-label">Insights</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">{overview.get('total_changes', 0)}</div>
                    <div class="metric-label">Changes</div>
                </div>
            </div>
        </div>
        
        <div class="insights-container">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💡</div>
                    <div class="card-title">Evolution Insights</div>
                </div>
                
                <div class="category-filter">
                    <button class="filter-btn active" onclick="filterInsights('all')">All</button>
                    <button class="filter-btn" onclick="filterInsights('performance')">Performance</button>
                    <button class="filter-btn" onclick="filterInsights('patterns')">Patterns</button>
                    <button class="filter-btn" onclick="filterInsights('growth')">Growth</button>
                    <button class="filter-btn" onclick="filterInsights('optimization')">Optimization</button>
                    <button class="filter-btn" onclick="filterInsights('strategy')">Strategy</button>
                </div>
                
                <div id="insights-list">
                    <!-- Insights will be populated by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <script>
        const insightsData = {json.dumps(insights_data, indent=2)};
        
        function renderInsights(filter = 'all') {{
            const container = document.getElementById('insights-list');
            container.innerHTML = '';
            
            const filteredInsights = filter === 'all' ? 
                insightsData : 
                insightsData.filter(insight => insight.category === filter);
            
            filteredInsights.forEach(insight => {{
                const item = document.createElement('div');
                item.className = `insight-item ${{insight.type.replace('_', '')}}`;
                
                let recommendationHtml = '';
                if (insight.recommendation) {{
                    recommendationHtml = `
                        <div class="insight-recommendation">
                            💡 <strong>Recommendation:</strong> ${{insight.recommendation}}
                        </div>
                    `;
                }}
                
                item.innerHTML = `
                    <div class="insight-header">
                        <div class="insight-title">${{insight.title}}</div>
                        <div class="confidence-badge">${{(insight.confidence * 100).toFixed(0)}}%</div>
                    </div>
                    <div class="insight-description">${{insight.description}}</div>
                    ${{recommendationHtml}}
                `;
                
                container.appendChild(item);
            }});
        }}
        
        function filterInsights(category) {{
            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Render filtered insights
            renderInsights(category);
        }}
        
        // Initial render
        document.addEventListener('DOMContentLoaded', () => renderInsights());
    </script>
</body>
</html>'''
    
    def _create_methodology_section(self) -> str:
        """Create methodology section for the report"""
        return """## Methodology

### Analysis Approach
This analysis examines prompt evolution through multiple dimensions:

1. **Performance Tracking**: Score progression across iterations
2. **Change Pattern Analysis**: Identification of modification types and frequencies
3. **Growth Analysis**: Prompt length, complexity, and structure evolution  
4. **Success Attribution**: Correlation between changes and performance improvements

### Confidence Scoring
Insights are assigned confidence scores based on:
- **Data Volume**: More examples increase confidence
- **Statistical Significance**: Clear trends vs. noise
- **Consistency**: Repeated patterns across iterations
- **Impact Magnitude**: Size of observed effects

### Insight Categories
- **Performance**: Overall evolution success and score trends
- **Patterns**: Successful vs. failed change types
- **Growth**: Prompt size and complexity evolution
- **Optimization**: Efficiency of change strategies
- **Strategy**: High-level recommendations for future evolution

### Limitations
- Analysis based on available evaluation data
- Insights reflect patterns in this specific evolution run
- Recommendations should be validated in new contexts
- Correlation does not imply causation

*Generated by OpenCanvas Evolution Analysis Module*
"""
    
    def _get_confidence_badge(self, confidence: float) -> str:
        """Get confidence badge for markdown"""
        if confidence >= 0.8:
            return "🟢"
        elif confidence >= 0.6:
            return "🟡"
        else:
            return "🔴"