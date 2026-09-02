from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('user/', views.user, name="user"),
    path('logout/', views.logout, name="logout"),
    path('admin-login/', views.admin_login, name="admin_login"),
    path('admin-change-password/', views.admin_change_password, name="admin_change_password"),
    path('admin-dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('admin-logout/', views.admin_logout, name="admin_logout"),
    path('delete-donor/<int:donor_id>/', views.delete_donor, name="delete_donor"),
]