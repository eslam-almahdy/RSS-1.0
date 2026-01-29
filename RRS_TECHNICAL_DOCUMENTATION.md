# Enterprise RRS - Technical Documentation
## Architecture, Design Decisions, and Implementation Guide

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Design Philosophy](#design-philosophy)
3. [Core Components](#core-components)
4. [Database Schema](#database-schema)
5. [Authentication & Security](#authentication--security)
6. [Risk Assessment Engine](#risk-assessment-engine)
7. [Multi-User Architecture](#multi-user-architecture)
8. [API Reference](#api-reference)
9. [Deployment Guide](#deployment-guide)
10. [Future Enhancements](#future-enhancements)

---

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                   Web Browser (Client)                   │
│                  http://localhost:8503                   │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/WebSocket
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit Web Framework                     │
│                (rrs_dashboard.py)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Multi-User Interface Layer                       │  │
│  │  - Login Screen                                   │  │
│  │  - Risk Manager Dashboard                         │  │
│  │  - Department Contributor Dashboard               │  │
│  │  - View Only Dashboard                            │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Business Logic Layer                        │
│                (rrs_core.py)                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  - Risk Dataclass (ISO 31000 Structure)          │  │
│  │  - ImpactAssessment (Multi-Dimensional)          │  │
│  │  - RiskInterdependencyEngine                     │  │
│  │  - RiskPrioritizer                               │  │
│  │  - Energy Supply Risk Templates                  │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Data Access Layer                           │
│                (rrs_database.py)                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  - RRSDatabase Class                              │  │
│  │  - Authentication Methods                         │  │
│  │  - CRUD Operations                                │  │
│  │  - Audit Logging                                  │  │
│  │  - Session Management                             │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              SQLite Database                             │
│           rrs_enterprise.db (Embedded)                   │
│  - 12 Tables (Users, Risks, Audit, etc.)                │
│  - Transaction Support (ACID)                           │
│  - File-Based Storage                                   │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. Presentation Layer (rrs_dashboard.py)
- User interface rendering
- Input validation
- Session state management
- Role-based view routing
- Data visualization (Plotly charts)

#### 2. Business Logic Layer (rrs_core.py)
- Risk data structures (ISO 31000 compliant)
- Risk scoring algorithms
- Interdependency analysis
- Risk prioritization
- Template management

#### 3. Data Access Layer (rrs_database.py)
- Database connection management
- CRUD operations
- Authentication and authorization
- Audit logging
- Session management
- Password hashing

#### 4. Persistence Layer (SQLite)
- Data storage
- Transaction management
- Concurrent access control
- Data integrity enforcement

---

## Design Philosophy

### 1. Security-First Design
**Principle:** All access must be authenticated and authorized.

**Implementation:**
- Password hashing with PBKDF2-HMAC-SHA256
- Session-based authentication
- Role-based access control (RBAC)
- Account lockout after failed attempts
- Comprehensive audit logging

**Rationale:** Energy supply risk data is sensitive. Unauthorized access could compromise strategic planning or regulatory compliance.

### 2. ISO 31000 / COSO ERM Compliance
**Principle:** Risk management must align with international standards.

**Implementation:**
- Structured risk categories matching COSO domains
- Risk identification, analysis, evaluation, treatment workflow
- Monitoring and review via audit trails
- Communication via multi-stakeholder platform

**Rationale:** Regulatory compliance and best practice adherence required for audits.

### 3. Multi-User Collaboration
**Principle:** Risk management is a shared responsibility across departments.

**Implementation:**
- Three-tier role model (Manager/Contributor/Viewer)
- Department-specific data isolation
- Approval workflows
- Audit trails for accountability

**Rationale:** Effective risk management requires input from operations, trading, IT, compliance, etc.

### 4. Data Integrity and Auditability
**Principle:** All changes must be tracked and reversible.

**Implementation:**
- Risk versioning (risk_history table)
- Audit log for all actions
- Change attribution (who, when, what)
- Immutable audit trail

**Rationale:** Required for compliance audits and historical analysis.

### 5. Scalability and Extensibility
**Principle:** System must grow with organization needs.

**Implementation:**
- Modular architecture (separate core/database/dashboard)
- Template-based risk entry
- Extensible risk categories
- Plugin architecture for future modules

**Rationale:** Initial deployment may be small, but enterprise systems grow over time.

---

## Core Components

### rrs_core.py

#### Risk Dataclass
**Purpose:** Core data structure for risk representation.

**Key Attributes:**
```python
@dataclass
class Risk:
    risk_id: str                    # Unique identifier
    risk_name: str                  # Short descriptive name
    category: RiskCategory          # Strategic, Financial, etc.
    description: str                # Detailed description
    risk_owner: str                 # Responsible person
    owner_department: str           # Owning department
    causes: List[str]               # Root causes
    triggers: List[str]             # Triggering events
    affected_processes: List[str]   # Impacted processes
    likelihood: LikelihoodLevel     # 1-5 scale
    impact: ImpactAssessment        # Multi-dimensional
    existing_controls: List[str]    # Current mitigations
    mitigation_strategy: Optional[MitigationStrategy]
    mitigation_actions: List[MitigationAction]
    linked_risks: List[str]         # Related risk IDs
    dependencies: List[RiskInterdependency]
    quantitative: Optional[Dict]    # Numerical estimates
    status: RiskStatus              # Current state
    last_reviewed: datetime
    next_review_due: Optional[datetime]
```

**Design Decisions:**
- **Dataclass:** Type safety, automatic __init__/__repr__, immutability options
- **Enums:** Constrained choices prevent data quality issues
- **Optional fields:** Flexibility for phased risk entry
- **Lists for causes/triggers:** Supports multiple root causes per risk

#### ImpactAssessment
**Purpose:** Multi-dimensional impact scoring.

**Dimensions:**
1. Financial: Direct monetary impact
2. Operational: Process disruption severity
3. Regulatory: Compliance violation risk
4. Reputational: Brand/stakeholder impact

**Scoring Method:**
```python
def get_overall_score(self) -> int:
    scores = [
        self.financial.value,
        self.operational.value,
        self.regulatory.value,
        self.reputational.value
    ]
    return round(sum(scores) / len(scores))
```

**Rationale:** Energy supply risks rarely have single-dimension impacts. Financial loss may accompany operational disruption and reputational damage.

#### RiskInterdependencyEngine
**Purpose:** Model cause-effect relationships between risks.

**Key Methods:**
- `find_risk_chains()`: Identify cascading risk paths
- `calculate_amplified_impact()`: Compute cumulative effect
- `identify_critical_risks()`: Find high-centrality nodes

**Algorithm:**
Graph-based analysis where risks are nodes and interdependencies are directed edges. Uses breadth-first search for chain discovery.

**Use Case:** "Supply disruption" risk may trigger "price volatility" risk, which triggers "margin compression" risk. Engine identifies this cascade.

#### RiskPrioritizer
**Purpose:** Rank risks for management attention.

**Scoring Formula:**
```
Priority Score = Residual Risk Score × Urgency Multiplier
Urgency Multiplier = f(next_review_due, escalation_required)
```

**Categorization:**
- **Immediate Action:** Score ≥ 19 OR requires_escalation
- **High Priority:** 13 ≤ Score < 19
- **Medium Priority:** 7 ≤ Score < 13
- **Monitor:** Score < 7

---

## Database Schema

### Entity Relationship Diagram
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   users     │1      N │   sessions   │         │ audit_log   │
│─────────────│◄────────┤──────────────│         │─────────────│
│ user_id (PK)│         │ session_id PK│         │ audit_id PK │
│ username    │         │ user_id (FK) │         │ user_id FK  │
│ password_*  │         │ expires_at   │         │ action      │
│ role        │         └──────────────┘         │ entity_type │
│ department  │                                  │ entity_id   │
└─────────────┘                                  │ timestamp   │
                                                 └─────────────┘

┌─────────────────┐         ┌──────────────────┐
│     risks       │1      N │  risk_history    │
│─────────────────│◄────────┤──────────────────│
│ risk_id (PK)    │         │ history_id (PK)  │
│ risk_name       │         │ risk_id (FK)     │
│ category        │         │ version          │
│ likelihood      │         │ risk_data_json   │
│ impact_json     │         │ changed_by       │
│ residual_score  │         │ changed_date     │
│ risk_level      │         └──────────────────┘
│ version         │
└─────────────────┘
       │1                    ┌──────────────────────┐
       │                   N │ risk_interdependencies│
       └─────────────────────┤──────────────────────│
                             │ dependency_id (PK)   │
                             │ source_risk_id (FK)  │
                             │ target_risk_id (FK)  │
                             │ relationship_type    │
                             │ impact_multiplier    │
                             └──────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│mitigation_actions│1      N │ action_history   │
│──────────────────│◄────────┤──────────────────│
│ action_id (PK)   │         │ history_id (PK)  │
│ risk_id (FK)     │         │ action_id (FK)   │
│ responsible_*    │         │ old_status       │
│ deadline         │         │ new_status       │
│ status           │         │ changed_by       │
│ progress_%       │         └──────────────────┘
└──────────────────┘

┌─────────────────┐         ┌──────────────────────┐
│ questionnaires  │1      N │questionnaire_responses│
│─────────────────│◄────────┤──────────────────────│
│questionnaire_id │         │ response_id (PK)     │
│ title           │         │ questionnaire_id FK  │
│ target_dept     │         │ respondent_user_id FK│
│ questions_json  │         │ responses_json       │
│ due_date        │         │ submitted_date       │
└─────────────────┘         └──────────────────────┘
```

### Table Details

#### users
**Purpose:** User authentication and profiles

**Columns:**
- `user_id` (PK): Auto-increment integer
- `username` (UNIQUE): Login identifier
- `password_hash`: PBKDF2-HMAC-SHA256 hash
- `salt`: Random 32-byte salt
- `full_name`: Display name
- `email`: Contact email
- `role`: Risk Manager / Department Contributor / View Only
- `department`: User's department
- `is_active`: Account status (0/1)
- `created_date`: Account creation timestamp
- `last_login`: Last successful login
- `failed_login_attempts`: Failed login counter
- `account_locked`: Lockout flag after 5 failed attempts

**Indexes:** username (unique), role, department

#### risks
**Purpose:** Complete risk register

**JSON Columns:**
- `impact_json`: ImpactAssessment serialized
- `existing_controls_json`: List of control descriptions
- `mitigation_actions_json`: List of MitigationAction objects
- `dependencies_json`: List of RiskInterdependency objects
- `quantitative_json`: Optional numerical estimates (probability distributions, VaR, etc.)

**Computed Columns:**
- `inherent_score`: Likelihood × Overall Impact (before controls)
- `residual_score`: Likelihood × Impact (after controls)
- `risk_level`: Low/Medium/High/Critical (calculated from residual_score)

#### risk_history
**Purpose:** Risk change versioning (complete audit trail)

**Columns:**
- `history_id` (PK): Auto-increment
- `risk_id` (FK): Reference to risks table
- `version`: Version number (increments with each update)
- `risk_data_json`: Complete risk snapshot as JSON
- `changed_by`: Username who made change
- `changed_date`: Timestamp of change
- `change_reason`: Optional explanation

**Use Case:** Rollback to previous risk version, historical analysis, audit compliance

#### risk_interdependencies
**Purpose:** Model cause-effect relationships

**Columns:**
- `source_risk_id`: Risk that causes/triggers
- `target_risk_id`: Risk that is affected
- `relationship_type`: "causes", "amplifies", "mitigates"
- `impact_multiplier`: Effect magnitude (e.g., 1.5 = 50% increase)
- `probability_increase`: Additional likelihood (e.g., 0.2 = +20%)
- `validated`: Boolean flag (requires Risk Manager approval)

**Algorithm Support:** Graph algorithms for chain detection, critical node identification

#### mitigation_actions
**Purpose:** Track risk treatment actions

**Columns:**
- `action_id` (PK): Unique identifier
- `risk_id` (FK): Associated risk
- `description`: Action description
- `responsible_person`: Owner
- `responsible_department`: Owning department
- `deadline`: Due date
- `status`: Not Started / In Progress / Completed / On Hold
- `progress_percentage`: 0-100%
- `cost_estimate`: Optional budget
- `expected_risk_reduction`: Estimated impact on residual score

#### audit_log
**Purpose:** Complete system activity log

**Logged Actions:**
- User login/logout
- Risk create/update/delete
- User account changes
- Approval actions
- Report generation

**Columns:**
- `user_id`: Who performed action
- `action`: CREATE / UPDATE / DELETE / VIEW / APPROVE / LOGIN
- `entity_type`: RISK / USER / ACTION / REPORT
- `entity_id`: ID of affected entity
- `details`: Action description
- `timestamp`: When action occurred

**Retention:** Never deleted (compliance requirement)

---

## Authentication & Security

### Password Hashing
**Algorithm:** PBKDF2-HMAC-SHA256

**Parameters:**
- Hash function: SHA-256
- Iterations: 100,000
- Salt length: 32 bytes (256 bits)
- Key derivation: 256-bit hash

**Code:**
```python
def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(32)  # Generate new salt
    
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',                      # Hash algorithm
        password.encode('utf-8'),      # Password as bytes
        salt.encode('utf-8'),          # Salt as bytes
        100000                         # Iterations
    )
    return pwd_hash.hex(), salt        # Return hex strings
```

**Security Properties:**
- **Rainbow table resistant:** Unique salt per user
- **Brute force resistant:** 100,000 iterations (slow)
- **Future-proof:** Iterations can be increased as compute power grows

### Session Management
**Token Generation:**
```python
session_id = secrets.token_urlsafe(32)  # 256-bit entropy, URL-safe base64
```

**Session Lifecycle:**
1. User authenticates → Session created with 8-hour expiration
2. Each request validates session (check expiration, is_active flag)
3. User logs out → Session invalidated (is_active = 0)
4. Session expires after 8 hours of inactivity

**Security Properties:**
- **Unpredictable tokens:** Cryptographically secure random generation
- **Session fixation protection:** New token on each login
- **Timeout protection:** Automatic expiration after 8 hours

### Access Control Matrix

| Feature | Risk Manager | Department Contributor | View Only |
|---------|-------------|------------------------|-----------|
| View all risks | ✅ | ✅ (Read-only) | ✅ (Read-only) |
| Create risk (any dept) | ✅ | ❌ | ❌ |
| Create risk (own dept) | ✅ | ✅ | ❌ |
| Edit risk (any dept) | ✅ | ❌ | ❌ |
| Edit risk (own dept) | ✅ | ✅ | ❌ |
| Delete risk | ✅ | ❌ | ❌ |
| Approve risk | ✅ | ❌ | ❌ |
| View dashboard | ✅ | ✅ | ✅ |
| Manage interdependencies | ✅ | ❌ | ❌ |
| Track mitigations | ✅ | ✅ (Own dept) | ❌ |
| Generate reports | ✅ | ❌ | ✅ (View only) |
| Create users | ✅ | ❌ | ❌ |
| View audit log | ✅ | ❌ | ❌ |

**Enforcement:** Checked in dashboard routing and database layer

### Account Lockout
**Policy:**
- 5 failed login attempts → Account locked
- Locked accounts cannot login (requires Risk Manager to unlock)
- Counter resets on successful login

**Implementation:**
```python
# Failed login
attempts = user['failed_login_attempts'] + 1
locked = 1 if attempts >= 5 else 0
cursor.execute('''
    UPDATE users 
    SET failed_login_attempts = ?, account_locked = ?
    WHERE user_id = ?
''', (attempts, locked, user['user_id']))
```

---

## Risk Assessment Engine

### Scoring Algorithms

#### Inherent Risk Score
**Formula:**
```
Inherent Score = Likelihood × Overall Impact
```

**Range:** 1-25

**Calculation:**
```python
likelihood = 4  # Likely
impact = ImpactAssessment(
    financial=5,      # Very High
    operational=4,    # High
    regulatory=3,     # Medium
    reputational=5    # Very High
)
overall_impact = (5 + 4 + 3 + 5) / 4 = 4.25 → 4 (rounded)
inherent_score = 4 × 4 = 16
risk_level = "High" (13-18 range)
```

#### Residual Risk Score
**Formula:**
```
Residual Score = (Likelihood after controls) × (Impact after controls)
```

**Purpose:** Measure risk after existing controls and planned mitigations

**Example:**
```
Inherent: 4 × 4 = 16 (High)
After controls: 2 × 3 = 6 (Low)
Risk reduction: 62.5%
```

#### Risk Level Assignment
```python
if residual_score >= 19:
    risk_level = "Critical"  # Red
elif residual_score >= 13:
    risk_level = "High"      # Orange
elif residual_score >= 7:
    risk_level = "Medium"    # Yellow
else:
    risk_level = "Low"       # Green
```

### Risk Heat Map Algorithm
**Purpose:** Visualize risk distribution across likelihood/impact matrix

**Matrix:** 5×5 grid (Likelihood on Y-axis, Impact on X-axis)

**Cell Calculation:**
```python
matrix = [[0 for _ in range(5)] for _ in range(5)]

for risk in risks:
    likelihood_idx = risk['likelihood'] - 1  # Convert to 0-index
    impact_idx = risk['impact']['overall_impact'] - 1
    
    if 0 <= likelihood_idx < 5 and 0 <= impact_idx < 5:
        matrix[likelihood_idx][impact_idx] += 1  # Count risks in cell
```

**Visualization:**
- Color scale: Green (low) → Yellow (medium) → Red (high)
- Cell text: Number of risks in that cell
- Hover: Risk names in cell

### Interdependency Analysis

#### Graph Representation
```
Risks = Nodes
Interdependencies = Directed Edges

Example:
  Supply Disruption → Price Volatility → Margin Compression
       (1.5x)              (1.3x)
```

#### Chain Detection Algorithm
```python
def find_risk_chains(source_risk_id: str, max_depth: int = 5) -> List[List[Risk]]:
    chains = []
    visited = set()
    
    def dfs(current_id, path, depth):
        if depth > max_depth:
            return
        
        if current_id in visited:
            return  # Prevent cycles
        
        visited.add(current_id)
        path.append(current_id)
        
        # Find outgoing dependencies
        dependencies = get_dependencies_from(current_id)
        
        if not dependencies:
            chains.append(path.copy())  # Leaf node, save chain
        else:
            for dep in dependencies:
                dfs(dep.target_risk_id, path, depth + 1)
        
        path.pop()
        visited.remove(current_id)
    
    dfs(source_risk_id, [], 0)
    return chains
```

#### Amplified Impact Calculation
```python
def calculate_amplified_impact(risk_chain: List[Risk]) -> float:
    base_score = risk_chain[0].residual_score
    amplification = 1.0
    
    for i in range(len(risk_chain) - 1):
        dependency = find_dependency(risk_chain[i], risk_chain[i+1])
        amplification *= dependency.impact_multiplier
    
    return base_score * amplification
```

**Example:**
```
Supply Disruption (score=16) → Price Volatility (1.5x) → Margin Compression (1.3x)
Amplified Impact = 16 × 1.5 × 1.3 = 31.2 (Critical!)
```

---

## Multi-User Architecture

### Session State Management
**Challenge:** Streamlit reruns entire script on each interaction

**Solution:** Session state persistence
```python
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
```

**Lifecycle:**
1. User logs in → Session created in database
2. `st.session_state.session_id` stores token
3. Each page load validates session (check expiration)
4. Logout → Invalidate database session, clear session state

### Role-Based Dashboard Routing
```python
def main():
    if not st.session_state.authenticated:
        login_screen()
    else:
        role = st.session_state.user['role']
        
        if role == UserRole.RISK_MANAGER.value:
            risk_manager_dashboard()
        elif role == UserRole.DEPARTMENT_CONTRIBUTOR.value:
            department_contributor_dashboard()
        elif role == UserRole.VIEW_ONLY.value:
            view_only_dashboard()
```

### Department Data Isolation
**Requirement:** Contributors only see/edit own department risks

**Implementation:**
```python
def get_all_risks(self, department: Optional[str] = None) -> List[Dict]:
    if department:
        cursor.execute('''
            SELECT * FROM risks 
            WHERE owner_department = ? OR contributor_department = ?
            ORDER BY residual_score DESC
        ''', (department, department))
    else:
        cursor.execute('SELECT * FROM risks ORDER BY residual_score DESC')
    
    # ... (parse and return)
```

**Dashboard Code:**
```python
if user['role'] == UserRole.DEPARTMENT_CONTRIBUTOR.value:
    risks = db.get_all_risks(department=user['department'])
else:
    risks = db.get_all_risks()  # Risk Manager sees all
```

### Concurrent Access Handling
**Challenge:** Multiple users modifying same risk simultaneously

**SQLite Locking:**
- Default mode: DEFERRED transactions
- Write lock acquired on first INSERT/UPDATE/DELETE
- Readers can coexist, but blocked during writes

**Optimistic Locking (Future):**
- Add `lock_version` column to risks table
- Increment on each update
- Check version matches before update:
```sql
UPDATE risks 
SET ..., lock_version = lock_version + 1 
WHERE risk_id = ? AND lock_version = ?
```

---

## API Reference

### rrs_database.py

#### RRSDatabase Class

##### `__init__(db_path: str = "rrs_enterprise.db")`
Initialize database connection and create tables if not exist.

##### `authenticate_user(username: str, password: str) -> Optional[Dict]`
**Returns:** User dict if successful, None if failed

**Side Effects:**
- Updates `last_login` on success
- Increments `failed_login_attempts` on failure
- Locks account after 5 failures
- Logs LOGIN audit event

##### `create_session(user_id: int, ip_address: str = "", user_agent: str = "") -> str`
**Returns:** Session ID (32-byte token)

**Session Duration:** 8 hours

##### `validate_session(session_id: str) -> Optional[Dict]`
**Returns:** User dict if valid, None if expired/invalid

##### `store_risk(risk_dict: dict, username: str) -> bool`
**Parameters:**
- `risk_dict`: Risk data (see Risk dataclass structure)
- `username`: User performing action

**Side Effects:**
- Archives previous version to risk_history on update
- Increments version number
- Logs CREATE/UPDATE audit event

**Returns:** True if successful, False if error

##### `get_all_risks(department: Optional[str] = None) -> List[Dict]`
**Returns:** List of risk dicts, optionally filtered by department

**JSON Parsing:** Automatically deserializes JSON columns (impact, causes, etc.)

##### `create_user(username, password, full_name, role, department, email) -> int`
**Returns:** New user_id

**Side Effects:**
- Hashes password with unique salt
- Logs CREATE USER audit event

##### `log_audit(user_id, username, action, entity_type, entity_id, details, ip_address)`
Log auditable action to audit_log table.

---

### rrs_core.py

#### Risk Dataclass
```python
@dataclass
class Risk:
    risk_id: str
    risk_name: str
    category: RiskCategory
    description: str
    risk_owner: str
    owner_department: str
    # ... (see Core Components section)
```

#### ImpactAssessment Class
##### `get_overall_score() -> int`
Calculate average impact across all dimensions.

**Returns:** Integer 1-5

#### RiskInterdependencyEngine Class
##### `__init__(risks: List[Risk])`
Initialize with risk list.

##### `find_risk_chains(source_risk_id: str, max_depth: int = 5) -> List[List[str]]`
Find all risk chain paths from source risk.

**Returns:** List of chains (each chain is list of risk IDs)

##### `calculate_amplified_impact(risk_chain: List[str]) -> float`
Calculate cumulative impact across chain.

##### `identify_critical_risks(threshold_score: float = 20.0) -> List[str]`
Find risks with high centrality in interdependency network.

#### RiskPrioritizer Class
##### `prioritize_risks(risks: List[Risk]) -> List[Tuple[Risk, float]]`
**Returns:** List of (risk, priority_score) tuples, sorted descending

##### `categorize_risks(risks: List[Risk]) -> Dict[str, List[Risk]]`
**Returns:** Dict with keys "immediate", "high", "medium", "monitor"

---

## Deployment Guide

### Development Deployment (Current)

#### Prerequisites
- Python 3.12+
- pip package manager
- 500MB disk space
- Port 8503 available

#### Steps
1. Install dependencies:
```bash
pip install -r rrs_requirements.txt
```

2. Initialize database:
```bash
python rrs_database.py
```
This creates `rrs_enterprise.db` and default admin user.

3. Launch dashboard:
```bash
streamlit run rrs_dashboard.py --server.port 8503
```

4. Access application:
```
http://localhost:8503
```

5. Login with default credentials:
```
Username: admin
Password: admin123
```

6. **Immediately change admin password** via User Management.

### Production Deployment

#### Option 1: Docker Container
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY rrs_requirements.txt .
RUN pip install --no-cache-dir -r rrs_requirements.txt

COPY rrs_core.py rrs_database.py rrs_dashboard.py ./

# Initialize database
RUN python rrs_database.py

EXPOSE 8503

CMD ["streamlit", "run", "rrs_dashboard.py", "--server.port", "8503", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t enterprise-rrs .
docker run -p 8503:8503 -v /path/to/data:/app/data enterprise-rrs
```

#### Option 2: Linux Service (systemd)
Create `/etc/systemd/system/rrs.service`:
```ini
[Unit]
Description=Enterprise RRS Risk Assessment System
After=network.target

[Service]
Type=simple
User=rrs
WorkingDirectory=/opt/rrs
Environment="PATH=/opt/rrs/venv/bin"
ExecStart=/opt/rrs/venv/bin/streamlit run rrs_dashboard.py --server.port 8503 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rrs
sudo systemctl start rrs
```

#### Option 3: Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name rrs.yourcompany.com;
    
    location / {
        proxy_pass http://localhost:8503;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

With SSL (Let's Encrypt):
```bash
sudo certbot --nginx -d rrs.yourcompany.com
```

### Database Backup Strategy

#### Daily Backups
```bash
#!/bin/bash
# backup_rrs.sh

BACKUP_DIR="/backups/rrs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Copy database
cp /opt/rrs/rrs_enterprise.db $BACKUP_DIR/rrs_enterprise_$TIMESTAMP.db

# Compress
gzip $BACKUP_DIR/rrs_enterprise_$TIMESTAMP.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete
```

Add to crontab:
```
0 2 * * * /opt/rrs/backup_rrs.sh
```

#### Point-in-Time Recovery
SQLite doesn't support PITR natively. Options:
1. **File-based snapshots:** Copy database file every hour
2. **SQLite Backup API:** Use Python to create consistent backups while database is in use

Example:
```python
import sqlite3

def backup_database(source_db, backup_db):
    source = sqlite3.connect(source_db)
    backup = sqlite3.connect(backup_db)
    
    with backup:
        source.backup(backup)
    
    source.close()
    backup.close()

backup_database('rrs_enterprise.db', 'rrs_enterprise_backup.db')
```

### Monitoring and Alerting

#### Health Check Endpoint
Add to rrs_dashboard.py:
```python
@st.cache_resource
def health_check():
    try:
        db = get_database()
        conn = db.connect()
        conn.execute("SELECT 1")
        conn.close()
        return "healthy"
    except:
        return "unhealthy"
```

#### Log Monitoring
Streamlit logs to stdout/stderr. Capture with:
```bash
streamlit run rrs_dashboard.py 2>&1 | tee -a /var/log/rrs/app.log
```

Parse logs for errors:
```bash
grep -i "error\|exception\|traceback" /var/log/rrs/app.log
```

#### Database Metrics
Monitor:
- Database file size growth
- Query response times
- Failed login attempts (potential attack)
- Active sessions

Query for failed logins:
```sql
SELECT username, COUNT(*) as failed_attempts 
FROM audit_log 
WHERE action = 'LOGIN' AND details LIKE '%failed%' 
  AND timestamp > datetime('now', '-1 hour')
GROUP BY username;
```

---

## Future Enhancements

### Phase 2 Features (Next Release)

#### 1. Risk Interdependency Visualization
**Technology:** NetworkX + Plotly

**Implementation:**
```python
import networkx as nx
import plotly.graph_objects as go

def create_risk_network_graph(risks, interdependencies):
    G = nx.DiGraph()
    
    # Add nodes
    for risk in risks:
        G.add_node(risk['risk_id'], 
                   name=risk['risk_name'],
                   score=risk['residual_score'])
    
    # Add edges
    for dep in interdependencies:
        G.add_edge(dep['source_risk_id'], 
                   dep['target_risk_id'],
                   weight=dep['impact_multiplier'])
    
    # Calculate layout
    pos = nx.spring_layout(G)
    
    # Create Plotly figure
    # ... (node/edge traces)
    
    return fig
```

**Features:**
- Interactive node selection (click to view risk details)
- Edge thickness proportional to impact multiplier
- Node color based on risk level (red=critical, etc.)
- Zoom, pan, filter controls

#### 2. Mitigation Action Workflow
**Database Changes:**
```sql
ALTER TABLE mitigation_actions ADD COLUMN approved_by TEXT;
ALTER TABLE mitigation_actions ADD COLUMN approved_date TEXT;
ALTER TABLE mitigation_actions ADD COLUMN actual_completion_date TEXT;
```

**UI Features:**
- Kanban board view (Not Started | In Progress | Completed)
- Deadline countdown timers
- Email reminders (due in 7 days, overdue)
- Progress tracking with comments
- Budget vs actual cost tracking

#### 3. Department Questionnaires
**Workflow:**
1. Risk Manager creates questionnaire template
2. System sends to department contributors
3. Contributors fill out structured forms
4. Responses automatically create risk entries
5. Risk Manager reviews and approves

**Question Types:**
- Multiple choice (risk category)
- Likert scale (likelihood/impact)
- Free text (risk description)
- File upload (supporting documentation)

#### 4. Advanced Reporting
**Report Types:**
- Executive risk dashboard (PDF)
- Risk register export (Excel)
- Audit compliance report
- Trend analysis (risk scores over time)
- Department comparison

**Export Formats:**
- PDF (ReportLab or WeasyPrint)
- Excel (openpyxl)
- CSV (pandas)

#### 5. Automated Notifications
**Email Triggers:**
- New risk submitted (notify Risk Manager)
- Risk approval required (notify department)
- Mitigation action overdue (notify owner)
- Risk review due (notify risk owner)
- Account locked (notify user + admin)

**Technology:** smtplib or SendGrid API

### Phase 3 Features (Future)

#### 1. Monte Carlo Simulation Integration
Combine with SERE engine:
```python
from sere_core import MonteCarloEngine

def run_risk_simulation(risk: Risk) -> Dict:
    engine = MonteCarloEngine()
    
    # Define probability distribution for likelihood
    likelihood_dist = {1: 0.1, 2: 0.2, 3: 0.4, 4: 0.2, 5: 0.1}
    
    # Run simulation
    results = engine.simulate(
        scenarios=10000,
        likelihood_dist=likelihood_dist,
        impact_range=(risk.impact.get_overall_score() - 1,
                     risk.impact.get_overall_score() + 1)
    )
    
    return {
        'var_95': results.var_95,
        'cvar_95': results.cvar_95,
        'expected_loss': results.expected_loss
    }
```

#### 2. Machine Learning Risk Identification
**Use Case:** Analyze historical incident data to predict emerging risks

**Model:** LSTM or Transformer for time series forecasting

**Features:**
- Past risk events (frequency, severity)
- External data (market prices, weather, news sentiment)
- Operational metrics (volume, errors, SLA breaches)

**Output:** Probability of risk materialization in next 30/60/90 days

#### 3. External Data Connectors
**Integrations:**
- Market data APIs (Bloomberg, Reuters)
- Weather APIs (NOAA, Weather.com)
- Regulatory databases (FERC, EPA)
- News sentiment (NewsAPI, Twitter)

**Architecture:**
```python
class ExternalDataConnector:
    def fetch_market_data(self, symbol: str, start_date: datetime) -> pd.DataFrame
    def fetch_weather_forecast(self, location: str) -> Dict
    def fetch_regulatory_updates(self, keywords: List[str]) -> List[Dict]
```

#### 4. Mobile Application
**Technology:** React Native or Flutter

**Features:**
- View risk dashboard
- Receive push notifications
- Update mitigation action progress
- Approve risks (Risk Manager)
- Offline mode with sync

#### 5. Advanced Analytics
**Features:**
- Risk heatmap animation (over time)
- Correlation analysis (risk co-occurrence)
- Scenario analysis ("what if" tool)
- Risk clustering (identify risk patterns)
- Predictive analytics (forecast risk trends)

**Technology:** scikit-learn, statsmodels, Prophet

---

## Testing Strategy

### Unit Tests
```python
# test_rrs_core.py
import pytest
from rrs_core import Risk, ImpactAssessment, RiskPrioritizer

def test_impact_assessment_overall_score():
    impact = ImpactAssessment(
        financial=5, operational=4, regulatory=3, reputational=5
    )
    assert impact.get_overall_score() == 4  # (5+4+3+5)/4 = 4.25 → 4

def test_risk_level_assignment():
    risk = create_test_risk(likelihood=5, impact=5)
    assert risk.residual_score == 25
    assert risk.risk_level == "Critical"
```

### Integration Tests
```python
# test_rrs_database.py
def test_authenticate_user():
    db = RRSDatabase(":memory:")  # In-memory for testing
    
    # Create user
    user_id = db.create_user("testuser", "testpass", "Test User",
                             UserRole.DEPARTMENT_CONTRIBUTOR, "IT")
    
    # Authenticate
    user = db.authenticate_user("testuser", "testpass")
    assert user is not None
    assert user['username'] == "testuser"
    
    # Wrong password
    user = db.authenticate_user("testuser", "wrongpass")
    assert user is None

def test_risk_versioning():
    db = RRSDatabase(":memory:")
    
    # Create risk
    risk_v1 = create_test_risk(risk_id="TEST-001", risk_name="Test Risk v1")
    db.store_risk(risk_v1, "testuser")
    
    # Update risk
    risk_v2 = create_test_risk(risk_id="TEST-001", risk_name="Test Risk v2")
    db.store_risk(risk_v2, "testuser")
    
    # Check history
    history = db.get_risk_history("TEST-001")
    assert len(history) == 1  # One archived version
    assert history[0]['version'] == 1
```

### End-to-End Tests
```python
# test_rrs_dashboard.py (using Selenium or Playwright)
def test_login_workflow():
    browser.get("http://localhost:8503")
    
    # Enter credentials
    browser.find_element_by_id("login_username").send_keys("admin")
    browser.find_element_by_id("login_password").send_keys("admin123")
    
    # Click login
    browser.find_element_by_text("Login").click()
    
    # Verify redirect to dashboard
    assert "Risk Dashboard" in browser.page_source
```

---

## Performance Optimization

### Database Indexing
```sql
CREATE INDEX idx_risks_category ON risks(category);
CREATE INDEX idx_risks_department ON risks(owner_department);
CREATE INDEX idx_risks_residual_score ON risks(residual_score DESC);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
```

### Query Optimization
```python
# Bad: Load all risks, filter in Python
all_risks = db.get_all_risks()
critical_risks = [r for r in all_risks if r['risk_level'] == 'Critical']

# Good: Filter in SQL
cursor.execute('''
    SELECT * FROM risks 
    WHERE risk_level = 'Critical' 
    ORDER BY residual_score DESC
''')
critical_risks = cursor.fetchall()
```

### Caching
```python
# Cache database connection
@st.cache_resource
def get_database():
    return RRSDatabase()

# Cache risk list (invalidate every 5 minutes)
@st.cache_data(ttl=300)
def load_risks():
    return db.get_all_risks()
```

### Streamlit Optimization
```python
# Use st.form to batch updates (reduce reruns)
with st.form("risk_form"):
    risk_name = st.text_input("Risk Name")
    category = st.selectbox("Category", options=categories)
    # ... more fields
    
    submitted = st.form_submit_button("Save")
    if submitted:
        # Process form

# Use st.session_state to avoid redundant computation
if 'risk_data' not in st.session_state:
    st.session_state.risk_data = load_risks()  # Load once

risks = st.session_state.risk_data  # Reuse
```

---

## Troubleshooting

### Common Issues

#### Database Locked Error
**Symptom:** `sqlite3.OperationalError: database is locked`

**Cause:** Multiple processes trying to write simultaneously

**Solution:**
1. Increase timeout: `conn = sqlite3.connect(db_path, timeout=30.0)`
2. Use WAL mode: `PRAGMA journal_mode=WAL;`
3. Implement connection pooling

#### Session Expiration
**Symptom:** User logged out unexpectedly

**Cause:** Session expired after 8 hours

**Solution:**
1. Increase expiration time in `create_session()`
2. Implement "keep alive" pings
3. Add session extension on user activity

#### Slow Dashboard Loading
**Symptom:** Dashboard takes >5 seconds to load

**Cause:** Large risk register, inefficient queries

**Solution:**
1. Add database indexes (see Performance Optimization)
2. Implement pagination (show 50 risks per page)
3. Use caching (`@st.cache_data`)
4. Lazy load risk details (expand to view)

#### Memory Issues
**Symptom:** Application crashes with OOM error

**Cause:** Loading all risks into memory at once

**Solution:**
1. Implement pagination
2. Use database cursors (iterate without loading all)
3. Clear session state periodically

---

## Compliance and Auditing

### ISO 31000 Compliance Checklist
- ✅ **Principles:** Integrated, structured, customized, inclusive, dynamic, best available information
- ✅ **Framework:** Leadership commitment, integration into governance, accountability, resources
- ✅ **Process:** Communication, scope, risk assessment, risk treatment, monitoring, recording, reporting

### COSO ERM Alignment
- ✅ **Governance:** Role-based access control
- ✅ **Strategy:** Risk categories align with strategic objectives
- ✅ **Performance:** Risk dashboards and metrics
- ✅ **Review & Revision:** Audit trails and versioning
- ✅ **Information & Communication:** Multi-user platform

### Audit Trail Requirements
**Retention:** Perpetual (audit_log never deleted)

**Logged Events:**
- All risk changes (create, update, delete)
- User authentication (login, logout, failed attempts)
- User management (create, modify, disable)
- Approval actions
- Report generation

**Query for Specific Risk Audit:**
```sql
SELECT * FROM audit_log 
WHERE entity_type = 'RISK' AND entity_id = 'RISK-20260129-090138'
ORDER BY timestamp DESC;
```

---

## Conclusion

Enterprise RRS provides a comprehensive, ISO 31000 / COSO ERM compliant risk management platform tailored for energy supply processes. The modular architecture, robust security, and multi-user collaboration features support enterprise-scale risk governance.

**Key Strengths:**
- Security-first design with proper authentication
- Complete audit trail for compliance
- Multi-dimensional risk assessment
- Interdependency modeling
- Role-based access control
- Extensible architecture

**Roadmap:**
- Phase 2: Enhanced visualizations, mitigation tracking, questionnaires
- Phase 3: ML-powered risk identification, external data integration, mobile app

For questions or support, refer to RRS_QUICK_START.md or contact your system administrator.

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-29  
**Author:** Enterprise RRS Development Team  
**Classification:** Internal Use Only
