
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload, selectinload
from models import db, Question, User, Message
import traceback

questions_bp = Blueprint('questions_bp', __name__, url_prefix='/api/questions')

@questions_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_question():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = int(get_jwt_identity())

    if not title or not content:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 创建 Question 作为对话线程
        question_data = {
            'title': title,
            'user_id': user_id
        }
        if user.guidance_teacher_id:
            question_data['teacher_id'] = user.guidance_teacher_id

        question = Question(**question_data)
        # 创建第一条 Message
        message = Message(
            sender_id=user_id,
            content=content
        )
        question.messages.append(message)

        db.session.add(question)
        db.session.commit()
        
        return jsonify({'code': 201, 'message': '问题已提交', 'data': question.to_dict(current_user_id=user_id)}), 201
    except Exception as e:
        db.session.rollback()
        tb_str = traceback.format_exc()
        print(f"--- CREATE QUESTION TRACEBACK START ---")
        print(tb_str)
        print(f"--- CREATE QUESTION TRACEBACK END ---")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@questions_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_questions():
    search_keyword = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = int(get_jwt_identity())

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 根据用户角色构建查询
        if user.user_type == 'teacher':
            query = Question.query.filter_by(teacher_id=user_id)
        else:
            query = Question.query.filter_by(user_id=user_id)

        query = query.options(
            joinedload(Question.author), 
            joinedload(Question.teacher),
            selectinload(Question.messages).options(joinedload(Message.sender))
        ).order_by(Question.created_at.desc())

        if search_keyword:
            query = query.filter(Question.title.ilike(f'%{search_keyword}%'))

        paginated_questions = query.paginate(page=page, per_page=per_page, error_out=False)
        
        questions_data = [q.to_dict(current_user_id=user_id) for q in paginated_questions.items]

        return jsonify({
            'code': 200,
            'data': {
                'questions': questions_data,
                'total': paginated_questions.total,
                'page': paginated_questions.page,
                'pages': paginated_questions.pages,
            }
        }), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@questions_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_details(question_id):
    user_id = int(get_jwt_identity())
    try:
        question = Question.query.options(
            selectinload(Question.messages).options(joinedload(Message.sender)),
            joinedload(Question.author),
            joinedload(Question.teacher)
        ).get(question_id)

        if not question:
            return jsonify({'code': 404, 'message': '问题不存在'}), 404

        # 权限检查：只有提问的学生或指定的老师可以查看
        if user_id != question.user_id and user_id != question.teacher_id:
            return jsonify({'code': 403, 'message': '无权访问此问题'}), 403

        # 标记消息为已读
        updated = False
        for msg in question.messages:
            if msg.sender_id != user_id and not msg.is_read:
                msg.is_read = True
                updated = True
        
        if updated:
            db.session.commit()
            
        return jsonify({'code': 200, 'data': question.to_dict_with_messages(current_user_id=user_id)}), 200
    except Exception as e:
        tb_str = traceback.format_exc()
        print(f"--- TRACEBACK START ---")
        print(tb_str)
        print(f"--- TRACEBACK END ---")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}', 'traceback': tb_str}), 500


@questions_bp.route('/<int:question_id>/messages', methods=['POST'])
@jwt_required()
def create_message(question_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'code': 400, 'message': '消息内容不能为空'}), 400

    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'code': 404, 'message': '问题不存在'}), 404

        # 权限检查：只有提问的学生或指定的老师可以发送消息
        if user_id != question.user_id and user_id != question.teacher_id:
            return jsonify({'code': 403, 'message': '无权在此问题下发送消息'}), 403

        message = Message(
            question_id=question.id,
            sender_id=user_id,
            content=content
        )
        
        db.session.add(message)
        db.session.commit()

        return jsonify({'code': 201, 'message': '消息已发送', 'data': message.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@questions_bp.route('/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    user_id = int(get_jwt_identity())
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'code': 404, 'message': '问题不存在'}), 404

        # 权限检查：只有提问的学生本人可以删除
        if user_id != question.user_id:
            return jsonify({'code': 403, 'message': '无权删除此问题'}), 403

        db.session.delete(question)
        db.session.commit()
        return jsonify({'code': 200, 'message': '问题已成功删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@questions_bp.route('/teacher-dashboard', methods=['GET'])
@jwt_required()
def get_teacher_dashboard_questions():
    user_id = int(get_jwt_identity())
    try:
        user = User.query.get(user_id)
        if not user or user.user_type != 'teacher':
            return jsonify({'code': 403, 'message': '仅教师有权访问'}), 403

        # 获取该老师指导的所有问题，并按学生ID和创建时间排序
        questions = Question.query.filter_by(teacher_id=user_id)\
            .options(joinedload(Question.author))\
            .order_by(Question.user_id, Question.created_at.desc())\
            .all()

        # 按学生ID对问题进行分组
        from collections import defaultdict
        student_questions_map = defaultdict(lambda: {'student_id': None, 'student_name': None, 'questions': []})

        for q in questions:
            student_id = q.author.id
            if not student_questions_map[student_id]['student_id']:
                student_questions_map[student_id]['student_id'] = student_id
                student_questions_map[student_id]['student_name'] = q.author.username
            
            student_questions_map[student_id]['questions'].append(q.to_dict(current_user_id=user_id))

        return jsonify({'code': 200, 'data': list(student_questions_map.values())}), 200

    except Exception as e:
        db.session.rollback()
        tb_str = traceback.format_exc()
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}', 'traceback': tb_str}), 500
