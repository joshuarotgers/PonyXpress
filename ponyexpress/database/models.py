"""Database models for PonyXpress"""
from datetime import datetime, date

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy instance (initialised in app factory)
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Application user with role-based access (carrier, substitute, admin)."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class RouteTrace(db.Model):
    """Daily route drawn by a carrier and stored as GeoJSON."""

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    carrier_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    geojson = db.Column(db.Text)  # Route polyline as GeoJSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back-refs
    carrier = db.relationship("User", backref="routes")


class MailboxStop(db.Model):
    """GPS point for a mailbox stop, optionally with photo attachment."""

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route_trace.id"))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    label = db.Column(db.String(120))
    photo = db.Column(db.String(150))

    route = db.relationship("RouteTrace", backref="mailboxes")


class PackageScan(db.Model):
    """A single barcode scan event during delivery."""

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route_trace.id"))
    barcode = db.Column(db.String(120))

    # Delivery options
    too_big = db.Column(db.Boolean, default=False)
    too_small = db.Column(db.Boolean, default=False)

    # Geo-tagging
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional photo
    photo = db.Column(db.String(150))

    route = db.relationship("RouteTrace", backref="scans")