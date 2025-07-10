from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.sales import (
    Employee, Team, Project, Target, MarketingBudget, 
    PerformanceKPI, PerformanceScore, Commission, CommissionRate
)
from datetime import datetime, date
from sqlalchemy import func, and_, extract
import calendar

sales_bp = Blueprint('sales', __name__)

# ===== مسارات الموظفين =====
@sales_bp.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': emp.id,
        'name': emp.name,
        'role': emp.role,
        'base_salary': emp.base_salary,
        'team_id': emp.team_id,
        'team_name': emp.team.name if emp.team else None,
        'phone': emp.phone,
        'email': emp.email,
        'hire_date': emp.hire_date.isoformat() if emp.hire_date else None
    } for emp in employees])

@sales_bp.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    
    employee = Employee(
        name=data['name'],
        role=data['role'],
        base_salary=data['base_salary'],
        team_id=data.get('team_id'),
        phone=data.get('phone'),
        email=data.get('email'),
        hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None
    )
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify({'message': 'تم إنشاء الموظف بنجاح', 'id': employee.id}), 201

@sales_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    data = request.get_json()
    
    employee.name = data.get('name', employee.name)
    employee.role = data.get('role', employee.role)
    employee.base_salary = data.get('base_salary', employee.base_salary)
    employee.team_id = data.get('team_id', employee.team_id)
    employee.phone = data.get('phone', employee.phone)
    employee.email = data.get('email', employee.email)
    
    if data.get('hire_date'):
        employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
    
    db.session.commit()
    
    return jsonify({'message': 'تم تحديث بيانات الموظف بنجاح'})

# ===== مسارات المشاريع =====
@sales_bp.route('/projects', methods=['GET'])
def get_projects():
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Project.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if month and year:
        query = query.filter(
            extract('month', Project.signature_date) == int(month),
            extract('year', Project.signature_date) == int(year)
        )
    
    projects = query.order_by(Project.signature_date.desc()).all()
    
    return jsonify([{
        'id': proj.id,
        'employee_id': proj.employee_id,
        'employee_name': proj.employee.name,
        'client_name': proj.client_name,
        'project_value': proj.project_value,
        'product_type': proj.product_type,
        'signature_date': proj.signature_date.isoformat(),
        'is_from_social_media': proj.is_from_social_media,
        'marketing_cost_allocated': proj.marketing_cost_allocated,
        'commission_rate': proj.commission_rate,
        'final_commission': proj.final_commission,
        'notes': proj.notes
    } for proj in projects])

@sales_bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    
    project = Project(
        employee_id=data['employee_id'],
        client_name=data['client_name'],
        project_value=data['project_value'],
        product_type=data['product_type'],
        signature_date=datetime.strptime(data['signature_date'], '%Y-%m-%d').date(),
        is_from_social_media=data.get('is_from_social_media', False),
        notes=data.get('notes')
    )
    
    # حساب العمولة الأولية
    employee = Employee.query.get(data['employee_id'])
    achievement_rate = calculate_achievement_rate(employee.id, project.signature_date.month, project.signature_date.year)
    commission_rate = get_commission_rate(employee.role, achievement_rate)
    
    # تطبيق خصم السوشيال ميديا
    if project.is_from_social_media:
        commission_rate -= 0.005  # خصم 0.5%
    
    project.commission_rate = commission_rate
    project.final_commission = project.project_value * commission_rate
    
    db.session.add(project)
    db.session.commit()
    
    # تحديث الأهداف المحققة
    update_target_achievement(employee.id, project.signature_date.month, project.signature_date.year)
    
    # توزيع تكلفة التسويق إذا كان المشروع من السوشيال ميديا
    if project.is_from_social_media:
        allocate_marketing_cost(project.id, project.signature_date.month, project.signature_date.year)
    
    return jsonify({'message': 'تم إنشاء المشروع بنجاح', 'id': project.id}), 201

# ===== مسارات الأهداف =====
@sales_bp.route('/targets', methods=['GET'])
def get_targets():
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Target.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if month and year:
        query = query.filter_by(month=int(month), year=int(year))
    
    targets = query.all()
    
    return jsonify([{
        'id': target.id,
        'employee_id': target.employee_id,
        'employee_name': target.employee.name,
        'month': target.month,
        'year': target.year,
        'target_amount': target.target_amount,
        'achieved_amount': target.achieved_amount,
        'achievement_percentage': target.achievement_percentage
    } for target in targets])

