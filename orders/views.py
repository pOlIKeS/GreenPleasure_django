from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from .models import Order, OrderItem
from products.models import Product
from .mixins import LoginRequiredMixinWithMessage

# Cart functions (session-based)
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'quantity': 1,
            'price': str(product.price)
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} добавлен в корзину!')
    return redirect('products:product_list')


def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        if cart[str(product_id)]['quantity'] > 1:
            cart[str(product_id)]['quantity'] -= 1
        else:
            del cart[str(product_id)]
    
    request.session['cart'] = cart
    return redirect('orders:cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = float(item['price']) * item['quantity']
        total_price += item_total
        
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': float(item['price']),
            'item_total': item_total
        })
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'orders/cart.html', context)


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Ваша корзина пуста!')
        return redirect('products:product_list')
    
    # Calculate total price for display
    total_price = 0
    for product_id, item in cart.items():
        total_price += float(item['price']) * item['quantity']
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if not phone or not address:
            messages.error(request, 'Пожалуйста, заполните все поля!')
            ctx = {'phone': phone, 'address': address, 'total_price': total_price}
            return render(request, 'orders/checkout.html', ctx)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            phone=phone,
            address=address
        )
        
        # Create order items
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price_at_order=item['price']
            )
        
        # Clear cart
        request.session['cart'] = {}
        messages.success(request, 'Заказ успешно оформлен!')
        return redirect('accounts:profile')
    
    # Pre-fill form with profile data
    initial_phone = ''
    initial_address = ''
    if hasattr(request.user, 'profile'):
        initial_phone = getattr(request.user.profile, 'phone', '')
        initial_address = getattr(request.user.profile, 'default_address', '')
    
    context = {
        'phone': initial_phone,
        'address': initial_address,
        'total_price': total_price
    }
    return render(request, 'orders/checkout.html', context)


class OrderListView(LoginRequiredMixinWithMessage, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')


class OrderDetailView(LoginRequiredMixinWithMessage, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs['pk'], user=self.request.user)