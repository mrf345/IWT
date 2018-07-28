from django.contrib.auth.models import User
from django.db.models import (
    Model, CharField, DateField, ForeignKey,
    CASCADE, IntegerField)


class Texts(Model):
    text = CharField(max_length=1999)
    title = CharField(max_length=200)
    date = DateField(auto_now=True)
    viewed = IntegerField(default=0)
    shared = IntegerField(default=0)
    user_id = ForeignKey(
        User, 
        on_delete=CASCADE,
        null=True)

    def __str__(self):
        return 'Text number (%i)' % self.id
