#-*- coding:utf-8 -*-
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.blog import get_post

bp = Blueprint("comment", __name__)

@login_required
def comment(id):
    post = get_post(id)
    
    if request.method == "post":
        comment_text = request.form["comment_text"]
        error = None
        
        if not comment_text:
            error = "Comment is required."
        
        if error is not None:
            flash(error)
        else:
            db = get_db
            db.execute(
                "INSERT INTO comment (post_id, user_id, comment_text) VALUES (?, ?, ?)",
                (g.post["id"], g.user["id"], comment_text)
            )
            db.commit()
            return redirect(url_for("blog.post", id=id))
            
    return render_template("blog/post.html", post=post)
    
def comments():
    db = get_db()
    comments = db.execute(
        "SELECT c.id, post_id, user_id, comment_text, username"
        "From (comment c INNER JOIN user u ON c.user_id = u.id) INNER JOIN post p ON c.post_id = p.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/post.html", post=post)
    
#def get_comment()
    
    
    
    
    
    
    
    
    
    
    
    
    