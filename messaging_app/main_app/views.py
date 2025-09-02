from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DeleteView
from . models import Chat, ChatMember
from . forms import CreateChatForm
from django.http import HttpResponseForbidden

# Create your views here.

class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")

class MyChatsPageView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chats/chat_list.html"
    context_object_name = "chats"

    def get_queryset(self):
        return (
            Chat.objects.filter( memberships_user = self.request.user ).distinct().prefetch_related("participants")
        )
    
class ChatMembershipMixin:
    def dispatch(self, request, *args, **kwargs):
        chat_id = kwargs.get("chat_id")
        self.chat = get_object_or_404(Chat, pk = chat_id)
        is_member = ChatMember.objects.filter( chat = self.chat, user = request.user).exists()

        if not is_member:
            return HttpResponseForbidden("Not a group member")
        return super()(request, *args, **kwargs)
            
        
    