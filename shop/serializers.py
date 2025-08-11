from rest_framework import serializers
from .models import Post, Comment, PostImage

class PostImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'image_url']
    def get_image_url(self, obj):
        r = self.context.get('request'); url = obj.image.url if obj.image else None
        return r.build_absolute_uri(url) if (r and url) else url

class PostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    images = PostImageSerializer(source='images', many=True, read_only=True)
    summary = serializers.CharField(read_only=True)
    class Meta:
        model = Post
        fields = ['id','title','content','price','size',
                  'shoulder','chest','somae','chongjang',
                  'waist','bottom_top','thigh','mit_dan',
                  'uploaded_image','image_url','category','category_name',
                  'summary','images']
    def get_image_url(self, obj):
        r = self.context.get('request'); url = obj.uploaded_image.url if obj.uploaded_image else None
        return r.build_absolute_uri(url) if (r and url) else url

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'parent',
            'title','content',
            'uploaded_image','image_url',
            'author','author_name',
            'created_date','updated_date',
            'replies_count',
        ]
        read_only_fields = ['id','author_name','created_date','updated_date','replies_count']

    def get_author_name(self, obj):
        return getattr(obj.author, 'username', None)

    def get_image_url(self, obj):
        r = self.context.get('request'); url = obj.uploaded_image.url if obj.uploaded_image else None
        return r.build_absolute_uri(url) if (r and url) else url
