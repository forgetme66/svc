from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()

class User(db.Model):
    """用户基础模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100))
    user_type = db.Column(db.String(20), nullable=False, default='student')  # student, teacher, admin
    student_id = db.Column(db.String(50), unique=True)  # 学号
    teacher_id = db.Column(db.String(50), unique=True)  # 工号
    college = db.Column(db.String(100))  # 学院
    major = db.Column(db.String(100))  # 专业
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    files = db.relationship('File', backref=db.backref('owner', lazy=True), foreign_keys='File.user_id')
    questions = db.relationship('Question', backref=db.backref('author', lazy=True), foreign_keys='Question.user_id')
    
    # 新增：指导教师关联
    guidance_teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    guidance_teacher = db.relationship('User', remote_side=[id], backref=db.backref('students', lazy='dynamic'))
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        # 新增：UTC转北京时间
        from datetime import timedelta
        created_at_local = self.created_at + timedelta(hours=8) if self.created_at else None
        updated_at_local = self.updated_at + timedelta(hours=8) if self.updated_at else None
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'user_type': self.user_type,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'college': self.college,
            'major': self.major,
            'phone': self.phone,
            'is_active': self.is_active,
            # 核心修改：格式化时间为前端易解析的格式
            'created_at': created_at_local.strftime('%Y-%m-%d %H:%M:%S') if created_at_local else '',
            'updated_at': updated_at_local.strftime('%Y-%m-%d %H:%M:%S') if updated_at_local else '',
            # 可选：添加register_time别名，适配前端字段名
            'register_time': created_at_local.strftime('%Y-%m-%d %H:%M:%S') if created_at_local else ''
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class File(db.Model):
    """文件模型"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    file_key = db.Column(db.String(255), unique=True, nullable=False, index=True)  # 存储文件名
    file_type = db.Column(db.String(50))  # 文件类型
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    description = db.Column(db.Text)  # 文件描述
    is_public = db.Column(db.Boolean, default=False)  # 是否公开
    
    # 毕业设计相关字段
    document_type = db.Column(db.String(50))  # 文档类型：proposal（选题报告）、outline（大纲）、draft（初稿）、final（终稿）
    submission_stage = db.Column(db.String(50))  # 上交阶段：early（早期）、mid（中期）、final（最终）
    teacher_feedback = db.Column(db.Text)  # 教师评价反馈
    is_submitted = db.Column(db.Boolean, default=True)  # 是否已上交
    submitted_at = db.Column(db.DateTime)  # 上交时间
    feedback_at = db.Column(db.DateTime)  # 反馈时间
    feedback_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 反馈教师
    reminder_count = db.Column(db.Integer, default=0)  # 催交次数
    last_reminder_at = db.Column(db.DateTime)  # 最后催交时间
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_key': self.file_key,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'description': self.description,
            'is_public': self.is_public,
            'owner': self.owner.real_name if self.owner else '',
            'document_type': self.document_type,
            'submission_stage': self.submission_stage,
            'teacher_feedback': self.teacher_feedback,
            'is_submitted': self.is_submitted,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'feedback_at': self.feedback_at.isoformat() if self.feedback_at else None,
            'reminder_count': self.reminder_count,
            'last_reminder_at': self.last_reminder_at.isoformat() if self.last_reminder_at else None,
            'owner': self.owner.username if self.owner else '',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<File {self.filename}>'


