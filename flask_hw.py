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
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start_date/end_date")


# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
    max_date, = session.query(func.max(Measurement.date)).all()
    one_yr_date = pd.to_datetime(max_date[0]) - dt.timedelta(days=366)
                                                         
    last_12_months_prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(func.strftime(Measurement.date) >= str(one_yr_date)).\
    order_by(Measurement.date.asc()).all()

    return jsonify(last_12_months_prcp)

# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def station_list():
    stations = session.query(Station.station).all()
    return jsonify(stations)

# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route('/api/v1.0/tobs')
def last_years_temps():
    max_date_2, = session.query(func.max(Measurement.date)).all()
    one_yr_date_2 = pd.to_datetime(max_date_2[0]) - dt.timedelta(days=366)
    last_12_temp = session.query(Measurement.tobs).\
                filter(Measurement.station == 'USC00519281', func.strftime(Measurement.date) >= str(one_yr_date_2)).all()
    return jsonify(last_12_temp)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start_date>/<end_date>')
def calc_temps(start_date, end_date):
    calcs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    return jsonify(calcs)

if __name__ == "__main__":
    app.run(debug=True)