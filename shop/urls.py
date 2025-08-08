from django.urls import path
from . import views
urlpatterns = [
    path('', views.shoplist, name='shoplist'),
    path('<int:pk>/', views.shopdetail, name='shopdetail'),
    path('mypage/', views.myPage, name='mypage'),
    path('create/', views.create, name='itemcreate'),
    path('top/', views.top, name='top'),
    path('bottom/', views.bottom, name='bottom'),
    path('outer/', views.outer, name='outer'),
    path('etc/', views.etc, name='etc'),
    path('shoes/',views.shoes,name='shoes'),
    path('search/', views.search, name='search'),
    ]