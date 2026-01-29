"""
Enterprise RRS - Risk Assessment System for Energy Supply Process
Core Risk Engine Module

Implements ISO 31000 / COSO ERM aligned risk assessment framework
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import json
import hashlib


class RiskCategory(Enum):
    """Risk categories aligned with energy supply process"""
    STRATEGIC = "Strategic"
    MARKET = "Market"
    OPERATIONAL = "Operational"
    REGULATORY = "Regulatory & Compliance"
    TECHNOLOGY = "Technology & Data"
    GOVERNANCE = "Governance & Decision-Making"
    FORECASTING = "Forecasting"
    PROCUREMENT = "Procurement & Hedging"


class ImpactDimension(Enum):
    """Multi-dimensional impact assessment"""
    FINANCIAL = "Financial"
    OPERATIONAL = "Operational"
    REGULATORY = "Regulatory"
    REPUTATIONAL = "Reputational"


class LikelihoodLevel(Enum):
    """Likelihood scale (1-5)"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class ImpactLevel(Enum):
    """Impact scale (1-5)"""
    NEGLIGIBLE = 1
    MINOR = 2
    MODERATE = 3
    MAJOR = 4
    CRITICAL = 5


class RiskStatus(Enum):
    """Risk lifecycle status"""
    IDENTIFIED = "Identified"
    UNDER_ASSESSMENT = "Under Assessment"
    APPROVED = "Approved"
    MITIGATION_PLANNED = "Mitigation Planned"
    UNDER_CONTROL = "Under Control"
    CLOSED = "Closed"


class MitigationStrategy(Enum):
    """Standard mitigation strategies (ISO 31000)"""
    AVOID = "Avoid"
    REDUCE = "Reduce"
    TRANSFER = "Transfer"
    ACCEPT = "Accept"


class ActionStatus(Enum):
    """Mitigation action status"""
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


@dataclass
class ImpactAssessment:
    """Multi-dimensional impact assessment"""
    financial: ImpactLevel
    financial_amount_min: Optional[float] = None  # EUR
    financial_amount_max: Optional[float] = None  # EUR
    operational: ImpactLevel = ImpactLevel.MINOR
    regulatory: ImpactLevel = ImpactLevel.MINOR
    reputational: ImpactLevel = ImpactLevel.MINOR
    narrative: str = ""
    
    def get_max_impact(self) -> ImpactLevel:
        """Return highest impact across dimensions"""
        impacts = [self.financial, self.operational, self.regulatory, self.reputational]
        return max(impacts, key=lambda x: x.value)
    
    def get_overall_score(self) -> int:
        """Calculate weighted impact score"""
        weights = {
            'financial': 0.40,
            'operational': 0.25,
            'regulatory': 0.20,
            'reputational': 0.15
        }
        return int(
            self.financial.value * weights['financial'] +
            self.operational.value * weights['operational'] +
            self.regulatory.value * weights['regulatory'] +
            self.reputational.value * weights['reputational']
        )


@dataclass
class RiskInterdependency:
    """Link between risks showing cause-effect relationships"""
    source_risk_id: str
    target_risk_id: str
    relationship_type: str  # "triggers", "amplifies", "causes", "depends_on"
    impact_multiplier: float = 1.0  # How much source affects target
    probability_increase: float = 0.0  # Percentage increase in likelihood
    description: str = ""
    validated: bool = False
    
    def to_dict(self) -> dict:
        return {
            'source': self.source_risk_id,
            'target': self.target_risk_id,
            'type': self.relationship_type,
            'multiplier': self.impact_multiplier,
            'prob_increase': self.probability_increase,
            'description': self.description,
            'validated': self.validated
        }


@dataclass
class MitigationAction:
    """Concrete action to mitigate risk"""
    action_id: str
    description: str
    responsible_person: str
    responsible_department: str
    deadline: datetime
    status: ActionStatus
    progress_percentage: int = 0
    cost_estimate: Optional[float] = None
    expected_risk_reduction: Optional[int] = None  # Percentage
    notes: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def is_overdue(self) -> bool:
        """Check if action is overdue"""
        return datetime.now() > self.deadline and self.status != ActionStatus.COMPLETED
    
    def to_dict(self) -> dict:
        return {
            'action_id': self.action_id,
            'description': self.description,
            'responsible_person': self.responsible_person,
            'responsible_department': self.responsible_department,
            'deadline': self.deadline.isoformat(),
            'status': self.status.value,
            'progress': self.progress_percentage,
            'cost': self.cost_estimate,
            'risk_reduction': self.expected_risk_reduction,
            'notes': self.notes
        }


