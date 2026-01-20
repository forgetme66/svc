from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, TeacherStudent, File
from datetime import datetime
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')

@teacher_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """获取教师管理的学生列表"""
    try:
        teacher_id = int(get_jwt_identity())
        logger.info(f'教师 {teacher_id} 查询学生列表')
        
        teacher = User.query.get(teacher_id)
        
        if not teacher:
            logger.warning(f'教师 {teacher_id} 不存在')
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if teacher.user_type != 'teacher' and teacher.user_type != 'admin':
            logger.warning(f'用户 {teacher_id} 不是教师或管理员，user_type={teacher.user_type}')
            return jsonify({'code': 403, 'message': '只有教师和管理员可以查看学生列表'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '', type=str)
        
        logger.info(f'查询参数 - 页码: {page}, 每页数: {per_page}, 关键词: {keyword}')
        
        # 查询学生关系
        query = TeacherStudent.query.filter_by(teacher_id=teacher_id)
        logger.info(f'初始查询：教师 {teacher_id} 管理的所有学生')
        
        # 关键词搜索
        if keyword:
            logger.info(f'应用关键词搜索: {keyword}')
            query = query.join(User, TeacherStudent.student_id == User.id).filter(
                TeacherStudent.teacher_id == teacher_id,
                (User.username.ilike(f'%{keyword}%')) |
                (User.real_name.ilike(f'%{keyword}%')) |
                (User.student_id.ilike(f'%{keyword}%'))
            )
        
        paginated = query.order_by(TeacherStudent.created_at.desc()).paginate(page=page, per_page=per_page)
        
        logger.info(f'查询结果 - 总数: {paginated.total}, 返回: {len(paginated.items)}, 总页数: {paginated.pages}')
        
        if paginated.items:
            student_ids = [ts.student_id for ts in paginated.items]
            logger.info(f'返回学生ID列表: {student_ids}')
        else:
            logger.info('没有找到匹配的学生')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'students': [ts.to_dict() for ts in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        }), 200
    
    except Exception as e:
        logger.error(f'Get students error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/students', methods=['POST'])
@jwt_required()
def add_student():
    """添加学生到教师的管理列表"""
    try:
        teacher_id = int(get_jwt_identity())
        logger.info(f'教师 {teacher_id} 尝试添加学生')
        
        teacher = User.query.get(teacher_id)
        
        if not teacher:
            logger.warning(f'教师 {teacher_id} 不存在')
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if teacher.user_type != 'teacher' and teacher.user_type != 'admin':
            logger.warning(f'用户 {teacher_id} 不是教师或管理员，user_type={teacher.user_type}')
            return jsonify({'code': 403, 'message': '只有教师和管理员可以管理学生'}), 403
        
        data = request.get_json()
        logger.info(f'请求数据: {data}')
        
        if not data or not data.get('student_id'):
            logger.warning('学生ID为空')
            return jsonify({'code': 400, 'message': '学生ID不能为空'}), 400
        
        student_id = data.get('student_id')
        logger.info(f'尝试添加学生 {student_id} 给教师 {teacher_id}')
        
        # 检查学生是否存在
        student = User.query.get(student_id)
        if not student:
            logger.warning(f'学生 {student_id} 不存在')
            return jsonify({'code': 404, 'message': '学生不存在'}), 404
        
        logger.info(f'学生 {student_id} 信息: username={student.username}, user_type={student.user_type}')
        
        if student.user_type != 'student':
            logger.warning(f'用户 {student_id} 不是学生，user_type={student.user_type}')
            return jsonify({'code': 400, 'message': '该用户不是学生'}), 400
        
        # 检查该学生是否已经被任何教师管理
        any_existing = TeacherStudent.query.filter_by(student_id=student_id).first()
        if any_existing:
            existing_teacher = User.query.get(any_existing.teacher_id)
            existing_teacher_name = existing_teacher.real_name or existing_teacher.username if existing_teacher else "未知教师"
            logger.warning(f'学生 {student_id} 已经被教师 {any_existing.teacher_id}({existing_teacher_name}) 管理')
            return jsonify({
                'code': 400, 
                'message': f'该学生已经被教师"{existing_teacher_name}"管理，一个学生只能被一个教师管理'
            }), 400

        # 检查是否已经添加过（冗余检查，但保留以防万一）
        existing = TeacherStudent.query.filter_by(
            teacher_id=teacher_id,
            student_id=student_id
        ).first()
        
        if existing:
            logger.warning(f'学生 {student_id} 已经被添加到教师 {teacher_id} 的管理列表中')
            return jsonify({'code': 400, 'message': '该学生已经被添加到您的管理列表中'}), 400
        
        # 创建关系
        ts = TeacherStudent(teacher_id=teacher_id, student_id=student_id)
        db.session.add(ts)
        db.session.commit()
        
        logger.info(f'学生 {student_id} 成功添加到教师 {teacher_id} 的管理列表中，关系ID: {ts.id}')
        
        return jsonify({
            'code': 201,
            'message': '学生添加成功',
            'data': ts.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Add student error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'添加失败: {str(e)}'}), 500


