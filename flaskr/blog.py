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
from flaskr.db import get_db, close_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    posts = post_list()
    comments = comment_list()
    
    return render_template("blog/index.html", posts=posts, comments=comments)
    
@bp.route("/<int:id>")
def post(id):
    post = (
        get_db().execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )
    
    if post is None:
        abort(404, "Post doesn't exist.")
    
    comments = comment_list()
    posts = post_list()
    
    return render_template("blog/post.html", comments=comments, post=post, posts=posts)
     

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.post", id=id))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))

@bp.route("/<int:id>", methods=("GET", "POST"))
@login_required
def add_comment(id):
    post = (
        get_db().execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )
    
    if request.method == "POST":
        comment_text = request.form["comment_text"]
        error = None
        
        if not comment_text:
            error = "Comment is required."
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO comment (post_id, user_id, comment_text) VALUES (?, ?, ?)",
                (post["id"], g.user["id"], comment_text)
            )
            db.commit()
            return redirect(url_for("blog.post", id=id))
            
    return render_template("blog/post.html", post=post)
    
def post_list():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    
    return posts

def get_post(id, check_author=True):
    post = (
        get_db().execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, "Post id doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post
    
def comment_list():
    db = get_db()
    comments = db.execute(
        "SELECT c.id, user_id, post_id, comment_time, comment_text, username"
        " FROM comment c JOIN user u ON c.user_id = u.id"
        " ORDER BY comment_time DESC"
    ).fetchall()
    
    return comments
   
def get_comment(id):
    db = get_db()
    comment = db.execute(
        "SELECT c.id, user_id, comment_time, comment_text, username"
        " FROM comment c JOIN user u ON c.user_id = u.id"
        " WHERE c.id = ?",
        (id,),
    ).fetchone()
    
    return comment


