from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_discount = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	# Automatski kreira korisnički profil odmah nakon registracije.
    if created:
        UserProfile.objects.create(user=instance)


class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    is_like = models.BooleanField()  

    class Meta:
        unique_together = ('user', 'product')


class Product(models.Model):
	title = models.CharField(max_length=200)
	brand = models.CharField(max_length=100, blank=True)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=8, decimal_places=2)
	image = models.ImageField(upload_to='products/', blank=True, null=True)
	image_url = models.URLField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.brand} - {self.title}"

	@property
	def primary_image_url(self):
		# Glavna slika proizvoda: prvo lokalni upload (MEDIA), a ako nije postavljen onda URL (Firebase/CDN).
		if self.image:
			return self.image.url
		return self.image_url or '/static/img/product-placeholder.svg'


class Order(models.Model):
	STATUS_RECEIVED = 'received'
	STATUS_PROCESSING = 'processing'
	STATUS_SHIPPED = 'shipped'
	STATUS_DELIVERED = 'delivered'
	STATUS_CANCELLED = 'cancelled'

	STATUS_CHOICES = (
		(STATUS_RECEIVED, 'Zaprimljena'),
		(STATUS_PROCESSING, 'U obradi'),
		(STATUS_SHIPPED, 'Poslana'),
		(STATUS_DELIVERED, 'Dostavljena'),
		(STATUS_CANCELLED, 'Otkazana'),
	)

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')

	order_number = models.CharField(max_length=20)

	size = models.CharField(max_length=5)
	color = models.CharField(max_length=20)
	quantity = models.PositiveIntegerField(default=1)
	unit_price = models.DecimalField(max_digits=8, decimal_places=2)
	currency = models.CharField(max_length=10, default='EUR')

	full_name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	address = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	postal_code = models.CharField(max_length=10)
	delivery_method = models.CharField(max_length=30)
	payment_method = models.CharField(max_length=30)
	# Podaci o plaćanju (nikad ne spremati puni broj kartice/PAN niti CVV)
	payment_card_brand = models.CharField(max_length=30, blank=True)
	payment_card_last4 = models.CharField(max_length=4, blank=True)
	notes = models.TextField(blank=True)

	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.order_number} ({self.user})"

	@property
	def total_price(self):
		return (self.unit_price or 0) * (self.quantity or 0)

	@property
	def payment_method_display(self) -> str:
		mapping = {
			'cod': 'Pouzećem',
			'card': 'Karticom',
			'paypal': 'PayPal',
		}
		value = (self.payment_method or '').strip().lower()
		return mapping.get(value, self.payment_method)

	@property
	def delivery_method_display(self) -> str:
		mapping = {
			'standard': 'Standard (3-5 dana)',
			'express': 'Express (1-2 dana)',
		}
		value = (self.delivery_method or '').strip().lower()
		return mapping.get(value, self.delivery_method)
