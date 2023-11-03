# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


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
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > query_date).\
    filter(Measurement.prcp > 0).\
    order_by(Measurement.date.desc()).all()
    
    session.close()

    # Create a dictionary from the precipitation analysis results
    query_results = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        query_results.append(precipitation_dict)
    
    return jsonify(query_results)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)    

    # Query all stations
    results = session.query(Station.station).all()

    # Close session
    session.close()

    return jsonify(results)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    active_station_tobs = session.query(Measurement.tobs).\
    filter(Measurement.date > query_date).\
    filter(Measurement.station == "USC00519281").all()

    # Close session
    session.close()

    return jsonify(active_station_tobs)


@app.route("/api/v1.0/<start>")
def temperature_by_start_date(start_date):
    """Fetch the TMIN, TAVG and TMAX for all the dates greater than or equal to the start date."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    proper_date = date.replace("-", "")
    for date in dates:
        search_date = date["start_date"].replace("-", "")
    
        if search_date == proper_date:
            temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()

    # Close session
    session.close()
        
    return jsonify(temps)
    
 
@app.route("/api/v1.0/<start>/<end>")

def temperature_start_end_date(date_range):
    """Fetch the TMIN, TAVG and TMAX for the dates from the start date to the end date, inclusive."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = "2010-01-01"
    end_date = "2010-01-31"

    proper_date = date.replace("-", "")
    for date in dates:
        search_date = date["start_date"].replace("-", "")
    
        if search_date == proper_date:
            temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Close session
    session.close()
        
    return jsonify(temps)
    
    return jsonify({"error": f"data for that date not found. Please use yyyymmdd format"}), 404


if __name__ == '__main__':
    app.run(debug=True)
