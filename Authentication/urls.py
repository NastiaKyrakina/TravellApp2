from django.urls import path
from Authentication import views

urlpatterns = [
    path('registration/', views.registration_page, name='registration'),
    path('info/', views.information_page, name='info'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
]
