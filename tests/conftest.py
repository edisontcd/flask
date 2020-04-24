#-*- coding:utf-8 -*-

import os
import tempfile
import pytest

from flaskr import create_app
from flaskr.db import get_db
from flaskr.db import init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")
    
@pytest.fixture
def app():
    #为测试创建和配置一个新的app实例
    #tempfile.mkstemp() 创建并打开一个临时文件，返回该文件对象和路径。
    #DATABASE 路径被重载，这样它会指向临时路径，而不是实例文件夹。
    db_fd, db_path = tempfile.mkstemp()
    #用常规测试配置创建app
    app = create_app({"TESTING": True, "DATABASE": db_path})
    
    #创建数据库，载入测试数据
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    #生成器
    yield app
    
    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)
    
#client 固件调用 app.test_client() 由 app 固件创建的应用 对象。
#测试会使用客户端来向应用发送请求，而不用启动服务器。    
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

#runner 固件类似于 client 。 app.test_cli_runner() 创建一个运行器， 
#可以调用应用注册的 Click 命令。
@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
    
class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
        
    
    