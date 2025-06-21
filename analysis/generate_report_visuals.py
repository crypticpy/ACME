#!/usr/bin/env python3
"""Generate sophisticated visualizations for the comprehensive report."""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Modern color palette
COLORS = {
    'primary': '#1E3A8A',      # Deep blue
    'secondary': '#3B82F6',     # Bright blue
    'accent': '#F59E0B',        # Amber
    'negative': '#DC2626',      # Red
    'positive': '#10B981',      # Emerald
    'neutral': '#6B7280',       # Gray
    'mixed': '#8B5CF6',         # Purple
    'background': '#F9FAFB',    # Light gray
    'text': '#111827',          # Near black
    'chart_colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']
}

# Set up matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.titlesize': 18,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2
})

def load_data():
    """Load the analysis results."""
    results_path = Path("data/results/deep_analysis/deep_analysis_results_20250621_022354.json")
    with open(results_path, 'r') as f:
        return json.load(f)

def create_sentiment_overview(data):
    """Create an elegant sentiment overview visualization."""
    # Prepare data
    sentiments = []
    for q in data['question_analyses']:
        total = sum(q['sentiment_distribution'].values())
        for sentiment, count in q['sentiment_distribution'].items():
            sentiments.append({
                'Question': q['question_id'].replace('_', ' ').title(),
                'Sentiment': sentiment.capitalize(),
                'Count': count,
                'Percentage': (count/total)*100 if total > 0 else 0
            })
    
    df = pd.DataFrame(sentiments)
    
    # Create figure
    fig = go.Figure()
    
    # Define colors for sentiments
    sentiment_colors = {
        'Positive': COLORS['positive'],
        'Negative': COLORS['negative'],
        'Neutral': COLORS['neutral'],
        'Mixed': COLORS['mixed']
    }
    
    # Add bars for each sentiment
    for sentiment in ['Negative', 'Neutral', 'Mixed', 'Positive']:
        df_filtered = df[df['Sentiment'] == sentiment]
        fig.add_trace(go.Bar(
            name=sentiment,
            x=df_filtered['Question'],
            y=df_filtered['Percentage'],
            marker_color=sentiment_colors.get(sentiment, COLORS['neutral']),
            hovertemplate='%{y:.1f}%<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Community Sentiment by Question',
            'font': {'size': 24, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': '',
            'tickangle': -25,
            'tickfont': {'size': 12}
        },
        yaxis={
            'title': 'Percentage of Responses',
            'tickfont': {'size': 12},
            'ticksuffix': '%'
        },
        barmode='stack',
        height=500,
        width=1000,
        margin=dict(l=80, r=40, t=80, b=100),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 14},
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.3,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 12}
        },
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial, sans-serif"
        )
    )
    
    # Add subtle gridlines
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

def create_urgency_heatmap(data):
    """Create a sophisticated urgency heatmap."""
    # Prepare data
    questions = []
    themes_set = set()
    
    for q in data['question_analyses']:
        for theme in q['dominant_themes'][:5]:  # Top 5 themes per question
            themes_set.add(theme['theme'])
    
    themes_list = sorted(list(themes_set))
    
    # Create matrix
    matrix = []
    question_labels = []
    
    for q in data['question_analyses']:
        question_labels.append(q['question_id'].replace('_', ' ').title())
        row = []
        theme_dict = {t['theme']: t.get('urgency_score', 0.5) for t in q['dominant_themes']}
        for theme in themes_list:
            row.append(theme_dict.get(theme, 0))
        matrix.append(row)
    
    # Create figure
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[t.replace('_', ' ').title() for t in themes_list],
        y=question_labels,
        colorscale=[
            [0, '#E5F5F9'],
            [0.25, '#99D8C9'],
            [0.5, '#FDAE6B'],
            [0.75, '#E6550D'],
            [1, '#A63603']
        ],
        hovertemplate='Question: %{y}<br>Theme: %{x}<br>Urgency: %{z:.2f}<extra></extra>',
        colorbar=dict(
            title="Urgency Score",
            titleside="right",
            tickmode="linear",
            tick0=0,
            dtick=0.25,
            thickness=15,
            len=0.7,
            x=1.02
        )
    ))
    
    fig.update_layout(
        title={
            'text': 'Theme Urgency Heatmap Across Questions',
            'font': {'size': 24, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': 'Themes',
            'tickangle': -45,
            'tickfont': {'size': 11},
            'side': 'bottom'
        },
        yaxis={
            'title': 'Questions',
            'tickfont': {'size': 12}
        },
        height=600,
        width=1200,
        margin=dict(l=200, r=100, t=80, b=150),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 14}
    )
    
    return fig

