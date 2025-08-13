from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Wishlist, Category, Cartlist, Order, Orderlist,StoreStats, PostImage
from .forms import PostForm, CommentForm, PostImageForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import ChatMessage
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.utils import timezone
from datetime import date
import uuid
from uuid import uuid4
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
import re
from django.forms import modelformset_factory


#결제창
import requests, json, base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def create(request):
    if request.method == "POST":
        postform = PostForm(request.POST, request.FILES)
        if postform.is_valid():
            postform.save()
            return redirect('shopmypage')  # 원하는 곳으로
    else:
        postform = PostForm()
    return render(request, 'shop/postform.html', {'postform': postform})


def is_staff(user):
    return user.is_authenticated and user.is_staff

def shoplist(request):
    return render(request, 'shop/shoplist.html')


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
    stats, _ = StoreStats.objects.get_or_create(pk=1)
    return render(request, 'shop/shopmypage.html', {
        'posts': posts,
        'total_purchases': stats.total_purchases,
        'today_purchases': stats.today_purchases,
    })

PostImageFormSet = modelformset_factory(PostImage, form=PostImageForm, extra=5)

def create(request):
    if request.method == 'POST':
        postform = PostForm(request.POST, request.FILES)
        image_formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())

        if postform.is_valid() and image_formset.is_valid():
            post1 = postform.save(commit=False)
            post1.save()  # 🔥 반드시 저장해야 외래키 연결 가능

            for form in image_formset:
                if form.cleaned_data.get('image'):
                    PostImage.objects.create(post=post1, image=form.cleaned_data['image'])

            return redirect('mypage')
    else:
        postform = PostForm()
        image_formset = PostImageFormSet(queryset=PostImage.objects.none())

    return render(request, "shop/postform.html", {
        'postform': postform,
        'image_formset': image_formset,
    })

def category_view(request, slug):
    # 카테고리 있으면 가져오고, 없으면 None
    category = Category.objects.filter(slug=slug).first()

    if category:
        posts = Post.objects.filter(category=category)
        category_name = category.name
    else:
        posts = []
        category_name = slug.capitalize()  # slug를 이름처럼 표시

    return render(request, 'shop/category.html', {
        'category_name': category_name,
        'posts': posts
    })


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

from django.contrib.auth.decorators import login_required

@login_required
def order_status(request):
    if request.user.is_superuser:
        base_qs = (Order.objects
                  .select_related('post','post__category','user')
                  .filter(post__category__slug='event', status='결제대기')
                  .order_by('-created_at'))
    else:
        base_qs = (Order.objects
                  .select_related('post','post__category')
                  .filter(user=request.user, post__category__slug='event', status='결제대기')
                  .order_by('-created_at'))

    orders = base_qs

    # 🔹 winner=1 파라미터가 있으면 alert 메시지 세팅
    winner_alert_message = None
    if request.GET.get('winner') == '1':
        post_id = request.GET.get('post')
        if post_id:
            post = get_object_or_404(Post, pk=post_id)
            pending = (Order.objects
                       .filter(user=request.user, post=post, status='결제대기')
                       .order_by('-created_at')
                       .first())
            if pending:
                winner_alert_message = f"🎉 '{post.title}'에 {pending.amount:,}원으로 낙찰되었습니다. 결제를 진행해주세요."

    return render(request, 'shop/event.html', {
        'orders': orders,
        'winner_alert_message': winner_alert_message
    })


@login_required
def orderlist(request):
    if request.user.is_superuser:
        base_qs = Order.objects.select_related('post','post__category','user').order_by('-created_at')
    else:
        base_qs = Order.objects.select_related('post','post__category').filter(user=request.user).order_by('-created_at')

    # ✅ 결제대기(낙찰 직후) 는 주문내역에서 제외
    base_qs = base_qs.exclude(status='결제대기')

    event_orders = base_qs.filter(post__category__slug='event')
    regular_orders = base_qs.exclude(post__category__slug='event')

    return render(request, 'shop/orderlist.html', {
        'event_orders': event_orders,
        'regular_orders': regular_orders,
    })

