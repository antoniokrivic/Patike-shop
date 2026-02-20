from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('register/', views.register, name='register'),
	path('moje-narudzbe/', views.my_orders, name='my_orders'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
	# Prilagođeni admin CRUD
    path('staff/products/', views.admin_product_list, name='admin_product_list'),
    path('staff/products/create/', views.admin_product_create, name='admin_product_create'),
    path('staff/products/<int:pk>/', views.admin_product_detail, name='admin_product_detail'),
    path('staff/products/<int:pk>/edit/', views.admin_product_update, name='admin_product_update'),
    path('staff/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
	path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
	path('order/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<str:key>/', views.cart_update, name='cart_update'),
    path('cart/remove/<str:key>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
    path("toggle-like/<int:product_id>/", views.toggle_like, name="toggle_like"),
]
