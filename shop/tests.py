from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product


class OrderFlowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='antonio', password='pass12345')
		self.other = User.objects.create_user(username='other', password='pass12345')
		self.product = Product.objects.create(
			title='Test Shoe',
			brand='Nike',
			description='Desc',
			price='99.99',
			image_url='https://example.com/x.jpg',
		)
		self.product2 = Product.objects.create(
			title='Second Shoe',
			brand='Adidas',
			description='Desc 2',
			price='120.00',
			image_url='https://example.com/y.jpg',
		)

	def _valid_order_payload(self):
		return {
			'size': '42',
			'color': 'black',
			'quantity': 1,
			'full_name': 'Test User',
			'email': 'test@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'Zagreb',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'cod',
			'notes': '',
			'agree_terms': True,
		}

	def test_order_requires_login(self):
		# Can add to cart while logged out
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		# But checkout must require login
		# Ordering now happens in checkout (product page only adds to cart).
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
			follow=True,
		)
		resp = self.client.post(reverse('checkout'), data={
			'full_name': 'Test User',
			'email': 'test@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'Zagreb',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'cod',
			'agree_terms': 'on',
		}, follow=False)
		self.assertEqual(resp.status_code, 302)
		self.assertIn(reverse('login'), resp['Location'])
		self.assertEqual(Order.objects.count(), 0)

	def test_order_creates_and_redirects_to_confirmation(self):
		self.client.login(username='antonio', password='pass12345')
		# Add to cart first
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		resp = self.client.post(reverse('checkout'), data={
			'full_name': 'Test User',
			'email': 'test@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'Zagreb',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'cod',
			'agree_terms': 'on',
		}, follow=False)
		self.assertEqual(resp.status_code, 302)
		order = Order.objects.get()
		self.assertIn(order.order_number, resp['Location'])

	def test_confirmation_protected_per_user(self):
		order = Order.objects.create(
			user=self.user,
			product=self.product,
			order_number='PS-TEST1234',
			size='42',
			color='black',
			quantity=1,
			unit_price=self.product.price,
			full_name='Test User',
			email='test@example.com',
			phone='123',
			address='Street 1',
			city='Zagreb',
			postal_code='10000',
			delivery_method='standard',
			payment_method='cod',
			notes='',
		)
		url = reverse('order_confirmation', kwargs={'order_number': order.order_number})

		# not logged in -> redirected to login
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 302)
		self.assertIn(reverse('login'), resp['Location'])

		# logged in as other -> redirected home
		self.client.login(username='other', password='pass12345')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(resp['Location'], reverse('home'))

		# logged in as owner -> OK
		self.client.logout()
		self.client.login(username='antonio', password='pass12345')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, order.order_number)

	def test_order_requires_paypal_email_when_paypal_selected(self):
		# Add an item to cart first (product page only adds to cart)
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		self.client.login(username='antonio', password='pass12345')
		url = reverse('checkout')
		payload = {
			'full_name': 'Test User',
			'email': 't@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'City',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'paypal',
			'agree_terms': 'on',
		}
		response = self.client.post(url, payload, follow=False)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'paypal_email')
		self.assertEqual(Order.objects.count(), 0)

	def test_order_requires_card_details_when_card_selected_and_persists_last4(self):
		# Add an item to cart first
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		self.client.login(username='antonio', password='pass12345')
		url = reverse('checkout')
		payload = {
			'full_name': 'Test User',
			'email': 't@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'City',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'card',
			'cardholder_name': 'TEST USER',
			'card_number': '4111 1111 1111 1111',
			'card_expiry': '08/27',
			'card_cvv': '123',
			'agree_terms': 'on',
		}
		response = self.client.post(url, payload)
		if response.status_code != 302:
			# Re-post with follow=True so template context is available for errors
			followed = self.client.post(url, payload, follow=True)
			form = getattr(followed, 'context', None) and followed.context.get('form')
			errors = form.errors if form else None
			self.fail(f"Expected redirect (302) from checkout, got {response.status_code}. Form errors: {errors}")
		if Order.objects.count() != 1:
			followed = self.client.post(url, payload, follow=True)
			form = getattr(followed, 'context', None) and followed.context.get('form')
			errors = form.errors if form else None
			self.fail(f"Expected exactly 1 Order after checkout, got {Order.objects.count()}. Checkout status was {response.status_code}. Form errors: {errors}")
		order = Order.objects.latest('id')
		self.assertEqual(order.payment_method, 'card')
		self.assertEqual(order.payment_card_last4, '1111')
		self.assertEqual(order.payment_card_brand, 'Visa')

	def test_order_rejects_cvv_that_is_not_3_digits(self):
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		self.client.login(username='antonio', password='pass12345')
		url = reverse('checkout')
		payload = {
			'full_name': 'Test User',
			'email': 't@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'City',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'card',
			'cardholder_name': 'TEST USER',
			'card_number': '4111 1111 1111 1111',
			'card_expiry': '08/27',
			'card_cvv': '1234',
			'agree_terms': 'on',
		}
		response = self.client.post(url, payload, follow=False)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'card_cvv')
		self.assertEqual(Order.objects.count(), 0)

	def test_order_accepts_spaced_card_number_groups_of_4(self):
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		self.client.login(username='antonio', password='pass12345')
		url = reverse('checkout')
		payload = {
			'full_name': 'Test User',
			'email': 't@example.com',
			'phone': '123',
			'address': 'Street 1',
			'city': 'City',
			'postal_code': '10000',
			'delivery_method': 'standard',
			'payment_method': 'card',
			'cardholder_name': 'TEST USER',
			'card_number': '4111 1111 1111 1111',
			'card_expiry': '08/27',
			'card_cvv': '123',
			'agree_terms': 'on',
		}
		response = self.client.post(url, payload)
		if response.status_code != 302:
			form = getattr(response, 'context', None) and response.context.get('form')
			errors = form.errors if form else None
			self.fail(f"Expected redirect (302) from checkout, got {response.status_code}. Form errors: {errors}")
		order = Order.objects.get()
		self.assertEqual(order.payment_card_last4, '1111')

	def test_checkout_with_multiple_cart_items_creates_single_group(self):
		self.client.login(username='antonio', password='pass12345')
		# Add 2 different products
		self.client.post(
			reverse('cart_add', args=[self.product.pk]),
			data={'size': '42', 'color': 'black', 'quantity': 1},
		)
		self.client.post(
			reverse('cart_add', args=[self.product2.pk]),
			data={'size': '43', 'color': 'white', 'quantity': 2},
		)
		resp = self.client.post(
			reverse('checkout'),
			data={
				'full_name': 'Test User',
				'email': 'test@example.com',
				'phone': '123',
				'address': 'Street 1',
				'city': 'Zagreb',
				'postal_code': '10000',
				'delivery_method': 'standard',
				'payment_method': 'cod',
				'agree_terms': 'on',
			},
			follow=False,
		)
		self.assertEqual(resp.status_code, 302)
		orders = list(Order.objects.order_by('id'))
		self.assertEqual(len(orders), 2)
		self.assertEqual(orders[0].order_number, orders[1].order_number)
		# Confirmation should show both items
		confirm_url = reverse('order_confirmation', kwargs={'order_number': orders[0].order_number})
		resp2 = self.client.get(confirm_url)
		self.assertEqual(resp2.status_code, 200)
		self.assertContains(resp2, self.product.title)
		self.assertContains(resp2, self.product2.title)
