"""
Main Application Entry Point for the Civil Services Club Website.
This script initializes the Flask app, loads configurations, and defines
routes to serve dynamic content using data from various local modules.
"""

from flask import Flask, render_template

# Local Module Imports

import announcements_module
import notes_module
import core_module
import activities_module
import pyq_module
import gallery_module
import current_affairs_module

# Initialize Flask application
app = Flask(__name__)

# Load data from modules into variables for template rendering
announcements = announcements_module.announcements
core = core_module.core_members
images = gallery_module.images
events = activities_module.activities
feeds = current_affairs_module.current_affairs
notes_data = notes_module.notes
papers = pyq_module.pyqs

# ----------------------------------------------------------------             
# Routes
# ----------------------------------------------------------------

@app.route('/')
def home():
    """Renders the Home page with the latest club announcements."""
    return render_template('home.html', announcements=announcements)

@app.route('/about')
def about():
    """Renders the About page containing details of core members."""
    return render_template('about.html', core=core)

@app.route('/gallery')
def gallery():
    """Renders the visual Gallery of past events and activities."""
    return render_template('gallery.html', images=images)

@app.route('/activities')
def activities():
    """Renders the Activities page showcasing upcoming and past club events."""
    return render_template('activities.html', events=events)

@app.route('/current-affairs')
def current_affairs():
    """Renders the Current Affairs feed for exam preparation."""
    return render_template('current_affairs.html', feeds=feeds)

@app.route('/quizzes')
def quizzes():
    """Renders the Quizzes landing page."""
    return render_template('quizzes.html')

@app.route('/notes')
def notes():
    """Renders the study resources and notes section."""
    return render_template('notes.html', categories=notes_data)

@app.route('/pyqs')
def pyqs():
    """Renders the Previous Year Question (PYQ) papers section."""
    return render_template('pyqs.html', papers=papers)

# ----------------------------------------------------------------
# Execution
# ----------------------------------------------------------------

if __name__ == '__main__':
    # Runs the application on all available network interfaces
    app.run(host='0.0.0.0')