# app/routes.py
import os, io, zipfile
from flask import render_template, send_from_directory, abort, flash, redirect, url_for, request, send_file
from werkzeug.utils import secure_filename


from eventbus import emitter


# Allowed extensions for uploads
ALLOWED_EXTENSIONS = {"txt", "log", "csv", "pdf", "png", "jpg", "jpeg"}
UPLOAD_PERMISSIONS = {
    'data': True,
    'logs': False,
    'downloads': False,
    'archives': False,
}

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def sizeof_fmt(num, suffix="B"):
    """Convert bytes to human-readable string."""
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"


def init_routes(app):
    IMG_FOLDER = os.path.join("static", "images")
    LOG_FOLDER = os.path.join("logs")
    DOWN_FOLDER = os.path.join("downloads")
    ARCH_FOLDER = os.path.join("archives")
    DATA_FOLDER = os.path.join("data")
    COVERS_FOLDER = os.path.join("covers")

    app.config["IMG_FOLDER"] = IMG_FOLDER

    app.config["DATA_FOLDER"] = DATA_FOLDER
    app.config["LOG_FOLDER"] = LOG_FOLDER
    app.config["DOWN_FOLDER"] = DOWN_FOLDER
    app.config["ARCH_FOLDER"] = ARCH_FOLDER
    app.config["COVERS_FOLDER"] = COVERS_FOLDER

    FOLDER_MAP = {
        'data': app.config['DATA_FOLDER'],
        'logs': app.config['LOG_FOLDER'],
        'downloads': app.config['DOWN_FOLDER'],
        'archives': app.config['ARCH_FOLDER'],
        'covers': app.config['COVERS_FOLDER'],
    }

    @app.route('/')
    def index():
        emitter.emit('frontend.log', "Connection received.")
        logo = os.path.join(app.config["IMG_FOLDER"], "librarian.png")
        logo_cat = os.path.join(app.config["IMG_FOLDER"], "waiting_cat.png")
        
        # pass it to your Jinja template
        return render_template('index.html', logo=logo, logo_cat=logo_cat)
    
    @app.route('/favicon.ico')
    def favicon():
        emitter.emit('frontend.log', "Loading favicon.")
        return send_from_directory(
            app.config["IMG_FOLDER"],  # typically "app/static"
            'librarian.png',
            mimetype='image/x-icon'
        )

    
    # Handle nested subpaths for downloads
    @app.route("/<folder_type>/", defaults={'subpath': ''}, methods=["GET", "POST"])
    @app.route("/<folder_type>/<path:subpath>", methods=["GET", "POST"])
    def files_index(folder_type, subpath):
        if folder_type not in FOLDER_MAP:
            return "Invalid path", 404
        base_folder = FOLDER_MAP[folder_type]
        # Only downloads supports subpaths
        if subpath and folder_type != 'downloads':
            abort(404)
        # Compute actual folder on disk
        current_folder = os.path.join(base_folder, subpath)
        if not os.path.isdir(current_folder):
            abort(404)
        can_upload = UPLOAD_PERMISSIONS.get(folder_type, False)

        # Handle upload
        if request.method == 'POST':
            if not can_upload:
                flash("Uploads are not allowed in this folder.", "error")
                return redirect(url_for('files_index', folder_type=folder_type, subpath=subpath))
            uploaded = request.files.get('file')
            if uploaded and allowed_file(uploaded.filename):
                filename = secure_filename(uploaded.filename)
                dest = os.path.join(current_folder, filename)
                uploaded.save(dest)
                flash(f"Uploaded: {filename}", "success")
            else:
                flash("No file selected or type not allowed.", "error")
            return redirect(url_for('files_index', folder_type=folder_type, subpath=subpath))

        # List directories and files
        try:
            entries = os.listdir(current_folder)
        except OSError:
            entries = []
        dirs, files = [], []
        for name in sorted(entries, key=lambda x: x.lower()):
            if name.startswith('.'):
                continue
            full_path = os.path.join(current_folder, name)
            if os.path.isdir(full_path):
                # relative link path
                rel_path = os.path.join(subpath, name) if subpath else name
                dirs.append({'name': name, 'rel_path': rel_path})
            elif os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                files.append({'name': name, 'size_human': sizeof_fmt(size)})

        # Build breadcrumbs for navigation
        crumbs = []
        if folder_type == 'downloads':
            parts = subpath.split('/') if subpath else []
            for i in range(len(parts)):
                path = '/'.join(parts[:i+1])
                crumbs.append({'name': parts[i], 'path': path})

        return render_template(
            'files.html', folder_type=folder_type,
            subpath=subpath, dirs=dirs, files=files,
            can_upload=can_upload, crumbs=crumbs
        )

    @app.route("/<folder_type>/download/<path:filename>")
    def download_file(folder_type, filename):
        if folder_type not in FOLDER_MAP:
            abort(404)
        base = FOLDER_MAP[folder_type]
        # Security: still ensure it’s a real file under base
        full_path = os.path.join(base, filename)
        if not os.path.isfile(full_path):
            abort(404)

        # Let Flask join base + filename for us:
        return send_from_directory(
            directory=os.path.abspath(base),
            path=filename,
            as_attachment=True
        )

    @app.route("/<folder_type>/delete/<path:filename>", methods=["POST"])
    def delete_file(folder_type, filename):
        if folder_type not in FOLDER_MAP:
            return "Invalid path", 404
        base_folder = FOLDER_MAP[folder_type]
        full_path = os.path.join(base_folder, filename)
        if not os.path.isfile(full_path):
            flash(f"File not found: {filename}", "error")
        else:
            try:
                os.remove(full_path)
                flash(f"Deleted: {filename}", "success")
            except Exception as e:
                flash(f"Error deleting {filename}: {e}", "error")
        # Redirect back to same directory
        parent = os.path.dirname(filename)
        return redirect(url_for('files_index', folder_type=folder_type, subpath=parent))
    
    @app.route("/<folder_type>/batch", methods=["POST"])
    def batch_action(folder_type, subpath=""):
        if folder_type not in FOLDER_MAP:
            abort(404)
        base = FOLDER_MAP[folder_type]
        action = request.form.get("action")
        selected = request.form.getlist("selected_files")  # list of relative paths

        if not selected:
            flash("No files selected.", "error")
            return redirect(url_for('files_index', folder_type=folder_type, subpath=subpath))

        # FULL PATHS
        full_paths = [os.path.join(base, f) for f in selected]

        if action == "delete":
            # only delete if allowed
            for p in full_paths:
                if os.path.isfile(p):
                    try:
                        os.remove(p)
                    except Exception as e:
                        flash(f"Error deleting {os.path.basename(p)}: {e}", "error")
            flash(f"Deleted {len(full_paths)} files.", "success")
            return redirect(url_for('files_index', folder_type=folder_type, subpath=subpath))

        elif action == "download":
            # package into a ZIP in memory
            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for rel in selected:
                    full = os.path.join(base, rel)
                    if os.path.isfile(full):
                        # store with just the filename or full relative path
                        arcname = os.path.basename(rel)
                        zf.write(full, arcname)
            memory_file.seek(0)
            return send_file(
                memory_file,
                download_name=f"{folder_type}_{subpath or 'root'}_selection.zip",
                as_attachment=True
            )

        else:
            flash("Unknown action.", "error")
            return redirect(url_for('files_index', folder_type=folder_type, subpath=subpath))


    @app.route("/<folder_type>/download_all", methods=["GET"])
    def download_all(folder_type, subpath=""):
        if folder_type not in FOLDER_MAP:
            abort(404)
        base = FOLDER_MAP[folder_type]
        current = os.path.join(base, subpath)

        # Gather all files under current directory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(current):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    # arcname = path inside the zip: preserve subfolders
                    arcname = os.path.relpath(full_path, base)
                    zf.write(full_path, arcname)
        memory_file.seek(0)
        return send_file(
            memory_file,
            download_name=f"{folder_type}_{subpath or 'all'}.zip",
            as_attachment=True
        )