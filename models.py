from mongoengine import connect, Document, StringField

class User(Document):
    username = StringField(required=True)
    email = StringField(required=True)
    password = StringField(required=True)