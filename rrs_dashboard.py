"""
Enterprise RRS - Multi-User Dashboard
ISO 31000 / COSO ERM Compliant Risk Assessment System
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict
import json
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from rrs_database import RRSDatabase, UserRole, AuditAction
from rrs_core import (
    Risk, RiskCategory, ImpactDimension, LikelihoodLevel, ImpactLevel,
    RiskStatus, ImpactAssessment, RiskInterdependencyEngine, RiskPrioritizer
)


# Page config
st.set_page_config(
    page_title="XERGY Risk Register Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add 3D glowing logo to all pages
def add_page_logo():
    """Add professional 3D glowing logo to top right of every page"""
    import os
    import base64
    
    logo_path = "xergy_logo.png"
    logo_html = ""
    
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
                logo_html = f'''
                <style>
                @keyframes glow {{
                    0%, 100% {{ 
                        filter: drop-shadow(0 0 8px rgba(79, 70, 229, 0.6))
                                drop-shadow(0 0 15px rgba(79, 70, 229, 0.4))
                                drop-shadow(0 0 20px rgba(79, 70, 229, 0.2));
                    }}
                    50% {{ 
                        filter: drop-shadow(0 0 12px rgba(79, 70, 229, 0.8))
                                drop-shadow(0 0 20px rgba(79, 70, 229, 0.6))
                                drop-shadow(0 0 30px rgba(79, 70, 229, 0.3));
                    }}
                }}
                
                .xergy-logo-container {{
                    position: fixed;
                    top: 10px;
                    left: 10px;
                    z-index: 999999;
                    pointer-events: auto;
                }}
                
                .xergy-logo-link {{
                    display: block;
                    text-decoration: none;
                    cursor: pointer;
                }}
                
                .xergy-logo {{
                    width: 120px;
                    height: auto;
                    background: linear-gradient(145deg, #ffffff, #f0f0f0);
                    padding: 12px;
                    border-radius: 16px;
                    box-shadow: 
                        8px 8px 16px rgba(0, 0, 0, 0.15),
                        -4px -4px 12px rgba(255, 255, 255, 0.9),
                        inset 2px 2px 4px rgba(255, 255, 255, 0.5),
                        inset -2px -2px 4px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s ease;
                    animation: glow 3s ease-in-out infinite;
                    border: 1px solid rgba(79, 70, 229, 0.2);
                }}
                
                .xergy-logo:hover {{
                    transform: translateY(-2px) scale(1.05);
                    box-shadow: 
                        10px 10px 20px rgba(0, 0, 0, 0.2),
                        -5px -5px 15px rgba(255, 255, 255, 1),
                        inset 3px 3px 6px rgba(255, 255, 255, 0.6),
                        inset -3px -3px 6px rgba(0, 0, 0, 0.15);
                }}
                
                .xergy-badge {{
                    position: absolute;
                    bottom: -8px;
                    right: -8px;
                    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                    color: white;
                    font-size: 9px;
                    font-weight: 600;
                    padding: 4px 8px;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(79, 70, 229, 0.4);
                    letter-spacing: 0.5px;
                    pointer-events: auto;
                }}
                
                @media (max-width: 768px) {{
                    .xergy-logo-container {{
                        top: 10px;
                        left: 10px;
                    }}
                    .xergy-logo {{
                        width: 80px;
                        padding: 8px;
                    }}
                }}
                </style>
                
                <div class="xergy-logo-container">
                    <a href="https://x-ergy.com/" target="_blank" rel="noopener noreferrer" class="xergy-logo-link">
                        <div style="position: relative;">
                            <img src="data:image/png;base64,{logo_data}" class="xergy-logo" alt="XERGY Logo">
                            <div class="xergy-badge">ISO 31000</div>
                        </div>
                    </a>
                </div>
                '''
        except Exception as e:
            # Fallback: Create text-based logo if image fails
            logo_html = '''
            <style>
            .xergy-logo-container {
                position: fixed;
                top: 10px;
                left: 10px;
                z-index: 999999;
            }
            
            .xergy-logo-link {
                display: block;
                text-decoration: none;
                cursor: pointer;
            }
            
            .xergy-text-logo {
                background: linear-gradient(145deg, #ffffff, #f0f0f0);
                padding: 15px 20px;
                border-radius: 16px;
                box-shadow: 
                    8px 8px 16px rgba(0, 0, 0, 0.15),
                    -4px -4px 12px rgba(255, 255, 255, 0.9);
                font-size: 24px;
                font-weight: 700;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: 2px;
                filter: drop-shadow(0 0 10px rgba(79, 70, 229, 0.3));
                animation: glow 3s ease-in-out infinite;
            }
            
            @keyframes glow {
                0%, 100% { 
                    filter: drop-shadow(0 0 8px rgba(79, 70, 229, 0.6));
                }
                50% { 
                    filter: drop-shadow(0 0 15px rgba(79, 70, 229, 0.9));
                }
            }
            </style>
            
            <div class="xergy-logo-container">
                <a href="https://x-ergy.com/" target="_blank" rel="noopener noreferrer" class="xergy-logo-link">
                    <div class="xergy-text-logo">XERGY</div>
                </a>
            </div>
            '''
    else:
        # No logo file - use text logo
        logo_html = '''
        <style>
        .xergy-logo-container {
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 999999;
        }
        
        .xergy-logo-link {
            display: block;
            text-decoration: none;
            cursor: pointer;
        }
        
        .xergy-text-logo {
            background: linear-gradient(145deg, #ffffff, #f0f0f0);
            padding: 15px 20px;
            border-radius: 16px;
            box-shadow: 
                8px 8px 16px rgba(0, 0, 0, 0.15),
                -4px -4px 12px rgba(255, 255, 255, 0.9),
                inset 2px 2px 4px rgba(255, 255, 255, 0.5),
                inset -2px -2px 4px rgba(0, 0, 0, 0.1);
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 2px;
            transition: all 0.3s ease;
        }
        
        .xergy-text-logo:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 
                10px 10px 20px rgba(0, 0, 0, 0.2),
                -5px -5px 15px rgba(255, 255, 255, 1);
        }
        
        @keyframes glow {
            0%, 100% { 
                filter: drop-shadow(0 0 8px rgba(79, 70, 229, 0.6))
                        drop-shadow(0 0 15px rgba(79, 70, 229, 0.4));
            }
            50% { 
                filter: drop-shadow(0 0 12px rgba(79, 70, 229, 0.8))
                        drop-shadow(0 0 20px rgba(79, 70, 229, 0.6));
            }
        }
        
        .xergy-text-logo {
            animation: glow 3s ease-in-out infinite;
        }
        </style>
        
        <div class="xergy-logo-container">
            <a href="https://x-ergy.com/" target="_blank" rel="noopener noreferrer" class="xergy-logo-link">
                <div class="xergy-text-logo">XERGY</div>
            </a>
        </div>
        '''
    
    st.markdown(logo_html, unsafe_allow_html=True)

# Apply logo to all pages
add_page_logo()

# Initialize database
@st.cache_resource
def get_database():
    return RRSDatabase()

db = get_database()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None


def login_screen():
    """Login interface"""
    
    # Check if logo exists and prepare background
    import os
    import base64
    
    logo_html = ""
    logo_path = "xergy_logo.png"
    
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
                logo_html = f'''
                <div style="
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    opacity: 0.05;
                    width: 60%;
                    max-width: 800px;
                    z-index: 0;
                    pointer-events: none;
                ">
                    <img src="data:image/png;base64,{logo_data}" style="width: 100%; height: auto;">
                </div>
                '''
        except:
            pass
    
    if logo_html:
        st.markdown(logo_html, unsafe_allow_html=True)
    
    # Add CSS for positioning
    st.markdown("""
        <style>
        .main > div {
            position: relative;
            z-index: 1;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create Facebook-style banner background for title
    banner_html = ""
    banner_path = "xergy_banner.png"
    
    # Try to load banner image
    banner_bg = ""
    if os.path.exists(banner_path):
        try:
            with open(banner_path, "rb") as f:
                banner_data = base64.b64encode(f.read()).decode()
                banner_bg = f"background-image: url('data:image/png;base64,{banner_data}');"
        except:
            # Fallback to gradient
            banner_bg = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
    else:
        # Fallback to gradient if no image
        banner_bg = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
    
    banner_html = f'''
    <style>
    .title-banner {{
        position: relative;
        width: 100%;
        max-width: 1200px;
        height: 180px;
        margin: -20px auto 30px auto;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }}
    
    .title-banner-bg {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        {banner_bg}
        background-size: cover;
        background-position: center;
        opacity: 0.5;
        z-index: 1;
    }}
    
    .title-banner-content {{
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        padding: 20px;
    }}
    
    .title-banner h1 {{
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        letter-spacing: 2px;
    }}
    
    .title-banner .subtitle {{
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 400;
        margin-top: 10px;
        text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3);
    }}
    
    @media (max-width: 768px) {{
        .title-banner {{
            height: 120px;
            margin: -10px auto 20px auto;
        }}
        .title-banner h1 {{
            font-size: 2rem;
        }}
        .title-banner .subtitle {{
            font-size: 0.9rem;
        }}
    }}
    </style>
    
    <div class="title-banner">
        <div class="title-banner-bg"></div>
        <div class="title-banner-content">
            <h1>XERGY Risk Register Platform</h1>
            <div class="subtitle">ISO 31000 / COSO ERM Compliant</div>
        </div>
    </div>
    '''
    
    st.markdown(banner_html, unsafe_allow_html=True)
    
    # Title is now in the banner, skip the default streamlit title
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_login, col_info = st.columns(2)
        
        with col_login:
            if st.button("Login", type="primary", use_container_width=True):
                if username and password:
                    user = db.authenticate_user(username, password)
                    
                    if user:
                        session_id = db.create_session(user['user_id'])
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.session_id = session_id
                        st.rerun()
                    else:
                        st.error("Invalid credentials or account locked")
                else:
                    st.warning("Please enter username and password")
        
        with col_info:
            with st.expander("Default Credentials"):
                st.info("Username: admin\nPassword: admin123")
        
        st.markdown("---")
        st.markdown("**Role-Based Access:**")
        st.markdown("- **Risk Manager**: Full access, approval workflow")
        st.markdown("- **Department Contributor**: Submit and edit department risks")
        st.markdown("- **View Only**: Read-only dashboard access")


def logout():
    """Logout and clear session"""
    if st.session_state.session_id:
        db.invalidate_session(st.session_state.session_id)
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.session_id = None
    st.rerun()


def risk_manager_dashboard():
    """Full risk manager dashboard with all features"""
    st.title("XERGY Risk Register Platform")
    st.markdown(f"**Risk Manager**: {st.session_state.user['full_name']} | {st.session_state.user['department']}")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select View", [
            "Risk Dashboard",
            "Risk Register",
            "Add/Edit Risk",
            "Risk Interdependencies",
            "Mitigation Tracking",
            "Reports",
            "User Management",
            "Audit Log"
        ])
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()
    
    if page == "Risk Dashboard":
        show_risk_dashboard()
    elif page == "Risk Register":
        show_risk_register()
    elif page == "Add/Edit Risk":
        show_risk_form()
    elif page == "Risk Interdependencies":
        show_risk_interdependencies()
    elif page == "Mitigation Tracking":
        show_mitigation_tracking()
    elif page == "Reports":
        show_reports()
    elif page == "User Management":
        show_user_management()
    elif page == "Audit Log":
        show_audit_log()


