from django.urls import path
from . import views
urlpatterns = [
    path('', views.shoplist, name='shoplist'),
    path('<int:pk>/', views.shopdetail, name='shopdetail'),
    path('mypage/', views.shopmyPage, name='mypage'),
    path('create/', views.create, name='itemcreate'),
    path('mypage/order_status/', views.order_status, name='order_status'),
    path('mypage/order_history/', views.order_history, name='order_history'),
    path('mypage/wishlist/', views.wishlist, name='wishlist'),
    path('mypage/contact/', views.contact, name='contact'),
    path('mypage/contact_history/', views.contact_history, name='contact_history'),
    ]