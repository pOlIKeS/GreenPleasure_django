def cart_context_processor(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total
    }