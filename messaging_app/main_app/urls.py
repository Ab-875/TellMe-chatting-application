from django.urls import path, include
from django.contrib import admin
from . views import MyChatsPageView, CreateChatView, ChatDetailPageView, ChatUpdateView, ChatDeleteView, SendMessagePageView, MessageEditView, MessageDeleteView, SignUpView

urlpatterns = [
   path("", MyChatsPageView.as_view(), name="home"),
   path("signup/", SignUpView.as_view(), name="signup"),

   path("chats/", MyChatsPageView.as_view(), name="my_chats_page"),
   path("chats/new/", CreateChatView.as_view(), name="create_chat"),
   path("chats/<int:chat_id>/", ChatDetailPageView.as_view(), name="chat_detail_page"),
   path("chats/<int:chat_id>/edit/", ChatUpdateView.as_view(), name="chat_edit"),
   path("chats/<int:chat_id>/delete/", ChatDeleteView.as_view(), name="chat_delete"),
   
   path("chats/<int:chat_id>/send/", SendMessagePageView.as_view(), name="send_message"),
   path("chats/<int:chat_id>/messages/<int:message_id>/edit/", MessageEditView.as_view(), name="message_edit"),
   path("chats/<int:chat_id>/messages/<int:message_id>/delete/", MessageDeleteView.as_view(), name="message_delete"),
]
