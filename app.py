from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure PostgreSQL connection (replace with your actual credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://voldemarq:9996@localhost/voldemarq'  # Adjust as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the database model
class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format YYYY-MM-DD
    start_time = db.Column(db.String(5), nullable=False)  # Format HH:MM
    end_time = db.Column(db.String(5), nullable=False)  # Format HH:MM
    available = db.Column(db.Boolean, default=False)

# Create tables (only needs to be run once)
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve form data
        member = request.form["member"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        available = request.form.get("available") == "on"

        # Save data to the database
        new_availability = Availability(
            member=member,
            date=date,
            start_time=start_time,
            end_time=end_time,
            available=available
        )
        db.session.add(new_availability)
        db.session.commit()

        return redirect(url_for("index"))

    # Fetch all availability records
    all_availability = Availability.query.all()

    # Determine if each meeting is "Upcoming" or "Past"
    current_datetime = datetime.now()
    for entry in all_availability:
        meeting_datetime = datetime.strptime(f"{entry.date} {entry.start_time}", "%Y-%m-%d %H:%M")
        entry.status = "Upcoming" if meeting_datetime >= current_datetime else "Past"

    return render_template("index.html", availability=all_availability)

if __name__ == "__main__":
    app.run(debug=True)
