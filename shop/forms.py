from django import forms
from shop.models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title", "content", "price", "size",
            "shoulder", "chest", "somae", "chongjang",
            "waist", "bottom_top", "thigh", "mit_dan",
            "category", "uploaded_image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
            "size": forms.TextInput(attrs={"class": "form-control"}),
            "shoulder": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "chest": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "somae": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "chongjang": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "waist": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "bottom_top": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "thigh": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "mit_dan": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


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