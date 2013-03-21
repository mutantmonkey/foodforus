from flask import abort, redirect, request, jsonify

from foodforus import app
from foodforus import db
from foodforus import models

import datetime


def top4_restaurants(key, dtstart):
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

    sorted_restaurants = sorted(restaurants.items(), key=lambda x: x[1])
    sorted_restaurants.reverse()
    # TODO: weight restaurants if there is a tie
    return sorted_restaurants[:4]


@app.route('/foodnow')
def foodnow():
    # TODO: figure out where to eat
    # TODO: divide up into 15 minute windows
    pass


@app.route('/food/<string:key>/<string:time>')
def foodat(key, time):
    dtstart = datetime.datetime.now()
    parsed = datetime.datetime.strptime(time.strip(), '%H:%M')
    dtstart = dtstart.replace(hour=parsed.hour, minute=parsed.minute, second=0,
            microsecond=0)
    restaurants = top4_restaurants(key, dtstart)
    print(restaurants)

    return jsonify({'restaurants': [x for x in restaurants]})

    #return jsonify({'resturants': [x.serialize() for x in
    #    models.Restaurant.query.get(restaurants[0][0])]})


@app.route('/vote', methods=['POST'])
def vote():
    rname = request.form['restaurant'].strip().lower()
    restaurant = models.Restaurant.query.filter(models.Restaurant.name == rname).first()
    if not restaurant:
        restaurant = models.Restaurant(rname)
        db.session.add(restaurant)
        db.session.commit()

    # TODO: check request signature
    # TODO: check for duplicate votes (update old one?)

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

    foodvote = models.FoodVote(request.form['key'], request.form['user'],
            restaurant.id, dtstart, dtend)
    db.session.add(foodvote)
    db.session.commit()

    return jsonify(foodvote.serialize())

