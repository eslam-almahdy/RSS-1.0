# Enterprise RRS - Risk Assessment System
## Quick Start Guide

## Overview
Enterprise RRS (Risk Assessment System) is an ISO 31000 / COSO ERM compliant risk management platform designed for energy supply processes. It provides comprehensive risk identification, assessment, interdependency analysis, and mitigation tracking with multi-user role-based access control.

## System Access

### Dashboard URL
```
http://localhost:8503
```

### Default Login Credentials
- **Username:** admin
- **Password:** admin123
- **Role:** Risk Manager (full access)

**⚠️ IMPORTANT:** Change the default admin password immediately after first login!

## User Roles

### 1. Risk Manager (Full Access)
**Access Rights:**
- View, create, edit, and delete all risks
- Manage risk interdependencies
- Approve risk assessments
- Track mitigation actions
- Generate reports
- Create and manage users
- View audit logs

**Primary Responsibilities:**
- Overall risk governance
- Risk register maintenance
- Approval workflow management
- Strategic risk reporting
- User access management

### 2. Department Contributor (Department-Specific Access)
**Access Rights:**
- View all risks (read-only)
- Create and edit risks for own department
- Submit risk assessments for approval
- Update mitigation action progress
- View risk dashboard (read-only)

**Primary Responsibilities:**
- Identify department-specific risks
- Provide risk assessments
- Update mitigation progress
- Respond to risk questionnaires

### 3. View Only (Read-Only Access)
**Access Rights:**
- View risk dashboard
- View risk register (read-only)
- View reports (read-only)
- No editing capabilities

**Primary Responsibilities:**
- Management oversight
- Audit review
- Compliance monitoring

## Quick Start Workflow

### For Risk Managers

#### Step 1: Login
1. Open browser to `http://localhost:8503`
2. Enter credentials: admin / admin123
3. Click "Login"

#### Step 2: Create Additional Users
1. Navigate to "User Management" in sidebar
2. Fill in user details:
   - Username (unique)
   - Full Name
   - Email
   - Password
   - Role (Risk Manager / Department Contributor / View Only)
   - Department
3. Click "Create User"

#### Step 3: Add Your First Risk
1. Navigate to "Add/Edit Risk" in sidebar
2. Fill in required fields (*):
   - **Risk ID:** Auto-generated (RISK-YYYYMMDD-HHMMSS)
   - **Risk Name:** Short descriptive name
   - **Category:** Select from dropdown (Strategic, Financial, Operational, etc.)
   - **Risk Owner:** Person responsible
   - **Owner Department:** Department owning the risk
   - **Status:** Select current status (Identified, Under Assessment, etc.)
   - **Likelihood:** Rate 1-5 (Rare to Almost Certain)
   - **Description:** Detailed risk description
3. Complete Impact Assessment:
   - Financial Impact (1-5)
   - Operational Impact (1-5)
   - Regulatory Impact (1-5)
   - Reputational Impact (1-5)
4. Add Causes and Triggers (optional but recommended)
5. Click "Save Risk"

#### Step 4: View Risk Dashboard
1. Navigate to "Risk Dashboard"
2. Review key metrics:
   - Total Risks
   - Critical Risks
   - High Risks
   - Appetite Exceeded
3. Analyze Risk Heat Map
4. Review Top 10 Risks by Residual Score

#### Step 5: Monitor Audit Trail
1. Navigate to "Audit Log"
2. Filter by entity type (RISK, USER, ACTION)
3. Review all system activities

### For Department Contributors

#### Step 1: Login
1. Open browser to `http://localhost:8503`
2. Enter your credentials provided by Risk Manager
3. Click "Login"

#### Step 2: View Department Risks
1. Navigate to "My Department Risks"
2. Review existing risks for your department
3. Note any risks requiring updates

#### Step 3: Submit New Risk
1. Navigate to "Submit New Risk"
2. Complete risk form (same as Risk Manager process)
3. Department field is pre-filled with your department
4. Click "Save Risk"
5. Risk is submitted for Risk Manager approval

#### Step 4: View Overall Risk Landscape
1. Navigate to "Risk Dashboard (Read-Only)"
2. Review organization-wide risk metrics
3. Understand context of your department's risks

