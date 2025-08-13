from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
 
    def __str__(self):
        return f'{self.name} - {self.slug}'

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    price = models.IntegerField(null=True, blank=True)
    starting_price = models.PositiveIntegerField(null=True, blank=True)
    size = models.CharField(max_length=10, null=True, blank=True)
    shoulder= models.FloatField(null=True, blank=True)
    chest= models.FloatField(null=True, blank=True)
    somae= models.FloatField(null=True, blank=True)
    chongjang= models.FloatField(null=True, blank=True)
    waist= models.FloatField(null=True, blank=True)
    bottom_top= models.FloatField(null=True, blank=True)
    thigh= models.FloatField(null=True, blank=True)
    mit_dan= models.FloatField(null=True, blank=True)
    uploaded_image = models.ImageField(upload_to='images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - {self.category}'

    @property
    def summary(self):
        field_labels = {
            "shoulder": "어깨",
            "chest": "가슴",
            "somae": "소매",
            "chongjang": "총장",
            "waist": "허리",
            "bottom_top": "밑위",
            "thigh": "허벅지",
            "mit_dan": "밑단",
            
        }
        parts = []
        for field, label in field_labels.items():
            v = getattr(self, field)
            if v not in (None, ""):
                parts.append(f"{label}: {v}")
        return " / ".join(parts)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f'Image for {self.post.title}'


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE,
                             related_name='comments', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100, default="No title")
    content = models.TextField()
    uploaded_image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        who = self.author.username if self.author else "익명"
        return f'{who} - {self.title}'
    
    def get_absolute_url(self):
        return reverse('contact_history')
    
    def is_reply(self):
        return self.parent_id is not None
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Cartlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    event_id = models.IntegerField()
    temp_field = models.BooleanField(default=True)  # ✅ 임시 필드 추가

    class Meta:
        ordering = ['timestamp']

class Orderlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class StoreStats(models.Model):
    # 사이트 전체 누적 구매 수량
    total_purchases = models.PositiveIntegerField(default=847342)
    today_purchases = models.PositiveIntegerField(default=21)
    last_purchase_date = models.DateField(default=date.today)