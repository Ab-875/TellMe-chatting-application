from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Chat(models.Model):
    name = models.CharField(max_length=40)
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, through='ChatMember', related_name='chats')

    class Meta:
        db_table = 'chats'

    def __str__(self):
        return self.name