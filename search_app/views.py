from django.contrib.postgres.search import SearchVector, SearchQuery
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from django.utils import timezone
from rest_framework import viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category, SearchHistory
from .forms import ProductForm, SearchForm
from .serializers import ProductSerializer
from decimal import Decimal, InvalidOperation
from django.utils.translation import activate
from django.urls import reverse
import logging
import re

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # request.FILESを追加
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        return HttpResponseForbidden("あなたの追加した商品ではありません。")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # request.FILESを追加
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'product': product})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        return HttpResponseForbidden("あなたの追加した商品ではありません。")

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def filter_products(queryset, query, category_name, min_price, max_price):
    if query:
        queryset = queryset.filter(name__icontains=query)
    
    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            queryset = queryset.filter(category=category)
        except Category.DoesNotExist:
            queryset = queryset.none()
    
    if min_price and min_price.strip() != '':
        queryset = queryset.filter(price__gte=min_price)
    if max_price and max_price.strip() != '':
        queryset = queryset.filter(price__lte=max_price)
    
    return queryset

def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all()
    query = request.GET.get('query')
    category_name = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'name')

    # 検索履歴を保存
    if query and request.user.is_authenticated:
        # 既存の同じクエリがある場合は最新のものだけを残す
        existing_histories = SearchHistory.objects.filter(user=request.user, query=query)
        if existing_histories.exists():
            existing_histories.exclude(id=existing_histories.latest('timestamp').id).delete()
            existing_history = existing_histories.latest('timestamp')
            existing_history.timestamp = timezone.now()
            existing_history.save()
        else:
            SearchHistory.objects.create(
                user=request.user,
                query=query,
                category=category_name,
                min_price=min_price if min_price else None,
                max_price=max_price if max_price else None,
                sort=sort_by
            )


    # 最近の検索履歴を取得
    recent_history = []
    if request.user.is_authenticated:
        recent_history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:30]

    cleaned_history = []
    if request.user.is_authenticated:
        recent_history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
        cleaned_history = [
            {
                'query': history.query,
                'category': history.category,
                'min_price': history.min_price if history.min_price else '任意',  # '任意'と表示
                'max_price': history.max_price if history.max_price else '任意',  # '任意'と表示
                'sort': history.sort,
                'timestamp': history.timestamp
            }
            for history in recent_history
        ]

    # 検索処理
    if query:
        search_vector = SearchVector('name', 'description')
        search_query = SearchQuery(query)
        results = results.annotate(search=search_vector).filter(
            Q(search=search_query) | Q(name__icontains=query) | Q(description__icontains=query)
        )

    # カテゴリフィルタリング
    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            results = results.filter(category=category)
        except Category.DoesNotExist:
            results = results.none()

    # 価格が空の場合、Noneに設定
    min_price = min_price if min_price else None
    max_price = max_price if max_price else None


    # min_priceとmax_priceが空でない場合のみ変換
    if min_price and min_price != "":
        try:
            min_price = Decimal(min_price)
        except InvalidOperation:
            min_price = None  # 無効な値の場合、Noneに設定

    if max_price and max_price != "":
        try:
            max_price = Decimal(max_price)
        except InvalidOperation:
            max_price = None  # 無効な値の場合、Noneに設定

    # min_priceとmax_priceがNoneならデフォルト値を設定
    if min_price is None:
        min_price = Decimal('0')  # 価格が指定されていない場合は0でフィルタ
    if max_price is None:
        max_price = Decimal('inf')  # 最大価格は無限大でフィルタ

    # 並び替え
    if sort_by == 'price_asc':
        results = results.order_by('price')
    elif sort_by == 'price_desc':
        results = results.order_by('-price')
    else:
        results = results.order_by('name')

    # ページネーション
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 関連商品を計算
    related_products = Product.objects.none()
    if results.exists():
        categories = results.values_list('category', flat=True).distinct()
        related_by_category = Product.objects.filter(category__in=categories).exclude(id__in=results)

        # 価格範囲
        price_range = results.aggregate(min_price=Min('price'), max_price=Max('price'))
        price_range_min = price_range.get('min_price', 0)
        price_range_max = price_range.get('max_price', Decimal('inf'))

        if price_range_min and price_range_max:
            price_range_min = Decimal(price_range_min)
            price_range_max = Decimal(price_range_max)
            related_products = related_by_category.filter(
                Q(price__gte=price_range_min * Decimal('0.8')) & Q(price__lte=price_range_max * Decimal('1.2'))
            )[:10]

    return render(request, 'search.html', {
        'form': form,
        'page_obj': page_obj,
        'result_count': results.count(),
        'categories': Category.objects.all(),
        'related_products': related_products,
        'recent_history': recent_history,
        'cleaned_history': cleaned_history,
    })

def ajax_search_view(request):
    if request.is_ajax() and request.method == "GET":
        query = request.GET.get('query', '')
        category_name = request.GET.get('category', '')
        min_price = request.GET.get('min_price', '').strip()  # スペースをトリム
        max_price = request.GET.get('max_price', '').strip()  # スペースをトリム
        sort_by = request.GET.get('sort', 'name')

        results = Product.objects.all()
        results = filter_products(results, query, category_name, min_price, max_price)

        # 並び替え処理
        if sort_by == 'price_asc':
            results = results.order_by('price')
        elif sort_by == 'price_desc':
            results = results.order_by('-price')
        else:
            results = results.order_by('name')

        products_data = [{"name": product.name, "price": str(product.price)} for product in results]  # Decimalを文字列に
        return JsonResponse(products_data, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductSearchAPI(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        category_name = request.GET.get('category', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        sort_by = request.GET.get('sort', 'name')

        results = Product.objects.all()

        # filter_products関数を使用
        results = filter_products(results, query, category_name, min_price, max_price)

        # 並び替え処理
        if sort_by == 'price_asc':
            results = results.order_by('price')
        elif sort_by == 'price_desc':
            results = results.order_by('-price')
        else:
            results = results.order_by('name')

        # シリアライズして返す
        serializer = ProductSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductSerializer(serializers.ModelSerializer):
    # Decimalフィールドを文字列として返すためにDecimalFieldを使用
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # カテゴリの名前もシリアライズ
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'category']

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password == password_confirm:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                login(request, user)  # 自動でログインさせる場合
                messages.success(request, 'Registration successful.')
                return redirect('search_view')  # 登録後にリダイレクトするビューの名前を指定
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'registration/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('search_view')
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('search_view')

@login_required
def search_history_list(request):
    history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'search_history_list.html', {'history': history})

def set_language_view(request):
    if request.method == 'POST' and 'language' in request.POST:
        language = request.POST['language']
        activate(language)  # 言語を変更
        request.session['language'] = language  # セッションに言語を保存
    print(request.session.get('language'))  # セッションに保存されている言語を確認
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('search_view')))