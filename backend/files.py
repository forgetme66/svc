from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, File, User
from datetime import datetime
import os
import uuid
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

files_bp = Blueprint('files', __name__, url_prefix='/api/files')

# 配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 创建上传文件夹
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """上传文件"""
    try:
        logger.info('File upload started')
        user_id = get_jwt_identity()
        logger.info(f'User ID: {user_id}')
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f'User not found: {user_id}')
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        logger.info(f'Request files: {request.files}')
        logger.info(f'Request form: {request.form}')
        
        # 检查是否有文件
        if 'file' not in request.files:
            logger.warning('No file in request')
            return jsonify({'code': 400, 'message': '没有文件被上传'}), 400
        
        file = request.files['file']
        logger.info(f'File name: {file.filename}')
        
        if file.filename == '':
            return jsonify({'code': 400, 'message': '文件名不能为空'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            logger.warning(f'File type not allowed: {file.filename}')
            return jsonify({'code': 400, 'message': f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        logger.info(f'File size: {file_size}')
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'code': 400, 'message': '文件大小不能超过100MB'}), 400
        
        if file_size == 0:
            return jsonify({'code': 400, 'message': '文件不能为空'}), 400
        
        # 获取表单数据
        description = request.form.get('description', '')
        is_public_str = request.form.get('is_public', 'false')
        is_public = is_public_str.lower() in ['true', '1', 'yes']
        
        logger.info(f'Description: {description}, Is public: {is_public}')
        
        # 获取毕业设计相关字段
        document_type = request.form.get('document_type')  # proposal, outline, draft, final
        submission_stage = request.form.get('submission_stage')  # early, mid, final
        
        logger.info(f'Document type: {document_type}, Submission stage: {submission_stage}')
        
        # 生成唯一的文件名
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'bin'
        file_key = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, file_key)
        
        logger.info(f'Saving file to: {file_path}')
        
        # 保存文件
        file.save(file_path)
        logger.info(f'File saved successfully')
        
        # 创建文件记录
        from datetime import datetime
        file_record = File(
            user_id=user_id,
            filename=original_filename,
            file_key=file_key,
            file_type=file_ext,
            file_size=file_size,
            description=description,
            is_public=is_public,
            document_type=document_type,
            submission_stage=submission_stage,
            is_submitted=True,
            submitted_at=datetime.utcnow() if document_type else None
        )
        
        db.session.add(file_record)
        db.session.commit()
        logger.info(f'File record created: {file_record.id}')
        
        return jsonify({
            'code': 201,
            'message': '文件上传成功',
            'data': file_record.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'File upload error: {str(e)}', exc_info=True)
        return jsonify({'code': 500, 'message': f'上传失败: {str(e)}'}), 500

@files_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    """获取用户的文件列表"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 根据用户类型获取文件
        if user.user_type == 'admin':
            # 管理员可以看所有文件
            query = File.query
        else:
            # 普通用户只能看自己的文件
            query = File.query.filter_by(user_id=user_id)
        
        paginated = query.order_by(File.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'files': [f.to_dict() for f in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500

@files_bp.route('/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """下载文件"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 检查权限
        if file_record.user_id != user_id and user.user_type != 'admin' and not file_record.is_public:
            return jsonify({'code': 403, 'message': '没有权限下载此文件'}), 403
        
        file_path = os.path.join(UPLOAD_FOLDER, file_record.file_key)
        
        if not os.path.exists(file_path):
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_record.filename
        )
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'下载失败: {str(e)}'}), 500

@files_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file_info(file_id):
    """获取文件信息"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 检查权限
        if file_record.user_id != user_id and user.user_type != 'admin' and not file_record.is_public:
            return jsonify({'code': 403, 'message': '没有权限查看此文件'}), 403
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': file_record.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500

@files_bp.route('/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    """更新文件信息"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 检查权限
        if file_record.user_id != user_id:
            return jsonify({'code': 403, 'message': '没有权限修改此文件'}), 403
        
        data = request.get_json()
        
        if 'description' in data:
            file_record.description = data['description']
        if 'is_public' in data:
            file_record.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': file_record.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500

@files_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """删除文件"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 检查权限
        if file_record.user_id != user_id:
            return jsonify({'code': 403, 'message': '没有权限删除此文件'}), 403
        
        # 删除物理文件
        file_path = os.path.join(UPLOAD_FOLDER, file_record.file_key)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除数据库记录
        db.session.delete(file_record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '文件删除成功'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500

@files_bp.route('/search', methods=['GET'])
@jwt_required()
def search_files():
    """搜索文件"""
    try:
        user_id = int(get_jwt_identity())  # JWT identity是字符串，转换为整数
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        keyword = request.args.get('keyword', '', type=str)
        file_type = request.args.get('file_type', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 根据用户类型构建查询
        if user.user_type == 'admin':
            query = File.query
        else:
            query = File.query.filter_by(user_id=user_id)
        
        # 关键词搜索
        if keyword:
            query = query.filter(File.filename.ilike(f'%{keyword}%'))
        
        # 文件类型筛选
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        paginated = query.order_by(File.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'code': 200,
            'message': '搜索成功',
            'data': {
                'files': [f.to_dict() for f in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'code': 500, 'message': f'搜索失败: {str(e)}'}), 500
