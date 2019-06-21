from django.urls import path
from UserProfile import views

urlpatterns = [
    path('payment', views.payment_page, name='payment'),
    path('verification/send', views.verification_send_page, name='verification.send_page'),
    path('diary/create/', views.create_diary, name='user_profile.diary_create'),
    path('diary/edit/<int:diary_id>/', views.edit_diary, name='user_profile.diary_edit'),
    path('diary/delete/', views.delete_diary, name='user_profile.diary_delete'),
    path('diary/change/status/', views.change_diary, name='user_profile.diary_change'),
    path('diary/<int:diary_id>/', views.diary_page, name='user_profile.diary_page'),
    path('diary/<int:diary_id>/diary_markers', views.diary_markers, name='user_profile.diary_markers'),
    path('note/create/', views.note_create_page, name='user_profile.note_create'),
    path('note/delete/', views.delete_note, name='note_delete'),
    path('note/edit/<slug:note_id>/', views.note_edit_page, name='note_edit'),
    path('note/<slug:note_id>/', views.note_page, name='note'),
    path('<slug:user_id>/load_notes/', views.load_notes, name='load_notes'),
    path('<slug:user_id>/', views.home, name='home'),

]


