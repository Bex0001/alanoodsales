from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.sales import Employee, Team, Project, Target, PerformanceKPI, PerformanceScore, Commission, MarketingBudget
from src.routes.auth import require_auth, require_role
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# ===== إدارة الموظفين =====
@admin_bp.route('/employees', methods=['GET'])
@require_auth
def get_all_employees():
    """الحصول على جميع الموظفين"""
    try:
        employees = Employee.query.all()
        return jsonify([emp.to_dict() for emp in employees]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب الموظفين: {str(e)}'}), 500

@admin_bp.route('/employees', methods=['POST'])
@require_auth
@require_role(['admin', 'sales_manager'])
def create_employee():
    """إضافة موظف جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'email', 'role', 'base_salary']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if Employee.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        employee = Employee(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            role=data['role'],
            base_salary=float(data['base_salary']),
            team_id=data.get('team_id'),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الموظف بنجاح',
            'employee': employee.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إضافة الموظف: {str(e)}'}), 500

@admin_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'sales_manager'])
def update_employee(employee_id):
    """تحديث بيانات الموظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        # تحديث البيانات
        if 'name' in data:
            employee.name = data['name']
        if 'email' in data:
            # التحقق من عدم تكرار البريد الإلكتروني
            existing = Employee.query.filter_by(email=data['email']).first()
            if existing and existing.id != employee_id:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
            employee.email = data['email']
        if 'phone' in data:
            employee.phone = data['phone']
        if 'role' in data:
            employee.role = data['role']
        if 'base_salary' in data:
            employee.base_salary = float(data['base_salary'])
        if 'team_id' in data:
            employee.team_id = data['team_id']
        if 'hire_date' in data:
            employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data['hire_date'] else None
        if 'is_active' in data:
            employee.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الموظف بنجاح',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث الموظف: {str(e)}'}), 500

@admin_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@require_auth
@require_role(['admin', 'sales_manager'])
def delete_employee(employee_id):
    """حذف الموظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # التحقق من عدم وجود مشاريع مرتبطة
        if employee.projects:
            return jsonify({'error': 'لا يمكن حذف الموظف لوجود مشاريع مرتبطة به'}), 400
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الموظف بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف الموظف: {str(e)}'}), 500

# ===== إدارة الفرق =====
@admin_bp.route('/teams', methods=['GET'])
@require_auth
def get_all_teams():
    """الحصول على جميع الفرق"""
    try:
        teams = Team.query.all()
        return jsonify([team.to_dict() for team in teams]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب الفرق: {str(e)}'}), 500

@admin_bp.route('/teams', methods=['POST'])
@require_auth
@require_role(['admin', 'sales_manager'])
def create_team():
    """إضافة فريق جديد"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'اسم الفريق مطلوب'}), 400
        
        team = Team(
            name=data['name'],
            description=data.get('description'),
            leader_id=data.get('leader_id')
        )
        
        db.session.add(team)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الفريق بنجاح',
            'team': team.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إضافة الفريق: {str(e)}'}), 500

@admin_bp.route('/teams/<int:team_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'sales_manager'])
def update_team(team_id):
    """تحديث بيانات الفريق"""
    try:
        team = Team.query.get_or_404(team_id)
        data = request.get_json()
        
        if 'name' in data:
            team.name = data['name']
        if 'description' in data:
            team.description = data['description']
        if 'leader_id' in data:
            team.leader_id = data['leader_id']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الفريق بنجاح',
            'team': team.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث الفريق: {str(e)}'}), 500

@admin_bp.route('/teams/<int:team_id>', methods=['DELETE'])
@require_auth
@require_role(['admin', 'sales_manager'])
def delete_team(team_id):
    """حذف الفريق"""
    try:
        team = Team.query.get_or_404(team_id)
        
        # التحقق من عدم وجود موظفين في الفريق
        if team.members:
            return jsonify({'error': 'لا يمكن حذف الفريق لوجود موظفين به'}), 400
        
        db.session.delete(team)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الفريق بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف الفريق: {str(e)}'}), 500

# ===== إدارة المشاريع =====
@admin_bp.route('/projects', methods=['GET'])
@require_auth
def get_all_projects():
    """الحصول على جميع المشاريع"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        employee_id = request.args.get('employee_id', type=int)
        
        query = Project.query
        
        if month and year:
            query = query.filter(
                db.extract('month', Project.signature_date) == month,
                db.extract('year', Project.signature_date) == year
            )
        
        if employee_id:
            query = query.filter(Project.employee_id == employee_id)
        
        projects = query.all()
        return jsonify([proj.to_dict() for proj in projects]), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المشاريع: {str(e)}'}), 500

@admin_bp.route('/projects/<int:project_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'sales_manager', 'team_leader'])
def update_project(project_id):
    """تحديث بيانات المشروع"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # التحقق من الصلاحيات
        if request.current_user.role == 'team_leader':
            # قائد الفريق يمكنه تعديل مشاريع فريقه فقط
            if not project.employee or project.employee.team_id != request.current_user.employee.team_id:
                return jsonify({'error': 'ليس لديك صلاحية لتعديل هذا المشروع'}), 403
        
        if 'client_name' in data:
            project.client_name = data['client_name']
        if 'project_value' in data:
            project.project_value = float(data['project_value'])
        if 'product_type' in data:
            project.product_type = data['product_type']
        if 'signature_date' in data:
            project.signature_date = datetime.strptime(data['signature_date'], '%Y-%m-%d').date()
        if 'is_from_social_media' in data:
            project.is_from_social_media = data['is_from_social_media']
        if 'notes' in data:
            project.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المشروع بنجاح',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث المشروع: {str(e)}'}), 500

