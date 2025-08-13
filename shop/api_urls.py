from django.urls import path
from .api_views import PostListAPIView, CommentListCreateAPIView

urlpatterns = [
    path('posts/', PostListAPIView.as_view(), name='api-posts'),
    path('comments/', CommentListCreateAPIView.as_view(), name='api-comments'),
]