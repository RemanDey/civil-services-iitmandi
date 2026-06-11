# Civil Services Club Website

A web application for the Civil Services Club at IIT Mandi, designed to provide comprehensive information about club activities, announcements, study materials, and resources for aspiring civil servants. This platform aims to be a central hub for members to stay updated and access valuable preparation content.

## Features

The website offers the following key functionalities:

-   **Dynamic Announcements**: Keep members informed with the latest news and updates.
-   **Upcoming and Past Activities**: Showcase club events, workshops, and interactive sessions.
-   **Gallery of Events**: A visual record of past club gatherings and activities.
-   **Curated Current Affairs Feeds**: Provide relevant news and analyses for civil services preparation.
-   **Notes and Study Materials**: Centralized access to important study resources.
-   **Previous Year Question Papers (PYQs)**: A collection of past examination papers for practice.
-   **Core Members Information**: Details about the club's organizing team.
-   **Responsive Navigation**: User-friendly navigation across various devices.

## Architecture Overview

This web application is built using a modular and lightweight architecture:

-   **Web Framework**: Developed with **Flask**, a micro web framework for Python, known for its simplicity and flexibility.
-   **Modular Data Management**: Content such as announcements, activities, notes, PYQs, and core member details are organized into separate Python modules. This approach enhances maintainability and makes content updates straightforward without altering the core application logic.
-   **Templating Engine**: Utilizes **Jinja2** for rendering dynamic HTML content, allowing for clean separation of presentation from business logic.
-   **Static Assets**: Cascading Style Sheets (CSS), JavaScript files, and images are served efficiently from the `static/` directory.

## Setup and Installation

Follow these steps to get the development environment up and running.

### Prerequisites

-   Python 3.x
-   pip (Python package installer)

### Installation Steps

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/remandey/civil-services-iitmandi.git
    cd civil-services-iitmandi
    ```

2.  **Create a virtual environment** (recommended to manage dependencies):
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment**:
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        venv\Scripts\activate
        ```

4.  **Install required Python packages**:
    ```bash
    pip install Flask Pillow numpy
    ```
    *Note: `Pillow` and `numpy` are dependencies for the `image_cropper.py` utility, not strictly for the web app's runtime.*

### Running the Application

1.  **Set Flask environment variables**:
    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development # Enables debug mode and auto-reloading
    ```
    *On Windows, use `set FLASK_APP=app.py` and `set FLASK_ENV=development`.*

2.  **Start the Flask development server**:
    ```bash
    flask run
    ```
    The application will typically be accessible at `http://127.0.0.1:5000/`.

## Code Structure Overview

The project is organized into the following directories and files:

```
/home/remandey/my-programs/civil-services-iitmandi/
├── app.py                      # Main Flask application file, defines routes and renders templates.
├── config.py                   # Application-wide configurations (e.g., SECRET_KEY, DEBUG).
├── announcements_module.py     # Stores data for club announcements.
├── activities_module.py        # Stores data for club activities (upcoming and past).
├── core_module.py              # Stores information about the club's core members.
├── notes_module.py             # Stores structured data for study notes and download links.
├── pyq_module.py               # Stores data for previous year question papers (PYQs).
├── static/                     # Contains static assets (CSS, JS, images).
│   ├── css/                    # CSS stylesheets.
│   ├── js/                     # JavaScript files for frontend interactivity.
│   │   └── main.js             # Handles responsive navbar toggle and active link highlighting.
│   └── images/                 # Image assets for the website.
│       └── image_cropper.py    # A standalone utility script for cropping images (not part of the web app's runtime).
└── templates/                  # Contains Jinja2 HTML templates for different web pages.
    ├── home.html
    ├── about.html
    ├── gallery.html
    ├── activities.html
    ├── current_affairs.html
    ├── quizzes.html
    ├── notes.html
    └── pyqs.html
```

## Key Components and Code Snippets

### `app.py` - Main Application Entry Point
This file initializes the Flask application, loads configurations, imports data modules, and defines all the routes for the website.

```python
# I MPORTING GLOBAL MODULES
from flask import Flask, render_template
#   IMPORTING LOCAL MODULES
from config import Config
import announcements_module
# ... other data module imports ...

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    announcements = announcements_module.announcements
    return render_template('home.html', announcements=announcements)

if __name__ == '__main__':
    app.run(debug=True)
```

### `config.py` - Application Configuration
Manages application-wide settings. `SECRET_KEY` is crucial for session management and security.

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'iit_mandi_csc_secret_2026'
    DEBUG = True # Set to False in production
```

### `announcements_module.py` - Example Data Module
Illustrates how data is structured and stored in Python lists of dictionaries, which are then imported and used by `app.py`.

```python
announcements = [
        {"date": "June 15, 2026", "title": "Interactive Session with UPSC CSE Rank 12", "tag": "Event"},
        {"date": "June 12, 2026", "title": "Weekly Mock Test 04 live this Sunday", "tag": "Quiz"},
        {"date": "June 08, 2026", "title": "June Edition Monthly Magazine uploaded", "tag": "Notes"}
    ]
```

### `static/js/main.js` - Frontend Interactivity
Handles client-side interactions, such as toggling the mobile navigation menu and highlighting the active navigation link.

```javascript
document.addEventListener("DOMContentLoaded", () => {
    // Mobile Responsive Navbar Toggle
    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", () => {
            navLinks.classList.toggle("active");
        });
    }

    // Assign active navigation classes contextually
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll(".nav-links a");
    links.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
});
```

## How to Add New Content

-   **Announcements, Activities, PYQs, Core Members**: Simply modify the respective `_module.py` file (e.g., `announcements_module.py`, `activities_module.py`) by adding new dictionary entries to the existing lists.
-   **Notes**: Update the `notes_module.py` dictionary with new categories or notes.
-   **New Web Page**: Create a new route in `app.py` using the `@app.route()` decorator and a corresponding HTML template file in the `templates/` directory.

## Image Cropper Utility
The `static/images/image_cropper.py` script is a standalone Python utility that uses `Pillow` (PIL) and `numpy` to crop images. It's not integrated into the web application's runtime but can be used as a helper tool for preparing image assets.

## Contributing
Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License
This project is open-source and available under the MIT License.
```