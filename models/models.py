# models.py
from mongoengine import Document, StringField, EmailField, ReferenceField, ListField, FloatField, CASCADE
from datetime import datetime
from mongoengine import DateTimeField

class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    created_at = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        return super(User, self).save(*args, **kwargs)

class Tag(Document):
    name = StringField(required=True, unique=True)
    user_id = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)

class Location(Document):
    name = StringField(required=True)
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    description = StringField(required=True, unique=True)  
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE)
    created_at = DateTimeField(default=datetime.utcnow)
     

class Friendship(Document):
    user_id = ReferenceField(User, required=True)
    friend_id = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)

class Fact(Document):
    description = StringField(required=True)
    location_id = ReferenceField(Location, reverse_delete_rule=CASCADE)
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE)
    tags = ListField(ReferenceField(Tag, reverse_delete_rule=CASCADE))  # Ensure proper handling of tag deletions
    created_at = DateTimeField(default=datetime.utcnow)