class Question(db.Model):
    """问题模型，作为对话的主题"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 允许为空
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_by_student = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_by_teacher = db.Column(db.DateTime, nullable=True)

    # 关系
    teacher = db.relationship('User', foreign_keys='Question.teacher_id', backref=db.backref('assigned_questions', lazy='dynamic'))
    messages = db.relationship('Message', backref='question', cascade="all, delete-orphan")

    def get_dynamic_status(self, current_user_id):
        if not self.messages:
            return "未知"

        # 确保消息按时间排序
        sorted_messages = sorted(self.messages, key=lambda m: m.created_at)
        last_message = sorted_messages[-1]
        
        # 判断当前用户角色（这需要数据库查询，但为了简化调用签名，我们在内部做）
        # 注意：这里可能会有性能问题，但在小规模应用中可接受
        # 更好的做法是从外部传入 current_user 对象
        # User 类在当前文件中定义，直接使用即可
        current_user = User.query.get(current_user_id)
        if not current_user:
            return "未知"
            
        is_teacher = (current_user.user_type == 'teacher')
        
        # 检查是否有未读消息（针对当前用户）
        # 如果是老师，关注来自学生的未读消息
        # 如果是学生，关注来自老师的未读消息
        has_unread_for_me = any(not m.is_read for m in self.messages if m.sender_id != current_user_id)

        if is_teacher:
            # --- 教师视角状态 ---
            if has_unread_for_me:
                return "待回答" # 有学生的新消息
            
            # 如果最后一条消息是学生发的，且没有未读（这在逻辑上有点冲突，除非已读但未回），通常算待回答
            if last_message.sender.user_type == 'student':
                return "待回答"
            
            # 如果最后一条是老师发的
            if last_message.sender.user_type == 'teacher':
                return "已回复"
                
        else:
            # --- 学生视角状态 ---
            if has_unread_for_me:
                return "待查看" # 老师回复了
            
            if last_message.sender.user_type == 'student':
                return "等待回答"
            elif last_message.sender.user_type == 'teacher':
                return "已回复" # 已查看
        
        return "开放中"

    def to_dict(self, current_user_id=None):
        """基本序列化，不含消息列表"""
        
        status = self.get_dynamic_status(current_user_id) if current_user_id else "未知"

        return {
            'id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'author_name': self.author.real_name if self.author else '未知用户',
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.real_name if self.teacher else '待分配',
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'status': status,
        }

    def to_dict_with_messages(self, current_user_id=None):
        """序列化问题，并包含完整的消息列表和作者信息"""
        question_dict = self.to_dict(current_user_id=current_user_id)
        # 在Python端对消息进行排序
        sorted_messages = sorted(self.messages, key=lambda m: m.created_at)
        question_dict['messages'] = [message.to_dict() for message in sorted_messages]
        # 补充完整的作者信息
        if self.author:
            question_dict['author'] = self.author.to_dict()
        return question_dict

    def __repr__(self):
        return f'<Question {self.title}>'


class Message(db.Model):
    """对话消息模型"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, server_default='0')

    # 关系
    sender = db.relationship('User', backref='sent_messages')

    def to_dict(self):
        """转换为字典"""
        sender_name = ''
        if self.sender:
            # 优先用真实姓名，否则用用户名，确保总有一个有效名字
            sender_name = self.sender.real_name or self.sender.username

        return {
            'id': self.id,
            'question_id': self.question_id,
            'sender_id': self.sender_id,
            'sender_name': sender_name,
            'sender_user_type': self.sender.user_type if self.sender else '',
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'is_read': self.is_read
        }

    def __repr__(self):
        return f'<Message {self.id} in Question {self.question_id}>'
class TeacherStudent(db.Model):
    """教师-学生关系表"""
    __tablename__ = 'teacher_students'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('managed_students', lazy=True))
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('teachers', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('teacher_id', 'student_id', name='unique_teacher_student'),)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'student': self.student.to_dict() if self.student else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<TeacherStudent teacher={self.teacher_id} student={self.student_id}>'


class PasswordReset(db.Model):
    """密码重置令牌"""
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('password_resets', lazy=True))
    
    def is_valid(self):
        """检查令牌是否有效"""
        return not self.used and self.expires_at > datetime.utcnow()
    
    def __repr__(self):
        return f'<PasswordReset user_id={self.user_id}>'



class TeacherReview(db.Model):
    """学生对教师的评价"""
    __tablename__ = 'teacher_reviews'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 分
    comment = db.Column(db.Text, nullable=False)  # 文字评价
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('reviews_given', lazy=True))
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('reviews_received', lazy=True))

    # 添加唯一约束，确保学生对教师只能评价一次
    __table_args__ = (db.UniqueConstraint('student_id', 'teacher_id', name='unique_student_teacher_review'),)

    def to_dict(self):
        """转换为字典（不显示学生身份）"""
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

    def to_dict_with_student(self):
        """包含学生信息的字典"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_username': self.student.username if self.student else None,
            'teacher_id': self.teacher_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }