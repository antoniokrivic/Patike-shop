from .cart import Cart


def cart(request):
    # U svaki template ubacuje broj stavki u košarici (badge u headeru).
    return {
        'cart_item_count': Cart(request).count_items()
    }