@dataclass
class ExistingControl:
    """Existing controls and safeguards"""
    control_id: str
    description: str
    control_type: str  # "Preventive", "Detective", "Corrective"
    effectiveness: str  # "Weak", "Moderate", "Strong"
    last_tested: Optional[datetime] = None
    responsible_department: str = ""
    
    def to_dict(self) -> dict:
        return {
            'control_id': self.control_id,
            'description': self.description,
            'type': self.control_type,
            'effectiveness': self.effectiveness,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'department': self.responsible_department
        }


@dataclass
class Risk:
    """
    Complete risk entity following ISO 31000 / COSO ERM framework
    """
    # Core identification
    risk_id: str
    risk_name: str
    category: RiskCategory
    description: str
    
    # Ownership & accountability
    risk_owner: str  # Person name
    owner_department: str
    contributor_department: Optional[str] = None
    
    # Risk characterization
    causes: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    affected_processes: List[str] = field(default_factory=list)
    
    # Assessment
    likelihood: LikelihoodLevel = LikelihoodLevel.MEDIUM
    impact: ImpactAssessment = field(default_factory=lambda: ImpactAssessment(
        financial=ImpactLevel.MODERATE
    ))
    
    # Controls & mitigation
    existing_controls: List[ExistingControl] = field(default_factory=list)
    mitigation_strategy: Optional[MitigationStrategy] = None
    mitigation_actions: List[MitigationAction] = field(default_factory=list)
    
    # Interdependencies
    linked_risks: List[str] = field(default_factory=list)  # Risk IDs
    dependencies: List[RiskInterdependency] = field(default_factory=list)
    
    # Quantitative (optional)
    quantitative_loss_min: Optional[float] = None
    quantitative_loss_expected: Optional[float] = None
    quantitative_loss_max: Optional[float] = None
    probability_percentage: Optional[float] = None
    stress_scenario_loss: Optional[float] = None
    
    # Governance
    status: RiskStatus = RiskStatus.IDENTIFIED
    risk_appetite_exceeded: bool = False
    requires_escalation: bool = False
    last_reviewed: datetime = field(default_factory=datetime.now)
    next_review_due: Optional[datetime] = None
    
    # Metadata
    created_by: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    last_updated_by: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    version: int = 1
    notes: str = ""
    
    def calculate_inherent_risk_score(self) -> int:
        """
        Calculate inherent risk score (before controls)
        Score = Likelihood × Impact
        Range: 1-25
        """
        return self.likelihood.value * self.impact.get_overall_score()
    
    def calculate_residual_risk_score(self) -> int:
        """
        Calculate residual risk score (after controls)
        Reduces inherent risk based on control effectiveness
        """
        inherent = self.calculate_inherent_risk_score()
        
        # Reduction based on controls
        reduction_factor = 1.0
        if self.existing_controls:
            strong_controls = sum(1 for c in self.existing_controls if c.effectiveness == "Strong")
            moderate_controls = sum(1 for c in self.existing_controls if c.effectiveness == "Moderate")
            
            # Each strong control reduces risk by 15%, moderate by 8%
            reduction = min(0.60, strong_controls * 0.15 + moderate_controls * 0.08)
            reduction_factor = 1.0 - reduction
        
        # Further reduction from mitigation actions
        if self.mitigation_actions:
            completed_actions = [a for a in self.mitigation_actions if a.status == ActionStatus.COMPLETED]
            if completed_actions:
                action_reduction = sum(a.expected_risk_reduction or 0 for a in completed_actions) / 100
                reduction_factor *= (1.0 - min(0.50, action_reduction))
        
        return int(inherent * reduction_factor)
    
    def get_risk_level(self) -> str:
        """
        Classify risk level based on residual score
        1-6: Low
        7-12: Medium
        13-18: High
        19-25: Critical
        """
        score = self.calculate_residual_risk_score()
        if score <= 6:
            return "Low"
        elif score <= 12:
            return "Medium"
        elif score <= 18:
            return "High"
        else:
            return "Critical"
    
    def needs_mitigation(self) -> bool:
        """Check if risk requires mitigation"""
        score = self.calculate_residual_risk_score()
        return score >= 13 or self.risk_appetite_exceeded
    
    def get_mitigation_effectiveness(self) -> float:
        """Calculate percentage of mitigation plan completed"""
        if not self.mitigation_actions:
            return 0.0
        completed = sum(1 for a in self.mitigation_actions if a.status == ActionStatus.COMPLETED)
        return (completed / len(self.mitigation_actions)) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'risk_id': self.risk_id,
            'risk_name': self.risk_name,
            'category': self.category.value,
            'description': self.description,
            'risk_owner': self.risk_owner,
            'owner_department': self.owner_department,
            'contributor_department': self.contributor_department,
            'causes': self.causes,
            'triggers': self.triggers,
            'affected_processes': self.affected_processes,
            'likelihood': self.likelihood.value,
            'impact': {
                'financial': self.impact.financial.value,
                'financial_min': self.impact.financial_amount_min,
                'financial_max': self.impact.financial_amount_max,
                'operational': self.impact.operational.value,
                'regulatory': self.impact.regulatory.value,
                'reputational': self.impact.reputational.value,
                'narrative': self.impact.narrative
            },
            'existing_controls': [c.to_dict() for c in self.existing_controls],
            'mitigation_strategy': self.mitigation_strategy.value if self.mitigation_strategy else None,
            'mitigation_actions': [a.to_dict() for a in self.mitigation_actions],
            'linked_risks': self.linked_risks,
            'dependencies': [d.to_dict() for d in self.dependencies],
            'quantitative': {
                'loss_min': self.quantitative_loss_min,
                'loss_expected': self.quantitative_loss_expected,
                'loss_max': self.quantitative_loss_max,
                'probability': self.probability_percentage,
                'stress_loss': self.stress_scenario_loss
            },
            'status': self.status.value,
            'risk_appetite_exceeded': self.risk_appetite_exceeded,
            'requires_escalation': self.requires_escalation,
            'inherent_score': self.calculate_inherent_risk_score(),
            'residual_score': self.calculate_residual_risk_score(),
            'risk_level': self.get_risk_level(),
            'last_reviewed': self.last_reviewed.isoformat(),
            'next_review_due': self.next_review_due.isoformat() if self.next_review_due else None,
            'created_by': self.created_by,
            'created_date': self.created_date.isoformat(),
            'last_updated_by': self.last_updated_by,
            'last_updated': self.last_updated.isoformat(),
            'version': self.version,
            'notes': self.notes
        }


