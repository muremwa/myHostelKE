from django.urls import path

from . import views

app_name = 'help'

urlpatterns = [
    path('faq/', views.FaqList.as_view(), name='faq-index'),

    path('faq/<slug:slug>/', views.FaqDetail.as_view(), name='faq'),

    path('accept-cookie/', views.accept_cookies, name='accept-cookie'),
]
