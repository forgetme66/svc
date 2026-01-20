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
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
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


class Message(db.Model):
    """系统消息/公告"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username if self.sender else None,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }


class MessageRecipient(db.Model):
    """消息接收者与已读状态"""
    __tablename__ = 'message_recipients'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    message = db.relationship('Message', foreign_keys=[message_id], backref=db.backref('recipients', lazy=True))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('inbox', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'recipient_id': self.recipient_id,
            'sender_id': self.message.sender_id if self.message else None,
            'sender_username': self.message.sender.username if self.message and self.message.sender else None,
            'sender_user_type': self.message.sender.user_type if self.message and self.message.sender else None,
            'sender': {
                'id': self.message.sender.id,
                'username': self.message.sender.username,
                'user_type': self.message.sender.user_type
            } if self.message and self.message.sender else None,
            'message': {
                'id': self.message.id,
                'content': self.message.content,
                'created_at': self.message.created_at.isoformat() if self.message else None
            } if self.message else None,
            'content': self.message.content if self.message else '',
            'created_at': self.message.created_at.isoformat() if self.message else None,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

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