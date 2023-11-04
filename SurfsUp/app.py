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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
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

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    active_station_tobs = session.query(Measurement.tobs).\
    filter(Measurement.date > query_date).\
    filter(Measurement.station == "USC00519281").all()

    # Close session
    session.close()

    # Unravel results into a 1D array and convert to a list
    tobs = list(np.ravel(active_station_tobs))
    return jsonify(tobs=tobs)


@app.route("/api/v1.0/<start>")
def temperature_by_start_date(start):
    """Fetch the TMIN, TAVG and TMAX for all the dates greater than or equal to the start date."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start = dt.datetime.strptime(start, "%m%d%Y")
    results = session.query(*sel).\
        filter(Measurement.date >= start).all()

    # Close session
    session.close()

    temps = list(np.ravel(results))
    
    return jsonify(temps)
    
    
@app.route("/api/v1.0/<start>/<end>")

def temperature_date_range(start, end):
    """Fetch the TMIN, TAVG and TMAX for the dates from the start date to the end date, inclusive."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    results = session.query(*sel).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Close session
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)
    
    
if __name__ == '__main__':
    app.run(debug=True)
