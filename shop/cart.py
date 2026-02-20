from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, TypedDict

from django.http import HttpRequest
from decimal import Decimal

from .models import Product


class CartItemData(TypedDict):
    product_id: int
    size: str
    color: str
    quantity: int
    unit_price: str  # sprema se kao string radi JSON/session kompatibilnosti


@dataclass(frozen=True)
class CartItem:
    key: str
    product: Product
    size: str
    color: str
    quantity: int
    unit_price: Decimal

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity


class Cart:
    # Košarica se sprema u session i identificira stavke po ključu (product_id, size, color).

    SESSION_KEY = 'cart'

    def __init__(self, request: HttpRequest):
        self.request = request
        self.session = request.session
        self._data: Dict[str, CartItemData] = self.session.get(self.SESSION_KEY, {})

    @staticmethod
    def make_key(product_id: int, size: str, color: str) -> str:
        return f"{product_id}:{size}:{color}"

    def save(self) -> None:
        self.session[self.SESSION_KEY] = self._data
        self.session.modified = True

    def clear(self) -> None:
        self._data = {}
        self.save()

    def add(self, *, product: Product, size: str, color: str, quantity: int = 1) -> str:
        if quantity < 1:
            quantity = 1

        key = self.make_key(product.id, size, color)
        if key in self._data:
            self._data[key]['quantity'] += int(quantity)
        else:
            # Cijena se računa uz popust (ako korisnik ima VIP profil).
            price = product.price
            user = self.request.user 
            if user.is_authenticated and hasattr(user, "userprofile"): 
                if user.userprofile.has_discount: 
                    price = price * Decimal("0.9")
            
            self._data[key] = { 
                'product_id': int(product.id), 
                'size': str(size), 'color': str(color), 
                'quantity': int(quantity), 
                'unit_price': str(price), 
            }

        self.save()
        return key

    def set_quantity(self, key: str, quantity: int) -> None:
        if key not in self._data:
            return
        quantity = int(quantity)
        if quantity < 1:
            self.remove(key)
            return
        if quantity > 10:
            quantity = 10
        self._data[key]['quantity'] = quantity
        self.save()

    def remove(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self.save()

    def items(self) -> List[CartItem]:
        if not self._data:
            return []

        product_ids = [item['product_id'] for item in self._data.values()]
        products = Product.objects.in_bulk(product_ids)

        resolved: List[CartItem] = []
        for key, item in self._data.items():
            product = products.get(item['product_id'])
            if not product:
                continue
            resolved.append(
                CartItem(
                    key=key,
                    product=product,
                    size=item['size'],
                    color=item['color'],
                    quantity=int(item['quantity']),
                    unit_price=Decimal(str(item['unit_price'])),
                )
            )
        return resolved

    def count_items(self) -> int:
        return sum(int(item['quantity']) for item in self._data.values())

    def subtotal(self) -> Decimal:
        total = Decimal('0')
        for item in self.items():
            total += item.total_price
        return total
