from django import forms
from django.contrib.auth.models import User
from . models import Chat, ChatMember

# https://stackoverflow.com/questions/14835607/django-form-exclude-a-user-instance-from-a-queryset

class CreateChatForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    participants = forms.ModelMultipleChoiceField(
        queryset = User.objects.none(),
        widget = forms.CheckboxSelectMultiple,
        help_text = "Select 1 or more Users",
        required = True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        querys = User.objects.all()
        if self.user is not None:
            querys = querys.exclude( pk = self.user.pk)
        self.fields["participants"].queryset = User.objects.exclude( pk = self.user.pk )

    def clean(self):
        cleaned = super().clean()
        others = cleaned.get("participants")

        if not others or others.count() == 0:
            raise forms.ValidationError("Pick at least one other User")
        return cleaned

    def save(self, creator):

        if creator is None:
            raise ValueError("require a creator user")

        users = list(self.cleaned_data["participants"])
        is_group = bool(self.cleaned_data["name"]) or len(users) > 1

        chat = Chat.objects.create(
            name = self.cleaned_data["name"] if is_group else "",
            is_group = is_group
        )    

        ChatMember.objects.create( chat = chat, user = creator, is_admin = True)

        for user in users:
            ChatMember.objects.create( chat = chat, user = user)

        return chat
    
# https://stackoverflow.com/questions/4170060/hadoop-map-reduce-chaining/4762414#4762414
class ChatUpdateForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    is_group = forms.BooleanField(required=False)
    members = forms.ModelMultipleChoiceField(
        queryset = User.objects.none(),
        widget = forms.CheckboxSelectMultiple,
        help_text = "Select 1 or more Users",
        required = True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.chat = kwargs.pop("chat", None)
        if self.user is None or self.chat is None:
            raise ValueError("Need User and Chat")
        super().__init__(*args, **kwargs)

        querys = User.objects.all().exclude( pk = self.user.pk)

        self.fields["members"].queryset = querys
        self.fields["name"].initial = self.chat.name
        self.fields["is_group"].initial = self.chat.is_group
        current_others = self.chat.participants.exclude( pk = self.user.pk )
        self.fields["members"].initial = current_others

    def clean(self):
        cleaned = super().clean()
        others = cleaned.get("members")
        name = cleaned.get("name")
        is_group = bool(cleaned.get("is_group"))

        if not others or others.count() == 0:
            raise forms.ValidationError("Need one User at least")

        inferred_is_group = bool(name) or others.count() > 1
        if is_group != inferred_is_group:
            raise forms.ValidationError(
                "Group Chat need more than one other user"
            )

        if not inferred_is_group and others.count() != 1:
            raise forms.ValidationError("one user allowed only")

        return cleaned
    
    def save(self):
        others = list(self.cleaned_data["members"])
        name = self.cleaned_data["name"]
        inferred_is_group = bool(name) or len(others) > 1

        self.chat.name = name if inferred_is_group else ""
        self.chat.is_group = inferred_is_group
        self.chat.save()

        desired_ids = {user.id for user in others}
        desired_ids.add(self.user.id)  

        current_ids = set(self.chat.participants.values_list("id", flat=True))

        to_add = desired_ids - current_ids
        to_remove = current_ids - desired_ids
        to_remove.discard(self.user.id)  

        if to_add:
            ChatMember.objects.bulk_create(
                [ChatMember(chat=self.chat, user_id=uid) for uid in to_add],
                ignore_conflicts=True,
            )
        if to_remove:
            ChatMember.objects.filter(chat=self.chat, user_id__in=to_remove).delete()

        ChatMember.objects.update_or_create(
            chat=self.chat, user=self.user, defaults={"is_admin": True}
        )

        return self.chat

