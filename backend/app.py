import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db, User
from auth import auth_bp
from files import files_bp

def create_app(config_name=None):
    """应用工厂函数"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    
    # 健康检查端点
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'code': 200, 'message': 'OK', 'status': 'healthy'}, 200
    
    # 创建数据库表和默认管理员
    with app.app_context():
        db.create_all()
        create_default_admin()
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': '资源不存在'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'code': 500, 'message': '服务器内部错误'}, 500
    
    return app

def create_default_admin():
    """创建默认管理员账户"""
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            real_name='系统管理员',
            user_type='admin',
            is_active=True
        )
        admin.set_password('Admin@123456')
        db.session.add(admin)
        db.session.commit()
        print('✓ 默认管理员账户已创建: username=admin, password=Admin@123456')
    else:
        print('✓ 管理员账户已存在')

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
