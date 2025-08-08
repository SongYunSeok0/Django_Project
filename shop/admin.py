from django.contrib import admin
from .models import Post, Comment, Category, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Comment)