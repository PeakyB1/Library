from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import RegisterForm, LoginForm
from django.views.generic import CreateView

class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'login.html'


class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('user_login')
