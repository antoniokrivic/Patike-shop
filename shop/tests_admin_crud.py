from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Product


class AdminProductCrudAccessTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            title='Test Shoe',
            brand='Nike',
            description='Desc',
            price='99.99',
        )

        self.user = User.objects.create_user(username='user', password='pass12345')
        self.staff = User.objects.create_user(username='staff', password='pass12345', is_staff=True)

    def test_anonymous_redirected_from_admin_pages(self):
        resp = self.client.get(reverse('admin_product_list'))
        # user_passes_test redirects to login by default
        self.assertEqual(resp.status_code, 302)

    def test_regular_user_redirected_from_admin_pages(self):
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('admin_product_list'))
        self.assertEqual(resp.status_code, 302)

    def test_staff_can_access_admin_product_list(self):
        self.client.login(username='staff', password='pass12345')
        resp = self.client.get(reverse('admin_product_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Admin · Proizvodi')

    def test_staff_can_create_update_delete_product(self):
        self.client.login(username='staff', password='pass12345')

        # Create
        resp = self.client.post(
            reverse('admin_product_create'),
            {
                'title': 'New Shoe',
                'brand': 'Adidas',
                'description': 'D',
                'price': '123.45',
                'image_url': 'https://example.com/x.jpg',
            },
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        created = Product.objects.get(title='New Shoe')

        # Update
        resp = self.client.post(
            reverse('admin_product_update', kwargs={'pk': created.pk}),
            {
                'title': 'New Shoe 2',
                'brand': 'Adidas',
                'description': 'D2',
                'price': '111.00',
                'image_url': 'https://example.com/x.jpg',
            },
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        created.refresh_from_db()
        self.assertEqual(created.title, 'New Shoe 2')

        # Delete confirm page
        resp = self.client.get(reverse('admin_product_delete', kwargs={'pk': created.pk}))
        self.assertEqual(resp.status_code, 200)

        # Delete POST
        resp = self.client.post(reverse('admin_product_delete', kwargs={'pk': created.pk}), follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=created.pk).exists())
