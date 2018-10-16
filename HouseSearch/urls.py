from django.urls import path
from HouseSearch import views

urlpatterns = [
    path('', views.house_search_page),
    path('<slug:user_id>/<slug:house_id>/', views.house_page),
    path('house/add/', views.house_add_page),

]

""" path('<slug:user_name>', views.home),
   path('login', views.login),
   path('logout', views.logout),
   path('registrations', views.registr),
"""
