from activity.models import Organizer

def user_organizer(request):
    if request.user.is_authenticated:
        organizer = Organizer.objects.filter(owner=request.user.profile)
        if organizer:
            return {'user_organizer': organizer}
    return {}