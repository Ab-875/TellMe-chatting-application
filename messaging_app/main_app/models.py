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
    

class ChatMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_memberships')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='memberships')

    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "chat_members"
        constraints = [
            models.UniqueConstraint(fields=["chat", "user"], name="unique_chat_member")
        ]

    def __str__(self):
        is_admin = 'admin' if self.is_admin else 'member'
        return f'{self.user} in {self.chat} {{is_admin}}'
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete= models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete= models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="chat_images/", null=True, blank=True)
    file = models.FileField(upload_to="chat_files/", null=True, blank=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return f'{self.sender}: {self.content}'