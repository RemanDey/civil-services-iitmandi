# Civil Services Club Website

A web application for the Civil Services Club at IIT Mandi, providing information about club activities, announcements, study materials, and resources for aspiring civil servants.

## Features

- **Announcements**: Latest club news and updates fetched from GitHub
- **Activities**: Upcoming and past club events and workshops
- **Gallery**: Photo gallery of club events
- **Current Affairs**: Scraped news feeds from Drishti IAS and PIB
- **Quizzes**: Backend-driven quiz module with UPSC PYQs and fallback questions
- **Notes**: Categorized study materials and download links
- **PYQs**: Previous Year Question Papers scraped from UPSC website
- **Core Members**: Club organizing team profiles

## Architecture

- **Framework**: Flask + Jinja2 templating
- **Data Modules**: Modular Python files for each content type (some fetch from GitHub raw JSON, others scrape live sources)
- **Scraping**: `requests` + `BeautifulSoup` for UPSC PYQs and Drishti/PIB current affairs
- **Quiz Engine**: `quizzes_module.py` with PDF extraction via `pypdf`, 6-hour cache, and fallback questions

## Setup

```bash
git clone https://github.com/remandey/civil-services-iitmandi.git
cd civil-services-iitmandi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Visit `http://127.0.0.1:5000/`.

## Production

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## Project Structure

```
├── app.py                      # Flask application (routes)
├── requirements.txt            # Python dependencies
├── test.py                     # Quick JSON fetch test
├── activities_module.py        # Fetches activities from GitHub raw JSON
├── announcements_module.py     # Fetches announcements from GitHub raw JSON
├── core_module.py              # Fetches core members from GitHub raw JSON
├── gallery_module.py           # Fetches gallery metadata from GitHub raw JSON
├── notes_module.py             # Fetches notes from GitHub raw JSON
├── current_affairs_module.py   # Scrapes Drishti IAS + PIB for current affairs
├── pyq_module.py               # Scrapes UPSC previous year question papers
├── quizzes_module.py           # Quiz engine (UPSC PDFs + fallback, 6hr cache)
├── IMPLEMENTATION_COMPLETE.md  # Quiz module implementation report
├── QUIZ_MODULE_DOCS.md         # Quiz module documentation
├── static/
│   ├── css/style.css           # Stylesheet
│   ├── js/main.js              # Navbar toggle, active link highlighting
│   └── images/                 # Logo, gallery photos, core member profiles
└── templates/
    ├── base.html               # Base layout
    ├── home.html               # Landing page
    ├── about.html              # Core members
    ├── gallery.html            # Photo gallery
    ├── activities.html         # Events timeline
    ├── current_affairs.html    # News feed
    ├── quizzes.html            # Interactive quiz
    ├── notes.html              # Study notes
    └── pyqs.html               # Previous year papers
```

## Data Flow

```
GitHub Raw JSON  →  Data Modules (activities, announcements, core, gallery, notes)
UPSC Website     →  Scraping Modules (pyq, current_affairs, quizzes)
                         ↓
                    app.py (routes)
                         ↓
                    Jinja2 Templates
                         ↓
                    Browser (CSS/JS)
```

## Adding Content

- **GitHub-sourced data**: Update the raw JSON files in the remote `civilservicesclub-iitmandi/website` repo
- **Static modules**: Edit the corresponding `_module.py` file (e.g., add entries to lists)
- **New page**: Add a route in `app.py` and a template in `templates/`

## Image Cropper

`static/images/image_cropper.py` is a standalone utility using Pillow + numpy for cropping images. Not part of the web app runtime.

## License

MIT
