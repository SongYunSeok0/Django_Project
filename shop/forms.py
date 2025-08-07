from django import forms
from shop.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'price','size','content','uploaded_image']
