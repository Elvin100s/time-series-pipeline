"""
Flask REST API for the Tétouan Power Consumption pipeline.

Exposes 12 endpoints (6 per database, mirrored between MySQL and MongoDB):
    CRUD:        POST / GET / PUT / DELETE on /api/{sql|mongo}/readings[/<timestamp>]
    Time-series: /latest and /range?start=...&end=...

Credentials are read from environment variables:
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MONGO_URI

Run:  python app.py    (listens on http://127.0.0.1:5000)
"""

from flask import Flask, request, jsonify
import mysql.connector
from pymongo import MongoClient
import os

app = Flask(__name__)

MYSQL_CONFIG = {
    "host":     os.environ["MYSQL_HOST"],
    "user":     os.environ["MYSQL_USER"],
    "password": os.environ["MYSQL_PASSWORD"],
    "database": os.environ["MYSQL_DATABASE"],
    "connection_timeout": 10,
}
MONGO_URI = os.environ["MONGO_URI"]


def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
mongo_coll = mongo_client["tetouan_power"]["readings"]


@app.route("/api/sql/readings", methods=["POST"])
def sql_create():
    d = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO weather_readings "
        "(timestamp, temperature, humidity, wind_speed, general_diffuse, diffuse_flows) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (d["timestamp"], d["temperature"], d["humidity"], d["wind_speed"],
         d.get("general_diffuse", 0), d.get("diffuse_flows", 0)),
    )
    for z in [1, 2, 3]:
        c.execute(
            "INSERT INTO power_consumption (zone_id, timestamp, consumption) "
            "VALUES (%s, %s, %s)",
            (z, d["timestamp"], d.get("zone{}".format(z), 0)),
        )
    conn.commit()
    conn.close()
    return jsonify({"message": "created", "timestamp": d["timestamp"]}), 201


@app.route("/api/sql/readings/latest", methods=["GET"])
def sql_latest():
    try:
        conn = get_db()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM weather_readings ORDER BY timestamp DESC LIMIT 1")
        w = c.fetchone()
        if not w:
            conn.close()
            return jsonify({"error": "empty"}), 404
        c.execute(
            "SELECT zone_id, consumption FROM power_consumption WHERE timestamp=%s",
            (w["timestamp"],),
        )
        zones = c.fetchall()
        conn.close()
        return jsonify({
            "timestamp":       str(w["timestamp"]),
            "temperature":     w["temperature"],
            "humidity":        w["humidity"],
            "wind_speed":      w["wind_speed"],
            "general_diffuse": w["general_diffuse"],
            "diffuse_flows":   w["diffuse_flows"],
            "zones": {"zone{}".format(r["zone_id"]): r["consumption"] for r in zones},
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sql/readings/range", methods=["GET"])
def sql_range():
    s = request.args.get("start")
    e = request.args.get("end")
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute(
        "SELECT * FROM weather_readings WHERE timestamp BETWEEN %s AND %s ORDER BY timestamp",
        (s, e),
    )
    ws = c.fetchall()
    out = []
    for w in ws:
        c.execute(
            "SELECT zone_id, consumption FROM power_consumption WHERE timestamp=%s",
            (w["timestamp"],),
        )
        zones = c.fetchall()
        out.append({
            "timestamp":       str(w["timestamp"]),
            "temperature":     w["temperature"],
            "humidity":        w["humidity"],
            "wind_speed":      w["wind_speed"],
            "general_diffuse": w["general_diffuse"],
            "diffuse_flows":   w["diffuse_flows"],
            "zones": {"zone{}".format(r["zone_id"]): r["consumption"] for r in zones},
        })
    conn.close()
    return jsonify({"count": len(out), "data": out})


@app.route("/api/sql/readings/<path:ts>", methods=["GET"])
def sql_read(ts):
    conn = get_db()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM weather_readings WHERE timestamp=%s", (ts,))
    w = c.fetchone()
    if not w:
        conn.close()
        return jsonify({"error": "not found"}), 404
    c.execute(
        "SELECT zone_id, consumption FROM power_consumption WHERE timestamp=%s",
        (ts,),
    )
    zones = c.fetchall()
    conn.close()
    return jsonify({
        "timestamp":       str(w["timestamp"]),
        "temperature":     w["temperature"],
        "humidity":        w["humidity"],
        "wind_speed":      w["wind_speed"],
        "general_diffuse": w["general_diffuse"],
        "diffuse_flows":   w["diffuse_flows"],
        "zones": {"zone{}".format(r["zone_id"]): r["consumption"] for r in zones},
    })


@app.route("/api/sql/readings/<path:ts>", methods=["PUT"])
def sql_update(ts):
    d = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE weather_readings SET temperature=%s, humidity=%s, wind_speed=%s "
        "WHERE timestamp=%s",
        (d.get("temperature"), d.get("humidity"), d.get("wind_speed"), ts),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "updated", "timestamp": ts})


@app.route("/api/sql/readings/<path:ts>", methods=["DELETE"])
def sql_delete(ts):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM weather_readings WHERE timestamp=%s", (ts,))
    c.execute("DELETE FROM power_consumption WHERE timestamp=%s", (ts,))
    conn.commit()
    conn.close()
    return jsonify({"message": "deleted", "timestamp": ts})


@app.route("/api/mongo/readings", methods=["POST"])
def mongo_create():
    d = request.json
    doc = {
        "timestamp": d["timestamp"],
        "weather": {
            "temperature":     d["temperature"],
            "humidity":        d["humidity"],
            "wind_speed":      d["wind_speed"],
            "general_diffuse": d.get("general_diffuse", 0),
            "diffuse_flows":   d.get("diffuse_flows", 0),
        },
        "consumption": {
            "zone1": d.get("zone1", 0),
            "zone2": d.get("zone2", 0),
            "zone3": d.get("zone3", 0),
            "total": d.get("zone1", 0) + d.get("zone2", 0) + d.get("zone3", 0),
        },
    }
    mongo_coll.insert_one(doc)
    return jsonify({"message": "created", "timestamp": d["timestamp"]}), 201


@app.route("/api/mongo/readings/latest", methods=["GET"])
def mongo_latest():
    doc = mongo_coll.find_one(sort=[("timestamp", -1)], projection={"_id": 0})
    if not doc:
        return jsonify({"error": "empty"}), 404
    return jsonify(doc)


@app.route("/api/mongo/readings/range", methods=["GET"])
def mongo_range():
    s = request.args.get("start")
    e = request.args.get("end")
    docs = list(mongo_coll.find(
        {"timestamp": {"$gte": s, "$lte": e}},
        {"_id": 0},
    ).sort("timestamp", 1))
    return jsonify({"count": len(docs), "data": docs})


@app.route("/api/mongo/readings/<path:ts>", methods=["GET"])
def mongo_read(ts):
    doc = mongo_coll.find_one({"timestamp": ts}, {"_id": 0})
    if not doc:
        return jsonify({"error": "not found"}), 404
    return jsonify(doc)


@app.route("/api/mongo/readings/<path:ts>", methods=["PUT"])
def mongo_update(ts):
    data = request.json
    updates = {}
    if "temperature" in data:
        updates["weather.temperature"] = data["temperature"]
    if "humidity" in data:
        updates["weather.humidity"] = data["humidity"]
    result = mongo_coll.update_one({"timestamp": ts}, {"$set": updates})
    if result.matched_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "updated"})


@app.route("/api/mongo/readings/<path:ts>", methods=["DELETE"])
def mongo_delete(ts):
    mongo_coll.delete_one({"timestamp": ts})
    return jsonify({"message": "deleted"})


if __name__ == "__main__":
    app.run(port=5000)
