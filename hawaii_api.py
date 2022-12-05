# 1. import Flask

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

hawaii_measurements = Base.classes.measurement
hawaii_stations = Base.classes.station

# Create app
app = Flask(__name__)

###############

@app.route("/")

def welcome():
        """List all the available routes"""
        return (
            f"<b>Available Routes:</b><br/>"
            f"Precipitation: <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
            f"Stations: <a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
            f"1-Year Temp Observations: <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
            f"<b>   For temp stats, replace yyyy-mm-dd in URL to return results</b><br/>"
            f"Temperature stat between 2010-01-01 and 2017-08-23 for dates greater than or equal to (yyyy-mm-dd): <a href='/api/v1.0/yyyy-mm-dd'>/api/v1.0/yyyy-mm-dd</a><br/>"
            f"Temperature stat between 2010-01-01 and 2017-08-23 for range of dates  (yyyy-mm-dd): <a href='/api/v1.0/yyyy-mm-dd/yyyy-mm-dd'>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</a><br/>"
            
        )

#####################################

@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)
        sel = [hawaii_measurements.date, hawaii_measurements.prcp]
        prcp_query = session.query(*sel).all()
        session.close()
#looping through query to build dictionary with renamed columns and assigning appending a list 
        precipitation = []
        for date, prcp in prcp_query:
            prcp_dict = {}
            prcp_dict["Date"] = date
            prcp_dict["Precipitation"] = prcp
            precipitation.append(prcp_dict)

        return jsonify(precipitation)

################################

@app.route("/api/v1.0/stations")

def stations():
        session = Session(engine)
        sel = [hawaii_stations.station, hawaii_stations.name]
        station_query = session.query(*sel).all()
        session.close()

        station_list = []
        for station, name in station_query:
            station_dict = {}
            station_dict["Station"] = station
            station_dict["Name"] = name
            station_list.append(station_dict)

        return jsonify(station_list)

############################

@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most-active station for the previous year of data.
def tobs():
    session = Session(engine)
    end_date = session.query(hawaii_measurements.date).order_by(hawaii_measurements.date.desc()).first()[0]
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    start_date = dt.date(end_date.year -1, end_date.month, end_date.day)
    sel = [hawaii_measurements.date,hawaii_measurements.tobs]
    date_range = session.query(*sel).filter(hawaii_measurements.date >= start_date).all()
    session.close()

    temp_obs = []
    for date, tobs in date_range:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temp_Observed"] = tobs
        temp_obs.append(tobs_dict)

    return jsonify(temp_obs)

##############################

@app.route("/api/v1.0/<start>")
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

def start_tobs(start):
    session = Session(engine)
    start_tobs_query = session.query(func.min(hawaii_measurements.tobs), func.avg(hawaii_measurements.tobs), func.max(hawaii_measurements.tobs)).\
        filter(hawaii_measurements.date >= start).all()
    session.close()

    start_tobs_summary = []
    for min, avg, max in start_tobs_query:
        start_tobs_dict = {}
        start_tobs_dict["Min"] = min
        start_tobs_dict["Average"] = avg
        start_tobs_dict["Max"] = max
        start_tobs_summary.append(start_tobs_dict)

    return jsonify(start_tobs_summary)

#####################################

@app.route("/api/v1.0/<start>/<end>")
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
def range_tobs(start, end):
    session = Session(engine)
    range_tobs_query = session.query(func.min(hawaii_measurements.tobs), func.avg(hawaii_measurements.tobs), func.max(hawaii_measurements.tobs)).\
        filter(hawaii_measurements.date >= start).filter(hawaii_measurements.date <= end).all()
    session.close()

    range_tobs_summary = []
    for min, avg, max in range_tobs_query:
        range_tobs_dict = {}
        range_tobs_dict["Min"] = min
        range_tobs_dict["Average"] = avg
        range_tobs_dict["Max"] = max
        range_tobs_summary.append(range_tobs_dict)

    return jsonify(range_tobs_summary)

#########################

if __name__ == "__main__":
    app.run(debug=True)