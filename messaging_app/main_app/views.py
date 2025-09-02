from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import FormView

# Create your views here.

class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")