import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

TEAL_PALETTE = ["#008080", "#00A896", "#028090", "#02C39A", "#F0F3F4", "#2B580C", "#639A67"]
NAVY_PALETTE = ["#1B365D", "#2C5364", "#203A43", "#0F2027", "#4A6FA5", "#166088"]

def plot_publications_by_year(years_dict: Dict[str, int]) -> go.Figure:
    """Line & bar trend of publications over years."""
    if not years_dict:
        fig = go.Figure()
        fig.add_annotation(text="No publication year data available", showarrow=False, font=dict(size=14))
        return fig

    # Sort years
    sorted_years = sorted(years_dict.keys(), key=lambda y: int(y) if y.isdigit() else 0)
    counts = [years_dict[y] for y in sorted_years]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sorted_years,
        y=counts,
        name="Papers Published",
        marker_color="#008080",
        opacity=0.85
    ))
    fig.add_trace(go.Scatter(
        x=sorted_years,
        y=counts,
        mode="lines+markers",
        name="Publication Velocity",
        line=dict(color="#1B365D", width=3),
        marker=dict(size=8, color="#00B4D8")
    ))

    fig.update_layout(
        title="<b>Publication Output Trend by Year</b>",
        xaxis_title="Year",
        yaxis_title="Number of Papers",
        template="plotly_white",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_journals_distribution(journals_dict: Dict[str, int]) -> go.Figure:
    """Horizontal bar chart for top publishing journals."""
    if not journals_dict:
        fig = go.Figure()
        fig.add_annotation(text="No journal data available", showarrow=False, font=dict(size=14))
        return fig

    # Sort ascending for horizontal bar
    sorted_items = sorted(journals_dict.items(), key=lambda x: x[1])[-8:]
    journals = [k[:35] + ("..." if len(k) > 35 else "") for k, _ in sorted_items]
    counts = [v for _, v in sorted_items]

    fig = go.Figure(go.Bar(
        x=counts,
        y=journals,
        orientation="h",
        marker=dict(
            color=counts,
            colorscale="Viridis",
            showscale=False
        )
    ))

    fig.update_layout(
        title="<b>Top Publishing Biomedical Journals</b>",
        xaxis_title="Papers",
        yaxis_title="",
        template="plotly_white",
        margin=dict(l=40, r=20, t=50, b=40)
    )
    return fig

def plot_sources_distribution(sources_dict: Dict[str, int]) -> go.Figure:
    """Donut chart for database sources."""
    if not sources_dict:
        fig = go.Figure()
        fig.add_annotation(text="No database source data", showarrow=False, font=dict(size=14))
        return fig

    labels = list(sources_dict.keys())
    values = list(sources_dict.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=["#0284C7", "#059669", "#D97706", "#7C3AED", "#DB2777"])
    )])

    fig.update_layout(
        title="<b>Database Retrieval Coverage</b>",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_study_types_distribution(types_dict: Dict[str, int]) -> go.Figure:
    """Pie chart for study / publication types."""
    if not types_dict:
        fig = go.Figure()
        fig.add_annotation(text="No study type data", showarrow=False, font=dict(size=14))
        return fig

    labels = [k[:25] for k in types_dict.keys()]
    values = list(types_dict.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=["#1B365D", "#008080", "#E63946", "#F4A261", "#2A9D8F"])
    )])

    fig.update_layout(
        title="<b>Study & Article Types</b>",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
