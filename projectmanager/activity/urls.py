from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('organizer/', views.OrganizerList.as_view(), name='organizer-list'),
    path('organizer/<int:pk>/', views.OrganizerDetail.as_view(), name='organizer-detail'),
    path('organizer/owner/', views.OrganizerOwnerList.as_view(), name='organizer-owner-list'),
    path('organizer/owner/<int:pk>/', views.OrganizerOwnerDetail.as_view(), name='organizer-owner-detail'),
    path('organizer/owner/<int:organizer_pk>/activity/<int:activity_pk>/checkin/', views.OrganizerOwnerActivityCheckin.as_view(), name='organizer_owner_activity_checkin'),
    path('organizer/owner/activity/<int:pk>/ticket/', views.OrganizerOwnerActivityTicketList.as_view(), name='organizer-owner-activity-ticket-list'),
    path('activity/search/', views.ActivitySearch.as_view(), name='activity-search'),
    path('activity/', views.ActivityList.as_view(), name='activity-list'),
    path('activity/<int:pk>/', views.ActivityDetail.as_view(), name='activity-detail'),
    path('ticket/<int:pk>/create', views.TicketCreate.as_view(), name='ticket-create'),
    path('ticket/', views.TicketList.as_view(), name='ticket-list'),
    path('ticket/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),
    path('ticket/<int:pk>/update/', views.TicketUpdate.as_view(), name='ticket-update'),
    path('ticket/checkin/', views.TicketCheckin.as_view(), name='ticket-checkin'),
    path('ticket/checkin/success', views.TicketCheckinSuccess.as_view(), name='ticket-checkin-success'),
]

def my_view(request, org_pk, ev_pk):
    # ...
    return redirect('organizer-owner-activity-checkin', org_pk=org_pk, ev_pk=ev_pk)