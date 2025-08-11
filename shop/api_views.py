# shop/api_views.py
from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = None
    def get_queryset(self):
        qs = Post.objects.order_by('-id')
        after = self.request.query_params.get('after')
        if after:
            qs = qs.filter(id__gt=after).order_by('id')
        return qs

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = None

    def get_queryset(self):
        qs = Comment.objects.all()
        post_id  = self.request.query_params.get('post')
        parent_id= self.request.query_params.get('parent')
        root     = self.request.query_params.get('root')
        after    = self.request.query_params.get('after')

        if parent_id:
            qs = qs.filter(parent_id=parent_id)                 # 대댓글 목록
        elif post_id:
            qs = qs.filter(post_id=post_id, parent__isnull=True) # 이벤트 포스트 루트 댓글
        elif root:
            qs = qs.filter(post__isnull=True, parent__isnull=True) # 일반 문의 루트만
        if after:
            qs = qs.filter(id__gt=after)
        return qs.order_by('created_date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user if self.request.user.is_authenticated else None)
