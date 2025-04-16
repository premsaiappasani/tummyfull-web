from bson import ObjectId
from db.connection import get_db

class User:
    def __init__(self, name, email, is_admin, is_active, is_vendor, _id=None):
        self._id = ObjectId(_id) if _id else None
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.is_active = is_active
        self.is_vendor = is_vendor
        self.collection = get_db().get_client().tummyfull.users

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            email=data.get('email'),
            is_admin=data.get('is_admin'),
            is_active=data.get('is_active'),
            is_vendor=data.get('is_vendor'),
            _id=data.get('_id')
        )

    def to_dict(self):
        return {
            '_id': str(self._id) if self._id else None,
            'name': self.name,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'is_vendor': self.is_vendor
        }

    @classmethod
    def find_all(cls):
        db = get_db()
        users_data = db.get_client().tummyfull.users.find()
        return [cls.from_dict(user_data) for user_data in users_data]

    @classmethod
    def find_by_id(cls, user_id):
        db = get_db()
        user_data = db.get_client().tummyfull.users.find_one({'_id': ObjectId(user_id)})
        return cls.from_dict(user_data) if user_data else None

    def save(self):
        data = self.to_dict()
        data['_id'] = ObjectId(data['_id']) if data['_id'] else None
        if not self._id:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id
        else:
            self.collection.update_one({'_id': self._id}, {'$set': data})

    def delete(self):
        if self._id:
            self.collection.delete_one({'_id': self._id})