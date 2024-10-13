from django.db.models.signals import post_save
from allauth.account.signals import user_signed_up
from .models import Profile
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(user_signed_up)
def createUser(request, user, **kwargs):
    profile = Profile.objects.create(
        user=user,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )
    print(f"Created profile for {user.username}")

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.get_or_create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'profile'):
#         instance.profile.save()
