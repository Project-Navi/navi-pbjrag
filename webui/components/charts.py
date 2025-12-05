"""Visualization helpers for PBJRAG analysis."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any


def blessing_pie_chart(chunks: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a pie chart showing distribution of blessing tiers.

    Args:
        chunks: List of analyzed chunks with 'blessing' field

    Returns:
        Plotly figure object
    """
    # Count blessing tiers
    tier_counts = {}
    for chunk in chunks:
        blessing = chunk.get('blessing', {})
        tier = blessing.get('tier', 'Unknown')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(tier_counts.keys()),
        values=list(tier_counts.values()),
        hole=0.3,
        marker=dict(
            colors=['#4CAF50', '#FFC107', '#F44336'],  # Green, Yellow, Red
            line=dict(color='#000000', width=2)
        )
    )])

    fig.update_layout(
        title="Blessing Tier Distribution",
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig


def phase_bar_chart(chunks: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a bar chart showing distribution of blessing phases.

    Args:
        chunks: List of analyzed chunks with 'blessing' field

    Returns:
        Plotly figure object
    """
    # Count phases
    phase_counts = {}
    for chunk in chunks:
        blessing = chunk.get('blessing', {})
        phase = blessing.get('phase', 'Unknown')
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    # Create bar chart
    df = pd.DataFrame({
        'Phase': list(phase_counts.keys()),
        'Count': list(phase_counts.values())
    })

    fig = px.bar(
        df,
        x='Phase',
        y='Count',
        title='Blessing Phase Distribution',
        color='Count',
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )

    return fig


def dimension_radar_chart(field_state: Dict[str, float]) -> go.Figure:
    """
    Create a radar chart showing 9-dimensional field state.

    Args:
        field_state: Dictionary with 9 dimension values

    Returns:
        Plotly figure object
    """
    # Define the 9 dimensions
    dimensions = [
        'coherence',
        'clarity',
        'completeness',
        'consistency',
        'correctness',
        'coupling',
        'complexity',
        'coverage',
        'changeability'
    ]

    # Extract values (default to 0.5 if missing)
    values = [field_state.get(dim, 0.5) for dim in dimensions]

    # Close the radar chart by repeating first value
    values_closed = values + [values[0]]
    dimensions_closed = dimensions + [dimensions[0]]

    # Create radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=dimensions_closed,
        fill='toself',
        fillcolor='rgba(76, 175, 80, 0.3)',
        line=dict(color='#4CAF50', width=2),
        name='Field State'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='rgba(255,255,255,0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title="9-Dimensional Field State"
    )

    return fig


def epc_timeline_chart(chunks: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a timeline showing EPC (Evolutionary Path Clarity) over chunks.

    Args:
        chunks: List of analyzed chunks with 'blessing' field

    Returns:
        Plotly figure object
    """
    epc_values = []
    for i, chunk in enumerate(chunks):
        blessing = chunk.get('blessing', {})
        epc = blessing.get('epc', 0.5)
        epc_values.append({'Chunk': i, 'EPC': epc})

    df = pd.DataFrame(epc_values)

    fig = px.line(
        df,
        x='Chunk',
        y='EPC',
        title='Evolutionary Path Clarity Timeline',
        markers=True
    )

    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, 1])
    )

    return fig
