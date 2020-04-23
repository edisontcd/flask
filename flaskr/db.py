#-*- coding:utf-8 -*-

import sqlite3, click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    #g 是一个特殊对象，独立于每一个请求。
    if 'db' not in g:
        g.db = sqlite3.connect(
            #current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用。
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        #sqlite3.Row 告诉连接返回类似于字典的行，这样可以通过列名称来操作数据。
        g.db.row_factory = sqlite3.Row
        
    return g.db

#close_db 通过检查 g.db 来确定连接是否已经建立。
#如果连接已建立，那么 就关闭连接。
def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
#用于运行schema.sql中的SQL命令。
def init_db():
    db = get_db()
    #open_resource() 打开一个文件，该文件名是相对于 flaskr 包的。
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#click.command() 定义一个名为 init-db 命令行，它调用 init_db 函数，并为用户显示一个成功的消息。   
@click.command('init-db')
@with_appcontext
def init_db_command():
    #清理现存的数据，建立新的表，初始化数据库。
    init_db()
    click.echo('Initialized the database.')

#把应用作为参数，在函数中进行注册。   
def init_app(app):
    #告诉 Flask 在返回响应后进行清理的时候调用此函数。
    app.teardown_appcontext(close_db)
    #添加一个新的 可以与 flask 一起工作的命令。
    app.cli.add_command(init_db_command)
