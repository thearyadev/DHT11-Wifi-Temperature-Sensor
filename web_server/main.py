from flask import Flask, render_template, request, Response
import json
import os
from datetime import datetime
import sqlite3
from database import SingleDatabase
import threading

lock = threading.Lock()  # to prevent recursive access error with sql database.

app = Flask(__name__, static_folder='static', static_url_path='')
databases = list()  # list of all the available databases
for f in os.listdir("./data/"):  # load the databases
    databases.append(SingleDatabase(dbname=f, path=f"./data/{f}", tlock=lock))  # pass thread lock in


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/latest/<room>")
def latest(room):
    """
    gets the most recent entry in the selected database
    :param room:
    :return:
    """
    for database in databases:  # search through databases
        if database.name == room:  # check for matching name
            return database.latest()  # get the latest entry for that database and return


@app.route("/24hours/<room>")
def last_24_hours(room):
    for database in databases:  # look for db
        if database.name == room:  # check for matching name
            dataRaw = database.full()  # get the raw data for the last 24 hours of entries.
            bucketed = {}  # holds the data bucketed by hour.
            for entry in dataRaw:  # iter all entries
                if datetime.fromtimestamp(entry["timestamp"]).hour in bucketed:
                    bucketed[datetime.fromtimestamp(entry["timestamp"]).hour]["temperature"].append(
                        # create a key with the hour of the entry and append that entry to the list
                        entry["temperature"])
                    bucketed[datetime.fromtimestamp(entry["timestamp"]).hour]["humidity"].append(
                        # create a key with the hour of the entry and append that entry to the list
                        entry["humidity"])
                else:
                    bucketed[datetime.fromtimestamp(entry["timestamp"]).hour] = {
                        # if the hour doesnt exist, init that dictionary with a list including the current data
                        "temperature": [entry['temperature'], ],
                        "humidity": [entry['humidity'], ]
                    }

            return {"timestamps": list(bucketed.keys()),  # return the data
                    "temperature": [sum(v['temperature']) / len(v['temperature']) for k, v in bucketed.items()],
                    "humidity": [sum(v['humidity']) / len(v['humidity']) for k, v in bucketed.items()]}


@app.route("/save", methods=["POST"])
def save_data():
    """
    endpoint to save data to a database.
    :return:
    """
    receivedData = json.loads(request.data)  # get the data
    for database in databases:  # find the database trying to be accessed
        if database.name == receivedData["room"]:  # if the database exists,
            # add to db
            database.write(receivedData)
            return Response("Data saved", status=200)  # send successful response
    # if the database is not found
    newDB = SingleDatabase(dbname=receivedData["room"], path=f"./data/{receivedData['room']}",
                           tlock=lock)  # if the DB does not exist, create one.
    databases.append(newDB)  # add to list of databases
    newDB.write(receivedData)  # write the new data

    return Response("Data saved", status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
