from django.test import TestCase
from django.urls import reverse


class NewsletterSubscribeTests(TestCase):
	def test_subscribe_requires_post(self):
		url = reverse('newsletter_subscribe')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 405)

	def test_subscribe_success_redirects_with_message(self):
		url = reverse('newsletter_subscribe')
		response = self.client.post(url, {'email': 'test@example.com'}, follow=True)
		self.assertEqual(response.status_code, 200)
		messages = list(response.context.get('messages', []))
		self.assertTrue(any('Uspješno' in str(m) or 'Hvala' in str(m) for m in messages))

	def test_subscribe_invalid_email_sets_error_message(self):
		url = reverse('newsletter_subscribe')
		response = self.client.post(url, {'email': 'not-an-email'}, follow=True)
		self.assertEqual(response.status_code, 200)
		messages = list(response.context.get('messages', []))
		self.assertTrue(any('nije ispravna' in str(m) for m in messages))
