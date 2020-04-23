#-*- coding:utf-8 -*-

import os
from flask import Flask

def create_app(test_config=None):
    #创建和配置app
    #instance_relative_config=True 告诉应用配置文件是相对于实例文件夹的相对路径。
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        #Flask.instance_path 可以找到实例文件夹的绝对路径。
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    if test_config is None:
        #如果有，加载实例配置文件
        app.config.from_pyfile('config.py', silent=True)
    else:
        #加载测试配置文件
        app.config.from_mapping(test_config)
        
    #确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    #初始化数据库。
    db.init_app(app)
    
    from . import auth
    #使用 app.register_blueprint() 导入并注册 蓝图。
    app.register_blueprint(auth.bp)
    
    return app
        
    