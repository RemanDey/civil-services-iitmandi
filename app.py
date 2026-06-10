from flask import Flask, render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ---- Routes ----

@app.route('/')
def home():
    # Mock data for announcements
    announcements = [
        {"date": "June 15, 2026", "title": "Interactive Session with UPSC CSE Rank 12", "tag": "Event"},
        {"date": "June 12, 2026", "title": "Weekly Mock Test 04 live this Sunday", "tag": "Quiz"},
        {"date": "June 08, 2026", "title": "June Edition Monthly Magazine uploaded", "tag": "Notes"}
    ]
    return render_template('home.html', announcements=announcements)

@app.route('/gallery')
def gallery():
    # Sample images for the gallery
    images = [
        {"url": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?q=80&w=600", "title": "Inaugural Meet 2026"},
        {"url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=600", "title": "Seminar by IAS Officer"},
        {"url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?q=80&w=600", "title": "Group Discussion Stage 1"},
        {"url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=600", "title": "Answer Writing Workshop"},
        {"url": "https://images.unsplash.com/photo-1577896851231-70ef18881754?q=80&w=600", "title": "Mock Interview Panel"},
        {"url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600", "title": "Interactive Study Session"}
    ]
    return render_template('gallery.html', images=images)

@app.route('/activities')
def activities():
    events = [
        {"status": "Upcoming", "date": "June 20, 2026", "title": "Strategy Session: Balancing B.Tech & UPSC", "desc": "A panel discussion featuring IIT alumni who successfully cleared the Civil Services Examination during or right after college."},
        {"status": "Past", "date": "May 25, 2026", "title": "Ethics & Integrity Workshop", "desc": "A comprehensive lecture breaking down GS Paper IV application strategies and case study workflows."},
        {"status": "Past", "date": "May 10, 2026", "title": "Mock Prelims Marathon", "desc": "Campus-wide simulated GS Paper I test with immediate detailed solutions and metric reports."}
    ]
    return render_template('activities.html', events=events)

@app.route('/current-affairs')
def current_affairs():
    feeds = [
        {"date": "June 11, 2026", "category": "Economy", "title": "Understanding the Digital Rupee Expansion Framework", "summary": "An in-depth analysis of the Reserve Bank of India's newly rolled out programmable functionalities for CBDC-R and its impact on structural liquidity."},
        {"date": "June 09, 2026", "category": "Environment", "title": "Global Biofuel Alliance: Targets vs Achievements", "summary": "Evaluating the clean energy transition benchmarks achieved by member countries under the GBA framework, specifically tracking ethanol blending mandates."},
        {"date": "June 05, 2026", "category": "Polity", "title": "The Evolution of Cooperative Federalism via Article 263", "summary": "Examining recent recommendations by the Inter-State Council secretariat concerning structural consultative machinery during interstate river water conflicts."}
    ]
    return render_template('current_affairs.html', feeds=feeds)

@app.route('/quizzes')
def quizzes():
    return render_template('quizzes.html')

@app.route('/notes')
def notes():
    categories = {
        "Polity": [
            {"title": "Constitutional & Non-Constitutional Bodies Summary", "type": "PDF"},
            {"title": "Emergency Provisions & Basic Structure Doctrine Notes", "type": "PDF"}
        ],
        "History": [
            {"title": "Modern India: Governor Generals & Key Land Revenue Reforms", "type": "PDF"},
            {"title": "Art & Architecture: Temple Styles of Ancient and Medieval India", "type": "PDF"}
        ],
        "Geography": [
            {"title": "Indian River Systems & Major Monsoonal Mechanics", "type": "PDF"}
        ]
    }
    return render_template('notes.html', categories=categories)

@app.route('/pyqs')
def pyqs():
    papers = [
        {"year": 2025, "exam": "UPSC CSE", "paper": "General Studies Paper I", "link": "#"},
        {"year": 2025, "exam": "UPSC CSE", "paper": "General Studies Paper II (CSAT)", "link": "#"},
        {"year": 2024, "exam": "UPSC CSE", "paper": "General Studies Paper I", "link": "#"},
        {"year": 2024, "exam": "UPSC IFoS", "paper": "Forestry Paper I", "link": "#"},
        {"year": 2023, "exam": "UPSC CSE", "paper": "GS Paper IV (Ethics)", "link": "#"}
    ]
    return render_template('pyqs.html', papers=papers)

if __name__ == '__main__':
    app.run(debug=True)