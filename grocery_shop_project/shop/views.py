from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from decimal import Decimal
from .models import Product, Sale, SaleItem
from .forms import RegisterForm, ProductForm
from django.contrib.auth.models import User
def is_admin(user):
    return user.is_staff or user.is_superuser
def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, username=phone, password=password)
        if user:
            login(request, user)
            return redirect('shop:products')
        else:
            messages.error(request, 'เบอร์หรือรหัสผ่านไม่ถูกต้อง')
    return render(request, 'shop/login.html')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                password=form.cleaned_data['password']
            )
            messages.success(request, 'สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ')
            return redirect('shop:login')
    else:
        form = RegisterForm()
    return render(request, 'shop/register.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('shop:login')
def products_view(request):
    products = Product.objects.order_by('category','name')
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = Decimal('0')
    for pid, qty in cart.items():
        try:
            prod = Product.objects.get(pk=int(pid))
            line = prod.price * qty
            subtotal += line
            cart_items.append({'product': prod, 'quantity': qty, 'line_total': line})
        except Product.DoesNotExist:
            continue
    context = {'products': products,'cart_items': cart_items,'subtotal': subtotal}
    return render(request, 'shop/products.html', context)
@login_required
@user_passes_test(is_admin)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มสินค้าสำเร็จ')
            return redirect('shop:products')
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'เพิ่มสินค้า'})
@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขสินค้าสำเร็จ')
            return redirect('shop:products')
    else:
        form = ProductForm(instance=prod)
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'แก้ไขสินค้า'})
@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    prod.delete()
    messages.success(request, 'ลบสินค้าสำเร็จ')
    return redirect('shop:products')
def cart_add(request, product_id):
    prod = get_object_or_404(Product, pk=product_id)
    qty = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    if cart[str(product_id)] > prod.stock:
        cart[str(product_id)] = prod.stock
    request.session['cart'] = cart
    messages.success(request, f'เพิ่ม {prod.name} จำนวน {qty} ชิ้น ลงตะกร้า')
    return redirect('shop:products')
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    subtotal = Decimal('0')
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
            line = p.price * qty
            subtotal += line
            items.append({'product': p, 'quantity': qty, 'line_total': line})
        except Product.DoesNotExist:
            pass
    return render(request, 'shop/cart.html', {'items': items, 'subtotal': subtotal})
def cart_update(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for key, val in request.POST.items():
            if key.startswith('qty_'):
                pid = key.split('_',1)[1]
                try:
                    qty = int(val)
                    prod = Product.objects.get(pk=int(pid))
                    if qty <= 0:
                        cart.pop(pid, None)
                    else:
                        cart[pid] = min(qty, prod.stock)
                except:
                    continue
        request.session['cart'] = cart
    return redirect('shop:cart')
@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'ตะกร้าว่าง')
        return redirect('shop:products')
    subtotal = Decimal('0')
    items_data = []
    for pid, qty in cart.items():
        prod = get_object_or_404(Product, pk=int(pid))
        if prod.stock < qty:
            messages.error(request, f'สินค้า {prod.name} ไม่เพียงพอ (คงเหลือ {prod.stock})')
            return redirect('shop:cart')
        line = prod.price * qty
        subtotal += line
        items_data.append((prod, qty, prod.price))
    discount = Decimal('0')
    if subtotal >= 1000:
        discount = subtotal * Decimal('0.10')
    elif subtotal >= 500:
        discount = subtotal * Decimal('0.05')
    elif subtotal >= 200:
        discount = Decimal('20')
    total = subtotal - discount
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method','cash')
        sale = Sale.objects.create(
            cashier=request.user,
            subtotal=subtotal,
            discount=discount,
            total=total,
            payment_method=payment_method
        )
        for prod, qty, price in items_data:
            SaleItem.objects.create(sale=sale, product=prod, price=price, quantity=qty)
            prod.stock = max(0, prod.stock - qty)
            prod.save()
        request.session['cart'] = {}
        messages.success(request, 'ชำระเงินสำเร็จ')
        return redirect('shop:receipt', sale_id=sale.id)
    return render(request, 'shop/checkout.html', {
        'items': items_data, 'subtotal': subtotal, 'discount': discount, 'total': total
    })
@login_required
def receipt_view(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    return render(request, 'shop/receipt.html', {'sale': sale})
@login_required
@user_passes_test(is_admin)
def reports_view(request):
    recent_sales = Sale.objects.order_by('-timestamp')[:20]
    low_stock = Product.objects.filter(stock__lte=5).order_by('stock')
    total_products = Product.objects.count()
    return render(request, 'shop/reports.html', {
        'recent_sales': recent_sales,
        'low_stock': low_stock,
        'total_products': total_products,
    })
