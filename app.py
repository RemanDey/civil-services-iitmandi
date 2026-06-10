# I MPORTING GLOBAL MODULES
from flask import Flask, render_template
#   IMPORTING LOCAL MODULES
from config import Config
###############################################################
##### Importing data modules for dynamic content rendering#####
import announcements_module
import notes_module
import core_module
import activities_module
import pyq_module
import gallery_module
import current_affairs_module
###############################################################
app = Flask(__name__)
app.config.from_object(Config)

# ---- Routes ----

@app.route('/')
def home():
    # Using data from announcements_module
    announcements = announcements_module.announcements
    return render_template('home.html', announcements=announcements)

@app.route('/about')
def about():
    core = core_module.core_members  # Importing the core members data from core_module.py
    return render_template('about.html', core=core)

@app.route('/gallery')
def gallery():
    # Sample images for the gallery
    images = gallery_module.images  # Importing the images data from gallery_module.py
    return render_template('gallery.html', images=images)

@app.route('/activities')
def activities():
    events = activities_module.activities
    return render_template('activities.html', events=events)

@app.route('/current-affairs')
def current_affairs():
    feeds = current_affairs_module.current_affairs  # Importing the current affairs data from current_affairs_module.py
    return render_template('current_affairs.html', feeds=feeds)

@app.route('/quizzes')
def quizzes():
    return render_template('quizzes.html')

@app.route('/notes')
def notes():
    notes_data = notes_module.notes  # Importing the notes data from notes.py

    return render_template('notes.html', categories=notes_data)

@app.route('/pyqs')
def pyqs():
    papers = pyq_module.pyqs  # Importing the PYQs data from pyq_module.py
    return render_template('pyqs.html', papers=papers)

if __name__ == '__main__':
    app.run(host='0.0.0.0')