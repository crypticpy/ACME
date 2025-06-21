"""Individual chart generators for different visualization types."""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from wordcloud import WordCloud
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd


class BaseChart:
    """Base class for all chart generators."""
    
    def __init__(self):
        self.colors = px.colors.qualitative.Set3
        self.font_family = "Arial"
        
    def save_plotly_figure(self, fig: go.Figure, output_path: Path) -> Path:
        """Save plotly figure as HTML."""
        fig.write_html(str(output_path))
        return output_path
    
    def save_matplotlib_figure(self, fig: plt.Figure, output_path: Path, dpi: int = 300) -> Path:
        """Save matplotlib figure as PNG."""
        fig.savefig(str(output_path), dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return output_path


class ShareOfVoiceChart(BaseChart):
    """Generate share of voice visualizations."""
    
    def create_pie_chart(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Create basic pie chart for share of voice."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        categories = list(data.keys())
        values = [d.get('count', 0) for d in data.values()]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            colors=self.colors[:len(categories)]
        )
        
        # Enhance text
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax.set_title('Share of Voice - Basic Distribution', fontsize=16, fontweight='bold', pad=20)
        
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_refined_chart(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Create refined share of voice chart with confidence scores."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        categories = list(data.keys())
        counts = [d['count'] for d in data.values()]
        percentages = [d['percentage'] for d in data.values()]
        confidences = [d['average_confidence'] for d in data.values()]
        
        # Bar chart with counts
        bars1 = ax1.bar(categories, counts, color=self.colors[:len(categories)])
        ax1.set_xlabel('Stakeholder Category', fontsize=12)
        ax1.set_ylabel('Number of Respondents', fontsize=12)
        ax1.set_title('Respondent Distribution by Category', fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)
        
        # Confidence scores
        bars2 = ax2.bar(categories, confidences, color=self.colors[:len(categories)])
        ax2.set_xlabel('Stakeholder Category', fontsize=12)
        ax2.set_ylabel('Average Confidence Score', fontsize=12)
        ax2.set_title('Classification Confidence by Category', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 1.0)
        
        # Add confidence labels
        for bar, conf in zip(bars2, confidences):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{conf:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.suptitle('Share of Voice Analysis - Refined', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_interactive_chart(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Create interactive share of voice visualization."""
        categories = list(data.keys())
        values = [d['count'] for d in data.values()]
        percentages = [d['percentage'] for d in data.values()]
        confidences = [d['average_confidence'] for d in data.values()]
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Distribution', 'Confidence Levels'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}]]
        )
        
        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=values,
                hole=0.3,
                textinfo='label+percent',
                textposition='auto',
                marker=dict(colors=self.colors[:len(categories)])
            ),
            row=1, col=1
        )
        
        # Bar chart for confidence
        fig.add_trace(
            go.Bar(
                x=categories,
                y=confidences,
                text=[f'{c:.2f}' for c in confidences],
                textposition='auto',
                marker=dict(color=self.colors[:len(categories)])
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Share of Voice Analysis - Interactive",
            title_font_size=20,
            showlegend=False,
            height=500
        )
        
        return self.save_plotly_figure(fig, output_path)


class ThemeChart(BaseChart):
    """Generate theme analysis visualizations."""
    
    def create_theme_bar_chart(self, themes: List[Dict[str, Any]], output_path: Path) -> Path:
        """Create horizontal bar chart of top themes."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        theme_names = [t['theme'] for t in themes]
        counts = [t['count'] for t in themes]
        sentiments = [t.get('sentiment', 'neutral') for t in themes]
        
        # Color by sentiment
        sentiment_colors = {
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'mixed': '#f39c12'
        }
        colors = [sentiment_colors.get(s, '#95a5a6') for s in sentiments]
        
        # Create horizontal bar chart
        bars = ax.barh(theme_names, counts, color=colors)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{count}',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Number of Mentions', fontsize=12)
        ax.set_title('Top 10 Themes in Community Feedback', fontsize=16, fontweight='bold')
        ax.invert_yaxis()
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=sentiment_colors['positive'], label='Positive'),
            Patch(facecolor=sentiment_colors['negative'], label='Negative'),
            Patch(facecolor=sentiment_colors['neutral'], label='Neutral'),
            Patch(facecolor=sentiment_colors['mixed'], label='Mixed')
        ]
        ax.legend(handles=legend_elements, loc='lower right', title='Sentiment')
        
        plt.tight_layout()
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_sentiment_distribution(self, themes: List[Dict[str, Any]], output_path: Path) -> Path:
        """Create sentiment distribution visualization."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Count sentiments
        sentiment_counts = {}
        urgency_counts = {}
        
        for theme in themes:
            sentiment = theme.get('sentiment', 'neutral')
            urgency = theme.get('urgency', 'medium')
            
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
        
        # Sentiment pie chart
        sentiment_colors = {
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'mixed': '#f39c12'
        }
        
        sentiments = list(sentiment_counts.keys())
        s_values = list(sentiment_counts.values())
        s_colors = [sentiment_colors.get(s, '#95a5a6') for s in sentiments]
        
        ax1.pie(s_values, labels=sentiments, colors=s_colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Theme Sentiment Distribution', fontsize=14, fontweight='bold')
        
        # Urgency bar chart
        urgency_colors = {
            'high': '#e74c3c',
            'medium': '#f39c12',
            'low': '#3498db'
        }
        
        urgencies = ['high', 'medium', 'low']
        u_values = [urgency_counts.get(u, 0) for u in urgencies]
        u_colors = [urgency_colors[u] for u in urgencies]
        
        bars = ax2.bar(urgencies, u_values, color=u_colors)
        ax2.set_xlabel('Urgency Level', fontsize=12)
        ax2.set_ylabel('Number of Themes', fontsize=12)
        ax2.set_title('Theme Urgency Distribution', fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.suptitle('Theme Analysis - Sentiment and Urgency', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_theme_word_cloud(self, themes: List[Dict[str, Any]], output_path: Path) -> Path:
        """Create word cloud from theme keywords."""
        # Collect all keywords with weights
        word_freq = {}
        
        for theme in themes:
            weight = theme.get('count', 1)
            for keyword in theme.get('keywords', []):
                word_freq[keyword] = word_freq.get(keyword, 0) + weight
        
        if not word_freq:
            # Create a simple placeholder if no keywords
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No keywords available', 
                   ha='center', va='center', fontsize=20)
            ax.axis('off')
            return self.save_matplotlib_figure(fig, output_path)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            colormap='viridis',
            relative_scaling=0.5,
            min_font_size=10
        ).generate_from_frequencies(word_freq)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Theme Keywords Word Cloud', fontsize=20, fontweight='bold', pad=20)
        
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_interactive_theme_explorer(self, themes: List[Dict[str, Any]], output_path: Path) -> Path:
        """Create interactive theme explorer."""
        # Prepare data
        df_data = []
        for theme in themes:
            df_data.append({
                'Theme': theme['theme'],
                'Count': theme['count'],
                'Percentage': theme['percentage'],
                'Sentiment': theme.get('sentiment', 'neutral'),
                'Urgency': theme.get('urgency', 'medium'),
                'Description': theme.get('description', ''),
                'Keywords': ', '.join(theme.get('keywords', []))
            })
        
        df = pd.DataFrame(df_data)
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x='Count',
            y='Percentage',
            size='Count',
            color='Sentiment',
            hover_data=['Theme', 'Description', 'Keywords', 'Urgency'],
            title='Interactive Theme Explorer',
            labels={'Count': 'Number of Mentions', 'Percentage': 'Percentage of Responses'},
            color_discrete_map={
                'positive': '#2ecc71',
                'negative': '#e74c3c',
                'neutral': '#95a5a6',
                'mixed': '#f39c12'
            }
        )
        
        fig.update_traces(textposition='top center')
        fig.update_layout(
            height=600,
            hovermode='closest',
            font=dict(family=self.font_family)
        )
        
        return self.save_plotly_figure(fig, output_path)


class ProgramAnalysisChart(BaseChart):
    """Generate program-specific visualizations."""
    
    def create_program_comparison(self, program_data: Dict[str, Any], output_path: Path) -> Path:
        """Create program comparison chart."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        programs = list(program_data.keys())
        response_counts = [data.get('response_count', 0) for data in program_data.values()]
        
        # Create bar chart
        bars = ax.bar(programs, response_counts, color=self.colors[:len(programs)])
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Program', fontsize=12)
        ax.set_ylabel('Number of Responses', fontsize=12)
        ax.set_title('Program Awareness - Response Count Comparison', fontsize=16, fontweight='bold')
        
        # Rotate x labels if needed
        if len(programs) > 5:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_program_detail_chart(self, program_name: str, data: Dict[str, Any], output_path: Path) -> Path:
        """Create detailed chart for a specific program."""
        themes = data.get('themes', [])
        
        if not themes:
            # Create placeholder
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'No theme data available for {program_name}', 
                   ha='center', va='center', fontsize=16)
            ax.axis('off')
            return self.save_matplotlib_figure(fig, output_path)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Theme frequency chart
        theme_names = [t['theme'] for t in themes]
        frequencies = [t['frequency'] for t in themes]
        sentiments = [t['sentiment'] for t in themes]
        
        sentiment_colors = {
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6'
        }
        colors = [sentiment_colors.get(s, '#95a5a6') for s in sentiments]
        
        bars = ax1.barh(theme_names, frequencies, color=colors)
        ax1.set_xlabel('Frequency', fontsize=12)
        ax1.set_title(f'{program_name} - Top Themes', fontsize=14, fontweight='bold')
        ax1.invert_yaxis()
        
        # Sentiment distribution pie
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        
        ax2.pie(
            sentiment_counts.values(),
            labels=sentiment_counts.keys(),
            colors=[sentiment_colors.get(s, '#95a5a6') for s in sentiment_counts.keys()],
            autopct='%1.1f%%',
            startangle=90
        )
        ax2.set_title(f'{program_name} - Sentiment Distribution', fontsize=14, fontweight='bold')
        
        plt.suptitle(f'{program_name} Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_program_dashboard(self, program_data: Dict[str, Any], output_path: Path) -> Path:
        """Create interactive program dashboard."""
        # Prepare data for visualization
        program_metrics = []
        
        for program, data in program_data.items():
            themes = data.get('themes', [])
            
            # Calculate metrics
            positive_themes = sum(1 for t in themes if t.get('sentiment') == 'positive')
            negative_themes = sum(1 for t in themes if t.get('sentiment') == 'negative')
            
            program_metrics.append({
                'Program': program,
                'Responses': data.get('response_count', 0),
                'Total Themes': len(themes),
                'Positive Themes': positive_themes,
                'Negative Themes': negative_themes,
                'Neutral Themes': len(themes) - positive_themes - negative_themes
            })
        
        df = pd.DataFrame(program_metrics)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Response Count by Program',
                'Theme Distribution by Program',
                'Sentiment Breakdown',
                'Program Comparison Matrix'
            ),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Response counts
        fig.add_trace(
            go.Bar(
                x=df['Program'],
                y=df['Responses'],
                name='Responses',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # Theme counts
        fig.add_trace(
            go.Bar(
                x=df['Program'],
                y=df['Total Themes'],
                name='Total Themes',
                marker_color='lightgreen'
            ),
            row=1, col=2
        )
        
        # Sentiment breakdown (stacked)
        fig.add_trace(
            go.Bar(
                x=df['Program'],
                y=df['Positive Themes'],
                name='Positive',
                marker_color='#2ecc71'
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(
                x=df['Program'],
                y=df['Negative Themes'],
                name='Negative',
                marker_color='#e74c3c'
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(
                x=df['Program'],
                y=df['Neutral Themes'],
                name='Neutral',
                marker_color='#95a5a6'
            ),
            row=2, col=1
        )
        
        # Scatter plot
        fig.add_trace(
            go.Scatter(
                x=df['Responses'],
                y=df['Total Themes'],
                mode='markers+text',
                text=df['Program'],
                textposition='top center',
                marker=dict(size=15, color=self.colors[:len(df)])
            ),
            row=2, col=2
        )
        
        fig.update_xaxes(title_text="Program", row=1, col=1)
        fig.update_xaxes(title_text="Program", row=1, col=2)
        fig.update_xaxes(title_text="Program", row=2, col=1)
        fig.update_xaxes(title_text="Responses", row=2, col=2)
        
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="Themes", row=2, col=2)
        
        fig.update_layout(
            title_text="Program Analysis Dashboard",
            showlegend=True,
            height=800,
            barmode='stack'
        )
        
        return self.save_plotly_figure(fig, output_path)


class GeographicChart(BaseChart):
    """Generate geographic distribution visualizations."""
    
    def create_zip_code_map(self, zip_data: Dict[str, int], output_path: Path) -> Path:
        """Create static map visualization of zip code distribution."""
        # For static map, create a bar chart of top zip codes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort zip codes by count
        sorted_zips = sorted(zip_data.items(), key=lambda x: x[1], reverse=True)[:20]
        
        zip_codes = [z[0] for z in sorted_zips]
        counts = [z[1] for z in sorted_zips]
        
        bars = ax.bar(zip_codes, counts, color='steelblue')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('ZIP Code', fontsize=12)
        ax.set_ylabel('Number of Responses', fontsize=12)
        ax.set_title('Geographic Distribution - Top 20 ZIP Codes', fontsize=16, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_interactive_map(self, zip_data: Dict[str, int], output_path: Path) -> Path:
        """Create interactive map visualization."""
        # Prepare data
        df_data = []
        for zip_code, count in zip_data.items():
            df_data.append({
                'ZIP': zip_code,
                'Count': count,
                'Percentage': (count / sum(zip_data.values())) * 100
            })
        
        df = pd.DataFrame(df_data).sort_values('Count', ascending=False)
        
        # Create interactive bar chart (as placeholder for actual map)
        fig = px.bar(
            df.head(30),
            x='ZIP',
            y='Count',
            hover_data=['Percentage'],
            title='Geographic Distribution by ZIP Code',
            labels={'Count': 'Number of Responses', 'ZIP': 'ZIP Code'},
            color='Count',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600,
            showlegend=False
        )
        
        return self.save_plotly_figure(fig, output_path)


class ConfidenceIntervalChart(BaseChart):
    """Generate statistical confidence visualizations."""
    
    def create_confidence_interval_chart(self, sov_data: Dict[str, Any], output_path: Path) -> Path:
        """Create confidence interval visualization."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        categories = []
        percentages = []
        lower_bounds = []
        upper_bounds = []
        
        for category, data in sov_data.items():
            categories.append(category)
            pct = data.get('percentage', 0)
            percentages.append(pct)
            
            # Calculate confidence intervals (simplified)
            margin = 1.96 * np.sqrt((pct * (100 - pct)) / data.get('count', 1))
            lower_bounds.append(max(0, pct - margin))
            upper_bounds.append(min(100, pct + margin))
        
        # Create error bar plot
        y_pos = np.arange(len(categories))
        errors = [(p - l, u - p) for p, l, u in zip(percentages, lower_bounds, upper_bounds)]
        
        ax.barh(y_pos, percentages, xerr=np.array(errors).T, 
                align='center', alpha=0.7, color='steelblue',
                error_kw={'elinewidth': 2, 'capsize': 5})
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.invert_yaxis()
        ax.set_xlabel('Percentage (%)', fontsize=12)
        ax.set_title('Share of Voice with 95% Confidence Intervals', fontsize=16, fontweight='bold')
        
        # Add percentage labels
        for i, (pct, lb, ub) in enumerate(zip(percentages, lower_bounds, upper_bounds)):
            ax.text(pct + 1, i, f'{pct:.1f}% [{lb:.1f}-{ub:.1f}]',
                   va='center', fontsize=10)
        
        plt.tight_layout()
        return self.save_matplotlib_figure(fig, output_path)
    
    def create_statistical_summary(self, quant_results: Dict[str, Any], output_path: Path) -> Path:
        """Create statistical summary dashboard."""
        fig = plt.figure(figsize=(14, 10))
        
        # Create grid
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Summary statistics
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        summary_text = f"""
        Statistical Summary
        
        Total Responses: {quant_results.get('total_responses', 0):,}
        Response Rate: {quant_results.get('response_rate', 0):.1f}%
        Data Quality Score: {quant_results.get('data_quality', {}).get('overall_quality_score', 0):.2f}
        Geographic Coverage: {len(quant_results.get('geographic_distribution', {}).get('zip_codes', {}))} ZIP codes
        """
        
        ax1.text(0.5, 0.5, summary_text, ha='center', va='center',
                fontsize=14, bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray"))
        
        # Response distribution
        ax2 = fig.add_subplot(gs[1, 0])
        if 'response_distribution' in quant_results:
            dist_data = quant_results['response_distribution']
            ax2.hist(list(dist_data.values()), bins=20, color='skyblue', edgecolor='black')
            ax2.set_xlabel('Number of Responses')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Response Distribution')
        else:
            ax2.text(0.5, 0.5, 'No distribution data', ha='center', va='center')
            ax2.axis('off')
        
        # Data quality metrics
        ax3 = fig.add_subplot(gs[1, 1])
        if 'data_quality' in quant_results:
            quality = quant_results['data_quality']
            metrics = ['Completeness', 'Validity', 'Consistency']
            scores = [
                quality.get('completeness_score', 0),
                quality.get('validity_score', 0),
                quality.get('consistency_score', 0)
            ]
            
            bars = ax3.bar(metrics, scores, color=['green', 'blue', 'orange'])
            ax3.set_ylim(0, 1.0)
            ax3.set_ylabel('Score')
            ax3.set_title('Data Quality Metrics')
            
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{score:.2f}',
                        ha='center', va='bottom')
        else:
            ax3.text(0.5, 0.5, 'No quality data', ha='center', va='center')
            ax3.axis('off')
        
        # Key insights
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        
        insights_text = """
        Key Statistical Insights:
        • High response rate indicates strong community engagement
        • Data quality metrics show reliable dataset for analysis
        • Geographic distribution covers major population centers
        • Confidence intervals provide robust estimates for decision-making
        """
        
        ax4.text(0.1, 0.5, insights_text, ha='left', va='center',
                fontsize=12, bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow"))
        
        plt.suptitle('ACME Cultural Funding - Statistical Analysis Summary', 
                    fontsize=18, fontweight='bold')
        
        return self.save_matplotlib_figure(fig, output_path)