@login_required
def wishlist(request):
    wish_posts = Post.objects.filter(wishlist__user=request.user)
    return render(request,
                  'shop/wishlist.html',
                  context={'posts': wish_posts})

@login_required
def cartlist(request):
    cart_posts = Post.objects.filter(cartlist__user=request.user)
    return render(request,
                  'shop/cartlist.html',
                  context={'posts': cart_posts})


def contact(request):
    commentform = CommentForm()

    qs = Comment.objects.filter(parent__isnull=True).order_by("-created_date")
    comments = qs.select_related('author').prefetch_related('replies__author')

    return render(request, "shop/contact.html", {
        "commentform": commentform,
        "comments": comments,
    })

def contact_history(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    comments = Comment.objects.filter(author_id=request.user.id).order_by('-id')
    return render(request, 'shop/contact_history.html', {'comments': comments})

def updatecomment(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('contact_history')
    else:
        form = CommentForm(instance=comment)

    return render(request, 'shop/commentform.html', {'commentform': form})


@login_required
def deletecomment(request, pk):
    comment = comment = Comment.objects.get(pk=pk)

    if request.method == "POST":
        comment.delete()
        return redirect('contact_history')  # 내 문의 내역 페이지로 이동

    return render(request, 'shop/comment_confirm_delete.html', {'comment': comment})

@login_required
def admincontact(request):
    if request.user.is_staff:
        qs = Comment.objects.filter(parent__isnull=True).order_by('-id')
    else:
        qs = Comment.objects.filter(author=request.user, parent__isnull=True).order_by('-id')
    comments = qs.select_related('author').prefetch_related('replies__author')  # N+1 방지
    return render(request, 'shop/admincontact.html', {'comments': comments})


@staff_member_required
def reply_comment(request, comment_id):
    parent = Comment.objects.get(pk=comment_id)

    if request.method != "POST":
        return redirect('admincontact')

    content = (request.POST.get('content') or '').strip()
    if not content:
        messages.error(request, "답글 내용을 입력하세요.")
        return redirect('admincontact')

    Comment.objects.create(
        author=request.user,
        content=content,
        parent=parent,     # ← 대댓글 연결 핵심
    )
    messages.success(request, "답글이 등록되었습니다.")
    return redirect('admincontact')

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
    return redirect('cartlist')


@login_required
@require_POST
def send_message(request):
    try:
        user = request.user
        message = request.POST.get('message')
        event_id = int(request.POST.get('event_id'))

        if message and event_id:
            print(message)
            print(event_id)
            ChatMessage.objects.create(user=user, message=message, event_id=event_id)
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'fail', 'error': 'Missing message or event_id'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'fail', 'error': str(e)}, status=500)

@login_required
def get_messages(request):
    try:
        event_id = int(request.GET.get('event_id', 0))
        last_id = int(request.GET.get('last_id', 0))

        # 1분 지난 메시지 삭제
        threshold = timezone.now() - timedelta(minutes=1)
        ChatMessage.objects.filter(timestamp__lt=threshold).delete()

        # 1분 이내 + last_id 이후 메시지만 반환
        messages = ChatMessage.objects.filter(
            event_id=event_id,
            id__gt=last_id,
            timestamp__gte=threshold
        ).values('id', 'user__username', 'message', 'timestamp')

        return JsonResponse(list(messages), safe=False)

    except Exception as e:
        return JsonResponse({'status': 'fail', 'error': str(e)}, status=500)

@login_required
def add_to_orderlist(request, pk):
    post = Post.objects.get(pk=pk)
    Orderlist.objects.get_or_create(user=request.user, post=post)
    return redirect('shopdetail', pk=pk)


