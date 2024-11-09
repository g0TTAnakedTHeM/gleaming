from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
from datetime import datetime
from ics import Calendar, Event
import io

app = Flask(__name__)

members = ["Odemar", "Sunrice", "MAGGA"]
availability_data = {}

def find_matching_availability():
    matching_dates = []
    for date, times in availability_data.get(members[0], {}).items():
        for time_range, available in times.items():
            if available and all(
                availability_data.get(member, {}).get(date, {}).get(time_range, False)
                for member in members
            ):
                matching_dates.append((date, time_range))
    return matching_dates

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        member = request.form["member"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        available = request.form.get("available") == "on"
        
        time_range = f"{start_time} - {end_time}"
        
        if member not in availability_data:
            availability_data[member] = {}
        if date not in availability_data[member]:
            availability_data[member][date] = {}
        availability_data[member][date][time_range] = available

        return redirect(url_for("index"))

    matching_availabilities = find_matching_availability()
    
    data = []
    for member, dates in availability_data.items():
        for date, times in dates.items():
            for time_range, available in times.items():
                data.append({"Member": member, "Date": date, "Time Range": time_range, "Available": available})
    df = pd.DataFrame(data)
    
    return render_template("index.html", members=members, df=df, matching_availabilities=matching_availabilities)

@app.route("/download_event/<date>/<time_range>")
def download_event(date, time_range):
    start_time, end_time = time_range.split(" - ")
    event_start = f"{date} {start_time}"
    event_end = f"{date} {end_time}"
    
    # Create a calendar event
    c = Calendar()
    e = Event()
    e.name = "Group Availability Match"
    e.begin = event_start
    e.end = event_end
    c.events.add(e)

    # Create a file in memory to download
    calendar_file = io.StringIO(str(c))
    return send_file(io.BytesIO(calendar_file.getvalue().encode()), as_attachment=True, download_name="group_event.ics", mimetype="text/calendar")

if __name__ == "__main__":
    app.run(debug=True)
