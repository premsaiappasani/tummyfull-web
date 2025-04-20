from bson import ObjectId
from datetime import datetime
from db.connection import get_db

class Meal:
    def __init__(self, user_id, meal_redeemed, booking_date=None, _id=None):
        self._id = _id if _id else ObjectId()
        self.user_id = user_id
        self.booking_date = booking_date if booking_date else datetime.utcnow()
        self.type = 'meal'
        self.meal_redeemed = meal_redeemed
        self.collection = get_db().get_client().tummyfull.meals

    @classmethod
    def _get_collection(cls):
         db = get_db()
         return db.get_client().tummyfull.meals

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            user_id=data.get('user_id'),
            booking_date=data.get('booking_date'),
            type=data.get('type', 'meal'),
            meal_redeemed=data.get('meal_redeemed', False)
        )

    def to_dict(self):
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'booking_date': self.booking_date,
            'type': self.type,
            'meal_redeemed': self.meal_redeemed
        }
    
    @classmethod
    def has_redeemed_today(cls, user_id):
        collection = cls._get_collection()
        today = datetime.date.today()
        try:
            user_id_obj = ObjectId(user_id) if isinstance(user_id, str) else user_id
        except Exception:
             print(f"Warning: Invalid user_id format for has_redeemed_today: {user_id}")
             return False

        redeemed_entry = collection.find_one({
            'user_id': user_id_obj,
            'booking_date': {
                '$gte': datetime.datetime.combine(today, datetime.time.min),
                '$lt': datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time.min)
            },
            'meal_redeemed': True
        })
        return redeemed_entry is not None
    
    @classmethod
    def create_redemption_entry(cls, user_id):
        collection = cls._get_collection()
        try:
            user_id_obj = ObjectId(user_id) if isinstance(user_id, str) else user_id
        except Exception:
             print(f"Error: Invalid user_id format for create_redemption_entry: {user_id}")
             return None

        redemption_data = {
            'user_id': user_id_obj,
            'booking_date': datetime.datetime.now(),
            'meal_redeemed': True,
            'type': 'meal'
        }
        result = collection.insert_one(redemption_data)
        print(f"Meal redemption entry created for user {user_id_obj} with ID: {result.inserted_id}")
        return result.inserted_id

    def save(self):
        self.collection.insert_one(self.to_dict())

    @classmethod
    def find_by_id(cls, id):
        data = get_db().get_client().tummyfull.meals.find_one({'_id': ObjectId(id)})
        return cls.from_dict(data) if data else None

    @classmethod
    def find_by_user_id(cls, user_id):
        cursor = get_db().get_client().tummyfull.meals.find({'user_id': user_id})
        return [cls.from_dict(data) for data in cursor]

    def __repr__(self):
        return f'<Meal {self._id}, Requested: {self.meal_redeemed}>'