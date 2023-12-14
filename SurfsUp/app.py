# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from pathlib import Path

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
 
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date.date, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(days=365)

    # Last 12 months of precipitation
    last_year = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= first_date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    precipitation_dict = {}
    for date, prcp in last_year:
        precipitation_dict[date] = prcp

    # Return a JSON representation
    return jsonify(precipitation_dict)

    session.close()
    
@app.route("/api/v1.0/stations")
def stations():
 
    # Query all stations
    results = session.query(station.station, station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return the JSON representation of your dictionary.
    return jsonify(all_stations)

    session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date.date, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most-active station for the previous year of data.
    temperature = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= first_date).\
    filter(measurement.station == 'USC00519281').\
    order_by(measurement.date).all()

    # Return a JSON list of temperature observations for the previous year.
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    # Return the JSON representation of your dictionary.
    return jsonify(temperature_totals)

    session.close()

@app.route("/api/v1.0/<start>")
def start_date(start):

    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(recent_date.date, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(days=365)

    # Calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= first_date).all()

    # Return the JSON representation of your dictionary.
    return jsonify(stats)

    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Calculate TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    stats_inc = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Return the JSON representation of your dictionary.
    return jsonify(stats_inc)

    session.close()

if __name__ == '__main__':
    app.run(debug=True)
