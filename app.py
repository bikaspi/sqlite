import datetime as dt
import numpy as np
import pandas as pd
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine('sqlite:///hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# map measurement class
Measurement = Base.classes.measurement
# map station class
Station = Base.classes.station

# create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def climate():
    '''List all available api routes.'''
    return(
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start<br/>'
        f'/api/v1.0/start/end<br/>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    '''Query for the dates and prcp from the last year'''
    prev = dt.date.today() - dt.timedelta(days=365)
    query = session.query(Measurement.date,func.sum(Measurement.prcp)).filter(Measurement.date >= prev).group_by(Measurement.date).order_by(Measurement.date).all()
    
    '''convert the query results to a Dictionary using date as the key and prcp as the value'''
    results_list = []
    for measurement in query:
        results_dict = {}
        results_dict['date'] = measurement[0]
        results_dict['prcp'] = measurement[1]
        results_list.append(results_dict)
    '''return the json representation of your dictionary'''
    return jsonify(results_list)

@app.route('/api/v1.0/stations')
def stations():
    '''Return a json list of stations from the dataset'''
    stations = session.query(Station.station).all()
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    '''Return a json list of Temperature Observations (tobs) for the previous year'''
    prev = dt.date.today() - dt.timedelta(days=365)
    query_tobs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= prev).group_by(Measurement.date).order_by(Measurement.date).all()
    tobs_list = []
    for temp in query_tobs:
        tobs_dict = {}
        tobs_dict['date'] = temp[0]
        tobs_dict['tobs'] = temp[1]
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

  

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)