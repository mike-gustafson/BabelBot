from django.urls import path
from . import views

urlpatterns = [
    path('', views.translate, name='translate'),
    path('translate/', views.translate, name='translate'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('about/', views.about, name='about'),
]