### For Viewers

#### Step 1: Login
1. Open browser to `http://localhost:8503`
2. Enter your credentials
3. Click "Login"

#### Step 2: Review Risk Dashboard
1. View key risk metrics
2. Analyze heat maps
3. Review top risks

#### Step 3: Explore Risk Register
1. Navigate to "Risk Register"
2. Use filters:
   - Category filter
   - Department filter
   - Risk Level filter
3. Expand risks to view details

#### Step 4: Access Reports
1. Navigate to "Reports"
2. View generated reports (feature in development)

## Risk Assessment Methodology

### Risk Scoring

#### Likelihood Scale (1-5)
1. **Rare (1):** May occur only in exceptional circumstances (<10% probability)
2. **Unlikely (2):** Could occur at some time (10-25% probability)
3. **Possible (3):** Might occur at some time (25-50% probability)
4. **Likely (4):** Will probably occur in most circumstances (50-75% probability)
5. **Almost Certain (5):** Expected to occur in most circumstances (>75% probability)

#### Impact Scale (1-5)
Each dimension (Financial, Operational, Regulatory, Reputational):
1. **Very Low (1):** Negligible impact, minimal disruption
2. **Low (2):** Minor impact, short-term disruption
3. **Medium (3):** Moderate impact, noticeable disruption
4. **High (4):** Major impact, significant disruption
5. **Very High (5):** Catastrophic impact, severe disruption

#### Risk Score Calculation
- **Inherent Risk Score** = Likelihood × Overall Impact
- **Residual Risk Score** = (Likelihood after controls) × (Impact after controls)
- **Overall Impact** = Average of all four impact dimensions

#### Risk Levels
- **Low:** Score 1-6 (Green)
- **Medium:** Score 7-12 (Yellow)
- **High:** Score 13-18 (Orange)
- **Critical:** Score 19-25 (Red)

### Risk Heat Map
The heat map visualizes risk distribution across likelihood (Y-axis) and impact (X-axis). Each cell shows the number of risks in that category. Use this to identify risk concentrations and prioritize mitigation efforts.

## Risk Categories

### 1. Strategic Risk
Business strategy, market positioning, competitive landscape

### 2. Financial Risk
Financial performance, cash flow, credit risk, market risk

### 3. Operational Risk
Process failures, system outages, supply chain disruptions

### 4. Compliance/Regulatory Risk
Legal compliance, regulatory changes, policy violations

### 5. Technology Risk
IT systems, cybersecurity, data integrity

### 6. Human Resources Risk
Key personnel, skills gaps, organizational culture

### 7. Environmental Risk
Climate change, environmental regulations, sustainability

### 8. Reputational Risk
Brand damage, stakeholder confidence, public perception

## Risk Status Options

- **Identified:** Risk has been identified but not yet assessed
- **Under Assessment:** Currently being evaluated
- **Assessed:** Assessment completed, awaiting mitigation plan
- **Mitigation In Progress:** Mitigation actions underway
- **Monitoring:** Risk under active monitoring
- **Closed:** Risk no longer applicable or fully mitigated

## Database Structure

### Tables Created
1. **users:** User authentication and profiles
2. **sessions:** Active user sessions
3. **risks:** Complete risk register
4. **risk_history:** Risk change versioning
5. **risk_interdependencies:** Risk cause-effect relationships
6. **mitigation_actions:** Action plans with progress tracking
7. **action_history:** Mitigation action change log
8. **questionnaires:** Department risk questionnaires
9. **questionnaire_responses:** Questionnaire submissions
10. **audit_log:** Complete audit trail
11. **risk_appetite:** Risk tolerance thresholds
12. **reports:** Generated report archive

### Audit Trail
All actions are logged:
- User logins/logouts
- Risk creation/updates/deletion
- User creation
- Approval actions
- Report generation

Access audit log via "Audit Log" page (Risk Manager only).

## Features In Development

### Phase 1 (Current)
✅ Multi-user authentication
✅ Role-based access control
✅ Risk register with CRUD operations
✅ Risk dashboard with heat maps
✅ User management
✅ Audit logging
✅ Database with versioning

