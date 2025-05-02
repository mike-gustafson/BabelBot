from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Website URLs
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('translate/', views.translate, name='translate'),
    path('ocr/process/', views.ocr, name='ocr_process'),
    path('tts/', views.tts, name='tts'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('account/translations/edit/', views.edit_translation, name='edit_translation'),
    path('account/translations/delete/<int:translation_id>/', views.delete_translation, name='delete_translation'),
    path('account/delete/', views.account_delete_confirm, name='account_delete_confirm'),
    path('register/', views.register, name='register'),
    
    # Password reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
