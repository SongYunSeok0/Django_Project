from django.contrib import admin
from .models import Post, Comment, Category, PostImage, ChatMessage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]
    list_display = ('title', 'category', 'starting_price')  # 관리자 목록에 표시
    fields = ('title', 'category', 'starting_price', 'content', 'size')  # 등록/수정 폼에 표시할 필드

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(ChatMessage)
