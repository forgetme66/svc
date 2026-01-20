#!/usr/bin/env python
"""
数据库迁移脚本 - 更新 File 表以支持毕业设计文档字段
"""
import os
import sys
from app import create_app
from models import db, File, User
from sqlalchemy import text

def migrate():
    """执行迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始迁移数据库...")
            
            # 删除旧表（如果需要重建）
            print("删除旧的数据库表...")
            try:
                # 删除所有相关表
                db.session.execute(text('DROP TABLE IF EXISTS files'))
                db.session.execute(text('DROP TABLE IF EXISTS message_recipients'))
                db.session.execute(text('DROP TABLE IF EXISTS messages'))
                db.session.execute(text('DROP TABLE IF EXISTS teacher_students'))
                db.session.execute(text('DROP TABLE IF EXISTS password_resets'))
                db.session.execute(text('DROP TABLE IF EXISTS users'))
                db.session.commit()
                print("✓ 数据库表已清空")
            except Exception as e:
                print(f"- 表清空失败: {e}")
                db.session.rollback()
            
            # 重新创建表
            print("创建新的数据库表...")
            db.create_all()
            print("✓ 数据库表已创建")
            
            print("\n迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate()
