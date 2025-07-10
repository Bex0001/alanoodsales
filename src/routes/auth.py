from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.auth import User, UserSession, Permission, RolePermission
from src.models.sales import Employee
from datetime import datetime, timedelta
import secrets
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def require_auth(f):
    """ديكوريتر للتحقق من المصادقة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'رمز المصادقة مطلوب'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_session = UserSession.query.filter_by(
            session_token=token,
            is_active=True
        ).first()
        
        if not user_session or user_session.expires_at < datetime.utcnow():
            return jsonify({'error': 'رمز المصادقة غير صالح أو منتهي الصلاحية'}), 401
        
        request.current_user = user_session.user
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(roles):
    """ديكوريتر للتحقق من الصلاحيات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'المصادقة مطلوبة'}), 401
            
            if request.current_user.role not in roles:
                return jsonify({'error': 'ليس لديك صلاحية للوصول لهذا المورد'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/register', methods=['POST'])
@require_auth
@require_role(['admin', 'sales_manager'])
def register():
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'اسم المستخدم موجود مسبقاً'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        # إنشاء المستخدم الجديد
        user = User(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            employee_id=data.get('employee_id')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء المستخدم: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'الحساب غير نشط'}), 401
        
        # إنشاء جلسة جديدة
        session_token = UserSession.generate_token()
        expires_at = datetime.utcnow() + timedelta(days=7)  # صالح لمدة أسبوع
        
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # تحديث آخر تسجيل دخول
        user.last_login = datetime.utcnow()
        
        db.session.add(user_session)
        db.session.commit()
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'token': session_token,
            'user': user.to_dict(),
            'expires_at': expires_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تسجيل الدخول: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """تسجيل الخروج"""
    try:
        token = request.headers.get('Authorization')
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_session = UserSession.query.filter_by(session_token=token).first()
        if user_session:
            user_session.is_active = False
            db.session.commit()
        
        return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تسجيل الخروج: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """الحصول على بيانات المستخدم الحالي"""
    return jsonify({
        'user': request.current_user.to_dict()
    }), 200

@auth_bp.route('/users', methods=['GET'])
@require_auth
@require_role(['admin', 'sales_manager'])
def get_users():
    """الحصول على قائمة المستخدمين"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المستخدمين: {str(e)}'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'sales_manager'])
def update_user(user_id):
    """تحديث بيانات المستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # تحديث البيانات المسموح بها
        if 'email' in data:
            # التحقق من عدم تكرار البريد الإلكتروني
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
            user.email = data['email']
        
        if 'role' in data:
            user.role = data['role']
        
        if 'employee_id' in data:
            user.employee_id = data['employee_id']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المستخدم بنجاح',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث المستخدم: {str(e)}'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_user(user_id):
    """حذف المستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        
        # منع حذف المستخدم الحالي
        if user.id == request.current_user.id:
            return jsonify({'error': 'لا يمكن حذف حسابك الخاص'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المستخدم بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف المستخدم: {str(e)}'}), 500

@auth_bp.route('/init-admin', methods=['POST'])
def init_admin():
    """إنشاء حساب المدير الأول (يستخدم مرة واحدة فقط)"""
    try:
        # التحقق من عدم وجود مديرين مسبقاً
        admin_exists = User.query.filter_by(role='admin').first()
        if admin_exists:
            return jsonify({'error': 'يوجد حساب مدير مسبقاً'}), 400
        
        data = request.get_json()
        
        # إنشاء حساب المدير
        admin_user = User(
            username=data.get('username', 'admin'),
            email=data.get('email', 'admin@aloud.com'),
            role='admin'
        )
        admin_user.set_password(data.get('password', 'admin123'))
        
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء حساب المدير بنجاح',
            'user': admin_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء حساب المدير: {str(e)}'}), 500

