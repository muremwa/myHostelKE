from django.urls import path

from . import views

app_name = 'book'

urlpatterns = [
    # book/
    path('', views.Index.as_view(), name='index'),

    # book/kinder/
    path('hostel/<slug:slug>/', views.HostelDetail.as_view(), name='hostel'),

    # book/kinder/09/
    path('hostel/<slug:slug>/<room_number>/', views.RoomDetail.as_view(), name='room'),

    # book/kinder/34/now/
    path('hostel/<slug:slug>/<room_number>/now/', views.RoomBooking.as_view(), name='now'),
]
