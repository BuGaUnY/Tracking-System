from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # print(dir(request))
        # print(request.path)
        if request.path == "/accounts/line/login/callback/":
            path = "https://liff.line.me/1656180859-N3MpgwlE/profile"
        else:
            path = "/profile"
        return path.format(username=request.user.username)
    
    def get_signup_redirect_url(self, request):
        # print(dir(request))
        # print(request.path)
        if request.path == "/accounts/line/login/callback/":
            path = "https://liff.line.me/1656180859-N3MpgwlE/profile"
        else:
            path = "/profile"
        return path.format(username=request.user.username)