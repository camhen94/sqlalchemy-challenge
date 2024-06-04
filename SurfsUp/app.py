import numpy as np
import pandas as pd
import datetime as dt
import re
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify

# Initialize the database engine
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect the existing database
Base = automap_base()
Base.prepare(autoload_with=engine)

# Map tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create a session
session = Session(engine)

# Initialize Flask application
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    return (
        "Welcome to the Hawaii Climate API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date.desc()).all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in precip_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    station_list = []
    for station, name, latitude, longitude, elevation in station_data:
        station_dict = {
            "Station": station,
            "Name": name,
            "Latitude": latitude,
            "Longitude": longitude,
            "Elevation": elevation
        }
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature_observations():
    session = Session(engine)
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()
    session.close()

    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in temp_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date_temps(start):
    session = Session(engine)
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    temp_list = [{
        "Minimum Temperature": min_temp,
        "Average Temperature": avg_temp,
        "Maximum Temperature": max_temp
    } for min_temp, avg_temp, max_temp in temp_data]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date_temps(start, end):
    session = Session(engine)
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_list = [{
        "Minimum Temperature": min_temp,
        "Average Temperature": avg_temp,
        "Maximum Temperature": max_temp
    } for min_temp, avg_temp, max_temp in temp_data]

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)

