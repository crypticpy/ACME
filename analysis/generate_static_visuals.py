#!/usr/bin/env python3
"""Generate static matplotlib visualizations for the report."""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Modern color palette
COLORS = {
    'primary': '#1E3A8A',
    'secondary': '#3B82F6', 
    'accent': '#F59E0B',
    'negative': '#DC2626',
    'positive': '#10B981',
    'neutral': '#6B7280',
    'mixed': '#8B5CF6',
    'background': '#F9FAFB',
    'text': '#111827',
    'chart_colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']
}

# Set up matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 16,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 18,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '-',
    'grid.linewidth': 0.5
})

def load_data():
    """Load the analysis results."""
    results_path = Path("data/results/deep_analysis/deep_analysis_results_20250621_022354.json")
    with open(results_path, 'r') as f:
        return json.load(f)

def create_sentiment_overview_static(data):
    """Create sentiment overview bar chart."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare data
    questions = []
    sentiments = {'Positive': [], 'Neutral': [], 'Mixed': [], 'Negative': []}
    
    for q in data['question_analyses']:
        q_label = q['question_id'].split('_')[0].upper()
        questions.append(q_label)
        
        total = sum(q['sentiment_distribution'].values())
        for sent in ['positive', 'neutral', 'mixed', 'negative']:
            count = q['sentiment_distribution'].get(sent, 0)
            pct = (count/total*100) if total > 0 else 0
            sentiments[sent.capitalize()].append(pct)
    
    # Create stacked bars
    width = 0.6
    x = np.arange(len(questions))
    
    bottom = np.zeros(len(questions))
    colors = {
        'Positive': COLORS['positive'],
        'Neutral': COLORS['neutral'],
        'Mixed': COLORS['mixed'],
        'Negative': COLORS['negative']
    }
    
    for sentiment in ['Negative', 'Neutral', 'Mixed', 'Positive']:
        values = sentiments[sentiment]
        ax.bar(x, values, width, bottom=bottom, label=sentiment, color=colors[sentiment], alpha=0.9)
        
        # Add percentage labels for significant values
        for i, (val, b) in enumerate(zip(values, bottom)):
            if val > 10:  # Only show if > 10%
                ax.text(i, b + val/2, f'{val:.0f}%', ha='center', va='center', 
                       fontsize=9, fontweight='bold', color='white')
        
        bottom += values
    
    # Customize
    ax.set_xlabel('Survey Questions', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage of Responses', fontsize=14, fontweight='bold')
    ax.set_title('Community Sentiment Distribution by Question', fontsize=18, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(questions)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    
    # Legend
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True, fancybox=True, shadow=True)
    
    # Add subtle grid
    ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig

def create_theme_frequency_chart(data):
    """Create horizontal bar chart of top themes."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get top themes
    themes = data['cross_question_synthesis']['recurring_themes']
    top_themes = sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:10]
    
    # Prepare data
    theme_names = []
    mentions = []
    questions = []
    
    for theme, info in reversed(top_themes):  # Reverse for top-to-bottom display
        name = theme.replace('_', ' ').title()
        if len(name) > 40:
            name = name[:37] + '...'
        theme_names.append(name)
        mentions.append(info['total_mentions'])
        questions.append(info['question_count'])
    
    y_pos = np.arange(len(theme_names))
    
    # Create bars
    bars = ax.barh(y_pos, mentions, color=COLORS['primary'], alpha=0.8, height=0.7)
    
    # Add value labels
    for i, (bar, mention, q_count) in enumerate(zip(bars, mentions, questions)):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{mention} mentions\nacross {q_count} questions', 
                va='center', fontsize=9, color=COLORS['text'])
    
    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(theme_names, fontsize=11)
    ax.set_xlabel('Total Mentions', fontsize=14, fontweight='bold')
    ax.set_title('Top 10 Recurring Themes Across All Questions', fontsize=18, fontweight='bold', pad=20)
    
    # Set x limit with some padding
    ax.set_xlim(0, max(mentions) * 1.3)
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    return fig

