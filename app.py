"""
Main Application Entry Point for the Civil Services Club Website.
Initializes Flask app, database, admin panel, and defines routes.
"""

from flask import Flask, render_template
from config import Config
from models import db, Announcement, Activity, CoreMember, GalleryImage, NoteCategory, Note
from admin import admin_bp
from seed import seed_all
import current_affairs_module
import pyq_module
import quizzes_module

app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(admin_bp)

with app.app_context():
    db.create_all()
    seed_all()


@app.context_processor
def inject_admin_status():
    from flask import session
    return {"admin_logged_in": session.get("admin_logged_in", False)}


# ----------------------------------------------------------------
# Routes
# ----------------------------------------------------------------

@app.route("/")
def home():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("home.html", announcements=announcements)


@app.route("/about")
def about():
    core = CoreMember.query.all()
    return render_template("about.html", core=core)


@app.route("/gallery")
def gallery():
    images = GalleryImage.query.all()
    return render_template("gallery.html", images=images)


@app.route("/activities")
def activities():
    events = Activity.query.order_by(Activity.created_at.desc()).all()
    return render_template("activities.html", events=events)


@app.route("/current-affairs")
def current_affairs():
    feeds = current_affairs_module.get_current_affairs()
    return render_template("current_affairs.html", feeds=feeds)


@app.route("/quizzes")
def quizzes():
    questions = quizzes_module.get_quizzes()
    return render_template("quizzes.html", questions=questions)


@app.route("/notes")
def notes():
    categories = NoteCategory.query.all()
    notes_data = {}
    for cat in categories:
        notes_data[cat.name] = [
            {"title": n.title, "type": n.type, "download_link": n.download_link}
            for n in cat.notes
        ]
    return render_template("notes.html", categories=notes_data)


@app.route("/pyqs")
def pyqs():
    papers = pyq_module.get_pyqs()
    exams = sorted({paper["exam"] for paper in papers})
    years = sorted({paper["year"] for paper in papers}, reverse=True)
    return render_template("pyqs.html", papers=papers, exams=exams, years=years)


# ----------------------------------------------------------------
# Execution
# ----------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0")
