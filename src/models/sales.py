from src.models.user import db
from datetime import datetime
from sqlalchemy import func

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # sales_rep, team_leader, sales_manager
    base_salary = db.Column(db.Float, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    team = db.relationship('Team', foreign_keys=[team_id], backref='members')
    projects = db.relationship('Project', backref='employee')
    targets = db.relationship('Target', backref='employee')
    performance_scores = db.relationship('PerformanceScore', backref='employee')

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    leader = db.relationship('Employee', foreign_keys=[leader_id], post_update=True)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    client_name = db.Column(db.String(200), nullable=False)
    project_value = db.Column(db.Float, nullable=False)
    product_type = db.Column(db.String(100), nullable=False)  # حديد إنشائي، خشب، ألومنيوم، حديد ديكور
    signature_date = db.Column(db.Date, nullable=False)
    is_from_social_media = db.Column(db.Boolean, default=False)
    marketing_cost_allocated = db.Column(db.Float, default=0.0)
    commission_rate = db.Column(db.Float, nullable=True)  # نسبة العمولة المحسوبة
    final_commission = db.Column(db.Float, nullable=True)  # العمولة النهائية بعد خصم التسويق
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Target(db.Model):
    __tablename__ = 'targets'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    achieved_amount = db.Column(db.Float, default=0.0)
    achievement_percentage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketingBudget(db.Model):
    __tablename__ = 'marketing_budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_budget = db.Column(db.Float, nullable=False)
    allocated_budget = db.Column(db.Float, default=0.0)  # المبلغ المخصص للمشاريع
    remaining_budget = db.Column(db.Float, default=0.0)  # المبلغ المتبقي
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    creator = db.relationship('Employee', backref='marketing_budgets')

class PerformanceKPI(db.Model):
    __tablename__ = 'performance_kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم مؤشر الأداء
    description = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Float, nullable=False)  # الوزن (0-1)
    max_score = db.Column(db.Float, default=10.0)  # أقصى نقاط
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PerformanceScore(db.Model):
    __tablename__ = 'performance_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    kpi_id = db.Column(db.Integer, db.ForeignKey('performance_kpis.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)  # النقاط المحققة
    weighted_score = db.Column(db.Float, nullable=True)  # النقاط المرجحة
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    kpi = db.relationship('PerformanceKPI', backref='scores')

class Commission(db.Model):
    __tablename__ = 'commissions'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    base_commission = db.Column(db.Float, default=0.0)  # العمولة الأساسية
    marketing_deduction = db.Column(db.Float, default=0.0)  # خصم التسويق
    performance_bonus = db.Column(db.Float, default=0.0)  # مكافأة الأداء
    final_commission = db.Column(db.Float, default=0.0)  # العمولة النهائية
    total_salary = db.Column(db.Float, default=0.0)  # إجمالي الراتب
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='commissions')
    approver = db.relationship('Employee', foreign_keys=[approved_by])

class CommissionRate(db.Model):
    __tablename__ = 'commission_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)  # sales_rep, team_leader, sales_manager
    min_achievement = db.Column(db.Float, nullable=False)  # الحد الأدنى لنسبة التحقيق
    max_achievement = db.Column(db.Float, nullable=True)  # الحد الأقصى لنسبة التحقيق
    commission_rate = db.Column(db.Float, nullable=False)  # نسبة العمولة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

