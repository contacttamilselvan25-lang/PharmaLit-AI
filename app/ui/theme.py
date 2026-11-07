import streamlit as st

def apply_scientific_theme():
    """Injects modern, executive scientific CSS styling into Streamlit."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main brand header styling */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
    }
    .brand-subtitle {
        font-size: 0.95rem;
        color: #B0BEC5;
        margin-top: 4px;
        font-weight: 400;
    }
    .brand-badge {
        background: rgba(0, 128, 128, 0.3);
        border: 1px solid #00B4D8;
        color: #E0FBFC;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Metric cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 12px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #CBD5E1;
    }
    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #008080;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Paper Card */
    .paper-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #008080;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .paper-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0F172A;
        line-height: 1.4;
        margin-bottom: 6px;
    }
    .paper-meta {
        font-size: 0.82rem;
        color: #475569;
        margin-bottom: 10px;
    }
    .badge-chip {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-pubmed { background: #E0F2FE; color: #0369A1; }
    .badge-epmc { background: #F0FDF4; color: #15803D; }
    .badge-s2 { background: #FEF3C7; color: #B45309; }
    .badge-oa { background: #DCFCE7; color: #166534; }
    .badge-doi { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748B; }

    /* Gap Card */
    .gap-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-top: 3px solid #0284C7;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .gap-theme {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .gap-question {
        background: #F0F9FF;
        border-left: 3px solid #0EA5E9;
        padding: 8px 12px;
        font-size: 0.88rem;
        color: #0369A1;
        font-style: italic;
        margin: 8px 0;
    }
    .gap-opportunity {
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.5;
    }

    /* Scientific callout */
    .scientific-callout {
        background: #F0FDFA;
        border-left: 4px solid #0D9488;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 14px 0;
        font-size: 0.9rem;
        color: #134E4A;
    }

    /* Code and DOI links */
    code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85em;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_brand_header(active_project_name: str = "", therapeutic_area: str = "", target_drug: str = ""):
    """Renders the executive top navigation and branding banner."""
    sub_text = "AI-Powered Literature Review & Research Intelligence Platform"
    if active_project_name:
        sub_text = f"Active Project: {active_project_name}"
        if therapeutic_area or target_drug:
            sub_text += f" • {therapeutic_area} ({target_drug})"

    header_html = f"""
    <div class="brand-container">
        <div>
            <h1 class="brand-title">PharmaLit AI</h1>
            <div class="brand-subtitle">{sub_text}</div>
        </div>
        <div>
            <span class="brand-badge">Scientific Edition v1.0</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
