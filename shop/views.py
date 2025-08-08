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

def myPage(request):
    posts = Post.objects.all()
    return render(request,
                  'shop/shopmypage.html',
                  context={'posts':posts})

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

def top(request):
    posts = Post.objects.filter(category__slug='top')
    return render(request, 'shop/top.html', {'posts': posts})

def outer(request):
    posts = Post.objects.filter(category__slug='outer')
    return render(request, 'shop/outer.html', {'posts': posts})

def bottom(request):
    posts = Post.objects.filter(category__slug='bottom')
    return render(request, 'shop/bottom.html', {'posts': posts})

def shoes(request):
    posts = Post.objects.filter(category__slug='shoes')
    return render(request, 'shop/shoes.html', {'posts': posts})

def etc(request):
    posts = Post.objects.filter(category__slug='etc')
    return render(request, 'shop/etc.html', {'posts': posts})


def search(request):
    query = request.GET.get('q')  # 검색어 받아오기
    posts = []

    if query:
        posts = Post.objects.filter(
            title__icontains=query
        )  # title에서 검색 (대소문자 구분 없이 포함된 것)

    return render(request, 'shop/search_results.html', {
        'query': query,
        'posts': posts
    })

def aboutme(request):
    return render(request, 'shop/aboutme.html')