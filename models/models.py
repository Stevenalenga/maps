# models.py
from mongoengine import Document, StringField, EmailField
from datetime import datetime
from mongoengine import DateTimeField

class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)