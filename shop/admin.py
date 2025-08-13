from django.contrib import admin
from .models import Post, Comment, Category, PostImage, ChatMessage
from .models import Order


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]
    list_display = ('title', 'category', 'starting_price')  # 관리자 목록에 표시
    fields = ('title', 'category', 'starting_price', 'content', 'size')  # 등록/수정 폼에 표시할 필드

class OrderAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'post', 'amount', 'status', 'created_at')
    search_fields = ('order_id', 'user__username', 'post__title')
    list_filter = ('status', 'created_at')



admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(ChatMessage)
admin.site.register(Order, OrderAdmin)
