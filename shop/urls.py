from django.urls import path
from . import views
urlpatterns = [
    path('', views.shoplist, name='shoplist'),
    path('<int:pk>/', views.shopdetail, name='shopdetail'),
    path('mypage/', views.myPage, name='mypage'),
    path('create/', views.create, name='itemcreate'),
    ]