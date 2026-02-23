from .cart import Cart


def cart_context(request):
    # U svaki template ubacuje broj stavki u košarici (badge u headeru).
    return {
        'cart_item_count': Cart(request).get_item_count()
    }
