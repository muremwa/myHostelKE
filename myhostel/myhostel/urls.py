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

    # staff-action/add-hostel/
    path('staff-actions/add-hostel/', book_views.StaffAddHostel.as_view(), name='add-hostel'),

    # staff-actions/bookings/
    path('staff-actions/bookings/', book_views.BookingList.as_view(), name='booking-list'),

    # staff-actions/booking/4/
    path('staff-actions/bookings/<int:pk>/', book_views.BookingDetail.as_view(), name="booking"),

    # specify-school/
    path('specify-school/', action_views.add_hostel, name="specify"),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# TODO: add adding hostel and room page, booking viewing pages, room restore page, a search functionality(by area,
# TODO: hostel, university) and a FAQs page.