@sales_bp.route('/targets', methods=['POST'])
def create_target():
    data = request.get_json()
    
    # التحقق من وجود هدف للموظف في نفس الشهر
    existing_target = Target.query.filter_by(
        employee_id=data['employee_id'],
        month=data['month'],
        year=data['year']
    ).first()
    
    if existing_target:
        return jsonify({'error': 'يوجد هدف بالفعل لهذا الموظف في هذا الشهر'}), 400
    
    target = Target(
        employee_id=data['employee_id'],
        month=data['month'],
        year=data['year'],
        target_amount=data['target_amount']
    )
    
    db.session.add(target)
    db.session.commit()
    
    return jsonify({'message': 'تم إنشاء الهدف بنجاح', 'id': target.id}), 201

# ===== مسارات ميزانية التسويق =====
@sales_bp.route('/marketing-budget', methods=['GET'])
def get_marketing_budget():
    month = request.args.get('month')
    year = request.args.get('year')
    
    if month and year:
        budget = MarketingBudget.query.filter_by(month=int(month), year=int(year)).first()
        if budget:
            return jsonify({
                'id': budget.id,
                'month': budget.month,
                'year': budget.year,
                'total_budget': budget.total_budget,
                'allocated_budget': budget.allocated_budget,
                'remaining_budget': budget.remaining_budget,
                'created_by': budget.created_by,
                'creator_name': budget.creator.name
            })
        else:
            return jsonify({'error': 'لا توجد ميزانية لهذا الشهر'}), 404
    
    budgets = MarketingBudget.query.order_by(MarketingBudget.year.desc(), MarketingBudget.month.desc()).all()
    return jsonify([{
        'id': budget.id,
        'month': budget.month,
        'year': budget.year,
        'total_budget': budget.total_budget,
        'allocated_budget': budget.allocated_budget,
        'remaining_budget': budget.remaining_budget,
        'created_by': budget.created_by,
        'creator_name': budget.creator.name
    } for budget in budgets])

@sales_bp.route('/marketing-budget', methods=['POST'])
def create_marketing_budget():
    data = request.get_json()
    
    # التحقق من وجود ميزانية للشهر
    existing_budget = MarketingBudget.query.filter_by(
        month=data['month'],
        year=data['year']
    ).first()
    
    if existing_budget:
        return jsonify({'error': 'توجد ميزانية بالفعل لهذا الشهر'}), 400
    
    budget = MarketingBudget(
        month=data['month'],
        year=data['year'],
        total_budget=data['total_budget'],
        remaining_budget=data['total_budget'],
        created_by=data['created_by']
    )
    
    db.session.add(budget)
    db.session.commit()
    
    # إعادة توزيع التكاليف على المشاريع الموجودة
    redistribute_marketing_costs(data['month'], data['year'])
    
    return jsonify({'message': 'تم إنشاء ميزانية التسويق بنجاح', 'id': budget.id}), 201

# ===== مسارات مؤشرات الأداء =====
@sales_bp.route('/performance-kpis', methods=['GET'])
def get_performance_kpis():
    kpis = PerformanceKPI.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': kpi.id,
        'name': kpi.name,
        'description': kpi.description,
        'weight': kpi.weight,
        'max_score': kpi.max_score
    } for kpi in kpis])

@sales_bp.route('/performance-kpis', methods=['POST'])
def create_performance_kpi():
    data = request.get_json()
    
    kpi = PerformanceKPI(
        name=data['name'],
        description=data.get('description'),
        weight=data['weight'],
        max_score=data.get('max_score', 10.0)
    )
    
    db.session.add(kpi)
    db.session.commit()
    
    return jsonify({'message': 'تم إنشاء مؤشر الأداء بنجاح', 'id': kpi.id}), 201

# ===== مسارات نقاط الأداء =====
@sales_bp.route('/performance-scores', methods=['GET'])
def get_performance_scores():
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = PerformanceScore.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if month and year:
        query = query.filter_by(month=int(month), year=int(year))
    
    scores = query.all()
    
    return jsonify([{
        'id': score.id,
        'employee_id': score.employee_id,
        'employee_name': score.employee.name,
        'kpi_id': score.kpi_id,
        'kpi_name': score.kpi.name,
        'month': score.month,
        'year': score.year,
        'score': score.score,
        'weighted_score': score.weighted_score,
        'notes': score.notes
    } for score in scores])

