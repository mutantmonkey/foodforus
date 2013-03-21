from flask import abort, redirect, request, jsonify

from foodforus import app
from foodforus import db
from foodforus import lib
from foodforus import models

import datetime


def top_restaurants(key, dtstart):
    restaurants = {}
    fooders = models.FoodVote.query.filter(models.FoodVote.vote_key ==
            key).filter(models.FoodVote.time_start >= dtstart).all()

    # tally up restaurant votes
    # we may need to move this out of memory if this gets super-popular
    for fooder in fooders:
        if fooder.restaurant_id in restaurants:
            restaurants[fooder.restaurant_id] += 1
        else:
            restaurants[fooder.restaurant_id] = 1

    # TODO: deal with ties by using weights from database

    sorted_restaurants = sorted(restaurants.items(), key=lambda x: x[1])
    sorted_restaurants.reverse()
    return sorted_restaurants


def top_times(key, dtstart):
    times = {}
    fooders = models.FoodVote.query.filter(models.FoodVote.vote_key ==
            key).filter(models.FoodVote.time_start >= dtstart).all()

    # tally up time votes
    # may need to be moved out of memory, blah blah blah
    for fooder in fooders:
        if fooder.time_start in times:
            times[fooder.time_start] += 1
        else:
            times[fooder.time_start] = 1

    sorted_times = sorted(times.items(), key=lambda x: x[1])
    sorted_times.reverse()
    return sorted_times


@app.route('/')
def index():
    return jsonify({'message': "Hello, yes, this is food for us."})


@app.route('/food/<string:key>')
def foodnow(key):
    dtstart = datetime.datetime.now()
    times = top_times(key, dtstart)

    restaurants = []
    for r in top_restaurants(key, dtstart):
        restaurants.append((models.Restaurant.query.get(r[0]).name, r[1]))

    return jsonify({
        'restaurants': [x for x in restaurants],
        'times': [(x[0].strftime('%H:%M'), x[1]) for x in times],
    })


@app.route('/food/<string:key>/<string:time>')
def foodat(key, time):
    dtstart = datetime.datetime.now()
    parsed = datetime.datetime.strptime(time.strip(), '%H:%M')
    dtstart = dtstart.replace(hour=parsed.hour, minute=parsed.minute, second=0,
            microsecond=0)

    restaurants = []
    for r in top_restaurants(key, dtstart):
        restaurants.append((models.Restaurant.query.get(r[0]).name, r[1]))

    return jsonify({'restaurants': [x for x in restaurants]})


@app.route('/vote', methods=['POST'])
def vote():
    sig = lib.sign_vote(app.config['VOTE_KEY'], request.form)
    if sig != request.form['sig']:
        abort(400)

    rname = request.form['restaurant'].strip().lower()
    restaurant = models.Restaurant.query.filter(models.Restaurant.name == rname).first()
    if not restaurant:
        restaurant = models.Restaurant(rname)
        db.session.add(restaurant)
        db.session.commit()

    dtstart = datetime.datetime.now()
    parsed = datetime.datetime.strptime(request.form['start'].strip(), '%H:%M')
    dtstart = dtstart.replace(hour=parsed.hour, minute=parsed.minute, second=0,
            microsecond=0)

    if 'end' in request.form:
        dtend = datetime.datetime.now()
        parsed = datetime.datetime.strptime(request.form['end'].strip(), '%H:%M')
        dtend = dtend.replace(hour=parsed.hour, minute=parsed.minute, second=0,
                microsecond=0)
    else:
        dtend = None

    # delete any existing votes by the same user
    votes = models.FoodVote.query.filter(models.FoodVote.user == request.form['user'].strip()).all()
    for vote in votes:
        db.session.delete(vote)
        db.session.commit()

    foodvote = models.FoodVote(request.form['key'], request.form['user'].strip(),
            restaurant.id, dtstart, dtend)
    db.session.add(foodvote)
    db.session.commit()

    return jsonify(foodvote.serialize())
