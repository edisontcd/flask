#-*- coding:utf-8 -*-

from flaskr import create_app

def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing