from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.path == "/accounts/line/login/callback/":
            path = "https://bugauny.pythonanywhere.com/profile"
        else:
            path = "/profile"
        return path.format(username=request.user.username)

    def get_signup_redirect_url(self, request):
        if request.path == "/accounts/line/login/callback/":
            path = "https://bugauny.pythonanywhere.com/profile"
        else:
            path = "/profile"
        return path.format(username=request.user.username)
    