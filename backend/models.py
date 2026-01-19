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
            'owner': self.owner.username if self.owner else '',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<File {self.filename}>'


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
