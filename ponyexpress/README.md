# PonyXpress 🚚

PonyXpress is a Progressive Web App built with **Flask**, **SQLite**, and **Flask-Login** to manage rural delivery routes and package scans.

## Features

* Role-based authentication (Carrier, Substitute, Admin)
* Interactive map (Leaflet + Leaflet-Draw) for drawing daily routes
* Live barcode scanning (QuaggaJS)
* Offline support via service worker & manifest
* Photo attachments for mailbox stops
* Admin dashboard – manage users & export scans to CSV

## Setup

1. **Clone & enter project**

```bash
git clone <repo-url>
cd ponyexpress
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
```

4. **Initialise the database**

```bash
flask --app app.py init-db
```

5. **Run the development server**

```bash
flask --app app.py run
```

The server will start at http://127.0.0.1:5000/.

> Default admin credentials: **admin / admin**

## Deployment

Set `SECRET_KEY` and use a production server like Gunicorn behind a reverse proxy. Configure HTTPS for PWA installability.

## License

MIT