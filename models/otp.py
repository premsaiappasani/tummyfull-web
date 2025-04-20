from bson import ObjectId
from datetime import datetime, timedelta
from db.connection import get_db

class OTP:

    def __init__(self, email, otp_code, expiry_time, is_used=False, created_at=None, _id=None):
        
        self._id = ObjectId(_id) if _id else None
        self.email = email
        self.otp_code = otp_code
        self.expiry_time = expiry_time
        self.is_used = is_used
        self.created_at = created_at if created_at else datetime.now()

    @classmethod
    def get_collection(cls):
        db_client = get_db().get_client()
        return db_client.tummyfull.otps

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            email=data.get('email'),
            otp_code=data.get('otp_code'),
            expiry_time=data.get('expiry_time'),
            is_used=data.get('is_used', False),
            created_at=data.get('created_at'),
            _id=data.get('_id')
        )

    def to_dict(self):
        return {
            '_id': self._id,
            'email': self.email,
            'otp_code': self.otp_code,
            'expiry_time': self.expiry_time,
            'is_used': self.is_used,
            'created_at': self.created_at
        }

    def save(self):
        collection = self.get_collection()
        data_to_save = self.to_dict()

        if self._id is None:
            result = collection.insert_one(data_to_save)
            self._id = result.inserted_id
        else:
            collection.update_one({'_id': self._id}, {'$set': data_to_save})

    @classmethod
    def create_and_save(cls, email, otp_code, expiry_minutes=5):
        expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
        new_otp = cls(email=email, otp_code=otp_code, expiry_time=expiry_time)
        new_otp.save()
        return new_otp


    @classmethod
    def find_active_by_email(cls, email):
        collection = cls.get_collection()
        otp_document = collection.find_one({
            'email': email,
            'is_used': False,
            'expiry_time': {'$gt': datetime.now()} 
        }, sort=[('created_at', -1)])

        return cls.from_dict(otp_document)


    def mark_as_used(self):
        if self._id:
            collection = self.get_collection()
            collection.update_one(
                {'_id': self._id},
                {'$set': {'is_used': True}}
            )
            self.is_used = True
        else:
            print("Warning: Cannot mark OTP as used, it has no _id (not saved yet?)")


    # Optional: Add a method to clean up expired OTPs periodically
    @classmethod
    def cleanup_expired_otps(cls):
         collection = cls.get_collection()
         result = collection.delete_many({
             'expiry_time': {'$lte': datetime.now()},
             'is_used': False
         })
         print(f"Cleaned up {result.deleted_count} expired OTPs.")


    def __repr__(self):
        return f"<OTP email='{self.email}' code='{self.otp_code}' used={self.is_used}>"

