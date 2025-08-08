from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    price = models.IntegerField(null=True)
    size = models.CharField(max_length=10, null=True)
    uploaded_image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return f' 제목:{self.title} - 내용 - {self.content} - 사이즈 - {self.size} - 가격 - {self.price}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100, default="No title")
    content = models.TextField()
    uploaded_image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        who = self.author.username if self.author else "익명"
        return f'{who} - {self.title}'