def department_contributor_dashboard():
    """Dashboard for department contributors"""
    st.title("XERGY Risk Register - Department View")
    st.markdown(f"**Contributor**: {st.session_state.user['full_name']} | {st.session_state.user['department']}")
    
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select View", [
            "My Department Risks",
            "Submit New Risk",
            "Risk Dashboard (Read-Only)"
        ])
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()
    
    if page == "My Department Risks":
        show_department_risks()
    elif page == "Submit New Risk":
        show_risk_form(department_only=True)
    elif page == "Risk Dashboard (Read-Only)":
        show_risk_dashboard(readonly=True)


def view_only_dashboard():
    """Read-only dashboard for viewers"""
    st.title("XERGY Risk Register - Viewer Dashboard")
    st.markdown(f"**Viewer**: {st.session_state.user['full_name']}")
    
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select View", [
            "Risk Dashboard",
            "Risk Register",
            "Reports"
        ])
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()
    
    if page == "Risk Dashboard":
        show_risk_dashboard(readonly=True)
    elif page == "Risk Register":
        show_risk_register(readonly=True)
    elif page == "Reports":
        show_reports(readonly=True)


def show_risk_dashboard(readonly=False):
    """Executive risk dashboard with heat maps and metrics"""
    st.header("Risk Dashboard")
    
    # Get all risks
    risks = db.get_all_risks()
    
    if not risks:
        st.info("No risks registered yet. Add your first risk to get started.")
        return
    
    # Calculate metrics
    total_risks = len(risks)
    critical_risks = len([r for r in risks if r.get('risk_level') == 'Critical'])
    high_risks = len([r for r in risks if r.get('risk_level') == 'High'])
    appetite_exceeded = len([r for r in risks if r.get('risk_appetite_exceeded')])
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Risks", total_risks)
    with col2:
        st.metric("Critical Risks", critical_risks)
    with col3:
        st.metric("High Risks", high_risks)
    with col4:
        st.metric("Appetite Exceeded", appetite_exceeded)
    
    st.markdown("---")
    
    # Heat map
    col_heat, col_category = st.columns(2)
    
    with col_heat:
        st.subheader("Risk Heat Map")
        fig_heat = create_risk_heat_map(risks)
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with col_category:
        st.subheader("Risks by Category")
        category_counts = {}
        for risk in risks:
            cat = risk['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        fig_cat = go.Figure(data=[
            go.Bar(x=list(category_counts.keys()), y=list(category_counts.values()))
        ])
        fig_cat.update_layout(
            xaxis_title="Category",
            yaxis_title="Number of Risks",
            showlegend=False
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    # Top risks table
    st.subheader("Top 10 Risks by Residual Score")
    top_risks = sorted(risks, key=lambda x: x.get('residual_score', 0) or 0, reverse=True)[:10]
    
    df_top = pd.DataFrame([{
        'Risk ID': r['risk_id'],
        'Risk Name': r['risk_name'],
        'Category': r['category'],
        'Department': r['owner_department'],
        'Likelihood': r['likelihood'],
        'Residual Score': r.get('residual_score', 0),
        'Risk Level': r.get('risk_level', 'Unknown'),
        'Status': r['status']
    } for r in top_risks])
    
    st.dataframe(df_top, use_container_width=True, hide_index=True)


def create_risk_heat_map(risks: List[Dict]) -> go.Figure:
    """Create risk heat map"""
    # Create matrix
    likelihood_levels = [1, 2, 3, 4, 5]
    impact_levels = [1, 2, 3, 4, 5]
    
    matrix = [[0 for _ in impact_levels] for _ in likelihood_levels]
    
    for risk in risks:
        likelihood = risk['likelihood'] - 1  # 0-indexed
        impact = risk['impact'].get('overall_impact', 3) - 1  # 0-indexed
        
        if 0 <= likelihood < 5 and 0 <= impact < 5:
            matrix[likelihood][impact] += 1
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
        y=['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost Certain'],
        colorscale='RdYlGn_r',
        text=matrix,
        texttemplate='%{text}',
        textfont={"size": 16},
        showscale=True
    ))
    
    fig.update_layout(
        xaxis_title="Impact",
        yaxis_title="Likelihood",
        height=400
    )
    
    return fig


