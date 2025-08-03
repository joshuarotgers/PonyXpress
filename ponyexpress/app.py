"""
Main Flask application for PonyXpress
"""
import os
import csv
from io import StringIO
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps

from database.models import db, User, RouteTrace, MailboxStop, PackageScan


def create_app():
    """Factory pattern for creating the Flask app"""
    app = Flask(__name__, instance_relative_config=True)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    app.config["SECRET_KEY"] = "change-this-secret"  # TODO: change in production
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ponyexpress.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Folder for uploading mailbox photos
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):  # noqa: D401
        """Flask-Login callback to load a user from the DB"""
        return User.query.get(int(user_id))

    # ------------------------------------------------------------------
    # Helper decorators
    # ------------------------------------------------------------------
    def roles_required(*roles):  # noqa: D401
        """Ensure the current user has at least one of the required roles."""

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated or current_user.role not in roles:
                    flash("You do not have permission to access this page.", "danger")
                    return redirect(url_for("index"))
                return f(*args, **kwargs)

            return decorated_function

        return decorator

    # ------------------------------------------------------------------
    # Routes – Authentication
    # ------------------------------------------------------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handle user login."""
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(url_for("index"))
            flash("Invalid credentials", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        """Logout the current user."""
        logout_user()
        flash("Logged out.", "info")
        return redirect(url_for("login"))

    # ------------------------------------------------------------------
    # Routes – General dashboards
    # ------------------------------------------------------------------
    @app.route("/")
    @login_required
    def index():
        """Role-aware landing page."""
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        return render_template("index.html")

    # ------------------------------------------------------------------
    # Routes – Carrier map & scans
    # ------------------------------------------------------------------
    @app.route("/map", methods=["GET", "POST"])
    @login_required
    @roles_required("carrier")
    def map_view():
        """Carrier can draw their daily route and save it."""
        if request.method == "POST":
            geojson = request.json.get("geojson")
            route = RouteTrace(geojson=str(geojson), carrier=current_user)
            db.session.add(route)
            db.session.commit()
            return jsonify({"success": True, "route_id": route.id})
        return render_template("map.html")

    @app.route("/scan/<int:route_id>", methods=["GET", "POST"])
    @login_required
    @roles_required("carrier")
    def scan(route_id):
        """Barcode scanning page for a given route."""
        route = RouteTrace.query.get_or_404(route_id)
        if request.method == "POST":
            data = request.json
            scan = PackageScan(
                route=route,
                barcode=data.get("barcode"),
                too_big=data.get("too_big", False),
                too_small=data.get("too_small", False),
                lat=data.get("lat"),
                lng=data.get("lng"),
            )
            # Automatically add a mailbox stop if the package is delivered to mailbox
            if scan.too_small:
                mailbox = MailboxStop(route=route, lat=scan.lat, lng=scan.lng, label="Auto stop")
                db.session.add(mailbox)
            db.session.add(scan)
            db.session.commit()
            return jsonify({"success": True})
        return render_template("scan.html", route=route)

    @app.route("/route/<int:route_id>")
    @login_required
    @roles_required("substitute", "carrier")
    def view_route(route_id):
        """Substitutes and carriers can view an existing route trace."""
        route = RouteTrace.query.get_or_404(route_id)
        return render_template("map.html", route=route)

    # ------------------------------------------------------------------
    # Routes – Admin dashboard & utilities
    # ------------------------------------------------------------------
    @app.route("/admin")
    @login_required
    @roles_required("admin")
    def admin_dashboard():
        users = User.query.all()
        routes = RouteTrace.query.order_by(RouteTrace.date.desc()).all()
        return render_template("admin_dashboard.html", users=users, routes=routes)

    @app.route("/admin/user/add", methods=["POST"])
    @login_required
    @roles_required("admin")
    def add_user():
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("User added.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/user/delete/<int:user_id>")
    @login_required
    @roles_required("admin")
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "info")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/export/csv")
    @login_required
    @roles_required("admin")
    def export_csv():
        """Generate a CSV of all scans for download."""
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["Date", "Carrier", "Barcode", "TooBig", "TooSmall", "Lat", "Lng", "Timestamp"])
        scans = PackageScan.query.order_by(PackageScan.timestamp.desc()).all()
        for scan in scans:
            cw.writerow([
                scan.route.date,
                scan.route.carrier.username,
                scan.barcode,
                scan.too_big,
                scan.too_small,
                scan.lat,
                scan.lng,
                scan.timestamp,
            ])
        output = si.getvalue()
        return send_file(
            StringIO(output),
            mimetype="text/csv",
            as_attachment=True,
            download_name="scans.csv",
        )

    # ------------------------------------------------------------------
    # CLI helper – initialise DB
    # ------------------------------------------------------------------
    @app.cli.command("init-db")
    def init_db():  # noqa: D401
        """Create all tables and a default admin user."""
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", role="admin")
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
        print("✅ Database initialised with default admin (admin/admin)")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)