@login_required
def remove_from_orderlist(request, pk):
    
    post = get_object_or_404(Post, pk=pk)
    Orderlist.objects.filter(user=request.user, post=post).delete()
    Order.objects.filter(user=request.user, post=post).delete()
    post.is_sold = False
    post.save()
    return redirect('orderlist')

def bulk_action(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_posts')
        action = request.POST.get('action')

        posts = Post.objects.filter(pk__in=selected_ids)

        if action == 'delete':
            posts.delete()
        elif action == 'purchase':
            # 구매 처리 로직 (예: 주문 생성)
            pass

    return redirect('cartlist')

def purchase_selected(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_posts')
        posts = Post.objects.filter(pk__in=selected_ids)

        # 여기에 구매 처리 로직을 추가하세요
        # 예: 주문 생성, 결제 처리 등

        return redirect('cartlist')

def remove_from_cartlist_bulk(request):
    Post.is_sold = False
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_posts')
        # 예: 장바구니 모델에서 삭제
        Cartlist.objects.filter(user=request.user, post_id__in=selected_ids).delete()
    return redirect('cartlist')

#buy 버튼 클릭 시 결제창으로 이동
#https://github.com/tosspayments/tosspayments-sample/blob/main/django-javascript/payments/views.py

# API 요청에 헤더를 생성하는 함수
def create_headers(secret_key):
    # 토스페이먼츠 API는 시크릿 키를 사용자 ID로 사용하고, 비밀번호는 사용하지 않습니다.
    # 비밀번호가 없다는 것을 알리기 위해 시크릿 키 뒤에 콜론을 추가합니다.
    # @docs https://docs.tosspayments.com/reference/using-api/authorization#%EC%9D%B8%EC%A6%9D
    userpass = f"{secret_key}:"
    encoded_u = base64.b64encode(userpass.encode()).decode()
    print("Authorization header:", f"Basic {encoded_u}")  # 디버깅용 출력
    return {
        "Authorization": f"Basic {encoded_u}",
        "Content-Type": "application/json"
    }

# API 요청을 호출하고 응답 핸들링하는 함수
def send_payment_request(url, params, headers):
    response = requests.post(url, json=params, headers=headers)
    return response.json(), response.status_code

# 성공 및 실패 페이지 렌더링하는 함수
def handle_response(request, resjson, status_code, success_template, fail_template):
    if status_code == 200:
        return render(request, success_template, {
            "res": json.dumps(resjson, indent=4),
            "respaymentKey": resjson.get("paymentKey"),
            "resorderId": resjson.get("orderId"),
            "restotalAmount": resjson.get("totalAmount")
        })
    else:
        return render(request, fail_template, {
            "code": resjson.get("code"),
            "message": resjson.get("message")
        })

# 페이지 렌더링 함수
#shop/templates/shop/checkout.html
@login_required
def checkout(request, pk):
    post = get_object_or_404(Post, pk=pk)

    raw_amount = request.GET.get('amount')
    try:
        amount = int(raw_amount) if raw_amount is not None else int(post.price)
    except (TypeError, ValueError):
        amount = int(post.price)

    existing = (Order.objects
                .filter(user=request.user, post=post)
                .order_by('-created_at')
                .first())

    if existing and existing.status in ['결제완료', '배송출발', '배송완료']:
        messages.info(request, '이미 결제 완료된 주문입니다.')
        return redirect('orderlist')

    if existing and existing.status == '결제대기' and existing.order_id:
        order_id = existing.order_id
    else:
        prefix = 'BID-' if (existing and existing.order_id and existing.order_id.startswith('BID-')) else 'ORD-'
        order_id = f'{prefix}{uuid4()}'

    customer_key = "uuid-123e4567-e89b-12d3-a456-426614174000" if request.user.is_authenticated else "test_customer_1234"

    return render(request, 'shop/checkout.html', {
        'post': post,
        'amount': amount,
        'customer_key': customer_key,
        'order_id': order_id,
    })

@csrf_exempt  # API라서 csrf 검증 제외 (AJAX 요청 편의상)
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('orderId')
        amount = data.get('amount')
        order_name = data.get('orderName')
        user = request.user if request.user.is_authenticated else None

        # Order 모델에 주문 정보 저장 (추가)
        Order.objects.create(
            order_id=order_id,
            amount=amount,
            order_name=order_name,
            user=user,
        )
        return JsonResponse({'message': 'order created'}, status=201)

    return JsonResponse({'error': 'invalid method'}, status=405)

# 결제 성공 및 실패 핸들링
# TODO: 개발자센터에 로그인해서 내 시크릿 키를 입력하세요. 시크릿 키는 외부에 공개되면 안돼요.
# @docs https://docs.tosspayments.com/reference/using-api/api-keys
#shop/templates/shop/success.html
def add_order(post, user):
    obj, created = Orderlist.objects.get_or_create(user=user, post=post)
    return obj, created

def success(request, pk):
    resp = process_payment(request, settings.TOSS_API_SECRET_KEY, 'shop/success.html')
    Post.is_sold = False
    today = date.today()
    stats, _ = StoreStats.objects.get_or_create(
        pk=1,
        defaults={'total_purchases': 0, 'today_purchases': 0, 'last_purchase_date': today}
    )

    post = get_object_or_404(Post, pk=pk)

    # 결제 위젯이 리다이렉트로 전달한 값
    order_id = request.GET.get('orderId')
    confirmed_amount = request.GET.get('amount')
    try:
        confirmed_amount = int(confirmed_amount) if confirmed_amount is not None else post.price
    except ValueError:
        confirmed_amount = post.price

    # 1) 우선, 결제에서 온 orderId로 기존 주문을 찾는다.
    order = None
    if order_id:
        order = Order.objects.filter(order_id=order_id).first()

    # 2) 못 찾으면, 낙찰 시 만들어 둔 결제대기( 결제대기 ) 주문을 찾는다.
    #    (낙찰 버튼에서 Order(status='결제대기')로 생성해둔 케이스)
    if order is None:
        order = (Order.objects
                 .filter(user=request.user, post=post, status='결제대기')
                 .order_by('-created_at')
                 .first())

    if order:
        # 기존 주문을 결제 완료로 승격
        if order_id:
            order.order_id = order_id   # 결제에서 온 orderId로 갱신(선택)
        order.amount = confirmed_amount
        order.status = '결제완료'
        order.user = request.user
        order.post = post
        order.save(update_fields=['order_id', 'amount', 'status', 'user', 'post'])
        post.is_sold = True
        post.save(update_fields=['is_sold'])
    else:
        # 3) 어떤 것도 못 찾은 경우 새로 생성 (직접 결제 진입 등의 예외 케이스)
        if order_id:
            oid = order_id
        else:
            oid = str(uuid.uuid4())
        Order.objects.create(
            user=request.user,
            post=post,
            order_id=oid,
            amount=confirmed_amount,
            status='결제완료'
        )
        post.is_sold = True
        post.save(update_fields=['is_sold'])

    # (선택) 기존에 쓰던 Orderlist를 병행한다면 유지
    add_order(post, request.user)

    # 통계 갱신
    if stats.last_purchase_date != today:
        stats.today_purchases = 1
        stats.total_purchases += 1
        stats.last_purchase_date = today
    else:
        stats.today_purchases += 1
        stats.total_purchases += 1

    stats.save(update_fields=['total_purchases', 'today_purchases', 'last_purchase_date'])
    return resp


# 결제 승인 호출하는 함수
# @docs https://docs.tosspayments.com/guides/v2/payment-widget/integration#3-결제-승인하기
def process_payment(request, secret_key, success_template):
    print("process_payment 호출됨")  # 이 부분이 찍히는지 확인
    orderId = request.GET.get('orderId')
    amount = request.GET.get('amount')
    paymentKey = request.GET.get('paymentKey')

    if not all([orderId, amount, paymentKey]):
        # 필수 파라미터 없으면 바로 실패 페이지 렌더링
        return render(request, 'shop/fail.html', {
            "code": "INVALID_REQUEST",
            "message": "필수 파라미터(orderId, amount, paymentKey)가 없습니다."
        })

    url = "https://api.tosspayments.com/v1/payments/confirm"
    headers = create_headers(secret_key)
    params = {
        "orderId": orderId,
        "amount": int(amount),
        "paymentKey": paymentKey
    }

    resjson, status_code = send_payment_request(url, params, headers)
    return handle_response(request, resjson, status_code, success_template, 'shop/fail.html')

#결제 실패 페이지
##shop/templates/shop/fail.html
def fail(request, pk):
    return render(request, "shop/fail.html", {
        "code": request.GET.get('code'),
        "message": request.GET.get('message')
    })


# 브랜드페이 Access Token 발급
def callback_auth(request):
    customerKey = request.GET.get('customerKey')
    code = request.GET.get('code')
    print("callback_auth 호출됨:", customerKey, code)

    if not customerKey or not code:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    url = "https://api.tosspayments.com/v1/brandpay/authorizations/access-token"
    secret_key = settings.TOSS_API_SECRET_KEY
    headers = create_headers(secret_key)
    params = {
        "grantType": "AuthorizationCode",
        "customerKey": customerKey,
        "code": code
    }

    resjson, status_code = send_payment_request(url, params, headers)

    if status_code == 200:
        # customerToken 받음
        customer_token = resjson.get("customerToken")
        # TODO: customerToken을 DB/세션 등에 저장하거나 클라이언트가 다시 요청해서 가져갈 수 있게 하세요.

        # 임시로 JSON으로 바로 응답
        return JsonResponse({"customerToken": customer_token}, status=200)
    else:
        return JsonResponse(resjson, status=status_code)

def event(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/event.html', {'orders': user_orders})

# def order_status_detail(request, post_id):
#     orders = Order.objects.filter(user=request.user, post_id=post_id).order_by('-created_at')
#     return render(request, 'shop/order_status_detail.html', {'orders': orders})

@user_passes_test(lambda u: u.is_superuser)
def finalize_bid(request, pk):
    post = get_object_or_404(Post, pk=pk)

    messages = ChatMessage.objects.filter(event_id=pk)
    highest_bid, winner = 0, None

    for msg in messages:
        match = re.search(r'\d+', msg.message.replace(',', ''))
        if match:
            bid = int(match.group())
            if bid > highest_bid:
                highest_bid, winner = bid, msg.user

    if winner:
        # 결제 대기 주문 생성(주문내역 숨기기 전략이라면 결제대기 유지)
        Order.objects.create(
            user=winner,
            post=post,
            order_id=f'BID-{uuid.uuid4()}',
            amount=highest_bid,
            status='결제대기'
        )

        # 낙찰자에게 링크가 담긴 메시지 남기기 (당사자가 클릭해서 들어오면 alert 뜸)
        event_url = request.build_absolute_uri(
            reverse('order_status') + f'?winner=1&post={pk}'
        )
        ChatMessage.objects.create(
            user=winner,
            message=f"'{post.title}'에 {highest_bid:,}원으로 낙찰되었습니다! 여기서 결제 진행: {event_url}",
            event_id=pk
        )

    return redirect('shopdetail', pk=pk)



@login_required
def delivery_status(request):
    orders = Order.objects.select_related('post').filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/delivery_status.html', {'orders': orders})


@staff_member_required
@require_POST
def update_order_status(request, order_pk):
    status = request.POST.get('status')
    allowed = {'결제완료', '배송준비중', '배송출발', '배송완료', 'cancelled'}
    if status not in allowed:
        messages.error(request, "올바르지 않은 상태값입니다.")
        return redirect('orderlist')

    # 해당 주문의 상태 업데이트
    Order.objects.filter(pk=order_pk).update(status=status)
    messages.success(request, "주문 상태가 업데이트되었습니다.")
    return redirect('orderlist')