@teacher_bp.route('/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def remove_student(student_id):
    """删除学生从教师的管理列表"""
    try:
        teacher_id = int(get_jwt_identity())
        teacher = User.query.get(teacher_id)
        
        if not teacher:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if teacher.user_type != 'teacher' and teacher.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有教师和管理员可以管理学生'}), 403
        
        # 查找并删除关系
        ts = TeacherStudent.query.filter_by(
            teacher_id=teacher_id,
            student_id=student_id
        ).first()
        
        if not ts:
            return jsonify({'code': 404, 'message': '该学生不在您的管理列表中'}), 404
        
        db.session.delete(ts)
        db.session.commit()
        
        logger.info(f'Student {student_id} removed from teacher {teacher_id}')
        
        return jsonify({
            'code': 200,
            'message': '学生删除成功'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Remove student error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


@teacher_bp.route('/available-students', methods=['GET'])
@jwt_required()
def get_available_students():
    """获取可以添加的学生列表（未被该教师管理的）"""
    try:
        teacher_id = int(get_jwt_identity())
        logger.info(f'教师 {teacher_id} 查询可用学生列表')
        
        teacher = User.query.get(teacher_id)
        
        if not teacher:
            logger.warning(f'教师 {teacher_id} 不存在')
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if teacher.user_type != 'teacher' and teacher.user_type != 'admin':
            logger.warning(f'用户 {teacher_id} 不是教师或管理员，user_type={teacher.user_type}')
            return jsonify({'code': 403, 'message': '只有教师和管理员可以查看可用学生'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '', type=str)
        
        logger.info(f'查询参数 - 页码: {page}, 每页数: {per_page}, 关键词: {keyword}')
        
        # 获取已管理的学生ID列表
        managed_ids = db.session.query(TeacherStudent.student_id).filter_by(
            teacher_id=teacher_id
        ).all()
        managed_ids = [m[0] for m in managed_ids]
        logger.info(f'教师 {teacher_id} 已管理的学生ID: {managed_ids}')
        
        # 查询所有学生数量
        all_students_count = User.query.filter(User.user_type == 'student').count()
        logger.info(f'系统中学生总数: {all_students_count}')
        
        # 查询未被管理的学生
        if managed_ids:
            query = User.query.filter(
                (User.user_type == 'student') &
                (~User.id.in_(managed_ids))
            )
            logger.info(f'排除已管理的学生后，执行查询')
        else:
            query = User.query.filter(User.user_type == 'student')
            logger.info(f'教师未管理任何学生，查询所有学生')
        
        # 统计未管理的学生数
        unmanaged_count = query.count()
        logger.info(f'未被该教师管理的学生总数: {unmanaged_count}')
        
        # 关键词搜索
        if keyword:
            logger.info(f'应用关键词搜索: {keyword}')
            query = query.filter(
                (User.username.ilike(f'%{keyword}%')) |
                (User.real_name.ilike(f'%{keyword}%')) |
                (User.student_id.ilike(f'%{keyword}%'))
            )
            keyword_count = query.count()
            logger.info(f'关键词搜索结果数: {keyword_count}')
        
        paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
        
        logger.info(f'分页结果 - 总数: {paginated.total}, 返回: {len(paginated.items)}, 总页数: {paginated.pages}')
        
        if paginated.items:
            student_usernames = [s.username for s in paginated.items]
            logger.info(f'返回的学生用户名: {student_usernames}')
        else:
            logger.info('没有找到匹配的学生')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'students': [s.to_dict() for s in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        }), 200
    
    except Exception as e:
        logger.error(f'Get available students error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/student-info/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_info(student_id):
    """获取教师管理的特定学生详细信息"""
    try:
        teacher_id = int(get_jwt_identity())
        teacher = User.query.get(teacher_id)
        
        if not teacher:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if teacher.user_type != 'teacher' and teacher.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有教师和管理员可以查看学生信息'}), 403
        
        # 检查学生是否在该教师的管理列表中
        ts = TeacherStudent.query.filter_by(
            teacher_id=teacher_id,
            student_id=student_id
        ).first()
        
        if not ts:
            return jsonify({'code': 403, 'message': '您无权查看此学生的信息'}), 403
        
        student = ts.student
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': student.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f'Get student info error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


# ==================== 管理员专用接口 ====================

@teacher_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """管理员获取所有用户列表"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        
        if not admin:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if admin.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有管理员可以访问此接口'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '', type=str)
        user_type = request.args.get('user_type', '', type=str)
        
        logger.info(f'管理员 {admin_id} 查询用户列表, 参数: page={page}, per_page={per_page}, keyword={keyword}, user_type={user_type}')
        
        query = User.query
        
        # 按类型过滤
        if user_type:
            query = query.filter_by(user_type=user_type)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                (User.username.ilike(f'%{keyword}%')) |
                (User.real_name.ilike(f'%{keyword}%')) |
                (User.student_id.ilike(f'%{keyword}%'))
            )
        
        paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'users': [u.to_dict() for u in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        }), 200
    
    except Exception as e:
        logger.error(f'Admin get users error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/admin/teacher-students', methods=['GET'])
@jwt_required()
def admin_get_teacher_students():
    """管理员获取所有教师及其管理的学生"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        
        if not admin:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if admin.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有管理员可以访问此接口'}), 403
        
        logger.info(f'管理员 {admin_id} 查询教师及其学生关系')
        
        # 获取所有教师
        teachers = User.query.filter_by(user_type='teacher').all()
        
        result = []
        for teacher in teachers:
            # 获取该教师管理的学生
            teacher_students = TeacherStudent.query.filter_by(teacher_id=teacher.id).all()
            
            result.append({
                'teacher': teacher.to_dict(),
                'students': [
                    {
                        'id': ts.student_id,
                        'username': ts.student.username,
                        'real_name': ts.student.real_name,
                        'student_id': ts.student.student_id,
                        'email': ts.student.email,
                        'phone': ts.student.phone,
                        'college': ts.student.college,
                        'major': ts.student.major,
                        'created_at': ts.created_at.isoformat() if ts.created_at else None
                    }
                    for ts in teacher_students
                ],
                'student_count': len(teacher_students)
            })
        
        logger.info(f'返回 {len(result)} 个教师的信息')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'teachers': result,
                'total': len(result)
            }
        }), 200
    
    except Exception as e:
        logger.error(f'Admin get teacher students error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/admin/users', methods=['POST'])
@jwt_required()
def admin_create_user():
    """管理员创建用户"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        if not admin:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        if admin.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有管理员可以访问此接口'}), 403

        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type', 'student')

        if not username or not email or not password:
            return jsonify({'code': 400, 'message': '用户名、邮箱和密码为必填项'}), 400

        # 唯一性检查
        if User.query.filter_by(username=username).first():
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'code': 400, 'message': '邮箱已存在'}), 400

        user = User(
            username=username,
            email=email,
            real_name=data.get('real_name'),
            user_type=user_type,
            student_id=data.get('student_id'),
            teacher_id=data.get('teacher_id'),
            college=data.get('college'),
            major=data.get('major'),
            phone=data.get('phone'),
            is_active=data.get('is_active', True)
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        logger.info(f'管理员 {admin_id} 创建用户 {user.id} ({user.username})')

        return jsonify({'code': 201, 'message': '创建成功', 'data': user.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'Admin create user error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@teacher_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def admin_update_user(user_id):
    """管理员更新用户"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        if not admin:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        if admin.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有管理员可以访问此接口'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '目标用户不存在'}), 404

        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')

        # 唯一性检查（排除自身）
        if username and User.query.filter(User.username == username, User.id != user_id).first():
            return jsonify({'code': 400, 'message': '用户名已被占用'}), 400
        if email and User.query.filter(User.email == email, User.id != user_id).first():
            return jsonify({'code': 400, 'message': '邮箱已被占用'}), 400

        # 更新字段
        for field in ['username', 'email', 'real_name', 'user_type', 'student_id', 'teacher_id', 'college', 'major', 'phone', 'is_active']:
            if field in data:
                setattr(user, field, data.get(field))

        # 密码单独处理
        if data.get('password'):
            user.set_password(data.get('password'))

        db.session.commit()
        logger.info(f'管理员 {admin_id} 更新用户 {user.id} ({user.username})')

        return jsonify({'code': 200, 'message': '更新成功', 'data': user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Admin update user error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@teacher_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_user(user_id):
    """管理员删除用户（并清理关联关系）"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        if not admin:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        if admin.user_type != 'admin':
            return jsonify({'code': 403, 'message': '只有管理员可以访问此接口'}), 403

        if admin_id == user_id:
            return jsonify({'code': 400, 'message': '不能删除自己'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '目标用户不存在'}), 404

        # 删除教师-学生关系中与该用户相关的记录
        TeacherStudent.query.filter((TeacherStudent.teacher_id == user_id) | (TeacherStudent.student_id == user_id)).delete(synchronize_session=False)

        db.session.delete(user)
        db.session.commit()

        logger.info(f'管理员 {admin_id} 删除用户 {user_id}')

        return jsonify({'code': 200, 'message': '删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Admin delete user error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500



# ==================== 学生文档管理接口 ====================
@teacher_bp.route('/student-documents', methods=['GET'])
@jwt_required()
def get_student_documents():
    """获取教师管理的学生所有上交的文档"""
    try:
        from models import File
        teacher_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        student_id = request.args.get('student_id', type=int)
        document_type = request.args.get('document_type')
        submission_stage = request.args.get('submission_stage')

        # 获取教师管理的学生
        managed_students = db.session.query(TeacherStudent).filter_by(teacher_id=teacher_id).all()
        managed_student_ids = [ts.student_id for ts in managed_students]

        # 构建查询
        query = File.query.filter(File.user_id.in_(managed_student_ids))
        
        if student_id and student_id in managed_student_ids:
            query = query.filter_by(user_id=student_id)
        
        if document_type:
            query = query.filter_by(document_type=document_type)
        
        if submission_stage:
            query = query.filter_by(submission_stage=submission_stage)
        
        # 排除纯文件管理的文件，只返回有文档类型的毕业设计文档
        query = query.filter(File.document_type.isnot(None))
        query = query.order_by(File.created_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        items = [
            {
                **f.to_dict(),
                'student_username': User.query.get(f.user_id).username if f.user_id else None,
                'student_real_name': User.query.get(f.user_id).real_name if f.user_id else None,
            }
            for f in paginated.items
        ]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'documents': items,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        }), 200

    except Exception as e:
        logger.error(f'Get student documents error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/student-documents/<int:doc_id>/feedback', methods=['PUT'])
@jwt_required()
def add_document_feedback(doc_id):
    """添加文档评价"""
    try:
        teacher_id = int(get_jwt_identity())
        teacher = User.query.get(teacher_id)
        
        if teacher.user_type not in ('teacher', 'admin'):
            return jsonify({'code': 403, 'message': '只有教师或管理员可以评价文档'}), 403

        doc = File.query.get(doc_id)
        if not doc:
            return jsonify({'code': 404, 'message': '文档不存在'}), 404

        # 验证权限：教师只能评价自己管理的学生的文档
        if teacher.user_type == 'teacher':
            managed = TeacherStudent.query.filter_by(teacher_id=teacher_id, student_id=doc.user_id).first()
            if not managed:
                return jsonify({'code': 403, 'message': '您无权评价此文档'}), 403

        data = request.get_json() or {}
        feedback = data.get('feedback', '').strip()
        
        if not feedback:
            return jsonify({'code': 400, 'message': '评价内容不能为空'}), 400

        doc.teacher_feedback = feedback
        doc.feedback_by = teacher_id
        doc.feedback_at = datetime.utcnow()
        db.session.commit()

        logger.info(f'教师 {teacher_id} 评价了文档 {doc_id}')
        return jsonify({'code': 200, 'message': '评价成功'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Add feedback error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'评价失败: {str(e)}'}), 500


@teacher_bp.route('/student-documents/<int:doc_id>/remind', methods=['POST'])
@jwt_required()
def remind_student_submission(doc_id):
    """催交文档"""
    try:
        teacher_id = int(get_jwt_identity())
        teacher = User.query.get(teacher_id)
        
        if teacher.user_type not in ('teacher', 'admin'):
            return jsonify({'code': 403, 'message': '只有教师或管理员可以催交'}), 403

        doc = File.query.get(doc_id)
        if not doc:
            return jsonify({'code': 404, 'message': '文档不存在'}), 404

        # 验证权限
        if teacher.user_type == 'teacher':
            managed = TeacherStudent.query.filter_by(teacher_id=teacher_id, student_id=doc.user_id).first()
            if not managed:
                return jsonify({'code': 403, 'message': '您无权催交此文档'}), 403

        doc.reminder_count = (doc.reminder_count or 0) + 1
        doc.last_reminder_at = datetime.utcnow()
        db.session.commit()

        logger.info(f'教师 {teacher_id} 催交了学生 {doc.user_id} 的文档 {doc_id}，催交次数: {doc.reminder_count}')
        
        return jsonify({
            'code': 200,
            'message': '催交成功',
            'data': {
                'reminder_count': doc.reminder_count,
                'last_reminder_at': doc.last_reminder_at.isoformat()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'Remind submission error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'催交失败: {str(e)}'}), 500


@teacher_bp.route('/student-documents/<int:doc_id>/download', methods=['GET'])
@jwt_required()
def download_student_document(doc_id):
    """下载学生文档"""
    try:
        teacher_id = int(get_jwt_identity())
        teacher = User.query.get(teacher_id)
        
        if teacher.user_type not in ('teacher', 'admin'):
            return jsonify({'code': 403, 'message': '只有教师或管理员可以下载文档'}), 403

        doc = File.query.get(doc_id)
        if not doc:
            return jsonify({'code': 404, 'message': '文档不存在'}), 404

        # 验证权限：教师只能下载自己管理的学生的文档
        if teacher.user_type == 'teacher':
            managed = TeacherStudent.query.filter_by(teacher_id=teacher_id, student_id=doc.user_id).first()
            if not managed:
                return jsonify({'code': 403, 'message': '您无权下载此文档'}), 403

        # 获取上传文件夹路径
        UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
        file_path = os.path.join(UPLOAD_FOLDER, doc.file_key)
        
        if not os.path.exists(file_path):
            return jsonify({'code': 404, 'message': '文件不存在'}), 404

        logger.info(f'教师 {teacher_id} 下载了文档 {doc_id}')
        return send_file(
            file_path,
            as_attachment=True,
            download_name=doc.filename
        )

    except Exception as e:
        logger.error(f'Download student document error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'下载失败: {str(e)}'}), 500

# ==================== 消息相关接口 ====================
@teacher_bp.route('/messages/send', methods=['POST'])
@jwt_required()
def send_message():
    """发送消息：管理员可发全体公告或指定用户；教师可群发给自己管理的学生或指定学生列表"""
    try:
        sender_id = int(get_jwt_identity())
        sender = User.query.get(sender_id)
        if not sender:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        data = request.get_json() or {}
        content = data.get('content', '').strip()
        target = data.get('target', 'users')  # 'all'|'teacher_students'|'users'
        user_ids = data.get('user_ids', [])  # optional list of user ids
        recipient_type = data.get('recipient_type', None)  # 'all'|'teacher'|'student'

        if not content:
            return jsonify({'code': 400, 'message': '消息内容不能为空'}), 400

        # 构造接收者列表
        recipient_ids = set()

        if sender.user_type == 'admin':
            if target == 'all':
                # 管理员发送，支持按用户类型筛选
                if recipient_type == 'teacher':
                    # 只发给教师
                    users = User.query.filter(User.is_active == True, User.user_type == 'teacher').all()
                elif recipient_type == 'student':
                    # 只发给学生
                    users = User.query.filter(User.is_active == True, User.user_type == 'student').all()
                else:
                    # 发给所有用户（包括其他管理员）
                    users = User.query.filter(User.is_active == True).all()
                recipient_ids = {u.id for u in users if u.id != sender_id}
            elif target == 'users' and user_ids:
                recipient_ids = set(user_ids)
            else:
                return jsonify({'code': 400, 'message': '管理员发送时 target 参数无效'}), 400

        elif sender.user_type == 'teacher':
            if target == 'teacher_students':
                # 教师群发给自己管理的学生
                managed = TeacherStudent.query.filter_by(teacher_id=sender_id).all()
                recipient_ids = {ts.student_id for ts in managed}
            elif target == 'users' and user_ids:
                # 验证这些用户是否为教师的学生或允许直接发送
                recipient_ids = set(user_ids)
            else:
                return jsonify({'code': 400, 'message': '教师发送时 target 参数无效'}), 400
        else:
            return jsonify({'code': 403, 'message': '只有教师或管理员可以发送消息'}), 403

        if not recipient_ids:
            return jsonify({'code': 400, 'message': '接收者为空'}), 400

        # 创建消息
        msg = db.session.query(db.session.bind.mapper_registry.maps[0].class_).class_ if False else None
        # 简单创建Message
        from models import Message, MessageRecipient
        message = Message(sender_id=sender_id, content=content)
        db.session.add(message)
        db.session.flush()

        # 为每个接收者创建接收记录
        recipients = []
        for rid in recipient_ids:
            # 跳过不存在的用户
            user = User.query.get(rid)
            if not user:
                continue
            mr = MessageRecipient(message_id=message.id, recipient_id=rid, is_read=False)
            recipients.append(mr)
            db.session.add(mr)

        db.session.commit()

        logger.info(f'用户 {sender_id} 发送消息 id={message.id} 给 {len(recipients)} 个接收者')
        return jsonify({'code': 201, 'message': '发送成功', 'data': {'message_id': message.id, 'recipient_count': len(recipients)}}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'Send message error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'发送失败: {str(e)}'}), 500


@teacher_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    """获取当前用户的收件箱消息（分页）"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        from models import MessageRecipient, Message
        query = MessageRecipient.query.filter_by(recipient_id=user_id)
        paginated = query.join(Message, MessageRecipient.message_id == Message.id).order_by(Message.created_at.desc()).paginate(page=page, per_page=per_page)

        items = [mr.to_dict() for mr in paginated.items]
        return jsonify({'code': 200, 'message': '获取成功', 'data': {'messages': items, 'total': paginated.total, 'pages': paginated.pages, 'current_page': page}}), 200
    except Exception as e:
        logger.error(f'Get messages error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/messages/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        user_id = int(get_jwt_identity())
        from models import MessageRecipient
        count = MessageRecipient.query.filter_by(recipient_id=user_id, is_read=False).count()
        return jsonify({'code': 200, 'message': '获取成功', 'data': {'unread': count}}), 200
    except Exception as e:
        logger.error(f'Get unread count error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_message_read(message_id):
    try:
        user_id = int(get_jwt_identity())
        from models import MessageRecipient
        mr = MessageRecipient.query.filter_by(message_id=message_id, recipient_id=user_id).first()
        if not mr:
            return jsonify({'code': 404, 'message': '消息不存在或无权访问'}), 404
        if not mr.is_read:
            from datetime import datetime
            mr.is_read = True
            mr.read_at = datetime.utcnow()
            db.session.commit()
        return jsonify({'code': 200, 'message': '已标记为已读'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Mark message read error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'标记失败: {str(e)}'}), 500
# ==================== 教师评价相关接口 ====================

@teacher_bp.route('/my-teachers', methods=['GET'])
@jwt_required()
def get_my_teachers():
    """学生获取自己的教师列表"""
    try:
        student_id = int(get_jwt_identity())
        user = User.query.get(student_id)
        
        if not user or user.user_type != 'student':
            return jsonify({'code': 403, 'message': '只有学生可以查看'}), 403

        # 获取与该学生相关的教师
        teacher_students = TeacherStudent.query.filter_by(student_id=student_id).all()
        teachers = []
        
        for ts in teacher_students:
            teacher = User.query.get(ts.teacher_id)
            if teacher:
                # 检查是否已经评价过
                from models import TeacherReview
                review = TeacherReview.query.filter_by(
                    student_id=student_id,
                    teacher_id=ts.teacher_id
                ).first()
                
                teachers.append({
                    'id': teacher.id,
                    'username': teacher.username,
                    'real_name': teacher.real_name,
                    'reviewed': review is not None
                })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {'teachers': teachers}
        }), 200
    except Exception as e:
        logger.error(f'Get my teachers error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/reviews', methods=['POST'])
@jwt_required()
def submit_teacher_review():
    """学生提交对教师的评价"""
    try:
        student_id = int(get_jwt_identity())
        user = User.query.get(student_id)
        
        if not user or user.user_type != 'student':
            return jsonify({'code': 403, 'message': '只有学生可以提交评价'}), 403

        data = request.get_json() or {}
        teacher_id = data.get('teacher_id')
        rating = data.get('rating')
        comment = data.get('comment', '').strip()

        # 验证参数
        if not teacher_id:
            return jsonify({'code': 400, 'message': '教师ID不能为空'}), 400
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'code': 400, 'message': '评分必须是1-5之间的整数'}), 400
        
        if not comment or len(comment) < 20:
            return jsonify({'code': 400, 'message': '评价内容不少于20字'}), 400

        # 检查教师是否存在
        teacher = User.query.get(teacher_id)
        if not teacher or teacher.user_type != 'teacher':
            return jsonify({'code': 404, 'message': '教师不存在'}), 404

        # 检查学生是否被该教师管理
        managed = TeacherStudent.query.filter_by(
            teacher_id=teacher_id,
            student_id=student_id
        ).first()
        if not managed:
            return jsonify({'code': 403, 'message': '您无权评价此教师'}), 403

        # 检查是否已经评价过
        from models import TeacherReview
        existing_review = TeacherReview.query.filter_by(
            student_id=student_id,
            teacher_id=teacher_id
        ).first()
        
        if existing_review:
            return jsonify({'code': 400, 'message': '您已经评价过该教师，无法重复评价'}), 400

        # 创建评价
        review = TeacherReview(
            student_id=student_id,
            teacher_id=teacher_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()

        logger.info(f'学生 {student_id} 评价了教师 {teacher_id}，评分: {rating}')
        return jsonify({
            'code': 201,
            'message': '评价提交成功',
            'data': {'review_id': review.id}
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Submit teacher review error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'提交失败: {str(e)}'}), 500


@teacher_bp.route('/reviews/for-me', methods=['GET'])
@jwt_required()
def get_my_reviews():
    """教师查看自己收到的评价汇总"""
    try:
        teacher_id = int(get_jwt_identity())
        user = User.query.get(teacher_id)
        
        if not user or user.user_type != 'teacher':
            return jsonify({'code': 403, 'message': '只有教师可以查看'}), 403

        from models import TeacherReview
        # 获取所有评价（不显示学生身份）
        reviews = TeacherReview.query.filter_by(teacher_id=teacher_id).order_by(
            TeacherReview.created_at.desc()
        ).all()

        review_list = [review.to_dict() for review in reviews]
        
        # 计算统计信息
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for review in reviews:
                rating_dist[review.rating] += 1
        else:
            avg_rating = 0
            rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'reviews': review_list,
                'total_count': len(reviews),
                'avg_rating': round(avg_rating, 1),
                'rating_distribution': rating_dist
            }
        }), 200
    except Exception as e:
        logger.error(f'Get my reviews error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/reviews/check-status', methods=['GET'])
