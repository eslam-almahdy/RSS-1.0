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

from rrs_database import RRSDatabase, UserRole, AuditAction
from rrs_core import (
    Risk, RiskCategory, ImpactDimension, LikelihoodLevel, ImpactLevel,
    RiskStatus, ImpactAssessment, RiskInterdependencyEngine, RiskPrioritizer
)


# Page config
st.set_page_config(
    page_title="Enterprise RRS - Risk Assessment System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.title("🛡️ Enterprise Risk Assessment System")
    st.markdown("### ISO 31000 / COSO ERM Compliant")
    
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
    st.title("🛡️ Enterprise Risk Assessment System")
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
    st.title("🛡️ Risk Assessment - Department View")
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
    st.title("🛡️ Risk Assessment - Viewer Dashboard")
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
        st.metric("Critical Risks", critical_risks, delta=None if critical_risks == 0 else f"⚠️")
    with col3:
        st.metric("High Risks", high_risks)
    with col4:
        st.metric("Appetite Exceeded", appetite_exceeded, delta=None if appetite_exceeded == 0 else f"⚠️")
    
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
                financial=financial_impact,
                operational=operational_impact,
                regulatory=regulatory_impact,
                reputational=reputational_impact
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
    st.info("Interdependency visualization - Coming soon")


def show_mitigation_tracking():
    """Mitigation action tracking"""
    st.header("Mitigation Action Tracking")
    st.info("Mitigation tracking - Coming soon")


def show_reports():
    """Generate and export reports"""
    st.header("Reports")
    st.info("Report generation - Coming soon")


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
