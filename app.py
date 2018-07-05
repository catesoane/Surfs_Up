# Import Dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Set up Database
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create references to Measurements and Station tables
Measurements = Base.classes.measurements
Station = Base.classes.station

session = Session(engine)

# Setup Flask
app = Flask(__name__)

# Setup Flask Routes
@app.route("/")
def homepage():
    return(
        f"Available Routes:<br/>"
        f"(Note: Most recent available date is 2017-08-23 while the latest is 2010-01-01.<br\>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Query dates and temperatures from last year.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- Returns a json list of stations.<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Returns a list of Temperature Observations(tobs) for previous year.<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"- Returns an Average, Max, and Min temperature for given date.<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"- Returns an Average, Max, and Min temperature for a given period.<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()

    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)
    
    return jsonify(rain_totals)

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)
    return jsonify(temperature_totals)

@app.route("/api/v1.0/<start>")
def trip1(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = (start_date - last_year) 
    end = dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start). filter(Measurements.date <= end). all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end = end_date - last_year
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


if __name__ == "__main__":
    app.run(debug=True)