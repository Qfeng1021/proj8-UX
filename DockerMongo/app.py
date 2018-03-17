import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times # Brevet time calculations
import config
import time
import logging
import datetime
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

client = MongoClient("db", 27017)
db = client.tododb
db.tododb.drop()


'''@app.route('/')
def todo():
    _items = db.tododb.find()
    items = [item for item in _items]

    return render_template('todo.html', items=items)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)

    return redirect(url_for('todo'))'''


@app.route('/submit', methods = ['POST'])
def submit():
    km_list, open_list, close_list = [],[],[]
    db.tododb.remove({"open" : {"$exists" : True}})
    km_request = request.form.getlist('km')
    open_request = request.form.getlist('open')
    close_request = request.form.getlist('close')
    for i in range(len(open_request)):
        if open_request[i] != "" and open_request[i] != "Wrong input":
            km_list.append(km_request[i])
            open_list.append(open_request[i])
            close_list.append(close_request[i])
    for i in range(len(open_list)):
        item_doc = {
            "km" : km_list[i],
            "open" : open_list[i],
            "close" : close_list[i]
        }
        db.tododb.insert_one(item_doc)
    return redirect(url_for("index"))

@app.route('/display', methods = ['POST'])
def display():
    item_list = []
    item = db.tododb.find({"open": {'$exists' : True}})
    for i in item:
        item_list.append(i)
    if len(item_list) == 0:
        return render_template("none.html")
    return render_template("todo.html", item = item_list)

###
# Globals
###
# app = flask.Flask(__name__)
# CONFIG = config.configuration()
# app.secret_key = CONFIG.SECRET_KEY

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    distance = request.args.get("distance", type = int)
    begin_time = request.args.get("begin_time", type = str)
    begin_date = request.args.get("begin_date", type = str)
    brevet_start_time = begin_date + " " + begin_time
    km = request.args.get('km', 999, type=float)

    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    # FIXME: These probably aren't the right open and close times
    # and brevets may be longer than 200km
    open_time = acp_times.open_time(km, distance, brevet_start_time)
    close_time = acp_times.close_time(km, distance, brevet_start_time)
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")


'''if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)'''