def create_theme_network(data):
    """Create an interactive theme network visualization."""
    # Extract cross-question themes
    themes = data['cross_question_synthesis']['recurring_themes']
    
    # Create nodes
    nodes = []
    edges = []
    
    # Add theme nodes
    for i, (theme, info) in enumerate(themes.items()):
        if info['total_mentions'] > 10:  # Filter significant themes
            nodes.append({
                'id': theme,
                'label': theme.replace('_', ' ').title(),
                'size': np.sqrt(info['total_mentions']) * 5,
                'color': COLORS['chart_colors'][i % len(COLORS['chart_colors'])],
                'mentions': info['total_mentions']
            })
    
    # Create edge list (simplified for visualization)
    node_ids = [n['id'] for n in nodes]
    for i, node1 in enumerate(node_ids):
        for j, node2 in enumerate(node_ids[i+1:], i+1):
            # Create edges between themes that appear in same questions
            q1 = set(themes[node1].get('question_ids', []))
            q2 = set(themes[node2].get('question_ids', []))
            overlap = len(q1.intersection(q2))
            if overlap > 0:
                edges.append({
                    'source': i,
                    'target': j,
                    'weight': overlap
                })
    
    # Create Plotly network graph
    edge_trace = []
    for edge in edges:
        x0, y0 = nodes[edge['source']]['size'], nodes[edge['source']]['size']
        x1, y1 = nodes[edge['target']]['size'], nodes[edge['target']]['size']
        
        # Simple circular layout
        angle0 = 2 * np.pi * edge['source'] / len(nodes)
        angle1 = 2 * np.pi * edge['target'] / len(nodes)
        
        x0, y0 = np.cos(angle0), np.sin(angle0)
        x1, y1 = np.cos(angle1), np.sin(angle1)
        
        edge_trace.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=edge['weight']*0.5, color='rgba(125,125,125,0.3)'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for i, node in enumerate(nodes):
        angle = 2 * np.pi * i / len(nodes)
        node_x.append(np.cos(angle))
        node_y.append(np.sin(angle))
        node_text.append(f"{node['label']}<br>{node['mentions']} mentions")
        node_size.append(node['size'])
        node_color.append(node['color'])
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[n['label'] for n in nodes],
        textposition="top center",
        textfont=dict(size=10),
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=edge_trace + [node_trace])
    
    fig.update_layout(
        title={
            'text': 'Interconnected Themes Network',
            'font': {'size': 24, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        height=800,
        width=1000,
        margin=dict(l=40, r=40, t=80, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

def create_stakeholder_sunburst(data):
    """Create a hierarchical stakeholder visualization."""
    # Prepare hierarchical data
    stakeholder_data = []
    
    for q in data['question_analyses']:
        q_name = q['question_id'].replace('_', ' ').title()
        for stakeholder, count in q['stakeholder_distribution'].items():
            if count > 0:
                stakeholder_data.append({
                    'question': q_name,
                    'stakeholder': stakeholder.replace('_', ' ').title(),
                    'count': count
                })
    
    df = pd.DataFrame(stakeholder_data)
    
    # Create sunburst
    fig = px.sunburst(
        df,
        path=['stakeholder', 'question'],
        values='count',
        color='count',
        color_continuous_scale=[
            [0, '#E8F5E9'],
            [0.5, '#66BB6A'],
            [1, '#2E7D32']
        ],
        title='Stakeholder Distribution Across Questions'
    )
    
    fig.update_layout(
        title={
            'font': {'size': 24, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=700,
        width=700,
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 14}
    )
    
    return fig

def create_program_impact_radar(data):
    """Create a radar chart for program analysis."""
    programs = data.get('program_analyses', {})
    
    # Select top programs
    top_programs = sorted(programs.items(), 
                         key=lambda x: x[1].get('mention_count', 0), 
                         reverse=True)[:6]
    
    # Prepare data
    categories = ['Mentions', 'Positive Sentiment', 'Strengths', 'Improvements Needed', 'Specific Requests']
    
    fig = go.Figure()
    
    for i, (prog_name, prog_data) in enumerate(top_programs):
        # Calculate metrics
        mentions = prog_data.get('mention_count', 0)
        sentiment = prog_data.get('sentiment_summary', {})
        positive = sentiment.get('positive', 0)
        total_sentiment = sum(sentiment.values()) if sentiment else 1
        
        values = [
            min(mentions / 50, 1) * 100,  # Normalize to 100
            (positive / total_sentiment * 100) if total_sentiment > 0 else 0,
            len(prog_data.get('strengths', [])) * 20,
            len(prog_data.get('improvement_areas', [])) * 20,
            len(prog_data.get('specific_requests', [])) * 20
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=prog_name,
            line=dict(width=2),
            marker=dict(size=8),
            opacity=0.6
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=True,
        title={
            'text': 'Program Performance Analysis',
            'font': {'size': 24, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=600,
        width=800,
        margin=dict(l=80, r=80, t=100, b=80),
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 14},
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.1
        )
    )
    
    return fig

def create_funding_flow_sankey(data):
    """Create a Sankey diagram showing funding needs flow."""
    # Extract themes and their relationships
    themes = data['cross_question_synthesis']['recurring_themes']
    
    # Create nodes
    source_nodes = ['Community Needs']
    theme_nodes = []
    outcome_nodes = ['Increased Funding', 'Process Improvements', 'Access Improvements', 'Program Development']
    
    for theme, info in sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:8]:
        theme_nodes.append(theme.replace('_', ' ').title())
    
    all_nodes = source_nodes + theme_nodes + outcome_nodes
    
    # Create links
    source = []
    target = []
    value = []
    
    # From source to themes
    for i, theme in enumerate(theme_nodes):
        source.append(0)  # Community Needs
        target.append(i + 1)
        # Use theme mention count as value
        theme_key = theme.lower().replace(' ', '_')
        value.append(themes.get(theme_key, {}).get('total_mentions', 10))
    
    # From themes to outcomes (simplified mapping)
    theme_to_outcome = {
        0: 1,  # Funding themes -> Increased Funding
        1: 1,
        2: 2,  # Process themes -> Process Improvements
        3: 3,  # Access themes -> Access Improvements
        4: 3,
        5: 4,  # Artist support -> Program Development
        6: 4,
        7: 2
    }
    
    for i, theme in enumerate(theme_nodes):
        source.append(i + 1)
        target.append(len(source_nodes) + len(theme_nodes) + theme_to_outcome.get(i, 0))
        value.append(themes.get(theme.lower().replace(' ', '_'), {}).get('total_mentions', 10) * 0.7)
    
    # Create Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=[COLORS['primary']] + COLORS['chart_colors'][:len(theme_nodes)] + 
                  [COLORS['positive'], COLORS['secondary'], COLORS['accent'], COLORS['mixed']]
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color='rgba(125,125,125,0.2)'
        )
    )])
    
    fig.update_layout(
        title={
            'text': 'Community Needs to Strategic Outcomes Flow',
            'font': {'size': 24, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=600,
        width=1000,
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 14}
    )
    
    return fig

def create_executive_dashboard(data):
    """Create a comprehensive executive dashboard."""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Response Distribution by Question',
            'Top Strategic Themes',
            'Sentiment Overview',
            'Urgency Distribution'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'bar'}],
            [{'type': 'pie'}, {'type': 'bar'}]
        ],
        horizontal_spacing=0.15,
        vertical_spacing=0.15
    )
    
    # 1. Response counts
    questions = []
    counts = []
    for q in data['question_analyses']:
        questions.append(q['question_id'].split('_')[0].upper())
        counts.append(q['response_count'])
    
    fig.add_trace(
        go.Bar(x=questions, y=counts, marker_color=COLORS['primary'], name='Responses'),
        row=1, col=1
    )
    
    # 2. Top themes
    themes = data['cross_question_synthesis']['recurring_themes']
    top_themes = sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:5]
    theme_names = [t[0].replace('_', ' ').title()[:20] + '...' if len(t[0]) > 20 else t[0].replace('_', ' ').title() for t in top_themes]
    theme_counts = [t[1]['total_mentions'] for t in top_themes]
    
    fig.add_trace(
        go.Bar(
            y=theme_names, 
            x=theme_counts, 
            orientation='h',
            marker_color=COLORS['chart_colors'][:5],
            name='Mentions'
        ),
        row=1, col=2
    )
    
    # 3. Overall sentiment
    total_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
    for q in data['question_analyses']:
        for sent, count in q['sentiment_distribution'].items():
            total_sentiment[sent] = total_sentiment.get(sent, 0) + count
    
    fig.add_trace(
        go.Pie(
            labels=[s.capitalize() for s in total_sentiment.keys()],
            values=list(total_sentiment.values()),
            marker_colors=[COLORS['positive'], COLORS['negative'], COLORS['neutral'], COLORS['mixed']],
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        ),
        row=2, col=1
    )
    
    # 4. Urgency distribution
    total_urgency = {'high': 0, 'medium': 0, 'low': 0}
    for q in data['question_analyses']:
        for urg, count in q['urgency_distribution'].items():
            total_urgency[urg] = total_urgency.get(urg, 0) + count
    
    fig.add_trace(
        go.Bar(
            x=['High', 'Medium', 'Low'],
            y=[total_urgency['high'], total_urgency['medium'], total_urgency['low']],
            marker_color=[COLORS['negative'], COLORS['accent'], COLORS['positive']],
            name='Urgency'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'ACME Cultural Funding Analysis - Executive Dashboard',
            'font': {'size': 28, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=800,
        width=1200,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 12}
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

def save_all_visualizations():
    """Generate and save all visualizations."""
    print("Loading data...")
    data = load_data()
    
    # Create output directory
    output_dir = Path("data/results/reports/visualizations")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Skip image export for now - just generate HTML
    can_export_images = False
    print("Generating interactive HTML visualizations...")
    
    # Generate all visualizations
    print("Creating sentiment overview...")
    fig1 = create_sentiment_overview(data)
    fig1.write_html(output_dir / f"sentiment_overview_{timestamp}.html")
    if can_export_images:
        fig1.write_image(output_dir / f"sentiment_overview_{timestamp}.png", width=1200, height=600, scale=2)
    
    print("Creating urgency heatmap...")
    fig2 = create_urgency_heatmap(data)
    fig2.write_html(output_dir / f"urgency_heatmap_{timestamp}.html")
    if can_export_images:
        fig2.write_image(output_dir / f"urgency_heatmap_{timestamp}.png", width=1400, height=700, scale=2)
    
    print("Creating theme network...")
    fig3 = create_theme_network(data)
    fig3.write_html(output_dir / f"theme_network_{timestamp}.html")
    if can_export_images:
        fig3.write_image(output_dir / f"theme_network_{timestamp}.png", width=1200, height=900, scale=2)
    
    print("Creating stakeholder sunburst...")
    fig4 = create_stakeholder_sunburst(data)
    fig4.write_html(output_dir / f"stakeholder_sunburst_{timestamp}.html")
    if can_export_images:
        fig4.write_image(output_dir / f"stakeholder_sunburst_{timestamp}.png", width=800, height=800, scale=2)
    
    print("Creating program radar...")
    fig5 = create_program_impact_radar(data)
    fig5.write_html(output_dir / f"program_radar_{timestamp}.html")
    if can_export_images:
        fig5.write_image(output_dir / f"program_radar_{timestamp}.png", width=1000, height=700, scale=2)
    
    print("Creating funding flow...")
    fig6 = create_funding_flow_sankey(data)
    fig6.write_html(output_dir / f"funding_flow_{timestamp}.html")
    if can_export_images:
        fig6.write_image(output_dir / f"funding_flow_{timestamp}.png", width=1200, height=700, scale=2)
    
    print("Creating executive dashboard...")
    fig7 = create_executive_dashboard(data)
    fig7.write_html(output_dir / f"executive_dashboard_{timestamp}.html")
    if can_export_images:
        fig7.write_image(output_dir / f"executive_dashboard_{timestamp}.png", width=1400, height=900, scale=2)
    
    # Also save as latest
    for fig, name in [
        (fig1, 'sentiment_overview'),
        (fig2, 'urgency_heatmap'),
        (fig3, 'theme_network'),
        (fig4, 'stakeholder_sunburst'),
        (fig5, 'program_radar'),
        (fig6, 'funding_flow'),
        (fig7, 'executive_dashboard')
    ]:
        fig.write_html(output_dir / f"{name}_LATEST.html")
        if can_export_images:
            fig.write_image(output_dir / f"{name}_LATEST.png", width=1200, height=700, scale=2)
    
    print(f"\n✓ All visualizations saved to {output_dir}")
    print("\nGenerated visualizations:")
    print("1. sentiment_overview - Community sentiment by question")
    print("2. urgency_heatmap - Theme urgency across questions")
    print("3. theme_network - Interconnected themes visualization")
    print("4. stakeholder_sunburst - Hierarchical stakeholder distribution")
    print("5. program_radar - Program performance analysis")
    print("6. funding_flow - Sankey diagram of needs to outcomes")
    print("7. executive_dashboard - Comprehensive overview dashboard")

if __name__ == "__main__":
    save_all_visualizations()