@sales_bp.route('/performance-scores', methods=['POST'])
def create_performance_score():
    data = request.get_json()
    
    # التحقق من وجود نقاط للموظف في نفس الشهر ونفس المؤشر
    existing_score = PerformanceScore.query.filter_by(
        employee_id=data['employee_id'],
        kpi_id=data['kpi_id'],
        month=data['month'],
        year=data['year']
    ).first()
    
    if existing_score:
        # تحديث النقاط الموجودة
        existing_score.score = data['score']
        kpi = PerformanceKPI.query.get(data['kpi_id'])
        existing_score.weighted_score = data['score'] * kpi.weight
        existing_score.notes = data.get('notes')
        existing_score.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'تم تحديث نقاط الأداء بنجاح'})
    else:
        # إنشاء نقاط جديدة
        kpi = PerformanceKPI.query.get(data['kpi_id'])
        score = PerformanceScore(
            employee_id=data['employee_id'],
            kpi_id=data['kpi_id'],
            month=data['month'],
            year=data['year'],
            score=data['score'],
            weighted_score=data['score'] * kpi.weight,
            notes=data.get('notes')
        )
        
        db.session.add(score)
        db.session.commit()
        
        return jsonify({'message': 'تم إنشاء نقاط الأداء بنجاح', 'id': score.id}), 201

# ===== مسارات العمولات =====
@sales_bp.route('/commissions', methods=['GET'])
def get_commissions():
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Commission.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if month and year:
        query = query.filter_by(month=int(month), year=int(year))
    
    commissions = query.all()
    
    return jsonify([{
        'id': comm.id,
        'employee_id': comm.employee_id,
        'employee_name': comm.employee.name,
        'month': comm.month,
        'year': comm.year,
        'base_commission': comm.base_commission,
        'marketing_deduction': comm.marketing_deduction,
        'performance_bonus': comm.performance_bonus,
        'final_commission': comm.final_commission,
        'total_salary': comm.total_salary,
        'is_approved': comm.is_approved,
        'approved_by': comm.approved_by,
        'approved_at': comm.approved_at.isoformat() if comm.approved_at else None
    } for comm in commissions])

@sales_bp.route('/commissions/calculate', methods=['POST'])
def calculate_commissions():
    data = request.get_json()
    month = data['month']
    year = data['year']
    employee_ids = data.get('employee_ids', [])
    
    if not employee_ids:
        # حساب العمولات لجميع الموظفين النشطين
        employees = Employee.query.filter_by(is_active=True).all()
        employee_ids = [emp.id for emp in employees]
    
    results = []
    
    for employee_id in employee_ids:
        commission = calculate_employee_commission(employee_id, month, year)
        results.append(commission)
    
    return jsonify({
        'message': f'تم حساب العمولات لشهر {month}/{year}',
        'results': results
    })

# ===== الدوال المساعدة =====
def calculate_achievement_rate(employee_id, month, year):
    """حساب نسبة تحقيق الهدف للموظف"""
    target = Target.query.filter_by(employee_id=employee_id, month=month, year=year).first()
    if not target:
        return 0.0
    
    # حساب إجمالي المبيعات للشهر
    total_sales = db.session.query(func.sum(Project.project_value)).filter(
        Project.employee_id == employee_id,
        extract('month', Project.signature_date) == month,
        extract('year', Project.signature_date) == year
    ).scalar() or 0.0
    
    if target.target_amount == 0:
        return 0.0
    
    return total_sales / target.target_amount

def get_commission_rate(role, achievement_rate):
    """الحصول على نسبة العمولة بناءً على الدور ونسبة التحقيق"""
    # نسب العمولة المحدثة حسب المتطلبات
    if role == 'sales_rep':
        if achievement_rate <= 0.5:
            return 0.01  # 1%
        elif achievement_rate <= 0.8:
            return 0.015  # 1.5%
        elif achievement_rate <= 1.0:
            return 0.02  # 2%
        else:
            return 0.025  # 2.5%
    elif role == 'team_leader':
        if achievement_rate <= 0.5:
            return 0.005  # 0.5%
        elif achievement_rate <= 0.8:
            return 0.0075  # 0.75%
        elif achievement_rate <= 1.0:
            return 0.01  # 1%
        else:
            return 0.0125  # 1.25%
    elif role == 'sales_manager':
        return 0.005  # 0.5% ثابت
    
    return 0.0