def show_risk_register(readonly=False):
    """Full risk register with filtering"""
    st.header("Risk Register")
    
    risks = db.get_all_risks()
    
    if not risks:
        st.info("No risks registered yet.")
        return
    
    # Filters
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        categories = list(set(r['category'] for r in risks))
        filter_category = st.multiselect("Filter by Category", options=categories, default=categories)
    
    with col_filter2:
        departments = list(set(r['owner_department'] for r in risks))
        filter_dept = st.multiselect("Filter by Department", options=departments, default=departments)
    
    with col_filter3:
        risk_levels = list(set(r.get('risk_level', 'Unknown') for r in risks))
        filter_level = st.multiselect("Filter by Risk Level", options=risk_levels, default=risk_levels)
    
    # Apply filters
    filtered_risks = [
        r for r in risks
        if r['category'] in filter_category
        and r['owner_department'] in filter_dept
        and r.get('risk_level', 'Unknown') in filter_level
    ]
    
    st.markdown(f"**Showing {len(filtered_risks)} of {len(risks)} risks**")
    
    # Display risks
    for risk in filtered_risks:
        with st.expander(f"{risk['risk_id']} - {risk['risk_name']} [{risk.get('risk_level', 'Unknown')}]"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Category:** {risk['category']}")
                st.markdown(f"**Owner:** {risk['risk_owner']}")
                st.markdown(f"**Department:** {risk['owner_department']}")
                st.markdown(f"**Status:** {risk['status']}")
                st.markdown(f"**Description:** {risk['description']}")
            
            with col2:
                st.markdown(f"**Likelihood:** {risk['likelihood']}/5")
                st.markdown(f"**Inherent Score:** {risk.get('inherent_score', 'N/A')}")
                st.markdown(f"**Residual Score:** {risk.get('residual_score', 'N/A')}")
                st.markdown(f"**Risk Level:** {risk.get('risk_level', 'Unknown')}")
                st.markdown(f"**Last Reviewed:** {risk['last_reviewed'][:10]}")


def show_risk_form(department_only=False):
    """Form to add/edit risks"""
    st.header("Add/Edit Risk")
    
    # Risk ID
    risk_id = st.text_input("Risk ID", value=f"RISK-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_name = st.text_input("Risk Name*")
        category = st.selectbox("Category*", options=[c.value for c in RiskCategory])
        risk_owner = st.text_input("Risk Owner*")
        owner_dept = st.text_input("Owner Department*",
                                   value=st.session_state.user['department'] if department_only else "")
    
    with col2:
        status = st.selectbox("Status*", options=[s.value for s in RiskStatus])
        likelihood = st.select_slider("Likelihood*", options=[1, 2, 3, 4, 5],
                                     format_func=lambda x: f"{x} - {LikelihoodLevel(x).name}")
    
    description = st.text_area("Risk Description*", height=100)
    
    # Impact assessment
    st.subheader("Impact Assessment")
    col_imp1, col_imp2, col_imp3, col_imp4 = st.columns(4)
    
    with col_imp1:
        financial_impact = st.select_slider("Financial Impact", options=[1, 2, 3, 4, 5],
                                           format_func=lambda x: ImpactLevel(x).name)
    with col_imp2:
        operational_impact = st.select_slider("Operational Impact", options=[1, 2, 3, 4, 5],
                                             format_func=lambda x: ImpactLevel(x).name)
    with col_imp3:
        regulatory_impact = st.select_slider("Regulatory Impact", options=[1, 2, 3, 4, 5],
                                            format_func=lambda x: ImpactLevel(x).name)
    with col_imp4:
        reputational_impact = st.select_slider("Reputational Impact", options=[1, 2, 3, 4, 5],
                                              format_func=lambda x: ImpactLevel(x).name)
    
    # Causes and triggers
    causes = st.text_area("Causes (one per line)", height=80)
    triggers = st.text_area("Triggers (one per line)", height=80)
    
    if st.button("Save Risk", type="primary"):
        if risk_name and category and risk_owner and owner_dept and description:
            # Create impact assessment
            impact = ImpactAssessment(
                financial=ImpactLevel(financial_impact),
                operational=ImpactLevel(operational_impact),
                regulatory=ImpactLevel(regulatory_impact),
                reputational=ImpactLevel(reputational_impact)
            )
            
            # Create risk dict
            risk_dict = {
                'risk_id': risk_id,
                'risk_name': risk_name,
                'category': category,
                'description': description,
                'risk_owner': risk_owner,
                'owner_department': owner_dept,
                'causes': [c.strip() for c in causes.split('\n') if c.strip()],
                'triggers': [t.strip() for t in triggers.split('\n') if t.strip()],
                'likelihood': likelihood,
                'impact': {
                    'financial': financial_impact,
                    'operational': operational_impact,
                    'regulatory': regulatory_impact,
                    'reputational': reputational_impact,
                    'overall_impact': impact.get_overall_score()
                },
                'status': status,
                'inherent_score': likelihood * impact.get_overall_score(),
                'residual_score': likelihood * impact.get_overall_score(),  # Initial residual = inherent
                'risk_level': 'Unknown',
                'last_reviewed': datetime.now().isoformat()
            }
            
            # Calculate risk level
            if risk_dict['residual_score'] >= 19:
                risk_dict['risk_level'] = 'Critical'
            elif risk_dict['residual_score'] >= 13:
                risk_dict['risk_level'] = 'High'
            elif risk_dict['residual_score'] >= 7:
                risk_dict['risk_level'] = 'Medium'
            else:
                risk_dict['risk_level'] = 'Low'
            
            # Save
            if db.store_risk(risk_dict, st.session_state.user['username']):
                st.success(f"Risk {risk_id} saved successfully!")
            else:
                st.error("Error saving risk")
        else:
            st.error("Please fill in all required fields (*)")


def show_risk_interdependencies():
    """Risk interdependency network visualization"""
    st.header("Risk Interdependencies")
    
    # Get all risks
    all_risks = db.get_all_risks()
    
    if not all_risks:
        st.info("No risks found. Add risks first before creating interdependencies.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Add Dependency", "Network View", "Dependency List"])
    
    with tab1:
        st.subheader("Create Risk Interdependency")
        
        col1, col2 = st.columns(2)
        
        risk_options = {f"{r['risk_id']} - {r['risk_name']}": r['risk_id'] for r in all_risks}
        
        with col1:
            source_risk = st.selectbox(
                "Source Risk (Causes/Triggers)",
                options=list(risk_options.keys()),
                key="source_risk"
            )
        
        with col2:
            target_risk = st.selectbox(
                "Target Risk (Affected)",
                options=list(risk_options.keys()),
                key="target_risk"
            )
        
        relationship_type = st.selectbox(
            "Relationship Type",
            ["Triggers", "Amplifies", "Causes", "Depends On", "Mitigates"]
        )
        
        col3, col4 = st.columns(2)
        
        with col3:
            impact_multiplier = st.slider(
                "Impact Multiplier",
                min_value=0.5,
                max_value=3.0,
                value=1.0,
                step=0.1,
                help="How much does the source risk amplify the target risk?"
            )
        
        with col4:
            probability_increase = st.slider(
                "Probability Increase (%)",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                help="How much does source risk increase likelihood of target risk?"
            )
        
        description = st.text_area(
            "Description",
            placeholder="Explain how these risks are related...",
            height=100
        )
        
        if st.button("Save Interdependency", type="primary"):
            source_id = risk_options[source_risk]
            target_id = risk_options[target_risk]
            
            if source_id == target_id:
                st.error("A risk cannot be dependent on itself!")
            else:
                # Store in database
                try:
                    conn = db.connect()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO risk_interdependencies 
                            (source_risk_id, target_risk_id, relationship_type, 
                             impact_multiplier, probability_increase, description, 
                             validated, created_by, created_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            source_id,
                            target_id,
                            relationship_type,
                            impact_multiplier,
                            probability_increase / 100.0,
                            description,
                            0,  # Not validated yet
                            st.session_state.user['username'],
                            datetime.now().isoformat()
                        ))
                        conn.commit()
                        conn.close()
                        st.success(f"Interdependency created: {source_id} → {target_id}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error saving interdependency: {e}")
    
    with tab2:
        st.subheader("Risk Network Visualization")
        
        # Get all interdependencies from database
        try:
            conn = db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT source_risk_id, target_risk_id, relationship_type, 
                           impact_multiplier, probability_increase
                    FROM risk_interdependencies
                ''')
                dependencies = cursor.fetchall()
                conn.close()
                
                if dependencies:
                    # Create network graph
                    import networkx as nx
                    
                    G = nx.DiGraph()
                    
                    # Add nodes
                    risk_dict = {r['risk_id']: r for r in all_risks}
                    for risk in all_risks:
                        G.add_node(risk['risk_id'], 
                                  label=risk['risk_name'],
                                  severity=risk.get('risk_severity', 'UNKNOWN'))
                    
                    # Add edges
                    edge_labels = {}
                    for dep in dependencies:
                        G.add_edge(dep['source_risk_id'], dep['target_risk_id'])
                        edge_labels[(dep['source_risk_id'], dep['target_risk_id'])] = dep['relationship_type']
                    
                    # Create layout
                    pos = nx.spring_layout(G, k=2, iterations=50)
                    
                    # Create edge traces
                    edge_trace = []
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        
                        edge_trace.append(
                            go.Scatter(
                                x=[x0, x1, None],
                                y=[y0, y1, None],
                                mode='lines',
                                line=dict(width=2, color='#888'),
                                hoverinfo='none',
                                showlegend=False
                            )
                        )
                    
                    # Create node trace
                    node_x = []
                    node_y = []
                    node_text = []
                    node_colors = []
                    
                    severity_colors = {
                        'CRITICAL': '#ff4444',
                        'HIGH': '#ff8800',
                        'MEDIUM': '#ffbb00',
                        'LOW': '#00aa00',
                        'UNKNOWN': '#888888'
                    }
                    
                    for node in G.nodes():
                        x, y = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        
                        risk_info = risk_dict.get(node, {})
                        node_text.append(f"{node}<br>{risk_info.get('risk_name', '')}<br>Severity: {risk_info.get('risk_severity', 'UNKNOWN')}")
                        node_colors.append(severity_colors.get(risk_info.get('risk_severity', 'UNKNOWN'), '#888888'))
                    
                    node_trace = go.Scatter(
                        x=node_x,
                        y=node_y,
                        mode='markers+text',
                        hoverinfo='text',
                        text=[node for node in G.nodes()],
                        textposition="top center",
                        hovertext=node_text,
                        marker=dict(
                            size=30,
                            color=node_colors,
                            line=dict(width=2, color='white')
                        ),
                        showlegend=False
                    )
                    
                    # Create figure
                    fig = go.Figure(data=edge_trace + [node_trace])
                    
                    fig.update_layout(
                        title="Risk Interdependency Network",
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Network statistics
                    st.divider()
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Nodes", len(G.nodes()))
                    with col2:
                        st.metric("Total Dependencies", len(G.edges()))
                    with col3:
                        # Most connected risk
                        if G.nodes():
                            degrees = dict(G.degree())
                            most_connected = max(degrees, key=degrees.get)
                            st.metric("Most Connected", most_connected, degrees[most_connected])
                    with col4:
                        # Isolated risks
                        isolated = [n for n in G.nodes() if G.degree(n) == 0]
                        st.metric("Isolated Risks", len(isolated))
                    
                else:
                    st.info("No interdependencies created yet. Add some in the 'Add Dependency' tab.")
        except Exception as e:
            st.error(f"Error loading network: {e}")
    
    with tab3:
        st.subheader("All Risk Interdependencies")
        
        # Get all interdependencies
        try:
            conn = db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT d.dependency_id, d.source_risk_id, d.target_risk_id, 
                           d.relationship_type, d.impact_multiplier, 
                           d.probability_increase, d.description, d.created_by, 
                           d.created_date, d.validated
                    FROM risk_interdependencies d
                    ORDER BY d.created_date DESC
                ''')
                deps = cursor.fetchall()
                conn.close()
                
                if deps:
                    for dep in deps:
                        with st.expander(f"{dep['source_risk_id']} → {dep['target_risk_id']} ({dep['relationship_type']})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Source Risk:** {dep['source_risk_id']}")
                                st.write(f"**Target Risk:** {dep['target_risk_id']}")
                                st.write(f"**Relationship:** {dep['relationship_type']}")
                            
                            with col2:
                                st.write(f"**Impact Multiplier:** {dep['impact_multiplier']}x")
                                st.write(f"**Probability Increase:** {dep['probability_increase'] * 100:.0f}%")
                                st.write(f"**Created By:** {dep['created_by']}")
                            
                            if dep['description']:
                                st.write(f"**Description:** {dep['description']}")
                            
                            # Delete button
                            if st.button(f"Delete", key=f"del_{dep['dependency_id']}"):
                                try:
                                    conn = db.connect()
                                    if conn:
                                        cursor = conn.cursor()
                                        cursor.execute('DELETE FROM risk_interdependencies WHERE dependency_id = ?', 
                                                     (dep['dependency_id'],))
                                        conn.commit()
                                        conn.close()
                                        st.success("Deleted!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting: {e}")
                else:
                    st.info("No interdependencies found.")
        except Exception as e:
            st.error(f"Error loading dependencies: {e}")


