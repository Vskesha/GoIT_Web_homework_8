from mongoengine import Document, StringField, BooleanField
from mongoengine import connect

connect(
    db="vs_hw8",
    host="mongodb+srv://vskesha:RuAEiY3cJXLDasAx@clustervs1.fmxueib.mongodb.net/?retryWrites=true&w=majority",
)


class Contact(Document):
    name = StringField(required=True)
    email = StringField(required=True)
    send = BooleanField()
    phone_number = StringField()
    preferred_notifications = StringField(default="email")