def update_target_achievement(employee_id, month, year):
    """تحديث نسبة تحقيق الهدف"""
    target = Target.query.filter_by(employee_id=employee_id, month=month, year=year).first()
    if not target:
        return
    
    # حساب إجمالي المبيعات المحققة
    total_sales = db.session.query(func.sum(Project.project_value)).filter(
        Project.employee_id == employee_id,
        extract('month', Project.signature_date) == month,
        extract('year', Project.signature_date) == year
    ).scalar() or 0.0
    
    target.achieved_amount = total_sales
    target.achievement_percentage = total_sales / target.target_amount if target.target_amount > 0 else 0.0
    target.updated_at = datetime.utcnow()
    
    db.session.commit()

def allocate_marketing_cost(project_id, month, year):
    """توزيع تكلفة التسويق على المشروع"""
    project = Project.query.get(project_id)
    if not project or not project.is_from_social_media:
        return
    
    # الحصول على ميزانية التسويق للشهر
    budget = MarketingBudget.query.filter_by(month=month, year=year).first()
    if not budget:
        return
    
    # حساب إجمالي قيمة المشاريع من السوشيال ميديا في الشهر
    total_social_projects_value = db.session.query(func.sum(Project.project_value)).filter(
        Project.is_from_social_media == True,
        extract('month', Project.signature_date) == month,
        extract('year', Project.signature_date) == year
    ).scalar() or 0.0
    
    if total_social_projects_value == 0:
        return
    
    # حساب نسبة المشروع من إجمالي المشاريع
    project_ratio = project.project_value / total_social_projects_value
    
    # حساب تكلفة التسويق المخصصة للمشروع
    allocated_cost = budget.total_budget * project_ratio
    
    # تحديث المشروع
    project.marketing_cost_allocated = allocated_cost
    project.final_commission = max(0, project.final_commission - allocated_cost)
    
    db.session.commit()

def redistribute_marketing_costs(month, year):
    """إعادة توزيع تكاليف التسويق على جميع المشاريع في الشهر"""
    # الحصول على جميع المشاريع من السوشيال ميديا في الشهر
    social_projects = Project.query.filter(
        Project.is_from_social_media == True,
        extract('month', Project.signature_date) == month,
        extract('year', Project.signature_date) == year
    ).all()
    
    if not social_projects:
        return
    
    # إعادة حساب التكاليف لكل مشروع
    for project in social_projects:
        allocate_marketing_cost(project.id, month, year)

def calculate_employee_commission(employee_id, month, year):
    """حساب العمولة الشاملة للموظف"""
    employee = Employee.query.get(employee_id)
    if not employee:
        return None
    
    # حساب العمولة الأساسية من المشاريع
    projects = Project.query.filter(
        Project.employee_id == employee_id,
        extract('month', Project.signature_date) == month,
        extract('year', Project.signature_date) == year
    ).all()
    
    base_commission = sum(proj.final_commission or 0 for proj in projects)
    marketing_deduction = sum(proj.marketing_cost_allocated or 0 for proj in projects)
    
    # حساب مكافأة الأداء
    performance_scores = PerformanceScore.query.filter_by(
        employee_id=employee_id,
        month=month,
        year=year
    ).all()
    
    total_weighted_score = sum(score.weighted_score or 0 for score in performance_scores)
    performance_bonus = total_weighted_score * 1000  # 1000 ريال لكل نقطة أداء
    
    # العمولة النهائية
    final_commission = base_commission + performance_bonus
    total_salary = employee.base_salary + final_commission
    
    # حفظ أو تحديث العمولة في قاعدة البيانات
    existing_commission = Commission.query.filter_by(
        employee_id=employee_id,
        month=month,
        year=year
    ).first()
    
    if existing_commission:
        existing_commission.base_commission = base_commission
        existing_commission.marketing_deduction = marketing_deduction
        existing_commission.performance_bonus = performance_bonus
        existing_commission.final_commission = final_commission
        existing_commission.total_salary = total_salary
        existing_commission.updated_at = datetime.utcnow()
    else:
        commission = Commission(
            employee_id=employee_id,
            month=month,
            year=year,
            base_commission=base_commission,
            marketing_deduction=marketing_deduction,
            performance_bonus=performance_bonus,
            final_commission=final_commission,
            total_salary=total_salary
        )
        db.session.add(commission)
    
    db.session.commit()
    
    return {
        'employee_id': employee_id,
        'employee_name': employee.name,
        'base_commission': base_commission,
        'marketing_deduction': marketing_deduction,
        'performance_bonus': performance_bonus,
        'final_commission': final_commission,
        'total_salary': total_salary
    }

