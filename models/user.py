from bson import ObjectId
from db.connection import get_db

class User:
    def __init__(self, name, employeeId, email, is_admin, is_active, is_vendor, _id=None):
        self._id = ObjectId(_id) if _id else None
        self.name = name
        self.employeeId = employeeId
        self.email = email
        self.is_admin = is_admin
        self.is_active = is_active
        self.is_vendor = is_vendor
        self.collection = get_db().get_client().tummyfull.users

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            employeeId=data.get('employeeId'),
            email=data.get('email'),
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True),
            is_vendor=data.get('is_vendor', False),
            _id=data.get('_id')
        )

    def to_dict(self):
        return {
            '_id': str(self._id) if self._id else None,
            'name': self.name,
            'employeeId': self.employeeId,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'is_vendor': self.is_vendor
        }
    
    @classmethod
    def _get_collection(cls):
         db = get_db()
         return db.get_client().tummyfull.users

    @classmethod
    def find_all(cls):
        users_data = cls._get_collection().find()
        return [cls.from_dict(user_data) for user_data in users_data]

    @classmethod
    def find_by_id(cls, user_id):
        user_data = cls._get_collection.find_one({'_id': ObjectId(user_id)})
        return cls.from_dict(user_data) if user_data else None

    def save(self):
        data = self.to_dict()
        data['_id'] = ObjectId(data['_id']) if data['_id'] else None
        if not self._id:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id
        else:
            self.collection.update_one({'_id': self._id}, {'$set': data})

    @classmethod
    def find_by_email_and_employeeId(cls, email, employeeId):
        collection = cls._get_collection()
        user_data = collection.find_one({'email': email, 'employeeId': employeeId})
        return cls.from_dict(user_data) if user_data else None

    def delete(self):
        if self._id:
            self.collection.delete_one({'_id': self._id})