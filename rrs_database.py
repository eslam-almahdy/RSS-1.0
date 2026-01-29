"""
Enterprise RRS - Database Layer
Multi-user database with authentication, audit trails, and versioning
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from enum import Enum


class UserRole(Enum):
    """User roles with different access levels"""
    RISK_MANAGER = "Risk Manager"
    DEPARTMENT_CONTRIBUTOR = "Department Contributor"
    VIEW_ONLY = "View Only"


class AuditAction(Enum):
    """Types of auditable actions"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    APPROVE = "APPROVE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class RRSDatabase:
    """
    Enterprise Risk Assessment Database
    Supports multi-user access, authentication, audit trails, versioning
    """
    
    def __init__(self, db_path: str = "rrs_enterprise.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def initialize_database(self):
        """Create all required tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table with authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL,
                department TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_date TEXT NOT NULL,
                last_login TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Risk register table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risks (
                risk_id TEXT PRIMARY KEY,
                risk_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                risk_owner TEXT NOT NULL,
                owner_department TEXT NOT NULL,
                contributor_department TEXT,
                causes TEXT,
                triggers TEXT,
                affected_processes TEXT,
                likelihood INTEGER NOT NULL,
                impact_json TEXT NOT NULL,
                existing_controls_json TEXT,
                mitigation_strategy TEXT,
                mitigation_actions_json TEXT,
                linked_risks TEXT,
                dependencies_json TEXT,
                quantitative_json TEXT,
                status TEXT NOT NULL,
                risk_appetite_exceeded BOOLEAN DEFAULT 0,
                requires_escalation BOOLEAN DEFAULT 0,
                inherent_score INTEGER,
                residual_score INTEGER,
                risk_level TEXT,
                last_reviewed TEXT NOT NULL,
                next_review_due TEXT,
                created_by TEXT NOT NULL,
                created_date TEXT NOT NULL,
                last_updated_by TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                notes TEXT
            )
        ''')
        
        # Risk history table (versioning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                risk_data_json TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_date TEXT NOT NULL,
                change_reason TEXT,
                FOREIGN KEY (risk_id) REFERENCES risks(risk_id)
            )
        ''')
        
        # Risk interdependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_interdependencies (
                dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_risk_id TEXT NOT NULL,
                target_risk_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                impact_multiplier REAL DEFAULT 1.0,
                probability_increase REAL DEFAULT 0.0,
                description TEXT,
                validated BOOLEAN DEFAULT 0,
                created_by TEXT NOT NULL,
                created_date TEXT NOT NULL,
                FOREIGN KEY (source_risk_id) REFERENCES risks(risk_id),
                FOREIGN KEY (target_risk_id) REFERENCES risks(risk_id)
            )
        ''')
        
        # Mitigation actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mitigation_actions (
                action_id TEXT PRIMARY KEY,
                risk_id TEXT NOT NULL,
                description TEXT NOT NULL,
                responsible_person TEXT NOT NULL,
                responsible_department TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL,
                progress_percentage INTEGER DEFAULT 0,
                cost_estimate REAL,
                expected_risk_reduction INTEGER,
                notes TEXT,
                created_date TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (risk_id) REFERENCES risks(risk_id)
            )
        ''')
        
        # Action history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT,
                old_progress INTEGER,
                new_progress INTEGER,
                changed_by TEXT NOT NULL,
                changed_date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (action_id) REFERENCES mitigation_actions(action_id)
            )
        ''')
        
        # Questionnaires table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questionnaires (
                questionnaire_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                target_department TEXT NOT NULL,
                questions_json TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_date TEXT NOT NULL,
                due_date TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Questionnaire responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questionnaire_responses (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                questionnaire_id TEXT NOT NULL,
                respondent_user_id INTEGER NOT NULL,
                responses_json TEXT NOT NULL,
                submitted_date TEXT NOT NULL,
                FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(questionnaire_id),
                FOREIGN KEY (respondent_user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Risk appetite settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_appetite (
                appetite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                threshold_score INTEGER NOT NULL,
                max_financial_impact REAL,
                review_frequency_days INTEGER,
                escalation_required BOOLEAN DEFAULT 1,
                set_by TEXT NOT NULL,
                set_date TEXT NOT NULL,
                notes TEXT
            )
        ''')
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                generated_by TEXT NOT NULL,
                generated_date TEXT NOT NULL,
                parameters_json TEXT,
                file_path TEXT,
                is_archived BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default admin user if not exists
        self.create_default_admin()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return pwd_hash.hex(), salt
    
    def create_default_admin(self):
        """Create default admin user if none exists"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = ?", (UserRole.RISK_MANAGER.value,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create default admin
            pwd_hash, salt = self.hash_password("admin123")  # Change in production!
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, full_name, email, role, department, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "admin",
                pwd_hash,
                salt,
                "System Administrator",
                "admin@company.com",
                UserRole.RISK_MANAGER.value,
                "Risk Management",
                datetime.now().isoformat()
            ))
            conn.commit()
            print("Default admin user created: username='admin', password='admin123'")
        
        conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user and return user data if successful
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get user
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND is_active = 1
        ''', (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        # Check if account is locked
        if user['account_locked']:
            conn.close()
            return None
        
        # Verify password
        pwd_hash, _ = self.hash_password(password, user['salt'])
        
        if pwd_hash == user['password_hash']:
            # Successful login
            cursor.execute('''
                UPDATE users 
                SET last_login = ?, failed_login_attempts = 0 
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), user['user_id']))
            
            # Log login
            self.log_audit(
                user['user_id'],
                username,
                AuditAction.LOGIN.value,
                details="Successful login"
            )
            
            conn.commit()
            conn.close()
            
            return dict(user)
        else:
            # Failed login
            attempts = user['failed_login_attempts'] + 1
            locked = 1 if attempts >= 5 else 0
            
            cursor.execute('''
                UPDATE users 
                SET failed_login_attempts = ?, account_locked = ?
                WHERE user_id = ?
            ''', (attempts, locked, user['user_id']))
            
            conn.commit()
            conn.close()
            return None
    
    def create_session(self, user_id: int, ip_address: str = "", user_agent: str = "") -> str:
        """Create a new session for authenticated user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        session_id = secrets.token_urlsafe(32)
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=8)  # 8 hour session
        
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, created_at, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_id,
            created_at.isoformat(),
            expires_at.isoformat(),
            ip_address,
            user_agent
        ))
        
        conn.commit()
        conn.close()
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate session and return user data"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.* 
            FROM sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.session_id = ? AND s.is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(result['expires_at'])
        if datetime.now() > expires_at:
            self.invalidate_session(session_id)
            return None
        
        return dict(result)
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session (logout)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions SET is_active = 0 WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password: str, full_name: str, role: UserRole,
                   department: str, email: str = "", created_by: str = "admin") -> int:
        """Create a new user"""
        conn = self.connect()
        cursor = conn.cursor()
        
        pwd_hash, salt = self.hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt, full_name, email, role, department, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            pwd_hash,
            salt,
            full_name,
            email,
            role.value,
            department,
            datetime.now().isoformat()
        ))
        
        user_id = cursor.lastrowid
        
        # Log user creation
        self.log_audit(
            None,
            created_by,
            AuditAction.CREATE.value,
            "USER",
            str(user_id),
            f"Created user: {username}"
        )
        
        conn.commit()
        conn.close()
        return user_id
    
    def log_audit(self, user_id: Optional[int], username: str, action: str,
                  entity_type: str = "", entity_id: str = "",
                  details: str = "", ip_address: str = ""):
        """Log an auditable action"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log (user_id, username, action, entity_type, entity_id, details, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            username,
            action,
            entity_type,
            entity_id,
            details,
            ip_address,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def store_risk(self, risk_dict: dict, username: str) -> bool:
        """Store or update a risk"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Check if risk exists
            cursor.execute("SELECT version FROM risks WHERE risk_id = ?", (risk_dict['risk_id'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing risk
                new_version = existing['version'] + 1
                
                # Archive current version to history
                cursor.execute("SELECT * FROM risks WHERE risk_id = ?", (risk_dict['risk_id'],))
                current_risk = dict(cursor.fetchone())
                
                cursor.execute('''
                    INSERT INTO risk_history (risk_id, version, risk_data_json, changed_by, changed_date, change_reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    risk_dict['risk_id'],
                    existing['version'],
                    json.dumps(current_risk),
                    username,
                    datetime.now().isoformat(),
                    "Updated risk"
                ))
                
                # Update risk
                cursor.execute('''
                    UPDATE risks SET
                        risk_name = ?, category = ?, description = ?,
                        risk_owner = ?, owner_department = ?, contributor_department = ?,
                        causes = ?, triggers = ?, affected_processes = ?,
                        likelihood = ?, impact_json = ?, existing_controls_json = ?,
                        mitigation_strategy = ?, mitigation_actions_json = ?,
                        linked_risks = ?, dependencies_json = ?, quantitative_json = ?,
                        status = ?, risk_appetite_exceeded = ?, requires_escalation = ?,
                        inherent_score = ?, residual_score = ?, risk_level = ?,
                        last_reviewed = ?, next_review_due = ?,
                        last_updated_by = ?, last_updated = ?, version = ?, notes = ?
                    WHERE risk_id = ?
                ''', (
                    risk_dict['risk_name'], risk_dict['category'], risk_dict['description'],
                    risk_dict['risk_owner'], risk_dict['owner_department'], risk_dict.get('contributor_department'),
                    json.dumps(risk_dict.get('causes', [])), json.dumps(risk_dict.get('triggers', [])),
                    json.dumps(risk_dict.get('affected_processes', [])),
                    risk_dict['likelihood'], json.dumps(risk_dict['impact']),
                    json.dumps(risk_dict.get('existing_controls', [])),
                    risk_dict.get('mitigation_strategy'), json.dumps(risk_dict.get('mitigation_actions', [])),
                    json.dumps(risk_dict.get('linked_risks', [])), json.dumps(risk_dict.get('dependencies', [])),
                    json.dumps(risk_dict.get('quantitative', {})),
                    risk_dict['status'], risk_dict.get('risk_appetite_exceeded', False),
                    risk_dict.get('requires_escalation', False),
                    risk_dict.get('inherent_score'), risk_dict.get('residual_score'), risk_dict.get('risk_level'),
                    risk_dict.get('last_reviewed'), risk_dict.get('next_review_due'),
                    username, datetime.now().isoformat(), new_version, risk_dict.get('notes', ''),
                    risk_dict['risk_id']
                ))
                
                action = AuditAction.UPDATE.value
            else:
                # Insert new risk
                cursor.execute('''
                    INSERT INTO risks (
                        risk_id, risk_name, category, description,
                        risk_owner, owner_department, contributor_department,
                        causes, triggers, affected_processes,
                        likelihood, impact_json, existing_controls_json,
                        mitigation_strategy, mitigation_actions_json,
                        linked_risks, dependencies_json, quantitative_json,
                        status, risk_appetite_exceeded, requires_escalation,
                        inherent_score, residual_score, risk_level,
                        last_reviewed, next_review_due,
                        created_by, created_date, last_updated_by, last_updated, version, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    risk_dict['risk_id'], risk_dict['risk_name'], risk_dict['category'], risk_dict['description'],
                    risk_dict['risk_owner'], risk_dict['owner_department'], risk_dict.get('contributor_department'),
                    json.dumps(risk_dict.get('causes', [])), json.dumps(risk_dict.get('triggers', [])),
                    json.dumps(risk_dict.get('affected_processes', [])),
                    risk_dict['likelihood'], json.dumps(risk_dict['impact']),
                    json.dumps(risk_dict.get('existing_controls', [])),
                    risk_dict.get('mitigation_strategy'), json.dumps(risk_dict.get('mitigation_actions', [])),
                    json.dumps(risk_dict.get('linked_risks', [])), json.dumps(risk_dict.get('dependencies', [])),
                    json.dumps(risk_dict.get('quantitative', {})),
                    risk_dict['status'], risk_dict.get('risk_appetite_exceeded', False),
                    risk_dict.get('requires_escalation', False),
                    risk_dict.get('inherent_score'), risk_dict.get('residual_score'), risk_dict.get('risk_level'),
                    risk_dict.get('last_reviewed'), risk_dict.get('next_review_due'),
                    username, datetime.now().isoformat(), username, datetime.now().isoformat(), 1, risk_dict.get('notes', '')
                ))
                
                action = AuditAction.CREATE.value
            
            # Log audit
            self.log_audit(None, username, action, "RISK", risk_dict['risk_id'],
                          f"{action} risk: {risk_dict['risk_name']}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing risk: {e}")
            conn.rollback()
            conn.close()
            return False
    
    def get_all_risks(self, department: Optional[str] = None) -> List[Dict]:
        """Get all risks, optionally filtered by department"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if department:
            cursor.execute('''
                SELECT * FROM risks 
                WHERE owner_department = ? OR contributor_department = ?
                ORDER BY residual_score DESC
            ''', (department, department))
        else:
            cursor.execute('SELECT * FROM risks ORDER BY residual_score DESC')
        
        risks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for risk in risks:
            risk['causes'] = json.loads(risk['causes']) if risk['causes'] else []
            risk['triggers'] = json.loads(risk['triggers']) if risk['triggers'] else []
            risk['affected_processes'] = json.loads(risk['affected_processes']) if risk['affected_processes'] else []
            risk['impact'] = json.loads(risk['impact_json'])
            risk['existing_controls'] = json.loads(risk['existing_controls_json']) if risk['existing_controls_json'] else []
            risk['mitigation_actions'] = json.loads(risk['mitigation_actions_json']) if risk['mitigation_actions_json'] else []
            risk['linked_risks'] = json.loads(risk['linked_risks']) if risk['linked_risks'] else []
            risk['dependencies'] = json.loads(risk['dependencies_json']) if risk['dependencies_json'] else []
            risk['quantitative'] = json.loads(risk['quantitative_json']) if risk['quantitative_json'] else {}
        
        return risks
    
    def get_audit_trail(self, entity_type: str = "", entity_id: str = "", limit: int = 100) -> List[Dict]:
        """Get audit trail"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if entity_type and entity_id:
            cursor.execute('''
                SELECT * FROM audit_log 
                WHERE entity_type = ? AND entity_id = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (entity_type, entity_id, limit))
        elif entity_type:
            cursor.execute('''
                SELECT * FROM audit_log 
                WHERE entity_type = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (entity_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM audit_log 
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs


if __name__ == "__main__":
    print("Enterprise RRS - Database Layer")
    print("Initializing database...")
    
    db = RRSDatabase()
    print("Database initialized successfully")
    print("\nDefault credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nTables created:")
    print("  - users (authentication)")
    print("  - sessions (session management)")
    print("  - risks (risk register)")
    print("  - risk_history (versioning)")
    print("  - risk_interdependencies")
    print("  - mitigation_actions")
    print("  - action_history")
    print("  - questionnaires")
    print("  - questionnaire_responses")
    print("  - audit_log")
    print("  - risk_appetite")
    print("  - reports")
