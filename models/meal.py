from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .booking import Booking 

db = SQLAlchemy()

class Meal(Booking):
    id = db.Column(db.Integer, db.ForeignKey('booking.id'), primary_key=True)
    meal_requested = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'meal',
    }

    def __repr__(self):
        return f'<Meal {self.id}, Requested: {self.meal_requested}>'