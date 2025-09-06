from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView, UpdateView, DeleteView, View
from . models import Chat, ChatMember, Message
from . forms import CreateChatForm, ChatUpdateForm, MessageCreateForm, MessageUpdateForm, SignUpForm
from django.http import HttpResponseForbidden
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

# Create your views here.
# https://stackoverflow.com/questions/4893673/adding-results-to-a-visible-autocompletetextarea-dropdown/4893813#4893813
# https://stackoverflow.com/questions/22381834/pointer-of-pointer-of-object-dereference/22381925#22381925
# https://stackoverflow.com/questions/35206978/r-select-from-data-frame-by-date-with-repeated-factors/35207032#35207032
# https://stackoverflow.com/questions/14483074/cannot-use-turkish-characters-with-entity-framework/14484140#14484140

class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("login")

class MyChatsPageView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chats/chat_list.html"
    context_object_name = "chats"

    def get_queryset(self):
        return (
            Chat.objects.filter( memberships__user = self.request.user ).distinct().prefetch_related("participants")
        )
    
class ChatMembershipMixin:
    def dispatch(self, request, *args, **kwargs):
        chat_id = kwargs.get("chat_id")
        self.chat = get_object_or_404(Chat, pk = chat_id)
        is_member = ChatMember.objects.filter( chat = self.chat, user = request.user).exists()

        if not is_member:
            return HttpResponseForbidden("Not a group member")
        return super().dispatch(request, *args, **kwargs)
            
class ChatDetailPageView(LoginRequiredMixin, ChatMembershipMixin, DetailView):
    model = Chat
    pk_url_kwarg = "chat_id"
    template_name = "chats/chat_detail.html"
    context_object_name = "chat"

    def get_object(self, queryset = None):
        return self.chat
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = self.chat.messages.select_related("sender").order_by("created_at")[:300]
        return context
    
class CreateChatView(LoginRequiredMixin, FormView):
    template_name = "chats/create_chat.html"
    form_class = CreateChatForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    

    def form_valid(self, form):
        chat = form.save(self.request.user)
        self.object = chat    
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("chat_detail_page", kwargs={"chat_id": self.object.id})
    
class ChatAdminRequiredMixin(LoginRequiredMixin):
    pk_url_kwarg = "chat_id"

    def get_queryset(self):
        return Chat.objects.filter(memberships__user = self.request.user, memberships__is_admin = True)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Exception:
            return HttpResponseForbidden("Unallowed access to manage chat")
        
        return super().dispatch(request, *args, **kwargs)
        
    def get_object(self, queryset = None):
        querys = queryset or self.get_queryset()
        return querys.get( pk = self.kwargs[self.pk_url_kwarg])
    
class ChatUpdateView(ChatAdminRequiredMixin, FormView):
    template_name = "chats/chat_edit.html"
    form_class = ChatUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["chat"] = self.object
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat"] = self.object
        return context

    def form_valid(self, form):
        chat = form.save()
        self.object = chat
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("chat_detail_page", kwargs={"chat_id": self.object.id})

class ChatDeleteView(ChatAdminRequiredMixin, DeleteView):
    model = Chat
    template_name = "chats/chat_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("my_chats_page")
    
class SendMessagePageView(LoginRequiredMixin, ChatMembershipMixin, FormView):
    form_class = MessageCreateForm
    template_name = 'chats/chat_detail.html'

    def form_valid(self, form):
        msg = Message.objects.create(
            chat = self.chat,
            sender = self.request.user,
            content = form.cleaned_data.get("content", "").strip(),
            image = form.cleaned_data.get("image"),
            file = form.cleaned_data.get("file"),
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{self.chat.id}",
            {"type": "chat.event", "event": "created", "message": msg.as_dict()},
        )
        return redirect("chat_detail_page", chat_id=self.chat.id)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

class MessageOwnerMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        self.message = get_object_or_404(Message, pk=kwargs.get("message_id"))

        if self.message.chat_id != int(kwargs.get("chat_id", 0)):
            return HttpResponseForbidden("incorrect chat")
            
        if self.message.sender_id != request.user.id:
            return HttpResponseForbidden("can only delete your messages")
            
        if not ChatMember.objects.filter(chat_id = self.message.chat_id, user=request.user).exists():
            return HttpResponseForbidden("not a group member")
            
            
        return super().dispatch(request, *args, **kwargs) 

class MessageEditView(MessageOwnerMixin, FormView):
    form_class = MessageUpdateForm
    template_name = "chats/message_edit.html"

    def get_initial(self):
        return {"content": "" if self.message.is_deleted else self.message.content}

    def form_valid(self, form):
        msg = self.message
        chat_id = msg.chat_id

        msg.content = form.cleaned_data["content"].strip()
        msg.is_deleted = False
        msg.edited_at = timezone.now()
        msg.image = None
        msg.file = None
        msg.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat_id}",
            {"type": "chat.event", "event": "updated", "message": msg.as_dict()},
        )
        return redirect("chat_detail_page", chat_id=chat_id)


class MessageDeleteView(MessageOwnerMixin, View):
    def post(self, request, *args, **kwargs):
        msg = self.message 
        chat_id = msg.chat_id              
        msg.is_deleted = True
        msg.content = ""
        msg.image = None
        msg.file = None
        msg.edited_at = timezone.now()
        msg.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat_id}",
            {"type": "chat.event", "event": "deleted", "message": msg.as_dict()},
        )
        return redirect("chat_detail_page", chat_id=chat_id)
