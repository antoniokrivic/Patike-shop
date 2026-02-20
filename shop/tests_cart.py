from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order


class CartFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='antonio', password='pass12345')
        self.product = Product.objects.create(
            title='Test Shoe',
            brand='Nike',
            description='Desc',
            price='99.99',
            image_url='https://example.com/x.jpg',
        )

    def test_add_to_cart_from_product_detail(self):
        url = reverse('cart_add', args=[self.product.pk])
        payload = {
            'size': '42',
            'color': 'black',
            'quantity': 2,
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], reverse('cart_detail'))

        cart_page = self.client.get(reverse('cart_detail'))
        self.assertContains(cart_page, 'Test Shoe')
        # quantity is rendered in an <input value="...">; still should include "2" somewhere
        self.assertContains(cart_page, 'value="2"', html=False)

    def test_checkout_requires_login(self):
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp['Location'])

    def test_checkout_creates_orders_and_clears_cart(self):
        # add to cart
        self.client.post(
            reverse('cart_add', args=[self.product.pk]),
            data={'size': '42', 'color': 'black', 'quantity': 1},
        )

        self.client.login(username='antonio', password='pass12345')
        checkout_payload = {
            'size': '42',
            'color': 'black',
            'quantity': 1,
            'full_name': 'Test User',
            'email': 't@example.com',
            'phone': '123',
            'address': 'Street 1',
            'city': 'City',
            'postal_code': '10000',
            'delivery_method': 'standard',
            'payment_method': 'cod',
            'notes': '',
            'agree_terms': 'on',
        }
        resp = self.client.post(reverse('checkout'), data=checkout_payload)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

        # cart should be empty
        cart_page = self.client.get(reverse('cart_detail'))
        self.assertContains(cart_page, 'Košarica je prazna')
