from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, Order, OrderItem
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import models

# Home Page - List All Products
def home(request):
    product = Product.objects.all()
    return render(request, 'store/home.html', {'product': product})

# Product Detail Page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

# Add Product to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('store:view_cart')

# View Cart
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum([item.subtotal() for item in cart_items])
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

# Remove item from cart
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('store:view_cart')

# Checkout View
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum([item.subtotal() for item in cart_items])

    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'store/checkout.html', context)

# Fake Payment View
@login_required
def fake_payment(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect('store:home')

    total = sum([item.subtotal() for item in cart_items])

    # Create Order
    order = Order.objects.create(
    user=request.user,
    total_price=total,
    is_paid=True,
    ordered_date=timezone.now(),
    payment_id='FAKE123456',
)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # Clear the cart
    cart_items.delete()

    return redirect('store:order_summary', order_id=order.id)

# Order Summary View
@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_summary.html', {'order': order})

# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    return render(request, 'signup.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# Product List View
def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    products = Product.objects.filter(is_available=True)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category:
        products = products.filter(category__iexact=category)

    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
    })

# Category View
def category_view(request, category):
    products = Product.objects.filter(category__iexact=category)
    return render(request, 'store/category_product.html', {
        'products': products,
        'selected_category': category
    })

# Category Products View
def category_products(request, category):
    products = Product.objects.filter(category__iexact=category)
    return render(request, 'store/category_products.html', {'products': products, 'category': category})
