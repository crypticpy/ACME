"""Visualization components for deep analysis results."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from rich.console import Console

console = Console()


class DeepAnalysisVisualizer:
    """Creates visualizations for deep analysis results from GPT-4.1 feature extraction."""
    
    def __init__(self):
        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
        # Color schemes
        self.sentiment_colors = {
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'mixed': '#f39c12'
        }
        
        self.urgency_colors = {
            'high': '#e74c3c',
            'medium': '#f39c12',
            'low': '#3498db'
        }
        
        self.stakeholder_colors = {
            'artist': '#9b59b6',
            'organization': '#3498db',
            'resident': '#2ecc71',
            'educator': '#e67e22',
            'business_owner': '#34495e',
            'funder': '#e74c3c',
            'venue_operator': '#16a085',
            'unknown': '#95a5a6'
        }
    
    def create_question_dashboard(self, question_analysis: Dict[str, Any], 
                                output_path: Path) -> Path:
        """Create a comprehensive dashboard for a single question's analysis."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Theme Distribution',
                'Sentiment Breakdown',
                'Urgency Levels',
                'Stakeholder Participation'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'pie'}],
                [{'type': 'bar'}, {'type': 'bar'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Theme distribution
        themes = question_analysis.get('dominant_themes', [])[:10]
        if themes:
            theme_names = [t['theme'] for t in themes]
            theme_counts = [t['count'] for t in themes]
            
            fig.add_trace(
                go.Bar(
                    x=theme_counts,
                    y=theme_names,
                    orientation='h',
                    marker_color='#3498db',
                    text=[f"{t['percentage']:.1f}%" for t in themes],
                    textposition='auto',
                ),
                row=1, col=1
            )
        
        # Sentiment pie chart
        sentiment_data = question_analysis.get('sentiment_distribution', {})
        if sentiment_data:
            fig.add_trace(
                go.Pie(
                    labels=[k for k in sentiment_data.keys()],
                    values=[v for v in sentiment_data.values()],
                    marker_colors=[self.sentiment_colors.get(k, '#95a5a6') for k in sentiment_data.keys()],
                    textinfo='label+percent',
                    hole=0.3
                ),
                row=1, col=2
            )
        
        # Urgency distribution
        urgency_data = question_analysis.get('urgency_distribution', {})
        if urgency_data:
            fig.add_trace(
                go.Bar(
                    x=list(urgency_data.keys()),
                    y=list(urgency_data.values()),
                    marker_color=[self.urgency_colors.get(k, '#95a5a6') for k in urgency_data.keys()],
                    text=list(urgency_data.values()),
                    textposition='auto',
                ),
                row=2, col=1
            )
        
        # Stakeholder distribution
        stakeholder_data = question_analysis.get('stakeholder_distribution', {})
        if stakeholder_data:
            fig.add_trace(
                go.Bar(
                    x=list(stakeholder_data.keys()),
                    y=list(stakeholder_data.values()),
                    marker_color=[self.stakeholder_colors.get(k, '#95a5a6') for k in stakeholder_data.keys()],
                    text=list(stakeholder_data.values()),
                    textposition='auto',
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': f"Analysis Dashboard: {question_analysis.get('question_id', 'Unknown')}",
                'font': {'size': 20}
            },
            showlegend=False,
            height=800,
            template='plotly_white'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Count", row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=2)
        fig.update_yaxes(showticklabels=False, row=1, col=1)
        
        # Save
        fig.write_html(str(output_path))
        console.print(f"[green]✓[/green] Created question dashboard: {output_path.name}")
        
        return output_path
    
    def create_theme_evolution_chart(self, question_analyses: List[Dict[str, Any]], 
                                   output_path: Path) -> Path:
        """Create a chart showing how themes evolve across questions."""
        # Extract themes across all questions
        theme_matrix = {}
        question_ids = []
        
        for analysis in question_analyses:
            q_id = analysis.get('question_id', '')
            question_ids.append(q_id)
            
            for theme in analysis.get('dominant_themes', [])[:5]:  # Top 5 themes per question
                theme_name = theme['theme']
                if theme_name not in theme_matrix:
                    theme_matrix[theme_name] = {}
                theme_matrix[theme_name][q_id] = theme['percentage']
        
        # Create heatmap data
        themes = list(theme_matrix.keys())[:20]  # Limit to top 20 themes overall
        heatmap_data = []
        
        for theme in themes:
            row = []
            for q_id in question_ids:
                row.append(theme_matrix[theme].get(q_id, 0))
            heatmap_data.append(row)
        
        # Create figure
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=question_ids,
            y=themes,
            colorscale='Blues',
            text=[[f"{val:.1f}%" for val in row] for row in heatmap_data],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Theme Prevalence (%)")
        ))
        
        fig.update_layout(
            title="Theme Evolution Across Questions",
            xaxis_title="Question ID",
            yaxis_title="Theme",
            height=600 + (len(themes) * 20),
            template='plotly_white'
        )
        
        fig.write_html(str(output_path))
        console.print(f"[green]✓[/green] Created theme evolution chart: {output_path.name}")
        
        return output_path
    
    def create_stakeholder_comparison_matrix(self, question_analyses: List[Dict[str, Any]], 
                                           output_path: Path) -> Path:
        """Create a matrix comparing stakeholder responses across questions."""
        # Prepare data
        stakeholder_types = ['artist', 'organization', 'resident', 'educator', 
                           'business_owner', 'funder', 'venue_operator']
        question_ids = [a.get('question_id', '') for a in question_analyses]
        
        # Create percentage matrix
        matrix_data = []
        
        for q_analysis in question_analyses:
            stakeholder_dist = q_analysis.get('stakeholder_distribution', {})
            total = sum(stakeholder_dist.values()) if stakeholder_dist else 1
            
            row = []
            for stakeholder in stakeholder_types:
                count = stakeholder_dist.get(stakeholder, 0)
                percentage = (count / total * 100) if total > 0 else 0
                row.append(percentage)
            
            matrix_data.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=stakeholder_types,
            y=question_ids,
            colorscale='Viridis',
            text=[[f"{val:.1f}%" for val in row] for row in matrix_data],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Participation Rate (%)")
        ))
        
        fig.update_layout(
            title="Stakeholder Participation Matrix by Question",
            xaxis_title="Stakeholder Type",
            yaxis_title="Question ID",
            height=400 + (len(question_ids) * 30),
            template='plotly_white',
            xaxis={'tickangle': -45}
        )
        
        fig.write_html(str(output_path))
        console.print(f"[green]✓[/green] Created stakeholder comparison matrix: {output_path.name}")
        
        return output_path
    
    def create_sentiment_urgency_scatter(self, all_themes: List[Dict[str, Any]], 
                                       output_path: Path) -> Path:
        """Create a scatter plot showing sentiment vs urgency for themes."""
        # Prepare data
        theme_names = []
        urgency_scores = []
        sentiment_scores = []
        sizes = []
        colors = []
        
        sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1, 'mixed': 0}
        
        for theme in all_themes[:50]:  # Top 50 themes
            theme_names.append(theme['theme'])
            urgency_scores.append(theme.get('urgency_score', 0.5))
            
            # Calculate sentiment score
            sent_dist = theme.get('sentiment_distribution', {})
            total = sum(sent_dist.values()) if sent_dist else 1
            sent_score = 0
            for sent, count in sent_dist.items():
                sent_score += sentiment_map.get(sent, 0) * (count / total)
            sentiment_scores.append(sent_score)
            
            sizes.append(theme.get('count', 1))
            
            # Color by dominant sentiment
            dominant_sent = max(sent_dist.items(), key=lambda x: x[1])[0] if sent_dist else 'neutral'
            colors.append(self.sentiment_colors.get(dominant_sent, '#95a5a6'))
        
        # Create scatter plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sentiment_scores,
            y=urgency_scores,
            mode='markers+text',
            marker=dict(
                size=[s/10 for s in sizes],  # Scale down sizes
                color=colors,
                line=dict(width=1, color='white'),
                sizemode='diameter',
                sizemin=5
            ),
            text=theme_names,
            textposition="top center",
            textfont=dict(size=9),
            hovertemplate='<b>%{text}</b><br>' +
                         'Sentiment Score: %{x:.2f}<br>' +
                         'Urgency Score: %{y:.2f}<br>' +
                         'Mentions: %{marker.size}<br>' +
                         '<extra></extra>'
        ))
        
        # Add quadrant lines
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=0.5, y=0.9, text="Positive & Urgent", showarrow=False, 
                          font=dict(size=12, color="gray"))
        fig.add_annotation(x=-0.5, y=0.9, text="Negative & Urgent", showarrow=False,
                          font=dict(size=12, color="gray"))
        fig.add_annotation(x=0.5, y=0.1, text="Positive & Less Urgent", showarrow=False,
                          font=dict(size=12, color="gray"))
        fig.add_annotation(x=-0.5, y=0.1, text="Negative & Less Urgent", showarrow=False,
                          font=dict(size=12, color="gray"))
        
        fig.update_layout(
            title="Theme Analysis: Sentiment vs Urgency",
            xaxis_title="Sentiment Score (Negative ← → Positive)",
            yaxis_title="Urgency Score (Low → High)",
            height=800,
            width=1200,
            template='plotly_white',
            xaxis=dict(range=[-1.2, 1.2]),
            yaxis=dict(range=[-0.1, 1.1])
        )
        
        fig.write_html(str(output_path))
        console.print(f"[green]✓[/green] Created sentiment-urgency scatter: {output_path.name}")
        
        return output_path
    
    def create_program_feedback_sunburst(self, program_analyses: Dict[str, Dict[str, Any]], 
                                       output_path: Path) -> Path:
        """Create a sunburst chart showing program feedback hierarchy."""
        labels = []
        parents = []
        values = []
        colors = []
        
        # Root
        labels.append("All Programs")
        parents.append("")
        values.append(sum(p.get('mention_count', 0) for p in program_analyses.values()))
        colors.append("#3498db")
        
        # Programs
        for program_name, program_data in program_analyses.items():
            labels.append(program_name)
            parents.append("All Programs")
            values.append(program_data.get('mention_count', 0))
            colors.append("#2980b9")
            
            # Sentiment categories
            sentiment_data = program_data.get('sentiment_summary', {})
            for sentiment, count in sentiment_data.items():
                if count > 0:
                    label = f"{program_name} - {sentiment}"
                    labels.append(label)
                    parents.append(program_name)
                    values.append(count)
                    colors.append(self.sentiment_colors.get(sentiment, '#95a5a6'))
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            textinfo="label+percent parent"
        ))
        
        fig.update_layout(
            title="Program Feedback Distribution by Sentiment",
            height=800,
            width=800,
            template='plotly_white'
        )
        
        fig.write_html(str(output_path))
        console.print(f"[green]✓[/green] Created program feedback sunburst: {output_path.name}")
        
        return output_path
    
    def create_insight_network_graph(self, cross_question_insights: List[Dict[str, Any]], 
                                   output_path: Path) -> Path:
        """Create a network graph showing connections between insights and questions."""
        # Prepare node data
        nodes = []
        edges = []
        
        # Add insight nodes
        for i, insight in enumerate(cross_question_insights):
            nodes.append({
                'id': f'insight_{i}',
                'label': insight['insight_type'],
                'group': 'insight',
                'size': insight.get('evidence_count', 10),
                'title': insight['description']
            })
            
            # Add edges to supporting questions
            for q_id in insight.get('supporting_questions', []):
                edges.append({
                    'from': f'insight_{i}',
                    'to': q_id,
                    'weight': insight.get('confidence', 0.5)
                })
        
        # Add question nodes
        unique_questions = set()
        for insight in cross_question_insights:
            unique_questions.update(insight.get('supporting_questions', []))
        
        for q_id in unique_questions:
            nodes.append({
                'id': q_id,
                'label': q_id,
                'group': 'question',
                'size': 20
            })
        
        # Create plotly network graph
        edge_trace = []
        for edge in edges:
            # Find node positions (simplified - in real implementation would use layout algorithm)
            from_idx = next(i for i, n in enumerate(nodes) if n['id'] == edge['from'])
            to_idx = next(i for i, n in enumerate(nodes) if n['id'] == edge['to'])
            
            edge_trace.append(go.Scatter(
                x=[from_idx, to_idx, None],
                y=[from_idx, to_idx, None],
                mode='lines',
                line=dict(width=edge['weight'] * 5, color='#888'),
                hoverinfo='none'
            ))
        
        node_trace = go.Scatter(
            x=[i for i in range(len(nodes))],
            y=[i * 2 for i in range(len(nodes))],
            mode='markers+text',
            text=[n['label'] for n in nodes],
            textposition="middle right",
            marker=dict(
                size=[n['size'] for n in nodes],
                color=['#e74c3c' if n['group'] == 'insight' else '#3498db' for n in nodes],
                line=dict(width=2, color='white')
            ),
            hovertext=[n.get('title', n['label']) for n in nodes],
            hoverinfo='text'
        )
        
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title="Cross-Question Insights Network",
            showlegend=False,
            hovermode='closest',
            height=800,
            template='plotly_white',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        fig.write_html(str(output_path))
        console.print(f"[green]✓[/green] Created insight network graph: {output_path.name}")
        
        return output_path
    
    def create_executive_summary_infographic(self, synthesis_results: Dict[str, Any], 
                                           output_path: Path) -> Path:
        """Create an executive summary infographic."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('ACME Cultural Funding Analysis - Executive Summary', fontsize=20, fontweight='bold')
        
        # 1. Key Metrics (top left)
        ax1.axis('off')
        metrics = synthesis_results.get('metadata', {})
        metrics_text = f"""
        Total Responses Analyzed: {metrics.get('total_responses', 0):,}
        Questions Analyzed: {metrics.get('questions_analyzed', 0)}
        Recurring Themes: {len(synthesis_results.get('recurring_themes', {}))}
        Systemic Issues: {len(synthesis_results.get('systemic_issues', []))}
        """
        ax1.text(0.1, 0.5, metrics_text, fontsize=14, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.5))
        ax1.set_title('Analysis Scope', fontsize=16, fontweight='bold')
        
        # 2. Top Themes (top right)
        themes = list(synthesis_results.get('recurring_themes', {}).items())[:5]
        if themes:
            theme_names = [t[0] for t in themes]
            theme_counts = [t[1]['total_mentions'] for t in themes]
            
            ax2.barh(theme_names, theme_counts, color='#3498db')
            ax2.set_xlabel('Total Mentions')
            ax2.set_title('Top 5 Recurring Themes', fontsize=16, fontweight='bold')
            
            # Add value labels
            for i, v in enumerate(theme_counts):
                ax2.text(v + 5, i, str(v), va='center')
        else:
            ax2.axis('off')
        
        # 3. Sentiment Overview (bottom left)
        sentiment_data = synthesis_results.get('sentiment_patterns', {}).get('overall_sentiment', {})
        if sentiment_data:
            sizes = list(sentiment_data.values())
            labels = [f"{k}\n{v:.1f}%" for k, v in sentiment_data.items()]
            colors = [self.sentiment_colors.get(k.split('\n')[0], '#95a5a6') for k in labels]
            
            ax3.pie(sizes, labels=labels, colors=colors, autopct='', startangle=90)
            ax3.set_title('Overall Sentiment Distribution', fontsize=16, fontweight='bold')
        else:
            ax3.axis('off')
        
        # 4. Strategic Insights (bottom right)
        ax4.axis('off')
        insights = synthesis_results.get('strategic_insights', [])[:3]
        if insights:
            insights_text = "Top Strategic Insights:\n\n"
            for i, insight in enumerate(insights, 1):
                # Wrap text for better display
                wrapped = '\n   '.join([insight[j:j+50] for j in range(0, len(insight), 50)])
                insights_text += f"{i}. {wrapped}\n\n"
            
            ax4.text(0.05, 0.95, insights_text, fontsize=11, verticalalignment='top',
                    wrap=True, bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.5))
            ax4.set_title('Strategic Insights', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(str(output_path), dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]✓[/green] Created executive summary infographic: {output_path.name}")
        
        return output_path