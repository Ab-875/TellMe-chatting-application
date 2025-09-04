from django.urls import path, include
from django.contrib import admin
from . views import MyChatsPageView, CreateChatView, ChatDetailPageView, ChatUpdateView

urlpatterns = [
   path("admin/", admin.site.urls),
   path("chats/", MyChatsPageView.as_view(), name="my_chats_page"),
   path("chats/new/", CreateChatView.as_view(), name="create_chat"),
   path("chats/<int:chat_id>/", ChatDetailPageView.as_view(), name="chat_detail_page"),
   path("chats/<int:chat_id>/edit/", ChatUpdateView.as_view(), name="chat_edit"),
]
