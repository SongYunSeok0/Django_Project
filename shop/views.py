from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Wishlist, Cartlist
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def shoplist(request):
    #db에서 query select * from post
    posts = Post.objects.all()
    return render(request,
                  template_name='shop/shoplist.html',
                  context={'posts':posts})


def shopdetail(request, pk):
    post = Post.objects.get(pk=pk)
    is_wished = False
    if request.user.is_authenticated:
        is_wished = post.wishlist_set.filter(user=request.user).exists()
    return render(request,
                  'shop/shopdetail.html',
                  context={'post':post, 'is_wished': is_wished})

def shopmyPage(request):
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

    return render(request, 'shop/search.html', {
        'query': query,
        'posts': posts
    })

def aboutme(request):
    return render(request, 'shop/aboutme.html')

def order_status(request):
    posts = Post.objects.all()
    return render(request,
                  'shop/order_status.html',
                  context={'posts':posts})

def order_history(request):
    posts = Post.objects.all()
    return render(request,
                  'shop/order_history.html',
                  context={'posts':posts})

#def wishlist(request):
#    posts = Post.objects.filter(category__slug='check')
#    return render(request,
#                  'shop/wishlist.html',
#                  context={'posts':posts})
@login_required
def wishlist(request):
    wish_posts = Post.objects.filter(wishlist__user=request.user)
    return render(request,
                  'shop/wishlist.html',
                  context={'posts': wish_posts})

@login_required
def cartlist(request):
    wish_posts = Post.objects.filter(cartlist__user=request.user)
    return render(request,
                  'shop/cartlist.html',
                  context={'posts': cart_posts})

def contact(request):
    if request.method == "POST":
        commentform = CommentForm(request.POST, request.FILES)
        if commentform.is_valid():
            comment = commentform.save(commit=False)
            comment.author = request.user if request.user.is_authenticated else None
            comment.save()  # ✅ 한 번만 저장 (루프 없음)
            messages.success(request, "문의가 등록되었습니다.")
            return redirect('contact')
    else:
        commentform = CommentForm()

    comments = Comment.objects.order_by("-created_date")  # ✅ 최신순
    return render(request, "shop/contact.html", {
        "commentform": commentform,
        "comments": comments,
    })

def contact_history(request):
    if not request.user.is_authenticated:
        return redirect('account_login')  # allauth 기본 로그인 URL name
    comments = Comment.objects.filter(author_id=request.user.id).order_by('-id')
    return render(request, 'shop/contact_history.html', {'comments': comments})

def updatecomment(request, pk):
    comment = Comment.objects.get(pk=pk)

    # 작성자 검증이 필요하면 아래 주석 해제
    # if comment.author != request.user:
    #     return redirect('my_inquiries')

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('contact_history')
    else:
        form = CommentForm(instance=comment)

    return render(request, 'shop/commentform.html', {'commentform': form})


# @login_required
def deletecomment(request, pk):
    comment = comment = Comment.objects.get(pk=pk)

    if request.method == "POST":
        comment.delete()
        return redirect('contact_history')  # 내 문의 내역 페이지로 이동

    return render(request, 'shop/comment_confirm_delete.html', {'comment': comment})

@login_required
def add_to_wishlist(request, pk):
    post = Post.objects.get(pk=pk)
    Wishlist.objects.get_or_create(user=request.user, post=post)
    return redirect('shopdetail', pk=pk)


@login_required
def remove_from_wishlist(request, pk):
    post = get_object_or_404(Post, pk=pk)
    Wishlist.objects.filter(user=request.user, post=post).delete()
    return redirect('shopdetail', pk=pk)

@login_required
def add_to_cartlist(request, pk):
    post = Post.objects.get(pk=pk)
    Cartlist.objects.get_or_create(user=request.user, post=post)
    return redirect('shopdetail', pk=pk)


@login_required
def remove_from_cartlist(request, pk):
    post = get_object_or_404(Post, pk=pk)
    Cartlist.objects.filter(user=request.user, post=post).delete()
    return redirect('shopdetail', pk=pk)