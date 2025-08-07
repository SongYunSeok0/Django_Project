from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    price = models.IntegerField(null=True)
    size = models.CharField(max_length=10, null=True)
    uploaded_image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return f' 제목:{self.title} - 내용 - {self.content} - 사이즈 - {self.size} - 가격 - {self.price}'

