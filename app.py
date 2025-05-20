import os
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://voldeamrq_user:frankfurt-postgres.render.com/voldeamrq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the database model
class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)  
    start_time = db.Column(db.String(5), nullable=False)  
    end_time = db.Column(db.String(5), nullable=False)  
    available = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()

def get_matching_availabilities():

    all_availabilities = Availability.query.filter_by(available=True).all()
    

    availability_dict = {}
    for availability in all_availabilities:
        key = (availability.date, availability.start_time, availability.end_time)
        if key not in availability_dict:
            availability_dict[key] = set()
        availability_dict[key].add(availability.member)

  
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
     
        member = request.form["member"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        available = request.form.get("available") == "on"

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


    all_availability = Availability.query.all()
    matching_availabilities = get_matching_availabilities()

    current_datetime = datetime.now()
    for entry in all_availability:
        meeting_datetime = datetime.strptime(f"{entry.date} {entry.start_time}", "%Y-%m-%d %H:%M")
        entry.status = "Upcoming" if meeting_datetime >= current_datetime else "Past"

    return render_template("index.html", availability=all_availability, matching_availabilities=matching_availabilities)

@app.route("/download_event")
def download_event():

    date = request.args.get("date")
    time_range = request.args.get("time_range")
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{date}T{time_range.split(' - ')[0].replace(':', '')}00Z
DTEND:{date}T{time_range.split(' - ')[1].replace(':', '')}00Z
SUMMARY:Group Meeting
END:VEVENT
END:VCALENDAR"""
    response = make_response(ics_content)
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response

if __name__ == "__main__":
    app.run(debug=True)
