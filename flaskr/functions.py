#-*- coding:utf-8 -*-
import functools
from flask import flash
from flask import g
from flaskr.db import get_db

# ----------Author functions----------
#在其他视图中验证，用户登录以后才能创建、编辑和删除博客帖子。
#在每个视图中可以使用 装饰器 来完成这个工作。
def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

def auth_post_list(username):
    db = get_db()
    auth_posts = db.execute(
        "SELECT u.id, username, title, body, created, author_id"
        " FROM user u JOIN post p ON u.id = p.author_id"
        " WHERE username = ?"
        " ORDER BY created DESC", (username,)
    ).fetchall()
    
    return auth_posts

# ----------Post functions----------
def post_list():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    
    return posts

def get_post(title, check_author=True):
    post = (
        get_db().execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE title = ?",
            (title,)
        )
        .fetchone()
    )

    if post is None:
        abort(404, "Post id doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post

# ----------Comment functions----------  
def comment_list():
    db = get_db()
    comments = db.execute(
        "SELECT c.id, user_id, post_id, comment_time, comment_text, username"
        " FROM comment c JOIN user u ON c.user_id = u.id"
        " ORDER BY comment_time DESC"
    ).fetchall()
    
    return comments
   
    