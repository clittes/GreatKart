
from django.urls import path
from . import views

urlpatterns = [

    path('', views.admin_dashboard,name='admin_dashboard'),
    path( 'block_user/<int:user_id>/', views.block_user, name='block_user' ),
    path( 'unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path( 'search_users', views.search_users, name='search_users'),
    path('logout/', views.logout_user, name='logout'),



]

