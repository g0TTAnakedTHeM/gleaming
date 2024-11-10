import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Set up the database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://voldeamrq_user:joNKx6hi4PE9MMcuOOgkX2XwELehChft@dpg-csobs5aj1k6c73becccg-a.frankfurt-postgres.render.com/voldeamrq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the database model
class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format YYYY-MM-DD
    start_time = db.Column(db.String(5), nullable=False)  # Format HH:MM
    end_time = db.Column(db.String(5), nullable=False)  # Format HH:MM
    available = db.Column(db.Boolean, default=False)

# Create tables (only needed the first time)
with app.app_context():
    db.create_all()

def get_matching_availabilities():
    # Query the database for all availability records where members are available
    all_availabilities = Availability.query.filter_by(available=True).all()
    
    # Organize by date and time range to find matching slots
    availability_dict = {}
    for availability in all_availabilities:
        key = (availability.date, availability.start_time, availability.end_time)
        if key not in availability_dict:
            availability_dict[key] = set()
        availability_dict[key].add(availability.member)

    # Find dates and time ranges where all members are available
    all_members = {"Odemar", "Sunrice", "MAGGA"}
    matching_availabilities = [
        (date, f"{start_time} - {end_time}")
        for (date, start_time, end_time), members in availability_dict.items()
        if members == all_members
    ]
    
    return matching_availabilities

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

    # Fetch all availability records and matching availability times
    all_availability = Availability.query.all()
    matching_availabilities = get_matching_availabilities()

    # Determine if each meeting is "Upcoming" or "Past"
    current_datetime = datetime.now()
    for entry in all_availability:
        meeting_datetime = datetime.strptime(f"{entry.date} {entry.start_time}", "%Y-%m-%d %H:%M")
        entry.status = "Upcoming" if meeting_datetime >= current_datetime else "Past"

    return render_template("index.html", availability=all_availability, matching_availabilities=matching_availabilities)

if __name__ == "__main__":
    app.run(debug=True)
