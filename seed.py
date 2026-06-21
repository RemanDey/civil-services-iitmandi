"""Seed the database from GitHub JSON sources."""
import json
import re
import requests
from models import db, Announcement, Activity, CoreMember, GalleryImage, NoteCategory, Note

GITHUB_BASE = "https://raw.githubusercontent.com/civilservicesclub-iitmandi/website"


def fetch_json(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            text = re.sub(r",\s*([}\]])", r"\1", resp.text)
            return json.loads(text)
    except Exception:
        pass
    return None


def seed_all():
    if Announcement.query.first() is not None:
        return

    data = fetch_json(f"{GITHUB_BASE}/main/announcements")
    if data:
        for item in data:
            db.session.add(Announcement(
                date=item.get("date", ""),
                title=item.get("title", ""),
                tag=item.get("tag", ""),
            ))

    data = fetch_json(f"{GITHUB_BASE}/refs/heads/main/activities")
    if data:
        for item in data:
            db.session.add(Activity(
                status=item.get("status", "Past"),
                date=item.get("date", ""),
                title=item.get("title", ""),
                desc=item.get("desc", ""),
            ))

    data = fetch_json(f"{GITHUB_BASE}/refs/heads/main/core")
    if data:
        for item in data:
            db.session.add(CoreMember(
                name=item.get("name", ""),
                role=item.get("role", ""),
                email=item.get("email", ""),
                profile_image=item.get("profile_image", "default.png"),
            ))

    data = fetch_json(f"{GITHUB_BASE}/refs/heads/main/gallery")
    if data:
        for item in data:
            db.session.add(GalleryImage(
                url=item.get("url", ""),
                title=item.get("title", ""),
            ))

    data = fetch_json(f"{GITHUB_BASE}/main/notes")
    if data:
        for cat_name, items in data.items():
            cat = NoteCategory.query.filter_by(name=cat_name).first()
            if not cat:
                cat = NoteCategory(name=cat_name)
                db.session.add(cat)
                db.session.flush()
            for item in items:
                db.session.add(Note(
                    title=item.get("title", ""),
                    type=item.get("type", ""),
                    download_link=item.get("download_link", ""),
                    category_id=cat.id,
                ))

    db.session.commit()
