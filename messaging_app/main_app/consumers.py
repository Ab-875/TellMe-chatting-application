import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import ChatMember, Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.chat_id = str(self.scope["url_route"]["kwargs"]["chat_id"])
        self.group_name = f"chat_{self.chat_id}"

        user = self.scope.get("user", AnonymousUser())
        if not user.is_authenticated:
            await self.close(code=4401)
            return 
    
        is_member = await sync_to_async(
            ChatMember.objects.filter(chat_id=self.chat_id, user=user).exists
        )()

        if not is_member:
            await self.close(code=4403)
            return
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # await self.send(json.dumps({"ok": True, "msg": "connected"}))


    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data or {})
            content = (payload.get("content") or "").strip()

        except Exception:
            content = ""
        if not content:
            return
        
        user = self.scope["user"]

        msg = await sync_to_async(Message.objects.create)(
            chat_id=self.chat_id, sender=user, content = content
        )

        event = {
            "type": "chat.message",
            "message": {
                "id": msg.id,
                "sender": user.username,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            },
        }
        await self.channel_layer.group_send(self.group_name, event)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))