from django import forms
from shop.models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'price', 'size', 'content', 'uploaded_image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'content', 'uploaded_image']
        widgets = {
            'title': forms.TextInput(attrs={
                "style": "width:100%; padding:12px 14px; font-size:16px; "
                         "border:1px solid #ccc; border-radius:6px;"
            }),
            'content': forms.Textarea(attrs={
                "rows": 5,
                "placeholder": (
                    "접수된 문의는 순차적으로 답변해 드리고 있습니다. "
                    "정확한 답변을 위해 문의 내용을 상세히 작성해 주세요."
                ),
                "style": ("width:100%; padding:14px 16px; font-size:15px; "
                          "border:1px solid #ccc; border-radius:6px; background:#f9f9f9;")
            }),
            'uploaded_image': forms.ClearableFileInput(attrs={
                "style": "display:none;"
            })
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'uploaded_image': '사진'
        }
