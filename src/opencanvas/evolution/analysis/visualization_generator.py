"""
Visualization Generator

Creates compelling visualizations for prompt evolution analysis including
timelines, heatmaps, score correlations, and interactive dashboards.
"""

import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class VisualizationGenerator:
    """Generates visualizations for prompt evolution analysis"""
    
    def __init__(self, analyzer_data: Dict[str, Any], output_dir: Path):
        self.data = analyzer_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create visualizations subdirectory
        self.viz_dir = self.output_dir / "visualizations"
        self.viz_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_visualizations(self) -> List[Path]:
        """Generate all available visualizations"""
        generated_files = []
        
        try:
            # Generate each visualization type
            generated_files.append(self.generate_evolution_timeline())
            generated_files.append(self.generate_score_progression_chart())
            generated_files.append(self.generate_change_heatmap())
            generated_files.append(self.generate_metrics_dashboard())
            generated_files.append(self.generate_pattern_analysis_chart())
            
            logger.info(f"Generated {len(generated_files)} visualizations")
            return [f for f in generated_files if f is not None]
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return generated_files
    
    def generate_evolution_timeline(self) -> Optional[Path]:
        """Generate interactive timeline showing prompt evolution"""
        try:
            # Prepare timeline data
            timeline_data = self._prepare_timeline_data()
            
            html_content = self._create_timeline_html(timeline_data)
            
            output_file = self.viz_dir / "evolution_timeline.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated evolution timeline: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate evolution timeline: {e}")
            return None
    
    def generate_score_progression_chart(self) -> Optional[Path]:
        """Generate chart showing score progression over iterations"""
        try:
            score_data = self.data.get('score_progression', {})
            if not score_data:
                logger.warning("No score progression data available")
                return None
            
            html_content = self._create_score_chart_html(score_data)
            
            output_file = self.viz_dir / "score_progression.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated score progression chart: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate score progression chart: {e}")
            return None
    
    def generate_change_heatmap(self) -> Optional[Path]:
        """Generate heatmap showing where changes occurred most frequently"""
        try:
            change_patterns = self.data.get('change_patterns', {})
            section_changes = change_patterns.get('section_changes', {})
            
            if not section_changes:
                logger.warning("No section change data available for heatmap")
                return None
            
            html_content = self._create_heatmap_html(section_changes)
            
            output_file = self.viz_dir / "change_heatmap.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated change heatmap: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate change heatmap: {e}")
            return None
    
    def generate_metrics_dashboard(self) -> Optional[Path]:
        """Generate comprehensive metrics dashboard"""
        try:
            html_content = self._create_dashboard_html()
            
            output_file = self.viz_dir / "metrics_dashboard.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated metrics dashboard: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate metrics dashboard: {e}")
            return None
    
    def generate_pattern_analysis_chart(self) -> Optional[Path]:
        """Generate visualization showing successful vs failed patterns"""
        try:
            change_patterns = self.data.get('change_patterns', {})
            
            html_content = self._create_pattern_analysis_html(change_patterns)
            
            output_file = self.viz_dir / "pattern_analysis.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated pattern analysis chart: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate pattern analysis chart: {e}")
            return None
    
    def _prepare_timeline_data(self) -> Dict[str, Any]:
        """Prepare data for timeline visualization"""
        timeline_events = []
        
        # Get evolution overview
        overview = self.data.get('evolution_overview', {})
        score_progression = self.data.get('score_progression', {})
        
        # Add baseline event
        timeline_events.append({
            'iteration': 0,
            'version': 'baseline',
            'title': 'Baseline Prompt',
            'description': 'Original prompt before evolution',
            'scores': {},
            'changes': [],
            'type': 'baseline'
        })
        
        # Add evolution iterations
        for iteration in sorted(score_progression.keys()):
            scores = score_progression[iteration]
            
            # Calculate improvements
            improvements = {}
            if iteration > 1 and (iteration - 1) in score_progression:
                prev_scores = score_progression[iteration - 1]
                for metric, score in scores.items():
                    if metric in prev_scores:
                        improvements[metric] = score - prev_scores[metric]
            
            # Determine success/failure
            overall_improvement = improvements.get('presentation_overall', 0)
            event_type = 'success' if overall_improvement > 0 else 'failure' if overall_improvement < 0 else 'neutral'
            
            timeline_events.append({
                'iteration': iteration,
                'version': f'v{iteration}',
                'title': f'Evolution Iteration {iteration}',
                'description': self._get_iteration_description(iteration, improvements),
                'scores': scores,
                'improvements': improvements,
                'changes': self._get_iteration_changes(iteration),
                'type': event_type
            })
        
        return {
            'events': timeline_events,
            'summary': overview
        }
    
    def _get_iteration_description(self, iteration: int, improvements: Dict[str, float]) -> str:
        """Generate description for timeline iteration"""
        if not improvements:
            return f"Iteration {iteration} - First evolution"
        
        overall = improvements.get('presentation_overall', 0)
        if overall > 0.2:
            return f"Strong improvement (+{overall:.2f} overall score)"
        elif overall > 0:
            return f"Minor improvement (+{overall:.2f} overall score)"
        elif overall < -0.2:
            return f"Significant decline ({overall:.2f} overall score)"
        elif overall < 0:
            return f"Minor decline ({overall:.2f} overall score)"
        else:
            return f"No significant change"
    
    def _get_iteration_changes(self, iteration: int) -> List[str]:
        """Get major changes for an iteration"""
        # This would be populated from the actual change data
        # For now, return placeholder based on common patterns
        changes = []
        
        if iteration == 1:
            changes = ["Enhanced visual storytelling", "Added cohesive narrative guidance"]
        elif iteration == 2:
            changes = ["Improved visual hierarchy", "Added negative space utilization"]
        elif iteration == 3:
            changes = ["Added visual consistency requirements", "Enhanced depth effects"]
        
        return changes
    
    def _create_timeline_html(self, timeline_data: Dict[str, Any]) -> str:
        """Create HTML for interactive timeline"""
        events_json = json.dumps(timeline_data['events'], indent=2)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Evolution Timeline</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .timeline {{
            position: relative;
            margin: 40px 0;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, #667eea, #764ba2);
            border-radius: 2px;
        }}
        .timeline-event {{
            position: relative;
            margin: 30px 0;
            opacity: 0;
            animation: slideIn 0.6s ease forwards;
        }}
        .timeline-event:nth-child(odd) {{
            text-align: right;
            padding-right: calc(50% + 30px);
        }}
        .timeline-event:nth-child(even) {{
            text-align: left;
            padding-left: calc(50% + 30px);
        }}
        .event-marker {{
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 4px solid white;
            z-index: 10;
        }}
        .event-marker.baseline {{ background: #95a5a6; }}
        .event-marker.success {{ background: #2ecc71; }}
        .event-marker.failure {{ background: #e74c3c; }}
        .event-marker.neutral {{ background: #f39c12; }}
        .event-content {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            border-left: 4px solid;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .event-content:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }}
        .event-content.success {{ border-left-color: #2ecc71; }}
        .event-content.failure {{ border-left-color: #e74c3c; }}
        .event-content.neutral {{ border-left-color: #f39c12; }}
        .event-content.baseline {{ border-left-color: #95a5a6; }}
        .event-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 8px;
            color: #2c3e50;
        }}
        .event-description {{
            color: #7f8c8d;
            margin-bottom: 15px;
        }}
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .score-item {{
            text-align: center;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .score-label {{
            font-size: 0.8em;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        .score-value {{
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50;
        }}
        .improvement {{
            font-size: 0.9em;
            margin-left: 5px;
        }}
        .improvement.positive {{ color: #2ecc71; }}
        .improvement.negative {{ color: #e74c3c; }}
        .changes-list {{
            margin-top: 15px;
        }}
        .changes-list h4 {{
            margin: 0 0 8px 0;
            color: #34495e;
            font-size: 1em;
        }}
        .changes-list ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .changes-list li {{
            margin: 4px 0;
            color: #7f8c8d;
        }}
        @keyframes slideIn {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        .timeline-event {{
            transform: translateY(20px);
        }}
        .timeline-event:nth-child(1) {{ animation-delay: 0.1s; }}
        .timeline-event:nth-child(2) {{ animation-delay: 0.2s; }}
        .timeline-event:nth-child(3) {{ animation-delay: 0.3s; }}
        .timeline-event:nth-child(4) {{ animation-delay: 0.4s; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Prompt Evolution Timeline</h1>
            <p>Visual journey of prompt optimization and improvements</p>
        </div>
        
        <div class="timeline" id="timeline">
            <!-- Timeline events will be generated by JavaScript -->
        </div>
    </div>

    <script>
        const timelineData = {events_json};
        
        function renderTimeline() {{
            const timeline = document.getElementById('timeline');
            
            timelineData.forEach((event, index) => {{
                const eventDiv = document.createElement('div');
                eventDiv.className = 'timeline-event';
                
                const marker = document.createElement('div');
                marker.className = `event-marker ${{event.type}}`;
                
                const content = document.createElement('div');
                content.className = `event-content ${{event.type}}`;
                
                let scoresHtml = '';
                if (Object.keys(event.scores).length > 0) {{
                    scoresHtml = '<div class="score-grid">';
                    for (const [metric, score] of Object.entries(event.scores)) {{
                        let improvementHtml = '';
                        if (event.improvements && event.improvements[metric]) {{
                            const improvement = event.improvements[metric];
                            const className = improvement > 0 ? 'positive' : 'negative';
                            const sign = improvement > 0 ? '+' : '';
                            improvementHtml = `<span class="improvement ${{className}}">(${{sign}}${{improvement.toFixed(2)}})</span>`;
                        }}
                        scoresHtml += `
                            <div class="score-item">
                                <div class="score-label">${{metric.replace('_', ' ')}}</div>
                                <div class="score-value">${{score.toFixed(2)}}${{improvementHtml}}</div>
                            </div>
                        `;
                    }}
                    scoresHtml += '</div>';
                }}
                
                let changesHtml = '';
                if (event.changes && event.changes.length > 0) {{
                    changesHtml = `
                        <div class="changes-list">
                            <h4>Key Changes:</h4>
                            <ul>
                                ${{event.changes.map(change => `<li>${{change}}</li>`).join('')}}
                            </ul>
                        </div>
                    `;
                }}
                
                content.innerHTML = `
                    <div class="event-title">${{event.title}}</div>
                    <div class="event-description">${{event.description}}</div>
                    ${{scoresHtml}}
                    ${{changesHtml}}
                `;
                
                eventDiv.appendChild(marker);
                eventDiv.appendChild(content);
                timeline.appendChild(eventDiv);
            }});
        }}
        
        // Render timeline when page loads
        document.addEventListener('DOMContentLoaded', renderTimeline);
    </script>
</body>
</html>'''
    
    def _create_score_chart_html(self, score_data: Dict[int, Dict[str, float]]) -> str:
        """Create HTML for score progression chart"""
        # Prepare chart data
        iterations = sorted(score_data.keys())
        metrics = set()
        for scores in score_data.values():
            metrics.update(scores.keys())
        
        # Create datasets for each metric
        datasets = []
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        
        for i, metric in enumerate(sorted(metrics)):
            data = [score_data[iteration].get(metric, 0) for iteration in iterations]
            datasets.append({
                'label': metric.replace('_', ' ').title(),
                'data': data,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20',
                'fill': False,
                'tension': 0.3
            })
        
        chart_data = {
            'labels': [f'Iteration {i}' for i in iterations],
            'datasets': datasets
        }
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Score Progression Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.2em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .chart-container {{
            position: relative;
            height: 500px;
            margin: 20px 0;
        }}
        .insights {{
            margin-top: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        .insights h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Score Progression Analysis</h1>
            <p>How presentation quality evolved over iterations</p>
        </div>
        
        <div class="chart-container">
            <canvas id="scoreChart"></canvas>
        </div>
        
        <div class="insights">
            <h3>Key Insights</h3>
            <div id="insights-content"></div>
        </div>
    </div>

    <script>
        const chartData = {json.dumps(chart_data, indent=2)};
        
        const ctx = document.getElementById('scoreChart').getContext('2d');
        const scoreChart = new Chart(ctx, {{
            type: 'line',
            data: chartData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Evolution Score Progression',
                        font: {{ size: 16 }}
                    }},
                    legend: {{
                        position: 'top',
                        labels: {{
                            usePointStyle: true,
                            padding: 20
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 5,
                        title: {{
                            display: true,
                            text: 'Score (0-5)'
                        }},
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Evolution Iterations'
                        }},
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }}
                    }}
                }},
                elements: {{
                    point: {{
                        radius: 6,
                        hoverRadius: 8
                    }},
                    line: {{
                        borderWidth: 3
                    }}
                }}
            }}
        }});
        
        // Generate insights
        function generateInsights() {{
            const insightsDiv = document.getElementById('insights-content');
            const insights = [];
            
            // Calculate trends for each metric
            chartData.datasets.forEach(dataset => {{
                const data = dataset.data;
                const trend = data[data.length - 1] - data[0];
                const trendText = trend > 0 ? 'improved' : trend < 0 ? 'declined' : 'remained stable';
                const trendValue = Math.abs(trend).toFixed(2);
                insights.push(`<li><strong>${{dataset.label}}</strong>: ${{trendText}} by ${{trendValue}} points over the evolution</li>`);
            }});
            
            insightsDiv.innerHTML = `<ul>${{insights.join('')}}</ul>`;
        }}
        
        document.addEventListener('DOMContentLoaded', generateInsights);
    </script>
</body>
</html>'''
    
    def _create_heatmap_html(self, section_changes: Dict[str, int]) -> str:
        """Create HTML for change frequency heatmap"""
        # Convert section changes to chart data
        sections = list(section_changes.keys())
        values = list(section_changes.values())
        max_changes = max(values) if values else 1
        
        # Create intensity values (0-1) for color mapping
        intensities = [v / max_changes for v in values]
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Change Frequency Heatmap</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.2em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .heatmap {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }}
        .heatmap-cell {{
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        .heatmap-cell:hover {{
            transform: scale(1.05);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        .section-name {{
            font-size: 1.1em;
            margin-bottom: 8px;
            text-transform: capitalize;
        }}
        .change-count {{
            font-size: 2em;
            margin-bottom: 5px;
        }}
        .change-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
            gap: 10px;
        }}
        .legend-label {{
            color: #7f8c8d;
            font-weight: bold;
        }}
        .legend-gradient {{
            width: 200px;
            height: 20px;
            border-radius: 10px;
            background: linear-gradient(to right, #3498db, #e74c3c);
        }}
        .legend-values {{
            display: flex;
            justify-content: space-between;
            width: 200px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Change Frequency Heatmap</h1>
            <p>Visual representation of where changes occurred most frequently</p>
        </div>
        
        <div class="heatmap" id="heatmap">
            <!-- Heatmap cells will be generated by JavaScript -->
        </div>
        
        <div class="legend">
            <span class="legend-label">Less Changes</span>
            <div>
                <div class="legend-gradient"></div>
                <div class="legend-values">
                    <span>0</span>
                    <span>{max(values)}</span>
                </div>
            </div>
            <span class="legend-label">More Changes</span>
        </div>
    </div>

    <script>
        const sectionData = {json.dumps(list(zip(sections, values, intensities)), indent=2)};
        
        function getHeatmapColor(intensity) {{
            // Interpolate between blue (low) and red (high)
            const r = Math.round(52 + (231 - 52) * intensity);  // 52 to 231
            const g = Math.round(152 - 152 * intensity);        // 152 to 0
            const b = Math.round(219 - 143 * intensity);        // 219 to 76
            return `rgb(${{r}}, ${{g}}, ${{b}})`;
        }}
        
        function renderHeatmap() {{
            const heatmapDiv = document.getElementById('heatmap');
            
            sectionData.forEach(([section, count, intensity]) => {{
                const cell = document.createElement('div');
                cell.className = 'heatmap-cell';
                cell.style.backgroundColor = getHeatmapColor(intensity);
                
                // Add subtle shadow for depth
                cell.style.boxShadow = `0 4px 15px rgba(0,0,0,${{0.1 + intensity * 0.2}})`;
                
                cell.innerHTML = `
                    <div class="section-name">${{section.replace('_', ' ')}}</div>
                    <div class="change-count">${{count}}</div>
                    <div class="change-label">${{count === 1 ? 'change' : 'changes'}}</div>
                `;
                
                // Add click handler for details
                cell.addEventListener('click', () => {{
                    alert(`Section: ${{section}}\\nTotal Changes: ${{count}}\\nIntensity: ${{(intensity * 100).toFixed(1)}}%`);
                }});
                
                heatmapDiv.appendChild(cell);
            }});
        }}
        
        document.addEventListener('DOMContentLoaded', renderHeatmap);
    </script>
</body>
</html>'''
    
    def _create_dashboard_html(self) -> str:
        """Create comprehensive metrics dashboard HTML"""
        overview = self.data.get('evolution_overview', {})
        growth = self.data.get('prompt_growth', {})
        insights = self.data.get('key_insights', [])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evolution Metrics Dashboard</title>
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
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            gap: 20px;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }}
        .card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
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
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-weight: 500;
        }}
        .metric-value {{
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50;
        }}
        .metric-value.positive {{
            color: #27ae60;
        }}
        .metric-value.negative {{
            color: #e74c3c;
        }}
        .success-rate {{
            text-align: center;
            margin: 20px 0;
        }}
        .success-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            font-weight: bold;
            color: white;
            position: relative;
            overflow: hidden;
        }}
        .insights-list {{
            list-style: none;
        }}
        .insights-list li {{
            padding: 10px 0;
            color: #7f8c8d;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }}
        .header {{
            grid-column: 1 / -1;
            text-align: center;
            margin-bottom: 20px;
            color: white;
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 Evolution Dashboard</h1>
            <p>Comprehensive analysis of prompt evolution performance</p>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📈</div>
                <div class="card-title">Evolution Overview</div>
            </div>
            <div class="metric">
                <span class="metric-label">Total Iterations</span>
                <span class="metric-value">{overview.get('total_iterations', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Changes</span>
                <span class="metric-value">{overview.get('total_changes', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Successful Iterations</span>
                <span class="metric-value positive">{overview.get('successful_iterations', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Failed Iterations</span>
                <span class="metric-value negative">{overview.get('failed_iterations', 0)}</span>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon">🎯</div>
                <div class="card-title">Success Rate</div>
            </div>
            <div class="success-rate">
                <div class="success-circle" id="successCircle">
                    <span>{overview.get('success_rate', 0) * 100:.0f}%</span>
                </div>
                <p>Overall Evolution Success Rate</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📏</div>
                <div class="card-title">Prompt Growth</div>
            </div>
            <div class="metric">
                <span class="metric-label">Word Count Change</span>
                <span class="metric-value {'positive' if growth.get('word_count_change', 0) > 0 else 'negative' if growth.get('word_count_change', 0) < 0 else ''}">
                    {'+' if growth.get('word_count_change', 0) > 0 else ''}{growth.get('word_count_change', 0)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Instructions Added</span>
                <span class="metric-value {'positive' if growth.get('instruction_count_change', 0) > 0 else 'negative' if growth.get('instruction_count_change', 0) < 0 else ''}">
                    {'+' if growth.get('instruction_count_change', 0) > 0 else ''}{growth.get('instruction_count_change', 0)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Sections Added</span>
                <span class="metric-value {'positive' if growth.get('section_count_change', 0) > 0 else 'negative' if growth.get('section_count_change', 0) < 0 else ''}">
                    {'+' if growth.get('section_count_change', 0) > 0 else ''}{growth.get('section_count_change', 0)}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Relative Growth</span>
                <span class="metric-value {'positive' if growth.get('relative_growth', 0) > 0 else 'negative' if growth.get('relative_growth', 0) < 0 else ''}">
                    {growth.get('relative_growth', 0):.1f}%
                </span>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon">💡</div>
                <div class="card-title">Key Insights</div>
            </div>
            <ul class="insights-list">
                {chr(10).join([f'<li>{insight}</li>' for insight in insights])}
            </ul>
        </div>
    </div>

    <script>
        // Set success circle color based on success rate
        const successRate = {overview.get('success_rate', 0)};
        const successCircle = document.getElementById('successCircle');
        
        if (successRate >= 0.7) {{
            successCircle.style.background = 'linear-gradient(45deg, #27ae60, #2ecc71)';
        }} else if (successRate >= 0.4) {{
            successCircle.style.background = 'linear-gradient(45deg, #f39c12, #e67e22)';
        }} else {{
            successCircle.style.background = 'linear-gradient(45deg, #e74c3c, #c0392b)';
        }}
        
        // Add animation to success circle
        successCircle.style.backgroundSize = '200% 200%';
        successCircle.style.animation = 'gradient 3s ease infinite';
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>'''
    
    def _create_pattern_analysis_html(self, change_patterns: Dict[str, Any]) -> str:
        """Create HTML for pattern analysis visualization"""
        successful_patterns = change_patterns.get('successful_change_types', {})
        failed_patterns = change_patterns.get('failed_change_types', {})
        
        # Prepare data for visualization
        pattern_data = []
        
        for pattern, scores in successful_patterns.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            pattern_data.append({
                'pattern': pattern,
                'type': 'success',
                'count': len(scores),
                'avg_impact': avg_score,
                'color': '#2ecc71'
            })
        
        for pattern, scores in failed_patterns.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            pattern_data.append({
                'pattern': pattern,
                'type': 'failure',
                'count': len(scores),
                'avg_impact': avg_score,
                'color': '#e74c3c'
            })
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.2em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        .chart-title {{
            text-align: center;
            margin-bottom: 20px;
            color: #2c3e50;
            font-weight: bold;
        }}
        .patterns-list {{
            margin-top: 30px;
        }}
        .pattern-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 5px solid;
        }}
        .pattern-item.success {{
            background: #d5f4e6;
            border-left-color: #2ecc71;
        }}
        .pattern-item.failure {{
            background: #fceaea;
            border-left-color: #e74c3c;
        }}
        .pattern-name {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .pattern-stats {{
            display: flex;
            gap: 15px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Pattern Analysis</h1>
            <p>Successful vs Failed Change Patterns</p>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">Pattern Impact Distribution</div>
                <canvas id="impactChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">Success vs Failure Count</div>
                <canvas id="countChart"></canvas>
            </div>
        </div>
        
        <div class="patterns-list">
            <h3>Detailed Pattern Analysis</h3>
            <div id="patterns-container"></div>
        </div>
    </div>

    <script>
        const patternData = {json.dumps(pattern_data, indent=2)};
        
        // Impact scatter chart
        const impactCtx = document.getElementById('impactChart').getContext('2d');
        const impactChart = new Chart(impactCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Successful Patterns',
                    data: patternData.filter(p => p.type === 'success').map(p => ({{
                        x: p.count,
                        y: p.avg_impact
                    }})),
                    backgroundColor: '#2ecc71',
                    borderColor: '#27ae60',
                }}, {{
                    label: 'Failed Patterns',
                    data: patternData.filter(p => p.type === 'failure').map(p => ({{
                        x: p.count,
                        y: p.avg_impact
                    }})),
                    backgroundColor: '#e74c3c',
                    borderColor: '#c0392b',
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Pattern Frequency vs Impact'
                    }},
                    legend: {{
                        position: 'top'
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Frequency (count)'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Average Impact'
                        }}
                    }}
                }}
            }}
        }});
        
        // Count pie chart
        const countCtx = document.getElementById('countChart').getContext('2d');
        const successCount = patternData.filter(p => p.type === 'success').length;
        const failureCount = patternData.filter(p => p.type === 'failure').length;
        
        const countChart = new Chart(countCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Successful Patterns', 'Failed Patterns'],
                datasets: [{{
                    data: [successCount, failureCount],
                    backgroundColor: ['#2ecc71', '#e74c3c'],
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Render pattern list
        function renderPatterns() {{
            const container = document.getElementById('patterns-container');
            
            patternData.forEach(pattern => {{
                const item = document.createElement('div');
                item.className = `pattern-item ${{pattern.type}}`;
                
                item.innerHTML = `
                    <div class="pattern-name">${{pattern.pattern.replace(':', ' → ')}}</div>
                    <div class="pattern-stats">
                        <span>Count: ${{pattern.count}}</span>
                        <span>Avg Impact: ${{pattern.avg_impact.toFixed(3)}}</span>
                    </div>
                `;
                
                container.appendChild(item);
            }});
        }}
        
        document.addEventListener('DOMContentLoaded', renderPatterns);
    </script>
</body>
</html>'''