class RiskInterdependencyEngine:
    """
    Analyzes risk chains and amplification effects
    """
    
    def __init__(self):
        self.risk_graph: Dict[str, List[RiskInterdependency]] = {}
    
    def add_dependency(self, dependency: RiskInterdependency):
        """Add a risk interdependency"""
        if dependency.source_risk_id not in self.risk_graph:
            self.risk_graph[dependency.source_risk_id] = []
        self.risk_graph[dependency.source_risk_id].append(dependency)
    
    def get_downstream_risks(self, risk_id: str) -> List[str]:
        """Get all risks affected by this risk"""
        if risk_id not in self.risk_graph:
            return []
        return [dep.target_risk_id for dep in self.risk_graph[risk_id]]
    
    def get_upstream_risks(self, risk_id: str) -> List[str]:
        """Get all risks that affect this risk"""
        upstream = []
        for source, dependencies in self.risk_graph.items():
            for dep in dependencies:
                if dep.target_risk_id == risk_id:
                    upstream.append(source)
        return upstream
    
    def calculate_amplified_impact(self, risk_id: str, base_impact: float) -> float:
        """
        Calculate total impact considering amplification from upstream risks
        """
        upstream = self.get_upstream_risks(risk_id)
        total_multiplier = 1.0
        
        for source_id in upstream:
            if source_id in self.risk_graph:
                for dep in self.risk_graph[source_id]:
                    if dep.target_risk_id == risk_id:
                        total_multiplier *= dep.impact_multiplier
        
        return base_impact * total_multiplier
    
    def find_risk_chains(self, start_risk_id: str, max_depth: int = 5) -> List[List[str]]:
        """
        Find all risk chains starting from a given risk
        Returns list of chains (each chain is a list of risk IDs)
        """
        chains = []
        
        def traverse(current_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            downstream = self.get_downstream_risks(current_id)
            
            if not downstream:
                # End of chain
                chains.append(path[:])
                return
            
            for next_id in downstream:
                if next_id not in path:  # Avoid cycles
                    path.append(next_id)
                    traverse(next_id, path, depth + 1)
                    path.pop()
        
        traverse(start_risk_id, [start_risk_id], 0)
        return chains
    
    def identify_critical_risks(self) -> List[Tuple[str, int]]:
        """
        Identify risks that affect many other risks (high centrality)
        Returns list of (risk_id, impact_count)
        """
        impact_counts = {}
        
        for source_id, dependencies in self.risk_graph.items():
            # Count direct impacts
            direct_impacts = len(dependencies)
            
            # Count indirect impacts (depth 2)
            indirect_impacts = 0
            for dep in dependencies:
                indirect_impacts += len(self.get_downstream_risks(dep.target_risk_id))
            
            impact_counts[source_id] = direct_impacts + indirect_impacts * 0.5
        
        # Sort by impact
        return sorted(impact_counts.items(), key=lambda x: x[1], reverse=True)


class RiskPrioritizer:
    """
    Prioritizes risks based on multiple criteria
    """
    
    def __init__(self, risk_appetite_threshold: int = 12):
        self.risk_appetite_threshold = risk_appetite_threshold
    
    def prioritize_risks(self, risks: List[Risk]) -> List[Risk]:
        """
        Prioritize risks by:
        1. Residual risk score
        2. Risk appetite exceeded
        3. Number of affected processes
        4. Mitigation effectiveness
        """
        def priority_score(risk: Risk) -> Tuple:
            residual_score = risk.calculate_residual_risk_score()
            appetite_exceeded = 1 if risk.risk_appetite_exceeded else 0
            process_impact = len(risk.affected_processes)
            mitigation_gap = 100 - risk.get_mitigation_effectiveness()
            
            return (-residual_score, -appetite_exceeded, -process_impact, -mitigation_gap)
        
        return sorted(risks, key=priority_score)
    
    def categorize_risks(self, risks: List[Risk]) -> Dict[str, List[Risk]]:
        """
        Categorize risks into action buckets
        """
        categories = {
            'Critical': [],
            'High': [],
            'Medium': [],
            'Low': [],
            'Acceptable': []
        }
        
        for risk in risks:
            level = risk.get_risk_level()
            if level in categories:
                categories[level].append(risk)
            else:
                categories['Acceptable'].append(risk)
        
        return categories
    
    def identify_escalation_needed(self, risks: List[Risk]) -> List[Risk]:
        """
        Identify risks requiring management escalation
        """
        escalation_criteria = []
        
        for risk in risks:
            if (risk.calculate_residual_risk_score() >= 19 or
                risk.risk_appetite_exceeded or
                risk.get_risk_level() == "Critical" or
                any(a.is_overdue() for a in risk.mitigation_actions)):
                escalation_criteria.append(risk)
        
        return escalation_criteria


# Example risk templates for energy supply process
ENERGY_SUPPLY_RISK_TEMPLATES = {
    'FORECAST_ERROR': {
        'name': 'Demand/Generation Forecast Error',
        'category': RiskCategory.FORECASTING,
        'description': 'Inaccurate forecasts lead to imbalanced positions and market exposure',
        'causes': [
            'Weather model limitations',
            'Insufficient historical data',
            'Model parameter errors',
            'Extreme weather events'
        ],
        'affected_processes': ['Forecasting', 'Trading', 'Position Management']
    },
    'MARKET_PRICE_SPIKE': {
        'name': 'Intraday Price Spike',
        'category': RiskCategory.MARKET,
        'description': 'Sudden price increases in intraday market increase procurement costs',
        'causes': [
            'Supply shortage in market',
            'Unexpected outages',
            'High demand period',
            'Market manipulation'
        ],
        'affected_processes': ['Trading', 'Portfolio Balancing', 'Financial Management']
    },
    'REBAP_PENALTY': {
        'name': 'ReBAP Penalty Exposure',
        'category': RiskCategory.OPERATIONAL,
        'description': 'Imbalance penalties due to delivery shortfall or surplus',
        'causes': [
            'Forecast error',
            'Generation unavailability',
            'Failed intraday trades',
            'Timing errors'
        ],
        'affected_processes': ['Operations', 'Trading', 'Finance']
    }
}


if __name__ == "__main__":
    print("Enterprise RRS - Risk Assessment System")
    print("Core Risk Engine Module Loaded")
    print(f"Risk Categories: {[c.value for c in RiskCategory]}")
    print(f"Mitigation Strategies: {[m.value for m in MitigationStrategy]}")
    print("\nRisk Templates Available:")
    for key, template in ENERGY_SUPPLY_RISK_TEMPLATES.items():
        print(f"  - {key}: {template['name']}")
