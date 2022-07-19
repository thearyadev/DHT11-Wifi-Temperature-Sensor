import sqlite3
import datetime
import os
import threading


class SingleDatabase:
    def __init__(self, dbname, path, tlock):
        self.path = path
        self.name = dbname
        self.tlock = tlock

        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS TemperatureLog (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, temperature INTEGER, humidity INTEGER)")
        self.connection.commit()

    def write(self, data: dict):
        try:
            self.tlock.acquire()
            self.cursor.execute(f"INSERT INTO TemperatureLog (timestamp, temperature, humidity)"
                                f" values ({datetime.datetime.now().timestamp()}, {data['temperature']}, {data['humidity']})")
            self.connection.commit()
        finally:
            self.tlock.release()

    def latest(self):
        try:
            self.tlock.acquire()
            self.cursor.execute("SELECT * FROM TemperatureLog ORDER BY id DESC LIMIT 1")
            if d := self.cursor.fetchone():
                return dict(d)
            return d
        finally:
            self.tlock.release()

    def full(self):
        try:
            self.tlock.acquire()
            self.cursor.execute("SELECT * FROM TemperatureLog")
            current = datetime.datetime.now()

            output = list()
            for entry in self.cursor.fetchall():
                entry_time = datetime.datetime.fromtimestamp(entry["timestamp"])
                if (current - entry_time) <= datetime.timedelta(hours=24):
                    output.append(dict(entry))
            return output
        finally:
            self.tlock.release()

    def __str__(self):
        return f"SingleDatabase(name={self.name}, path={self.path})"


if __name__ == "__main__":
    db = SingleDatabase("TESTROOM", "./data/TESTROOM")
    db.write({"temperature": 21, "humidity": 56})
    # for s in db.full():
    #     print(s['timestamp'], s['temperature'])