@admin_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@require_auth
@require_role(['admin', 'sales_manager'])
def delete_project(project_id):
    """حذف المشروع"""
    try:
        project = Project.query.get_or_404(project_id)
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المشروع بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف المشروع: {str(e)}'}), 500

# ===== إدارة الأهداف =====
@admin_bp.route('/targets', methods=['POST'])
@require_auth
@require_role(['admin', 'sales_manager'])
def create_target():
    """إضافة هدف جديد"""
    try:
        data = request.get_json()
        
        required_fields = ['employee_id', 'target_amount', 'month', 'year']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من عدم وجود هدف للموظف في نفس الشهر
        existing_target = Target.query.filter_by(
            employee_id=data['employee_id'],
            month=data['month'],
            year=data['year']
        ).first()
        
        if existing_target:
            return jsonify({'error': 'يوجد هدف للموظف في هذا الشهر مسبقاً'}), 400
        
        target = Target(
            employee_id=data['employee_id'],
            target_amount=float(data['target_amount']),
            month=data['month'],
            year=data['year']
        )
        
        db.session.add(target)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الهدف بنجاح',
            'target': target.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إضافة الهدف: {str(e)}'}), 500

@admin_bp.route('/targets/<int:target_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'sales_manager'])
def update_target(target_id):
    """تحديث الهدف"""
    try:
        target = Target.query.get_or_404(target_id)
        data = request.get_json()
        
        if 'target_amount' in data:
            target.target_amount = float(data['target_amount'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الهدف بنجاح',
            'target': target.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث الهدف: {str(e)}'}), 500

@admin_bp.route('/targets/<int:target_id>', methods=['DELETE'])
@require_auth
@require_role(['admin', 'sales_manager'])
def delete_target(target_id):
    """حذف الهدف"""
    try:
        target = Target.query.get_or_404(target_id)
        
        db.session.delete(target)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الهدف بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف الهدف: {str(e)}'}), 500

# ===== إدارة مؤشرات الأداء =====
@admin_bp.route('/kpis', methods=['GET'])
@require_auth
def get_all_kpis():
    """الحصول على جميع مؤشرات الأداء"""
    try:
        kpis = PerformanceKPI.query.all()
        return jsonify([kpi.to_dict() for kpi in kpis]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب مؤشرات الأداء: {str(e)}'}), 500

@admin_bp.route('/kpis', methods=['POST'])
@require_auth
@require_role(['admin', 'sales_manager'])
def create_kpi():
    """إضافة مؤشر أداء جديد"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'weight', 'max_score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        kpi = PerformanceKPI(
            name=data['name'],
            description=data.get('description'),
            weight=float(data['weight']),
            max_score=float(data['max_score'])
        )
        
        db.session.add(kpi)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة مؤشر الأداء بنجاح',
            'kpi': kpi.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إضافة مؤشر الأداء: {str(e)}'}), 500

@admin_bp.route('/kpis/<int:kpi_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'sales_manager'])
def update_kpi(kpi_id):
    """تحديث مؤشر الأداء"""
    try:
        kpi = PerformanceKPI.query.get_or_404(kpi_id)
        data = request.get_json()
        
        if 'name' in data:
            kpi.name = data['name']
        if 'description' in data:
            kpi.description = data['description']
        if 'weight' in data:
            kpi.weight = float(data['weight'])
        if 'max_score' in data:
            kpi.max_score = float(data['max_score'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث مؤشر الأداء بنجاح',
            'kpi': kpi.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث مؤشر الأداء: {str(e)}'}), 500

@admin_bp.route('/kpis/<int:kpi_id>', methods=['DELETE'])
@require_auth
@require_role(['admin', 'sales_manager'])
def delete_kpi(kpi_id):
    """حذف مؤشر الأداء"""
    try:
        kpi = PerformanceKPI.query.get_or_404(kpi_id)
        
        db.session.delete(kpi)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف مؤشر الأداء بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف مؤشر الأداء: {str(e)}'}), 500

# ===== إدارة ميزانية التسويق =====
@admin_bp.route('/marketing-budget', methods=['GET'])
@require_auth
@require_role(['admin', 'sales_manager'])
def get_marketing_budget():
    """الحصول على ميزانية التسويق"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not month or not year:
            return jsonify({'error': 'الشهر والسنة مطلوبان'}), 400
        
        budget = MarketingBudget.query.filter_by(month=month, year=year).first()
        
        if budget:
            return jsonify(budget.to_dict()), 200
        else:
            return jsonify({'budget_amount': 0, 'month': month, 'year': year}), 200
            
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب ميزانية التسويق: {str(e)}'}), 500

@admin_bp.route('/marketing-budget', methods=['POST'])
@require_auth
@require_role(['admin', 'sales_manager'])
def set_marketing_budget():
    """تحديد ميزانية التسويق"""
    try:
        data = request.get_json()
        
        required_fields = ['budget_amount', 'month', 'year']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # البحث عن ميزانية موجودة أو إنشاء جديدة
        budget = MarketingBudget.query.filter_by(
            month=data['month'],
            year=data['year']
        ).first()
        
        if budget:
            budget.budget_amount = float(data['budget_amount'])
            budget.notes = data.get('notes')
            message = 'تم تحديث ميزانية التسويق بنجاح'
        else:
            budget = MarketingBudget(
                budget_amount=float(data['budget_amount']),
                month=data['month'],
                year=data['year'],
                notes=data.get('notes')
            )
            db.session.add(budget)
            message = 'تم إضافة ميزانية التسويق بنجاح'
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'budget': budget.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديد ميزانية التسويق: {str(e)}'}), 500