def create_urgency_matrix(data):
    """Create urgency vs frequency matrix."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Collect theme data with urgency and frequency
    theme_data = []
    
    for q in data['question_analyses']:
        for theme in q['dominant_themes'][:5]:
            theme_data.append({
                'name': theme['theme'].replace('_', ' ').title(),
                'frequency': theme['count'],
                'urgency': theme.get('urgency_score', 0.5),
                'question': q['question_id'].split('_')[0].upper()
            })
    
    # Create scatter plot
    for i, td in enumerate(theme_data):
        color_idx = hash(td['question']) % len(COLORS['chart_colors'])
        ax.scatter(td['frequency'], td['urgency'], 
                  s=100, alpha=0.7,
                  color=COLORS['chart_colors'][color_idx],
                  edgecolors='white', linewidth=1.5)
        
        # Add labels for high-frequency or high-urgency themes
        if td['frequency'] > 15 or td['urgency'] > 0.8:
            ax.annotate(td['name'][:20], 
                       (td['frequency'], td['urgency']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.8)
    
    # Add quadrant lines
    ax.axhline(y=0.7, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=20, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    # Add quadrant labels
    ax.text(5, 0.95, 'High Urgency\nLow Frequency', fontsize=10, alpha=0.6, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.2))
    ax.text(35, 0.95, 'High Urgency\nHigh Frequency', fontsize=10, alpha=0.6,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='red', alpha=0.2))
    ax.text(5, 0.05, 'Low Urgency\nLow Frequency', fontsize=10, alpha=0.6,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='green', alpha=0.2))
    ax.text(35, 0.05, 'Low Urgency\nHigh Frequency', fontsize=10, alpha=0.6,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='blue', alpha=0.2))
    
    # Customize
    ax.set_xlabel('Theme Frequency (Number of Mentions)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Urgency Score', fontsize=14, fontweight='bold')
    ax.set_title('Theme Priority Matrix: Urgency vs Frequency', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlim(-2, max([td['frequency'] for td in theme_data]) * 1.1)
    ax.set_ylim(-0.05, 1.05)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig

def create_program_comparison(data):
    """Create program comparison chart."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    programs = data.get('program_analyses', {})
    top_programs = sorted(programs.items(), 
                         key=lambda x: x[1].get('mention_count', 0), 
                         reverse=True)[:6]
    
    # Chart 1: Mention counts and sentiment
    prog_names = []
    mentions = []
    positive_pct = []
    
    for prog_name, prog_data in top_programs:
        prog_names.append(prog_name)
        mentions.append(prog_data.get('mention_count', 0))
        
        sentiment = prog_data.get('sentiment_summary', {})
        total = sum(sentiment.values())
        pos = sentiment.get('positive', 0)
        positive_pct.append((pos/total*100) if total > 0 else 0)
    
    x = np.arange(len(prog_names))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, mentions, width, label='Mentions', color=COLORS['primary'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, positive_pct, width, label='Positive %', color=COLORS['positive'], alpha=0.8)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}%', ha='center', va='bottom', fontsize=9)
    
    ax1.set_xlabel('Programs', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Count / Percentage', fontsize=12, fontweight='bold')
    ax1.set_title('Program Mentions and Sentiment', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([p[:10] + '...' if len(p) > 10 else p for p in prog_names], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Chart 2: Strengths vs Improvements
    strengths_count = []
    improvements_count = []
    
    for _, prog_data in top_programs:
        strengths_count.append(len(prog_data.get('strengths', [])))
        improvements_count.append(len(prog_data.get('improvement_areas', [])))
    
    bars3 = ax2.bar(x - width/2, strengths_count, width, label='Strengths', color=COLORS['positive'], alpha=0.8)
    bars4 = ax2.bar(x + width/2, improvements_count, width, label='Improvements', color=COLORS['accent'], alpha=0.8)
    
    # Add value labels
    for bars in [bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    ax2.set_xlabel('Programs', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Items', fontsize=12, fontweight='bold')
    ax2.set_title('Identified Strengths vs Areas for Improvement', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([p[:10] + '...' if len(p) > 10 else p for p in prog_names], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Remove spines
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    plt.suptitle('Cultural Program Analysis', fontsize=18, fontweight='bold', y=1.05)
    plt.tight_layout()
    return fig

def create_executive_summary_visual(data):
    """Create a single-page executive summary visualization."""
    fig = plt.figure(figsize=(12, 16))
    
    # Create grid
    gs = fig.add_gridspec(5, 2, height_ratios=[1, 1.5, 1.5, 1.5, 0.5], 
                         width_ratios=[1, 1], hspace=0.4, wspace=0.3,
                         left=0.08, right=0.92, top=0.94, bottom=0.06)
    
    # Title
    fig.suptitle('ACME Cultural Funding Analysis - Executive Summary', 
                fontsize=24, fontweight='bold', y=0.98)
    
    # Key metrics (top row)
    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')
    
    metrics_text = (
        f"Total Responses: {data['metadata']['total_responses']:,} | "
        f"Questions Analyzed: {data['metadata']['questions_analyzed']} | "
        f"Programs Evaluated: {data['metadata']['programs_analyzed']} | "
        f"Analysis Duration: {data['metadata']['analysis_duration']}"
    )
    ax_metrics.text(0.5, 0.5, metrics_text, ha='center', va='center', 
                   fontsize=14, bbox=dict(boxstyle="round,pad=0.5", 
                   facecolor=COLORS['background'], edgecolor=COLORS['primary'], linewidth=2))
    
    # 1. Top themes (left)
    ax1 = fig.add_subplot(gs[1, 0])
    themes = data['cross_question_synthesis']['recurring_themes']
    top_themes = sorted(themes.items(), key=lambda x: x[1]['total_mentions'], reverse=True)[:5]
    
    theme_names = [t[0].replace('_', ' ').title()[:25] for t in top_themes]
    theme_counts = [t[1]['total_mentions'] for t in top_themes]
    
    bars = ax1.barh(range(len(theme_names)), theme_counts, 
                    color=COLORS['chart_colors'][:5], alpha=0.8)
    ax1.set_yticks(range(len(theme_names)))
    ax1.set_yticklabels(theme_names)
    ax1.set_xlabel('Mentions')
    ax1.set_title('Top 5 Critical Issues', fontweight='bold', fontsize=14)
    ax1.grid(axis='x', alpha=0.3)
    
    for i, (bar, count) in enumerate(zip(bars, theme_counts)):
        ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{count}', va='center', fontsize=10)
    
    # 2. Sentiment pie (right)
    ax2 = fig.add_subplot(gs[1, 1])
    total_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
    for q in data['question_analyses']:
        for sent, count in q['sentiment_distribution'].items():
            total_sentiment[sent] = total_sentiment.get(sent, 0) + count
    
    colors = [COLORS['positive'], COLORS['negative'], COLORS['neutral'], COLORS['mixed']]
    wedges, texts, autotexts = ax2.pie(total_sentiment.values(), 
                                       labels=[s.capitalize() for s in total_sentiment.keys()],
                                       colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Overall Community Sentiment', fontweight='bold', fontsize=14)
    
    # 3. Question comparison
    ax3 = fig.add_subplot(gs[2, :])
    questions = []
    neg_pct = []
    
    for q in data['question_analyses']:
        questions.append(q['question_id'].split('_')[0].upper())
        total = sum(q['sentiment_distribution'].values())
        neg = q['sentiment_distribution'].get('negative', 0)
        neg_pct.append((neg/total*100) if total > 0 else 0)
    
    x = np.arange(len(questions))
    bars = ax3.bar(x, neg_pct, color=[COLORS['negative'] if p > 50 else COLORS['accent'] for p in neg_pct], 
                   alpha=0.8)
    
    for bar, pct in zip(bars, neg_pct):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{pct:.0f}%', ha='center', va='bottom', fontsize=10)
    
    ax3.set_xticks(x)
    ax3.set_xticklabels(questions)
    ax3.set_ylabel('Negative Sentiment %')
    ax3.set_title('Negative Sentiment by Question - Identifying Pain Points', fontweight='bold', fontsize=14)
    ax3.set_ylim(0, max(neg_pct) * 1.15)
    ax3.grid(axis='y', alpha=0.3)
    ax3.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1)
    
    # 4. Strategic priorities
    ax4 = fig.add_subplot(gs[3, :])
    ax4.axis('off')
    
    priorities = [
        "1. Increase funding allocations by minimum 25%",
        "2. Simplify application and reporting processes", 
        "3. Address transportation and cost barriers",
        "4. Develop emerging artist support programs",
        "5. Build sustainable, equitable funding model"
    ]
    
    y_pos = 0.9
    ax4.text(0.5, y_pos, 'Priority Actions Required', ha='center', fontweight='bold', 
            fontsize=16, transform=ax4.transAxes)
    
    for i, priority in enumerate(priorities):
        y_pos -= 0.15
        color = COLORS['negative'] if i < 2 else COLORS['accent'] if i < 4 else COLORS['primary']
        ax4.text(0.1, y_pos, priority, fontsize=12, transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.1))
    
    # Footer
    ax5 = fig.add_subplot(gs[4, :])
    ax5.axis('off')
    ax5.text(0.5, 0.5, 
            'The Austin creative community needs transformative change in cultural funding allocation and access.',
            ha='center', va='center', fontsize=12, style='italic', 
            bbox=dict(boxstyle="round,pad=0.5", facecolor=COLORS['background'], 
                     edgecolor=COLORS['primary'], linewidth=1))
    
    # Remove spines where applicable
    for ax in [ax1, ax2, ax3]:
        if hasattr(ax, 'spines'):
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
    
    return fig

def save_all_static_visuals():
    """Generate and save all static visualizations."""
    print("Loading data...")
    data = load_data()
    
    # Create output directory
    output_dir = Path("data/results/reports/visualizations")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate visualizations
    print("Creating sentiment overview...")
    fig1 = create_sentiment_overview_static(data)
    fig1.savefig(output_dir / f"sentiment_overview_{timestamp}.png", dpi=300, bbox_inches='tight')
    fig1.savefig(output_dir / "sentiment_overview_LATEST.png", dpi=300, bbox_inches='tight')
    plt.close(fig1)
    
    print("Creating theme frequency chart...")
    fig2 = create_theme_frequency_chart(data)
    fig2.savefig(output_dir / f"theme_frequency_{timestamp}.png", dpi=300, bbox_inches='tight')
    fig2.savefig(output_dir / "theme_frequency_LATEST.png", dpi=300, bbox_inches='tight')
    plt.close(fig2)
    
    print("Creating urgency matrix...")
    fig3 = create_urgency_matrix(data)
    fig3.savefig(output_dir / f"urgency_matrix_{timestamp}.png", dpi=300, bbox_inches='tight')
    fig3.savefig(output_dir / "urgency_matrix_LATEST.png", dpi=300, bbox_inches='tight')
    plt.close(fig3)
    
    print("Creating program comparison...")
    fig4 = create_program_comparison(data)
    fig4.savefig(output_dir / f"program_comparison_{timestamp}.png", dpi=300, bbox_inches='tight')
    fig4.savefig(output_dir / "program_comparison_LATEST.png", dpi=300, bbox_inches='tight')
    plt.close(fig4)
    
    print("Creating executive summary visual...")
    fig5 = create_executive_summary_visual(data)
    fig5.savefig(output_dir / f"executive_summary_visual_{timestamp}.png", dpi=300, bbox_inches='tight')
    fig5.savefig(output_dir / "executive_summary_visual_LATEST.png", dpi=300, bbox_inches='tight')
    plt.close(fig5)
    
    print(f"\n✓ All static visualizations saved to {output_dir}")
    print("\nGenerated static visualizations:")
    print("1. sentiment_overview - Stacked bar chart of sentiment by question")
    print("2. theme_frequency - Top 10 themes horizontal bar chart")
    print("3. urgency_matrix - Scatter plot of urgency vs frequency")
    print("4. program_comparison - Dual charts for program analysis")
    print("5. executive_summary_visual - Single-page executive overview")

if __name__ == "__main__":
    save_all_static_visuals()