from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from functools import wraps
from models import db, User, PasswordReset
from datetime import datetime, timedelta
import secrets
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    # 至少8个字符，包含大小写字母和数字
    if len(password) < 8:
        return False, "密码至少需要8个字符"
    if not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"
    if not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    return True, "密码强度符合要求"

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'code': 400, 'message': '用户名、邮箱和密码不能为空'}), 400
        
        username = data.get('username').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        user_type = data.get('user_type', 'student')  # 默认为学生
        real_name = data.get('real_name', '').strip()
        student_id = data.get('student_id', '').strip()
        teacher_id = data.get('teacher_id', '').strip()
        college = data.get('college', '').strip()
        major = data.get('major', '').strip()
        phone = data.get('phone', '').strip()
        
        # 验证用户名
        if len(username) < 3 or len(username) > 80:
            return jsonify({'code': 400, 'message': '用户名长度需要3-80个字符'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        
        # 验证邮箱
        if not validate_email(email):
            return jsonify({'code': 400, 'message': '邮箱格式不正确'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'code': 400, 'message': '邮箱已被注册'}), 400
        
        # 验证密码
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'code': 400, 'message': msg}), 400
        
        # 验证用户类型
        if user_type not in ['student', 'teacher']:
            return jsonify({'code': 400, 'message': '用户类型不合法'}), 400
        
        # 验证学号/工号
        if user_type == 'student' and student_id:
            if User.query.filter_by(student_id=student_id).first():
                return jsonify({'code': 400, 'message': '学号已存在'}), 400
        
        if user_type == 'teacher' and teacher_id:
            if User.query.filter_by(teacher_id=teacher_id).first():
                return jsonify({'code': 400, 'message': '工号已存在'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            real_name=real_name,
            user_type=user_type,
            student_id=student_id if user_type == 'student' else None,
            teacher_id=teacher_id if user_type == 'teacher' else None,
            college=college,
            major=major,
            phone=phone
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '注册成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
        
        if not user.is_active:
            return jsonify({'code': 403, 'message': '账户已被禁用'}), 403
        
        if not user.check_password(password):
            return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
        
        # 生成JWT令牌（identity必须是字符串）
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        }), 200
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'code': 200,
            'message': '令牌刷新成功',
            'data': {
                'access_token': new_access_token
            }
        }), 200
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码 - 发送重置链接"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'code': 400, 'message': '邮箱不能为空'}), 400
        
        email = data.get('email').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # 出于安全考虑，即使邮箱不存在也返回相同信息
            return jsonify({
                'code': 200,
                'message': '如果该邮箱已注册，您将收到密码重置链接'
            }), 200
        
        # 生成重置令牌
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset)
        db.session.commit()
        
        # TODO: 发送邮件，暂时返回令牌用于测试
        return jsonify({
            'code': 200,
            'message': '如果该邮箱已注册，您将收到密码重置链接',
            'data': {
                'token': token  # 测试环境下返回，生产环境应通过邮件发送
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('password'):
            return jsonify({'code': 400, 'message': '令牌和新密码不能为空'}), 400
        
        token = data.get('token').strip()
        password = data.get('password')
        
        # 验证令牌
        reset = PasswordReset.query.filter_by(token=token).first()
        
        if not reset or not reset.is_valid():
            return jsonify({'code': 400, 'message': '重置链接无效或已过期'}), 400
        
        # 验证密码
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'code': 400, 'message': msg}), 400
        
        # 更新密码
        user = reset.user
        user.set_password(password)
        reset.used = True
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '密码重置成功'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新当前用户信息"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新允许的字段
        if 'real_name' in data:
            user.real_name = data['real_name'].strip()
        if 'phone' in data:
            user.phone = data['phone'].strip()
        if 'college' in data:
            user.college = data['college'].strip()
        if 'major' in data:
            user.major = data['major'].strip()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # JWT是无状态的，实际的登出可以在前端删除令牌
    # 如果需要令牌黑名单，可以在此添加逻辑
    return jsonify({
        'code': 200,
        'message': '登出成功'
    }), 200
