# shop/api_views.py
from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = None

    def get_queryset(self):
        qs = (Post.objects
              .select_related('category')
              .prefetch_related('images')  # PostImage FK related_name='images'
              .order_by('-id'))
        # 선택: 필터/검색/더보기
        q = self.request.query_params
        after = q.get('after')      # 무한스크롤 기준 id
        category = q.get('category')  # slug 기준이라면: category__slug
        search = q.get('q')

        if category:
            qs = qs.filter(category__slug=category)
        if search:
            qs = qs.filter(title__icontains=search)
        if after and after.isdigit():
            qs = qs.filter(id__lt=int(after))

        return qs

    def get_serializer_context(self):
        return {"request": self.request} 


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    # 익명 작성까지 허용하려면 AllowAny 로 바꾸세요.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = None

    def get_queryset(self):
        qs = (
            Comment.objects
            .select_related('author', 'post')
            .prefetch_related('replies__author')  # 대댓글 작성자까지 미리 로드
        )

        q = self.request.query_params
        post_id   = q.get('post')
        parent_id = q.get('parent')
        root      = q.get('root')
        after     = q.get('after')

        if parent_id and str(parent_id).isdigit():
            # 대댓글 목록
            qs = qs.filter(parent_id=int(parent_id))
        elif post_id and str(post_id).isdigit():
            # 특정 포스트의 루트 댓글
            qs = qs.filter(post_id=int(post_id), parent__isnull=True)
        elif root:
            # 일반 문의(포스트 연결 없음) 루트 댓글
            qs = qs.filter(post__isnull=True, parent__isnull=True)

        if after and str(after).isdigit():
            qs = qs.filter(id__gt=int(after))

        return qs.order_by('created_date')

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        # 클라이언트가 author를 임의로 넣지 못하게 서버에서 지정
        serializer.save(
            author=self.request.user if self.request.user.is_authenticated else None
        )
