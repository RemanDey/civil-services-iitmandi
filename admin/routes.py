import os
import time
from werkzeug.utils import secure_filename
from flask import (
    render_template, request, redirect, url_for,
    session, flash, current_app,
)
from werkzeug.security import check_password_hash
from admin import admin_bp, login_required
from models import db, Announcement, Activity, CoreMember, GalleryImage, NoteCategory, Note

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file, subfolder):
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(time.time())}{ext}"
        folder = os.path.join(current_app.root_path, "static", "images", subfolder)
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        return filename
    return None


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    cfg = current_app.config
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if (cfg.get("ADMIN_USERNAME") and cfg.get("ADMIN_PASSWORD_HASH")
                and username == cfg["ADMIN_USERNAME"]
                and check_password_hash(cfg["ADMIN_PASSWORD_HASH"], password)):
            session["admin_logged_in"] = True
            session.permanent = True
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "announcements": Announcement.query.count(),
        "activities": Activity.query.count(),
        "members": CoreMember.query.count(),
        "gallery": GalleryImage.query.count(),
        "note_categories": NoteCategory.query.count(),
        "notes": Note.query.count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


# ---------------------------------------------------------------------------
# Announcements CRUD
# ---------------------------------------------------------------------------

@admin_bp.route("/announcements/")
@login_required
def announcements_list():
    items = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("admin/generic_list.html",
                           entity_name="Announcements", entity_url="announcements",
                           columns=["Date", "Title", "Tag"],
                           rows=[(a.id, [a.date, a.title, a.tag]) for a in items])


