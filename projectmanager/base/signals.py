from allauth.account.signals import user_signed_up
from .models import Profile
from django.dispatch import receiver

@receiver(user_signed_up)
def createUser(request, user, **kwargs):
    profile = Profile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )