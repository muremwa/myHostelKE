from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from book import views as book_views
from action import views as action_views


urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # main
    path('', book_views.Home.as_view(), name='home'),

    # book/
    path('book/', include('book.urls')),

    # staff-action/add-hostel/
    path('staff-actions/', book_views.StaffActions.as_view(), name='staff'),

    # staff-actions/bookings/
    path('staff-actions/bookings/', book_views.BookingList.as_view(), name='booking-list'),

    # staff-actions/booking/4/
    path('staff-actions/bookings/<int:pk>/', book_views.BookingDetail.as_view(), name="booking"),

    # staff-actions/booking/4/delete/
    path('staff-actions/bookings/<int:pk>/delete/', book_views.BookingDelete.as_view(), name="booking-delete"),

    # specify-school/
    path('specify-school/', action_views.add_school, name="specify"),

    # un-specify-school/
    path('un-specify-school/', action_views.remove_school, name="un-specify"),

    # help/
    path('help/', include('action.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
