from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
def shoplist(request):
    #db에서 query select * from post
    posts = Post.objects.all()
    return render(request,
                  template_name='shop/shoplist.html',
                  context={'posts':posts})


def shopdetail(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request,
                  'shop/shopdetail.html',
                  context={'post':post})

def create(request):
    if request.method == 'POST':
        #작성하다가 제출 버튼을 누른 경우
        postform = PostForm(request.POST,request.FILES)
        if postform.is_valid():
            post1 = postform.save(commit=False)
            post1.title = post1.title + ""
            postform.save()
            return redirect('/shop/')
    else: #get
        postform = PostForm()
    return render(request,
                  template_name="shop/postform.html",
                  context={'postform':postform})