@jwt_required()
def check_review_status():
    """学生检查对某教师的评价状态"""
    try:
        student_id = int(get_jwt_identity())
        teacher_id = request.args.get('teacher_id', type=int)
        
        if not teacher_id:
            return jsonify({'code': 400, 'message': '教师ID不能为空'}), 400

        from models import TeacherReview
        review = TeacherReview.query.filter_by(
            student_id=student_id,
            teacher_id=teacher_id
        ).first()

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {'reviewed': review is not None}
        }), 200
    except Exception as e:
        logger.error(f'Check review status error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@teacher_bp.route('/reviews/all-teachers', methods=['GET'])
@jwt_required()
def get_all_teachers_ratings():
    """获取所有教师的评价统计（公开展示）"""
    try:
        student_id = int(get_jwt_identity())
        
        from models import TeacherReview
        
        # 获取所有有评价的教师
        all_reviews = TeacherReview.query.all()
        
        # 按教师分组计算统计
        teachers_stats = {}
        
        for review in all_reviews:
            teacher_id = review.teacher_id
            
            if teacher_id not in teachers_stats:
                teacher = User.query.get(teacher_id)
                if teacher and teacher.user_type == 'teacher':
                    teachers_stats[teacher_id] = {
                        'id': teacher_id,
                        'username': teacher.username,
                        'real_name': teacher.real_name,
                        'reviews': [],
                        'total_count': 0,
                        'avg_rating': 0,
                        'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                    }
            
            if teacher_id in teachers_stats:
                teachers_stats[teacher_id]['reviews'].append(review.to_dict())
                teachers_stats[teacher_id]['total_count'] += 1
                teachers_stats[teacher_id]['rating_distribution'][review.rating] += 1
        
        # 计算平均分
        for teacher_id, stats in teachers_stats.items():
            if stats['total_count'] > 0:
                avg = sum(r['rating'] for r in stats['reviews']) / stats['total_count']
                stats['avg_rating'] = round(avg, 1)
            # 限制显示的评价数量（只显示最新 3 条）
            stats['reviews'] = stats['reviews'][:3]
        
        # 按平均评分排序，高分在前
        teachers_list = sorted(
            list(teachers_stats.values()),
            key=lambda x: x['avg_rating'],
            reverse=True
        )
        
        # 检查学生的指导教师（用于标记哪些可以评价）
        my_teacher_ids = []
        if student_id:
            my_teachers = TeacherStudent.query.filter_by(student_id=student_id).all()
            my_teacher_ids = [ts.teacher_id for ts in my_teachers]
        
        # 为每个教师标记是否是学生的指导教师
        for teacher_stats in teachers_list:
            teacher_stats['is_my_teacher'] = teacher_stats['id'] in my_teacher_ids
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {'teachers': teachers_list}
        }), 200
    except Exception as e:
        logger.error(f'Get all teachers ratings error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500
