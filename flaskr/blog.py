#-*- coding:utf-8 -*-
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.functions import post_list, get_post, comment_list, login_required

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    posts = post_list()
    comments = comment_list()
    
    return render_template("blog/index.html", posts=posts, comments=comments)
    
@bp.route("/<title>")
def post(title):
    post = (
        get_db().execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE title = ?",
            (title,),
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


@bp.route("/<title>/update", methods=("GET", "POST"))
@login_required
def update(title):
    """Update a post if the current user is the author."""
    post = get_post(title)

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
                "UPDATE post SET title = ?, body = ? WHERE title = ?", (title, body, title)
            )
            db.commit()
            return redirect(url_for("blog.post", title=title))

    return render_template("blog/update.html", post=post)


@bp.route("/<title>/delete", methods=("POST",))
@login_required
def delete(title):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(title)
    db = get_db()
    db.execute("DELETE FROM post WHERE title = ?", (title,))
    db.commit()
    return redirect(url_for("blog.index"))

@bp.route("/<title>", methods=("GET", "POST"))
@login_required
def add_comment(title):
    post = (
        get_db().execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE title = ?",
            (title,)
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
            return redirect(url_for("blog.post", title=title))
            
    return render_template("blog/post.html", post=post)


