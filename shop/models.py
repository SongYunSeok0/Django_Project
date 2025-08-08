from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)

    def __str__(self):
        return f'{self.name} - {self.slug}'

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    price = models.IntegerField(null=True)
    size = models.CharField(max_length=10, null=True)
    uploaded_image = models.ImageField(upload_to='images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True)  # null=True 임시

    def __str__(self):
        return f'제목: {self.title} - 내용: {self.content} - 사이즈: {self.size} - 가격: {self.price}'
