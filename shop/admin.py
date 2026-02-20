from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile

from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('admin_image_preview', 'title', 'brand', 'price', 'created_at')
	list_display_links = ('admin_image_preview', 'title')
	list_select_related = ()
	search_fields = ('title', 'brand')
	readonly_fields = ('admin_image_preview',)
	fields = ('title', 'brand', 'description', 'price', 'image', 'image_url', 'admin_image_preview')

	def admin_image_preview(self, obj: Product):
		if not obj or not getattr(obj, 'primary_image_url', None):
			return '-'
		return format_html(
			'<img src="{}" style="width:42px;height:42px;object-fit:cover;border-radius:10px;" alt="{}" />',
			obj.primary_image_url,
			obj.title,
		)

	admin_image_preview.short_description = 'Slika'



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_discount')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'order_number',
		'user',
		'product',
		'quantity',
		'unit_price',
		'status',
		'created_at',
	)
	list_filter = ('status', 'created_at')
	search_fields = ('order_number', 'user__username', 'full_name', 'email', 'product__title')
