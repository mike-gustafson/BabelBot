from django.urls import path
from . import views

urlpatterns = [
    # Website URLs
    path('', views.home, name='home'),
    path('translate/', views.translate, name='translate'),
    path('about/', views.about, name='about'),
    path('account/', views.account, name='account'),
    path('account/delete/', views.account_delete_confirm, name='account_delete_confirm'),
    
    # POST request urls
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('translate/process/', views.translate, name='translate_process'),
    path('account/translations/edit/', views.handle_translation, name='edit_translation'),
    path('account/translations/delete/<int:translation_id>/', views.handle_translation, name='delete_translation'),
    
    # Password reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Login URL (redirects to home since login is handled there)
    path('login/', views.home, name='login'),
]
