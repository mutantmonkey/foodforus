from foodforus import db
import datetime


class Restaurant(db.Model):
    __tablename__ = "restaurants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    sunday_weight = db.Column(db.Integer, default=0, nullable=False)
    monday_weight = db.Column(db.Integer, default=0, nullable=False)
    tuesday_weight = db.Column(db.Integer, default=0, nullable=False)
    wednesday_weight = db.Column(db.Integer, default=0, nullable=False)
    thursday_weight = db.Column(db.Integer, default=0, nullable=False)
    friday_weight = db.Column(db.Integer, default=0, nullable=False)
    saturday_weight = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, name):
        self.name = name

    def serialize(self):
        return {
            'name': self.name,
        }

    def __repr__(self):
        return '<Restuarant: {0}>'.format(self.name)


class FoodVote(db.Model):
    __tablename__ = "food_votes"
    id = db.Column(db.Integer, primary_key=True)
    vote_key = db.Column(db.String)
    user = db.Column(db.Unicode)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    restaurant = db.relationship('Restaurant',
            backref=db.backref('restaurant', lazy='dynamic'))
    time_start = db.Column(db.DateTime, nullable=False)
    time_end = db.Column(db.DateTime)

    def __init__(self, vote_key, user, restaurant_id, time_start, time_end):
        self.vote_key = vote_key
        self.user = user
        self.restaurant_id = restaurant_id
        self.time_start = time_start
        self.time_end = time_end

    def serialize(self):
        return {
            'key': self.vote_key,
            'user': self.user,
            'datetime': str(self.datetime),
            'restaurant_id': self.restaurant_id,
            'start': str(self.time_start),
            'end': str(self.time_end),
        }

    def __repr__(self):
        return '<FoodVote: {0}>'.format(self.user)