@admin_bp.route("/announcements/new", methods=["GET", "POST"])
@login_required
def announcements_new():
    if request.method == "POST":
        db.session.add(Announcement(
            date=request.form["date"],
            title=request.form["title"],
            tag=request.form["tag"],
        ))
        db.session.commit()
        flash("Announcement added.", "success")
        return redirect(url_for("admin.announcements_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Announcement", entity_url="announcements",
                           fields=[
                               {"name": "date", "label": "Date", "type": "text", "placeholder": "e.g. June 21, 2026"},
                               {"name": "title", "label": "Title", "type": "text"},
                               {"name": "tag", "label": "Tag", "type": "text", "placeholder": "e.g. Current Affairs"},
                           ])


@admin_bp.route("/announcements/<int:id>/edit", methods=["GET", "POST"])
@login_required
def announcements_edit(id):
    item = Announcement.query.get_or_404(id)
    if request.method == "POST":
        item.date = request.form["date"]
        item.title = request.form["title"]
        item.tag = request.form["tag"]
        db.session.commit()
        flash("Announcement updated.", "success")
        return redirect(url_for("admin.announcements_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Announcement", entity_url="announcements",
                           fields=[
                               {"name": "date", "label": "Date", "type": "text", "value": item.date},
                               {"name": "title", "label": "Title", "type": "text", "value": item.title},
                               {"name": "tag", "label": "Tag", "type": "text", "value": item.tag},
                           ], is_edit=True, item_id=item.id)


@admin_bp.route("/announcements/<int:id>/delete", methods=["GET", "POST"])
@login_required
def announcements_delete(id):
    item = Announcement.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Announcement deleted.", "success")
        return redirect(url_for("admin.announcements_list"))
    return render_template("admin/delete_confirm.html",
                           entity_name="Announcement", entity_url="announcements", item=item)


# ---------------------------------------------------------------------------
# Activities CRUD
# ---------------------------------------------------------------------------

@admin_bp.route("/activities/")
@login_required
def activities_list():
    items = Activity.query.order_by(Activity.created_at.desc()).all()
    return render_template("admin/generic_list.html",
                           entity_name="Activities", entity_url="activities",
                           columns=["Date", "Title", "Status"],
                           rows=[(a.id, [a.date, a.title, a.status]) for a in items])


@admin_bp.route("/activities/new", methods=["GET", "POST"])
@login_required
def activities_new():
    if request.method == "POST":
        db.session.add(Activity(
            date=request.form["date"],
            title=request.form["title"],
            desc=request.form["desc"],
            status=request.form["status"],
        ))
        db.session.commit()
        flash("Activity added.", "success")
        return redirect(url_for("admin.activities_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Activity", entity_url="activities",
                           fields=[
                               {"name": "date", "label": "Date", "type": "text", "placeholder": "e.g. June 21, 2026"},
                               {"name": "title", "label": "Title", "type": "text"},
                               {"name": "desc", "label": "Description", "type": "textarea"},
                               {"name": "status", "label": "Status", "type": "select",
                                "options": [("Upcoming", "Upcoming"), ("Past", "Past")]},
                           ])


@admin_bp.route("/activities/<int:id>/edit", methods=["GET", "POST"])
@login_required
def activities_edit(id):
    item = Activity.query.get_or_404(id)
    if request.method == "POST":
        item.date = request.form["date"]
        item.title = request.form["title"]
        item.desc = request.form["desc"]
        item.status = request.form["status"]
        db.session.commit()
        flash("Activity updated.", "success")
        return redirect(url_for("admin.activities_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Activity", entity_url="activities",
                           fields=[
                               {"name": "date", "label": "Date", "type": "text", "value": item.date},
                               {"name": "title", "label": "Title", "type": "text", "value": item.title},
                               {"name": "desc", "label": "Description", "type": "textarea", "value": item.desc},
                               {"name": "status", "label": "Status", "type": "select",
                                "options": [("Upcoming", "Upcoming"), ("Past", "Past")],
                                "value": item.status},
                           ], is_edit=True, item_id=item.id)


@admin_bp.route("/activities/<int:id>/delete", methods=["GET", "POST"])
@login_required
def activities_delete(id):
    item = Activity.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Activity deleted.", "success")
        return redirect(url_for("admin.activities_list"))
    return render_template("admin/delete_confirm.html",
                           entity_name="Activity", entity_url="activities", item=item)


# ---------------------------------------------------------------------------
# Core Members CRUD
# ---------------------------------------------------------------------------

@admin_bp.route("/members/")
@login_required
def members_list():
    items = CoreMember.query.all()
    return render_template("admin/generic_list.html",
                           entity_name="Core Members", entity_url="members",
                           columns=["Name", "Role", "Email", "Image"],
                           rows=[(m.id, [m.name, m.role, m.email, m.profile_image]) for m in items])


@admin_bp.route("/members/new", methods=["GET", "POST"])
@login_required
def members_new():
    if request.method == "POST":
        filename = save_image(request.files.get("profile_image"), "core_members") or "default.png"
        db.session.add(CoreMember(
            name=request.form["name"],
            role=request.form["role"],
            email=request.form["email"],
            profile_image=filename,
        ))
        db.session.commit()
        flash("Core member added.", "success")
        return redirect(url_for("admin.members_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Core Member", entity_url="members",
                           fields=[
                               {"name": "name", "label": "Name", "type": "text"},
                               {"name": "role", "label": "Role", "type": "text"},
                               {"name": "email", "label": "Email", "type": "email"},
                               {"name": "profile_image", "label": "Profile Image", "type": "file", "accept": "image/*"},
                           ])


@admin_bp.route("/members/<int:id>/edit", methods=["GET", "POST"])
@login_required
def members_edit(id):
    item = CoreMember.query.get_or_404(id)
    if request.method == "POST":
        item.name = request.form["name"]
        item.role = request.form["role"]
        item.email = request.form["email"]
        uploaded = save_image(request.files.get("profile_image"), "core_members")
        if uploaded:
            item.profile_image = uploaded
        db.session.commit()
        flash("Core member updated.", "success")
        return redirect(url_for("admin.members_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Core Member", entity_url="members",
                           fields=[
                               {"name": "name", "label": "Name", "type": "text", "value": item.name},
                               {"name": "role", "label": "Role", "type": "text", "value": item.role},
                               {"name": "email", "label": "Email", "type": "email", "value": item.email},
                               {"name": "profile_image", "label": "Profile Image", "type": "file",
                                "accept": "image/*", "current_file": item.profile_image},
                           ], is_edit=True, item_id=item.id)


@admin_bp.route("/members/<int:id>/delete", methods=["GET", "POST"])
@login_required
def members_delete(id):
    item = CoreMember.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Core member deleted.", "success")
        return redirect(url_for("admin.members_list"))
    return render_template("admin/delete_confirm.html",
                           entity_name="Core Member", entity_url="members", item=item)


# ---------------------------------------------------------------------------
# Gallery CRUD
# ---------------------------------------------------------------------------

@admin_bp.route("/gallery/")
@login_required
def gallery_list():
    items = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template("admin/generic_list.html",
                           entity_name="Gallery Images", entity_url="gallery",
                           columns=["Image", "Title"],
                           rows=[(img.id, [img.url, img.title]) for img in items])


@admin_bp.route("/gallery/new", methods=["GET", "POST"])
@login_required
def gallery_new():
    if request.method == "POST":
        file = request.files.get("image")
        filename = save_image(file, "gallery")
        if not filename:
            flash("Please upload a valid image file.", "error")
            return redirect(url_for("admin.gallery_new"))
        db.session.add(GalleryImage(
            url=f"/static/images/gallery/{filename}",
            title=request.form["title"],
        ))
        db.session.commit()
        flash("Gallery image added.", "success")
        return redirect(url_for("admin.gallery_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Gallery Image", entity_url="gallery",
                           fields=[
                               {"name": "title", "label": "Title", "type": "text"},
                               {"name": "image", "label": "Image File", "type": "file", "accept": "image/*"},
                           ])


@admin_bp.route("/gallery/<int:id>/edit", methods=["GET", "POST"])
@login_required
def gallery_edit(id):
    item = GalleryImage.query.get_or_404(id)
    if request.method == "POST":
        item.title = request.form["title"]
        uploaded = save_image(request.files.get("image"), "gallery")
        if uploaded:
            item.url = f"/static/images/gallery/{uploaded}"
        db.session.commit()
        flash("Gallery image updated.", "success")
        return redirect(url_for("admin.gallery_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Gallery Image", entity_url="gallery",
                           fields=[
                               {"name": "title", "label": "Title", "type": "text", "value": item.title},
                               {"name": "image", "label": "Image File", "type": "file",
                                "accept": "image/*", "current_file": item.url},
                           ], is_edit=True, item_id=item.id)


@admin_bp.route("/gallery/<int:id>/delete", methods=["GET", "POST"])
@login_required
def gallery_delete(id):
    item = GalleryImage.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Gallery image deleted.", "success")
        return redirect(url_for("admin.gallery_list"))
    return render_template("admin/delete_confirm.html",
                           entity_name="Gallery Image", entity_url="gallery", item=item)


# ---------------------------------------------------------------------------
# Note Categories CRUD
# ---------------------------------------------------------------------------

@admin_bp.route("/note-categories/")
@login_required
def note_categories_list():
    items = NoteCategory.query.order_by(NoteCategory.name).all()
    return render_template("admin/generic_list.html",
                           entity_name="Note Categories", entity_url="note-categories",
                           entity_endpoint="note_categories",
                           columns=["Name", "Notes Count"],
                           rows=[(c.id, [c.name, len(c.notes)]) for c in items])


@admin_bp.route("/note-categories/new", methods=["GET", "POST"])
@login_required
def note_categories_new():
    if request.method == "POST":
        name = request.form["name"].strip()
        if NoteCategory.query.filter_by(name=name).first():
            flash("Category already exists.", "error")
            return redirect(url_for("admin.note_categories_new"))
        db.session.add(NoteCategory(name=name))
        db.session.commit()
        flash("Note category added.", "success")
        return redirect(url_for("admin.note_categories_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Note Category", entity_url="note-categories",
                           entity_endpoint="note_categories",
                           fields=[
                               {"name": "name", "label": "Category Name", "type": "text"},
                           ])


@admin_bp.route("/note-categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
def note_categories_edit(id):
    item = NoteCategory.query.get_or_404(id)
    if request.method == "POST":
        name = request.form["name"].strip()
        existing = NoteCategory.query.filter_by(name=name).first()
        if existing and existing.id != item.id:
            flash("Category name already taken.", "error")
            return redirect(url_for("admin.note_categories_edit", id=id))
        item.name = name
        db.session.commit()
        flash("Note category updated.", "success")
        return redirect(url_for("admin.note_categories_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Note Category", entity_url="note-categories",
                           entity_endpoint="note_categories",
                           fields=[
                               {"name": "name", "label": "Category Name", "type": "text", "value": item.name},
                           ], is_edit=True, item_id=item.id)


@admin_bp.route("/note-categories/<int:id>/delete", methods=["GET", "POST"])
@login_required
def note_categories_delete(id):
    item = NoteCategory.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Note category deleted.", "success")
        return redirect(url_for("admin.note_categories_list"))
    return render_template("admin/delete_confirm.html",
                           entity_name="Note Category", entity_url="note-categories",
                           entity_endpoint="note_categories", item=item)


# ---------------------------------------------------------------------------
# Notes CRUD
# ---------------------------------------------------------------------------

@admin_bp.route("/notes/")
@login_required
def notes_list():
    items = Note.query.order_by(Note.created_at.desc()).all()
    return render_template("admin/generic_list.html",
                           entity_name="Notes", entity_url="notes",
                           columns=["Title", "Type", "Category"],
                           rows=[(n.id, [n.title, n.type, n.category.name]) for n in items])


@admin_bp.route("/notes/new", methods=["GET", "POST"])
@login_required
def notes_new():
    categories = NoteCategory.query.order_by(NoteCategory.name).all()
    if not categories:
        flash("Create a note category first.", "warning")
        return redirect(url_for("admin.note_categories_new"))

    if request.method == "POST":
        db.session.add(Note(
            title=request.form["title"],
            type=request.form["type"],
            download_link=request.form["download_link"],
            category_id=int(request.form["category_id"]),
        ))
        db.session.commit()
        flash("Note added.", "success")
        return redirect(url_for("admin.notes_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Note", entity_url="notes",
                           fields=[
                               {"name": "title", "label": "Title", "type": "text"},
                               {"name": "type", "label": "Type", "type": "text",
                                "placeholder": "e.g. PDF, youtube"},
                               {"name": "download_link", "label": "Download Link", "type": "text",
                                "placeholder": "https://..."},
                               {"name": "category_id", "label": "Category", "type": "select",
                                "options": [(c.id, c.name) for c in categories]},
                           ])


@admin_bp.route("/notes/<int:id>/edit", methods=["GET", "POST"])
@login_required
def notes_edit(id):
    item = Note.query.get_or_404(id)
    categories = NoteCategory.query.order_by(NoteCategory.name).all()
    if request.method == "POST":
        item.title = request.form["title"]
        item.type = request.form["type"]
        item.download_link = request.form["download_link"]
        item.category_id = int(request.form["category_id"])
        db.session.commit()
        flash("Note updated.", "success")
        return redirect(url_for("admin.notes_list"))
    return render_template("admin/generic_form.html",
                           entity_name="Note", entity_url="notes",
                           fields=[
                               {"name": "title", "label": "Title", "type": "text", "value": item.title},
                               {"name": "type", "label": "Type", "type": "text", "value": item.type},
                               {"name": "download_link", "label": "Download Link",
                                "type": "text", "value": item.download_link},
                               {"name": "category_id", "label": "Category", "type": "select",
                                "options": [(c.id, c.name) for c in categories],
                                "value": item.category_id},
                           ], is_edit=True, item_id=item.id)


@admin_bp.route("/notes/<int:id>/delete", methods=["GET", "POST"])
@login_required
def notes_delete(id):
    item = Note.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(item)
        db.session.commit()
        flash("Note deleted.", "success")
        return redirect(url_for("admin.notes_list"))
    return render_template("admin/delete_confirm.html",
                           entity_name="Note", entity_url="notes", item=item)