### Phase 2 (Next Release)
⏳ Risk interdependency network visualization
⏳ Mitigation action tracking with deadlines
⏳ Automated email notifications
⏳ Department questionnaires
⏳ Advanced reporting (PDF export)
⏳ Risk appetite threshold alerts
⏳ Approval workflow for department submissions

### Phase 3 (Future)
⏳ Monte Carlo simulation integration
⏳ Quantitative risk analysis
⏳ Risk aggregation algorithms
⏳ External data connectors
⏳ Mobile app interface
⏳ AI-powered risk identification

## Technical Details

### Technology Stack
- **Backend:** Python 3.12
- **Web Framework:** Streamlit 1.31+
- **Database:** SQLite (embedded)
- **Visualization:** Plotly
- **Data Processing:** Pandas, NumPy

### System Requirements
- Python 3.12 or higher
- 4GB RAM minimum
- 500MB disk space
- Modern web browser (Chrome, Firefox, Edge)

### Installation
```bash
# Install dependencies
pip install -r rrs_requirements.txt

# Initialize database
python rrs_database.py

# Launch dashboard
streamlit run rrs_dashboard.py --server.port 8503
```

### File Structure
```
rrs_core.py                 # Core risk engine and data structures
rrs_database.py             # Database layer with authentication
rrs_dashboard.py            # Multi-user Streamlit interface
rrs_requirements.txt        # Python dependencies
rrs_enterprise.db           # SQLite database (created on init)
```

## Security Considerations

### Password Security
- Passwords hashed using PBKDF2-HMAC-SHA256
- 100,000 iterations for key derivation
- Unique salt per user
- Failed login attempt tracking
- Account lockout after 5 failed attempts

### Session Management
- Secure session tokens (32-byte URL-safe)
- 8-hour session expiration
- Session validation on each request
- Clean logout with session invalidation

### Access Control
- Role-based permissions enforced at database level
- Department-level data isolation for contributors
- Audit trail for all sensitive operations

### Best Practices
1. Change default admin password immediately
2. Use strong passwords (12+ characters, mixed case, numbers, symbols)
3. Assign minimum necessary role to each user
4. Review audit logs regularly
5. Disable accounts for departed employees
6. Conduct periodic user access reviews

## Compliance

### ISO 31000 Alignment
- **Risk Identification:** Structured risk categories
- **Risk Analysis:** Qualitative and quantitative assessment
- **Risk Evaluation:** Heat maps and scoring
- **Risk Treatment:** Mitigation action tracking
- **Monitoring and Review:** Audit trails and versioning
- **Communication:** Multi-stakeholder access

### COSO ERM Framework Alignment
- **Governance & Culture:** Role-based access control
- **Strategy & Objective-Setting:** Risk appetite thresholds
- **Performance:** Risk heat maps and dashboards
- **Review & Revision:** Version control and audit logs
- **Information, Communication & Reporting:** Multi-user platform

## Troubleshooting

### Cannot Login
- Verify credentials are correct (case-sensitive)
- Check if account is locked (contact Risk Manager)
- Ensure database file exists (rrs_enterprise.db)
- Try clearing browser cache

### Dashboard Not Loading
- Ensure Streamlit is running (`streamlit run rrs_dashboard.py`)
- Check port 8503 is available
- Verify rrs_core.py and rrs_database.py are in same directory
- Check terminal for error messages

### Cannot Save Risk
- Ensure all required fields (*) are filled
- Verify user has appropriate role permissions
- Check database file permissions
- Review audit log for error details

### Database Errors
- Ensure rrs_enterprise.db exists
- Run `python rrs_database.py` to reinitialize
- Check disk space availability
- Verify file write permissions

## Support

### Documentation Files
- **RRS_QUICK_START.md** (this file): User guide
- **rrs_core.py:** Inline code documentation
- **rrs_database.py:** Database schema documentation

### Contact
For technical support or questions, contact your system administrator.

## Version History

### Version 1.0 (Current)
- Initial release
- Core risk register functionality
- Multi-user authentication
- Role-based access control
- Risk dashboard with heat maps
- User management
- Audit logging

---

**Enterprise RRS - Risk Assessment System**  
ISO 31000 / COSO ERM Compliant  
Energy Supply Process Risk Management  

© 2026 - All Rights Reserved