def show_mitigation_tracking():
    """Mitigation action tracking"""
    st.header("Mitigation Action Tracking")
    
    # Get all risks for dropdown
    all_risks = db.get_all_risks()
    
    if not all_risks:
        st.info("No risks found. Add risks first before creating mitigation actions.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Add Action", "Dashboard", "All Actions", "Progress Report"])
    
    with tab1:
        st.subheader("Create Mitigation Action")
        
        # Risk selection
        risk_options = {f"{r['risk_id']} - {r['risk_name']}": r['risk_id'] for r in all_risks}
        selected_risk = st.selectbox("Select Risk", options=list(risk_options.keys()))
        risk_id = risk_options[selected_risk]
        
        # Action details
        action_description = st.text_area(
            "Action Description",
            placeholder="Describe the mitigation action in detail...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            responsible_person = st.text_input("Responsible Person")
            responsible_dept = st.selectbox(
                "Responsible Department",
                ["Finance", "IT", "Operations", "HR", "Legal", "Compliance", "Other"]
            )
            deadline = st.date_input("Deadline", min_value=datetime.now().date())
        
        with col2:
            status = st.selectbox(
                "Status",
                ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"]
            )
            progress = st.slider("Progress (%)", 0, 100, 0, 5)
            cost_estimate = st.number_input("Cost Estimate (€)", min_value=0.0, value=0.0, step=1000.0)
        
        expected_reduction = st.slider(
            "Expected Risk Reduction (%)",
            0, 100, 0, 5,
            help="How much will this action reduce the risk score?"
        )
        
        notes = st.text_area("Additional Notes", height=80)
        
        if st.button("Save Mitigation Action", type="primary"):
            if action_description and responsible_person:
                # Generate action ID
                action_id = f"ACT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                try:
                    conn = db.connect()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO mitigation_actions 
                            (action_id, risk_id, description, responsible_person, 
                             responsible_department, deadline, status, progress_percentage,
                             cost_estimate, expected_risk_reduction, notes, 
                             created_date, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            action_id,
                            risk_id,
                            action_description,
                            responsible_person,
                            responsible_dept,
                            deadline.isoformat(),
                            status,
                            progress,
                            cost_estimate,
                            expected_reduction,
                            notes,
                            datetime.now().isoformat(),
                            datetime.now().isoformat()
                        ))
                        
                        # Log to action history
                        cursor.execute('''
                            INSERT INTO action_history
                            (action_id, old_status, new_status, old_progress, 
                             new_progress, changed_by, changed_date, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            action_id,
                            None,
                            status,
                            0,
                            progress,
                            st.session_state.user['username'],
                            datetime.now().isoformat(),
                            "Action created"
                        ))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"Mitigation action created: {action_id}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error saving action: {e}")
            else:
                st.error("Please fill in all required fields!")
    
    with tab2:
        st.subheader("Mitigation Action Dashboard")
        
        # Get all actions
        try:
            conn = db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM mitigation_actions
                    ORDER BY deadline ASC
                ''')
                actions = cursor.fetchall()
                conn.close()
                
                if actions:
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_actions = len(actions)
                    completed = len([a for a in actions if a['status'] == 'Completed'])
                    in_progress = len([a for a in actions if a['status'] == 'In Progress'])
                    overdue = len([a for a in actions if a['deadline'] < datetime.now().date().isoformat() and a['status'] not in ['Completed', 'Cancelled']])
                    
                    with col1:
                        st.metric("Total Actions", total_actions)
                    with col2:
                        st.metric("Completed", completed, f"{(completed/total_actions*100):.0f}%")
                    with col3:
                        st.metric("In Progress", in_progress)
                    with col4:
                        st.metric("Overdue", overdue, delta_color="inverse")
                    
                    st.divider()
                    
                    # Status distribution chart
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        status_counts = {}
                        for action in actions:
                            status = action['status']
                            status_counts[status] = status_counts.get(status, 0) + 1
                        
                        fig_status = go.Figure(data=[go.Pie(
                            labels=list(status_counts.keys()),
                            values=list(status_counts.values()),
                            hole=.3
                        )])
                        fig_status.update_layout(title="Actions by Status", height=400)
                        st.plotly_chart(fig_status, use_container_width=True)
                    
                    with col2:
                        # Department distribution
                        dept_counts = {}
                        for action in actions:
                            dept = action['responsible_department']
                            dept_counts[dept] = dept_counts.get(dept, 0) + 1
                        
                        fig_dept = go.Figure(data=[go.Bar(
                            x=list(dept_counts.keys()),
                            y=list(dept_counts.values()),
                            marker_color='lightblue'
                        )])
                        fig_dept.update_layout(
                            title="Actions by Department",
                            xaxis_title="Department",
                            yaxis_title="Count",
                            height=400
                        )
                        st.plotly_chart(fig_dept, use_container_width=True)
                    
                    st.divider()
                    
                    # Timeline view - upcoming deadlines
                    st.subheader("Upcoming Deadlines")
                    
                    upcoming = sorted([a for a in actions if a['status'] not in ['Completed', 'Cancelled']], 
                                    key=lambda x: x['deadline'])[:10]
                    
                    if upcoming:
                        for action in upcoming:
                            deadline_date = datetime.fromisoformat(action['deadline']).date()
                            days_until = (deadline_date - datetime.now().date()).days
                            
                            if days_until < 0:
                                deadline_str = f"OVERDUE by {abs(days_until)} days"
                                color = "red"
                            elif days_until == 0:
                                deadline_str = "DUE TODAY"
                                color = "orange"
                            elif days_until <= 7:
                                deadline_str = f"Due in {days_until} days"
                                color = "orange"
                            else:
                                deadline_str = f"Due in {days_until} days"
                                color = "normal"
                            
                            with st.container():
                                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                                with col1:
                                    st.write(f"**{action['action_id']}**")
                                    st.caption(action['description'][:80] + "...")
                                with col2:
                                    st.write(f"**{action['responsible_person']}**")
                                    st.caption(action['responsible_department'])
                                with col3:
                                    if color == "red":
                                        st.error(deadline_str)
                                    elif color == "orange":
                                        st.warning(deadline_str)
                                    else:
                                        st.info(deadline_str)
                                with col4:
                                    st.progress(action['progress_percentage'] / 100.0)
                                    st.caption(f"{action['progress_percentage']}%")
                                st.divider()
                    else:
                        st.info("No upcoming actions.")
                else:
                    st.info("No mitigation actions found. Create one in the 'Add Action' tab.")
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
    
    with tab3:
        st.subheader("All Mitigation Actions")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_status = st.selectbox("Filter by Status", ["All", "Not Started", "In Progress", "Completed", "On Hold", "Cancelled"])
        with col2:
            filter_dept = st.selectbox("Filter by Department", ["All", "Finance", "IT", "Operations", "HR", "Legal", "Compliance", "Other"])
        with col3:
            filter_risk = st.selectbox("Filter by Risk", ["All"] + [f"{r['risk_id']}" for r in all_risks])
        
        # Get filtered actions
        try:
            conn = db.connect()
            if conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM mitigation_actions WHERE 1=1"
                params = []
                
                if filter_status != "All":
                    query += " AND status = ?"
                    params.append(filter_status)
                
                if filter_dept != "All":
                    query += " AND responsible_department = ?"
                    params.append(filter_dept)
                
                if filter_risk != "All":
                    query += " AND risk_id = ?"
                    params.append(filter_risk)
                
                query += " ORDER BY deadline ASC"
                
                cursor.execute(query, params)
                actions = cursor.fetchall()
                conn.close()
                
                if actions:
                    for action in actions:
                        # Determine if overdue
                        deadline_date = datetime.fromisoformat(action['deadline']).date()
                        is_overdue = deadline_date < datetime.now().date() and action['status'] not in ['Completed', 'Cancelled']
                        
                        status_emoji = {
                            'Not Started': '◦',
                            'In Progress': '●',
                            'Completed': '✓',
                            'On Hold': '‖',
                            'Cancelled': '✕'
                        }
                        
                        title = f"{status_emoji.get(action['status'], '•')} {action['action_id']} - {action['description'][:60]}"
                        if is_overdue:
                            title = f"[OVERDUE] " + title
                        
                        with st.expander(title):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Risk ID:** {action['risk_id']}")
                                st.write(f"**Description:** {action['description']}")
                                st.write(f"**Responsible:** {action['responsible_person']} ({action['responsible_department']})")
                                st.write(f"**Deadline:** {action['deadline']}")
                            
                            with col2:
                                st.write(f"**Status:** {action['status']}")
                                st.write(f"**Progress:** {action['progress_percentage']}%")
                                st.progress(action['progress_percentage'] / 100.0)
                                st.write(f"**Cost Estimate:** €{action['cost_estimate']:,.2f}")
                                st.write(f"**Expected Risk Reduction:** {action['expected_risk_reduction']}%")
                            
                            if action['notes']:
                                st.write(f"**Notes:** {action['notes']}")
                            
                            st.divider()
                            
                            # Update section
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                new_status = st.selectbox(
                                    "Update Status",
                                    ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"],
                                    index=["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"].index(action['status']),
                                    key=f"status_{action['action_id']}"
                                )
                            
                            with col2:
                                new_progress = st.slider(
                                    "Update Progress",
                                    0, 100, action['progress_percentage'], 5,
                                    key=f"progress_{action['action_id']}"
                                )
                            
                            with col3:
                                update_notes = st.text_input("Update Notes", key=f"notes_{action['action_id']}")
                            
                            if st.button(f"💾 Update", key=f"update_{action['action_id']}"):
                                try:
                                    conn = db.connect()
                                    if conn:
                                        cursor = conn.cursor()
                                        
                                        # Update action
                                        cursor.execute('''
                                            UPDATE mitigation_actions
                                            SET status = ?, progress_percentage = ?, last_updated = ?
                                            WHERE action_id = ?
                                        ''', (new_status, new_progress, datetime.now().isoformat(), action['action_id']))
                                        
                                        # Log to history
                                        cursor.execute('''
                                            INSERT INTO action_history
                                            (action_id, old_status, new_status, old_progress, 
                                             new_progress, changed_by, changed_date, notes)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                        ''', (
                                            action['action_id'],
                                            action['status'],
                                            new_status,
                                            action['progress_percentage'],
                                            new_progress,
                                            st.session_state.user['username'],
                                            datetime.now().isoformat(),
                                            update_notes or "Status/progress updated"
                                        ))
                                        
                                        conn.commit()
                                        conn.close()
                                        st.success("✅ Action updated!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating: {e}")
                            
                            # Delete button
                            if st.button(f"🗑️ Delete Action", key=f"delete_{action['action_id']}"):
                                try:
                                    conn = db.connect()
                                    if conn:
                                        cursor = conn.cursor()
                                        cursor.execute('DELETE FROM mitigation_actions WHERE action_id = ?', (action['action_id'],))
                                        conn.commit()
                                        conn.close()
                                        st.success("Deleted!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting: {e}")
                else:
                    st.info("No actions match the filter criteria.")
        except Exception as e:
            st.error(f"Error loading actions: {e}")
    
    with tab4:
        st.subheader("📈 Progress Report")
        
        try:
            conn = db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM mitigation_actions ORDER BY created_date ASC')
                actions = cursor.fetchall()
                conn.close()
                
                if actions:
                    # Overall progress
                    total_progress = sum(a['progress_percentage'] for a in actions) / len(actions)
                    st.metric("Overall Progress", f"{total_progress:.1f}%")
                    
                    st.divider()
                    
                    # Progress by risk
                    risk_progress = {}
                    for action in actions:
                        risk_id = action['risk_id']
                        if risk_id not in risk_progress:
                            risk_progress[risk_id] = []
                        risk_progress[risk_id].append(action['progress_percentage'])
                    
                    # Calculate average progress per risk
                    risk_avg_progress = {risk: sum(progs)/len(progs) for risk, progs in risk_progress.items()}
                    
                    fig = go.Figure(data=[go.Bar(
                        x=list(risk_avg_progress.keys()),
                        y=list(risk_avg_progress.values()),
                        marker_color='lightgreen',
                        text=[f"{v:.0f}%" for v in risk_avg_progress.values()],
                        textposition='outside'
                    )])
                    
                    fig.update_layout(
                        title="Average Progress by Risk",
                        xaxis_title="Risk ID",
                        yaxis_title="Progress (%)",
                        yaxis_range=[0, 105],
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.divider()
                    
                    # Cost analysis
                    st.subheader("💰 Cost Analysis")
                    
                    total_cost = sum(a['cost_estimate'] or 0 for a in actions)
                    completed_cost = sum(a['cost_estimate'] or 0 for a in actions if a['status'] == 'Completed')
                    in_progress_cost = sum(a['cost_estimate'] or 0 for a in actions if a['status'] == 'In Progress')
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Estimated Cost", f"€{total_cost:,.2f}")
                    with col2:
                        st.metric("Completed Actions Cost", f"€{completed_cost:,.2f}")
                    with col3:
                        st.metric("In Progress Cost", f"€{in_progress_cost:,.2f}")
                    
                    # Expected risk reduction
                    st.divider()
                    st.subheader("🎯 Expected Risk Reduction")
                    
                    completed_actions = [a for a in actions if a['status'] == 'Completed']
                    
                    if completed_actions:
                        total_reduction = sum(a['expected_risk_reduction'] or 0 for a in completed_actions)
                        avg_reduction = total_reduction / len(completed_actions)
                        
                        st.metric("Total Risk Reduction from Completed Actions", f"{total_reduction}%")
                        st.metric("Average Reduction per Action", f"{avg_reduction:.1f}%")
                    else:
                        st.info("No completed actions yet.")
                else:
                    st.info("No actions to report on.")
        except Exception as e:
            st.error(f"Error generating report: {e}")


def generate_risk_register_pdf(risks: List[Dict], department: str = "All") -> bytes:
    """Generate PDF report for risk register"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, 
                           topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("RISK REGISTER REPORT", title_style))
    elements.append(Spacer(1, 12))
    
    # Report metadata
    meta_data = [
        ["Report Date:", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Department:", department],
        ["Total Risks:", str(len(risks))]
    ]
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # Risk summary by status
    if risks:
        status_counts = {}
        severity_counts = {}
        for risk in risks:
            status = risk.get('status', 'Unknown')
            severity = risk.get('risk_severity', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        summary_data = [["Status", "Count"], ["", ""]]
        for status, count in status_counts.items():
            summary_data.append([status, str(count)])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
    
    # Detailed risk list
    elements.append(Paragraph("DETAILED RISK REGISTER", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    if risks:
        # Sort by risk score (descending)
        sorted_risks = sorted(risks, key=lambda x: x.get('risk_score', 0), reverse=True)
        
        for risk in sorted_risks:
            risk_data = [
                ["Risk ID:", risk.get('risk_id', 'N/A')],
                ["Risk Name:", risk.get('risk_name', 'N/A')],
                ["Category:", risk.get('category', 'N/A')],
                ["Department:", risk.get('department', 'N/A')],
                ["Status:", risk.get('status', 'N/A')],
                ["Likelihood:", risk.get('likelihood', 'N/A')],
                ["Impact:", risk.get('impact', 'N/A')],
                ["Risk Score:", str(risk.get('risk_score', 0))],
                ["Severity:", risk.get('risk_severity', 'N/A')],
                ["Owner:", risk.get('risk_owner', 'N/A')],
                ["Description:", risk.get('description', 'N/A')[:200] + "..." if len(risk.get('description', '')) > 200 else risk.get('description', 'N/A')],
            ]
            
            risk_table = Table(risk_data, colWidths=[1.5*inch, 4.5*inch])
            
            # Color code by severity
            severity = risk.get('risk_severity', '')
            if severity == 'CRITICAL':
                bg_color = colors.HexColor('#ff4444')
            elif severity == 'HIGH':
                bg_color = colors.HexColor('#ff8800')
            elif severity == 'MEDIUM':
                bg_color = colors.HexColor('#ffbb00')
            elif severity == 'LOW':
                bg_color = colors.HexColor('#00aa00')
            else:
                bg_color = colors.grey
            
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 8), (-1, 8), bg_color),
                ('TEXTCOLOR', (0, 8), (-1, 8), colors.white),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(risk_table)
            elements.append(Spacer(1, 15))
    else:
        elements.append(Paragraph("No risks found.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def show_reports(readonly=False):
    """Generate and export reports"""
    st.header("📊 Reports")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Risk Register Report", "Department Summary", "High Priority Risks", "Risk Trends"]
    )
    
    # Department filter
    departments = ["All", "Finance", "IT", "Operations", "HR", "Legal", "Compliance", "Other"]
    selected_dept = st.selectbox("Filter by Department", departments)
    
    st.divider()
    
    # Generate report based on selection
    if report_type == "Risk Register Report":
        st.subheader("📋 Complete Risk Register")
        
        # Get risks from database
        dept_filter = None if selected_dept == "All" else selected_dept
        risks = db.get_all_risks(department=dept_filter)
        
        if risks:
            # Display summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Risks", len(risks))
            with col2:
                critical = len([r for r in risks if r.get('risk_severity') == 'CRITICAL'])
                st.metric("Critical", critical)
            with col3:
                high = len([r for r in risks if r.get('risk_severity') == 'HIGH'])
                st.metric("High", high)
            with col4:
                active = len([r for r in risks if r.get('status') == 'ACTIVE'])
                st.metric("Active", active)
            
            st.divider()
            
            # Show preview table
            df = pd.DataFrame(risks)
            display_cols = ['risk_id', 'risk_name', 'category', 'department', 'risk_severity', 'risk_score', 'status']
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True, height=300)
            
            # PDF Download button
            st.divider()
            pdf_data = generate_risk_register_pdf(risks, selected_dept)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name=f"Risk_Register_{selected_dept}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                type="primary"
            )
            
        else:
            st.info("No risks found for the selected criteria.")
    
    elif report_type == "High Priority Risks":
        st.subheader("🔴 High Priority Risks Report")
        
        dept_filter = None if selected_dept == "All" else selected_dept
        all_risks = db.get_all_risks(department=dept_filter)
        high_priority = [r for r in all_risks if r.get('risk_severity') in ['CRITICAL', 'HIGH']]
        
        if high_priority:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Critical Risks", len([r for r in high_priority if r.get('risk_severity') == 'CRITICAL']))
            with col2:
                st.metric("High Risks", len([r for r in high_priority if r.get('risk_severity') == 'HIGH']))
            
            df = pd.DataFrame(high_priority)
            display_cols = ['risk_id', 'risk_name', 'risk_severity', 'risk_score', 'risk_owner', 'status']
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True, height=300)
            
            st.divider()
            pdf_data = generate_risk_register_pdf(high_priority, selected_dept)
            st.download_button(
                label="📥 Download High Priority PDF",
                data=pdf_data,
                file_name=f"High_Priority_Risks_{selected_dept}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.info("No high priority risks found.")
    
    else:
        st.info(f"{report_type} - Coming soon")


def show_user_management():
    """User management interface"""
    st.header("User Management")
    
    st.subheader("Create New User")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_username = st.text_input("Username")
        new_fullname = st.text_input("Full Name")
        new_email = st.text_input("Email")
    
    with col2:
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", options=[r.value for r in UserRole])
        new_dept = st.text_input("Department")
    
    if st.button("Create User"):
        if new_username and new_password and new_fullname and new_role and new_dept:
            role_enum = UserRole(new_role)
            user_id = db.create_user(
                new_username, new_password, new_fullname, role_enum,
                new_dept, new_email, st.session_state.user['username']
            )
            st.success(f"User created with ID: {user_id}")
        else:
            st.error("Please fill in all fields")


def show_audit_log():
    """Display audit log"""
    st.header("Audit Log")
    
    col1, col2 = st.columns(2)
    
    with col1:
        entity_type = st.selectbox("Filter by Entity Type", options=["ALL", "RISK", "USER", "ACTION"])
    
    with col2:
        limit = st.number_input("Number of Records", min_value=10, max_value=1000, value=100)
    
    logs = db.get_audit_trail(entity_type if entity_type != "ALL" else "", "", limit)
    
    if logs:
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
    else:
        st.info("No audit logs found")


def show_department_risks():
    """Show risks for specific department"""
    dept = st.session_state.user['department']
    st.header(f"Risks - {dept}")
    
    risks = db.get_all_risks(department=dept)
    
    if not risks:
        st.info(f"No risks registered for {dept} yet.")
        return
    
    for risk in risks:
        with st.expander(f"{risk['risk_id']} - {risk['risk_name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Category:** {risk['category']}")
                st.markdown(f"**Owner:** {risk['risk_owner']}")
                st.markdown(f"**Status:** {risk['status']}")
            
            with col2:
                st.markdown(f"**Residual Score:** {risk.get('residual_score', 'N/A')}")
                st.markdown(f"**Risk Level:** {risk.get('risk_level', 'Unknown')}")
                st.markdown(f"**Last Updated:** {risk['last_updated'][:10]}")


def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        login_screen()
    else:
        # Route based on role
        role = st.session_state.user['role']
        
        if role == UserRole.RISK_MANAGER.value:
            risk_manager_dashboard()
        elif role == UserRole.DEPARTMENT_CONTRIBUTOR.value:
            department_contributor_dashboard()
        elif role == UserRole.VIEW_ONLY.value:
            view_only_dashboard()


if __name__ == "__main__":
    main()
