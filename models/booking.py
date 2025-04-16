from bson import ObjectId
from datetime import datetime
from db.connection import get_db

class Booking:
    def __init__(self, user_id, booking_date=None, _id=None, type='booking'):
        self._id = _id if _id else ObjectId()
        self.user_id = user_id
        self.booking_date = booking_date if booking_date else datetime.utcnow()
        self.type = type
        self.collection = get_db().get_client().tummyfull.bookings

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data['user_id'],
            booking_date=data.get('booking_date'),
            _id=data.get('_id'),
            type=data.get('type', 'booking')
        )

    def to_dict(self):
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'booking_date': self.booking_date,
            'type': self.type
        }

    def save(self):
        self.collection.insert_one(self.to_dict())

    @classmethod
    def find_by_id(cls, id):
        data = get_db().get_client().tummyfull.bookings.find_one({'_id': ObjectId(id)})
        return cls.from_dict(data) if data else None

    @classmethod
    def find_by_user_id(cls, user_id):
        cursor = get_db().get_client().tummyfull.bookings.find({'user_id': user_id})
        return [cls.from_dict(data) for data in cursor]

    def __repr__(self):
        return f'<Booking {self._id}>'