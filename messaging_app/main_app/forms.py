from django import forms
from django.contrib.auth.models import User
from . models import Chat, ChatMember

# https://stackoverflow.com/questions/14835607/django-form-exclude-a-user-instance-from-a-queryset

class CreateChatForm(forms.form):
    name = forms.CharField(max_length=50, required=True)
    participants = forms.ModelMultipleChoiceField(
        queryset = User.objects.none(),
        widget = forms.CheckboxSelectMultiple,
        help_text = "Select 1 or more Users",
        required = True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("User")
        super().__init__(*args, **kwargs)
        self.fields["participants"].queryset = User.objects.exclude( pk = self.user.pk )

    def clean(self):
        cleaned = super().clean()
        others = cleaned.get("participants")

        if not others or others.count() == 0:
            raise forms.ValidationError("Pick at least one other User")
        return cleaned

    def save(self, creator):
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