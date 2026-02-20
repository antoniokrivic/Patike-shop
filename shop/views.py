from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .forms import CustomUserCreationForm, ProductOrderForm
from .models import Product, Order
from .cart import Cart
from .cart_forms import CartUpdateForm
from .cart_add_forms import AddToCartForm
from .admin_crud import admin_required
from .admin_forms import ProductAdminForm
from decimal import Decimal
from .models import ProductLike

from .firebase_storage import upload_fileobj_to_firebase

@require_POST
@login_required
def logout_view(request):
	auth_logout(request)
	messages.success(request, 'Uspješno si odjavljen.')
	return redirect('home')


def generate_order_number() -> str:
	# Generira kratki i čitljiv broj narudžbe koji se koristi kao grupni ID za checkout.
	# Example: PS-9F3A1C2B
	return f"PS-{uuid4().hex[:8].upper()}"




def toggle_like(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not_authenticated"}, status=403)

    product = Product.objects.get(id=product_id)
    action = request.POST.get("action")  

    like_obj, created = ProductLike.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"is_like": action == "like"}
    )

    if not created:
        like_obj.is_like = action == "like"
        like_obj.save()

    likes = ProductLike.objects.filter(product=product, is_like=True).count()
    dislikes = ProductLike.objects.filter(product=product, is_like=False).count()

    return JsonResponse({
        "likes": likes,
        "dislikes": dislikes,
        "status": "ok"
    })


def home(request):
	# Homepage: dohvat proizvoda + filteri (q/brand/cijena) + sortiranje.
    products = Product.objects.all()

	# Statistika cijena (min/max) za slider.
    price_stats = products.aggregate(min_price=Min('price'), max_price=Max('price'))
    min_price_available = price_stats['min_price']
    max_price_available = price_stats['max_price']

    if min_price_available is not None:
        slider_min = int(min_price_available.quantize(Decimal('1.'), rounding=ROUND_FLOOR))
    else:
        slider_min = 0

    if max_price_available is not None:
        slider_max = int(max_price_available.quantize(Decimal('1.'), rounding=ROUND_CEILING))
    else:
        slider_max = slider_min + 100

    if slider_min == slider_max:
        slider_max = slider_min + 100

	# Parametri filtera iz query stringa.
    search_query = request.GET.get('q', '').strip()
    selected_brand = request.GET.get('brand', '').strip()
    price_min_raw = request.GET.get('price_min', '').strip()
    price_max_raw = request.GET.get('price_max', '').strip()
    sort_option = request.GET.get('sort', 'newest').strip() or 'newest'

	# Tekstualna pretraga.
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(brand__icontains=search_query)
        )

	# Filter po brandu.
    if selected_brand:
        products = products.filter(brand__iexact=selected_brand)

	# Filter po cijeni.
    price_min = None
    if price_min_raw:
        try:
            price_min = Decimal(price_min_raw)
        except (InvalidOperation, ValueError):
            price_min = None
        else:
            products = products.filter(price__gte=price_min)

    price_max = None
    if price_max_raw:
        try:
            price_max = Decimal(price_max_raw)
        except (InvalidOperation, ValueError):
            price_max = None
        else:
            products = products.filter(price__lte=price_max)

    price_min_value = int(price_min) if price_min is not None else slider_min
    price_max_value = int(price_max) if price_max is not None else slider_max

    price_min_value = max(slider_min, min(price_min_value, slider_max))
    price_max_value = max(price_min_value, min(price_max_value, slider_max))

	# Sortiranje rezultata.
    sort_mapping = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low_high': 'price',
        'price_high_low': '-price',
        'title_az': 'title',
        'title_za': '-title',
    }
    sort_field = sort_mapping.get(sort_option, '-created_at')
    products = products.order_by(sort_field, 'id')

	# Popust (VIP) se računa nakon filtera i sortiranja.
    discounted = False
    if request.user.is_authenticated and hasattr(request.user, "userprofile"):
        discounted = request.user.userprofile.has_discount

    for p in products:
        if discounted:
            p.discounted_price = p.price * Decimal("0.9")
        else:
            p.discounted_price = None

	# Broj lajkova/dislajkova (za prikaz na karticama).
    for p in products:
        p.likes_count = ProductLike.objects.filter(product=p, is_like=True).count()
        p.dislikes_count = ProductLike.objects.filter(product=p, is_like=False).count()

	# Lista brandova za dropdown filter.
    brands_qs = Product.objects.exclude(brand='').values_list('brand', flat=True).distinct()
    brands = sorted(brands_qs, key=lambda brand: brand.lower())

	# Podaci za template.
    context = {
        'products': products,
        'brands': brands,
        'search_query': search_query,
        'selected_brand': selected_brand,
        'price_slider_min': slider_min,
        'price_slider_max': slider_max,
        'price_min_value': price_min_value,
        'price_max_value': price_max_value,
        'sort_option': sort_option,
        'result_count': products.count(),
    }

    return render(request, 'home.html', context)




@require_POST
def newsletter_subscribe(request):
	# Newsletter forma iz footera (demo): samo validira email i postavi poruku.
	email = (request.POST.get('email') or '').strip()
	if not email:
		messages.error(request, 'Upiši email adresu.')
	else:
		try:
			validate_email(email)
		except ValidationError:
			messages.error(request, 'Email adresa nije ispravna.')
		else:
			messages.success(request, 'Hvala! Uspješno si se pretplatio/la na novosti.')

	redirect_to = request.META.get('HTTP_REFERER')
	if redirect_to:
		return redirect(redirect_to)
	return redirect('home')


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.exclude(pk=product.pk).order_by('-created_at')[:4]
    form = ProductOrderForm(mode='product')

    discounted_price = None
    if request.user.is_authenticated and hasattr(request.user, "userprofile"):
        if request.user.userprofile.has_discount:
            discounted_price = product.price * Decimal("0.9")

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        if action not in {'add_to_cart', 'checkout'}:
            action = 'add_to_cart'

        form = ProductOrderForm(request.POST, mode='product')
        if form.is_valid():
            cleaned = form.cleaned_data
            cart = Cart(request)
            cart.add(
                product=product,
                size=str(cleaned.get('size') or ''),
                color=str(cleaned.get('color') or 'black'),
                quantity=int(cleaned.get('quantity') or 1),
            )
            messages.success(request, f"Dodano u košaricu: {product.title} (veličina {cleaned.get('size')})")

            # Redirect based on action
            if action == 'checkout' and request.user.is_authenticated:
                return redirect('checkout')
            if action == 'checkout':
                login_url = f"{reverse('login')}?next={reverse('checkout')}"
                return redirect(login_url)
            return redirect('cart_detail')
        # If invalid, fall through and re-render with errors.

    context = {
        'product': product,
        'form': form,
        'related_products': related_products,
        'discounted_price': discounted_price, 
    }
    return render(request, 'product_detail.html', context)



@require_POST
def cart_add(request, pk: int):
	# Dodavanje u košaricu (session). Odvojeno od product_detail da validacija bude jednostavna.
	product = get_object_or_404(Product, pk=pk)
	form = AddToCartForm(request.POST)
	if not form.is_valid():
		wants_json = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('accept') or '')
		if wants_json:
			return JsonResponse(
				{
					'ok': False,
					'errors': form.errors,
				},
				status=400,
			)
		# Re-render product page with errors and preserve user selections.
		related_products = Product.objects.exclude(pk=product.pk).order_by('-created_at')[:4]
		product_form = ProductOrderForm(request.POST, mode='product')
		# Inject field errors from AddToCartForm into product_form equivalents.
		for field in ['size', 'color', 'quantity']:
			if field in form.errors and field in product_form.fields:
				product_form.add_error(field, form.errors[field])
		return render(
			request,
			'product_detail.html',
			{
				'product': product,
				'form': product_form,
				'related_products': related_products,
			},
		)

	cleaned = form.cleaned_data
	cart = Cart(request)
	cart.add(
		product=product,
		size=str(cleaned['size']),
		color=str(cleaned['color']),
		quantity=int(cleaned['quantity'] or 1),
	)
	message = f"Dodano u košaricu: {product.title} (veličina {cleaned['size']})"
	messages.success(request, message)

	wants_json = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in (request.headers.get('accept') or '')
	if wants_json:
		return JsonResponse(
			{
				'ok': True,
				'message': message,
				'cartItemCount': cart.count_items(),
				'cartSubtotal': str(cart.subtotal()),
			},
		)

	go_checkout = bool(cleaned.get('checkout'))
	if go_checkout and request.user.is_authenticated:
		return redirect('checkout')
	if go_checkout:
		login_url = f"{reverse('login')}?next={reverse('checkout')}"
		return redirect(login_url)
	return redirect('cart_detail')


def cart_detail(request):
	cart = Cart(request)
	items = cart.items()
	context = {
		'cart_items': items,
		'cart_subtotal': cart.subtotal(),
	}
	return render(request, 'cart.html', context)


@require_POST
def cart_update(request, key: str):
	form = CartUpdateForm(request.POST)
	if form.is_valid():
		Cart(request).set_quantity(key, form.cleaned_data['quantity'])
		messages.success(request, 'Košarica je ažurirana.')
	return redirect('cart_detail')


@require_POST
def cart_remove(request, key: str):
	Cart(request).remove(key)
	messages.info(request, 'Stavka je uklonjena iz košarice.')
	return redirect('cart_detail')


@require_POST
def cart_clear(request):
	Cart(request).clear()
	messages.info(request, 'Košarica je ispražnjena.')
	return redirect('cart_detail')



@login_required
def checkout(request):
	cart = Cart(request)
	items = cart.items()
	if not items:
		messages.info(request, 'Košarica je prazna.')
		return redirect('home')

	if request.method == 'POST':
		form = ProductOrderForm(request.POST, mode='checkout')
		if form.is_valid():
			cleaned = form.cleaned_data

			payment_method = cleaned.get('payment_method')
			card_brand = ''
			card_last4 = ''
			if payment_method == 'card':
				# forms.py normalizes card_number to digits-only
				card_number = (cleaned.get('card_number') or '').strip()
				card_last4 = card_number[-4:] if len(card_number) >= 4 else ''
				if card_number.startswith('4'):
					card_brand = 'Visa'
				elif card_number.startswith('5'):
					card_brand = 'Mastercard'
				else:
					card_brand = 'Card'

			# Create one checkout group (one order_number) with multiple Order rows.
			# This keeps the current model structure but makes confirmation show *all* items.
			order_number = generate_order_number()
			while Order.objects.filter(order_number=order_number).exists():
				order_number = generate_order_number()

			last_order = None
			for item in items:
				last_order = Order.objects.create(
					user=request.user,
					product=item.product,
					order_number=order_number,
					size=item.size,
					color=item.color,
					quantity=item.quantity,
					unit_price=item.unit_price,
					full_name=cleaned['full_name'],
					email=cleaned['email'],
					phone=cleaned['phone'],
					address=cleaned['address'],
					city=cleaned['city'],
					postal_code=cleaned['postal_code'],
					delivery_method=cleaned['delivery_method'],
					payment_method=payment_method,
					payment_card_brand=card_brand,
					payment_card_last4=card_last4,
					notes=cleaned.get('notes', ''),
				)

			cart.clear()
			messages.success(request, 'Hvala! Narudžba je kreirana.')
			# Redirect to confirmation page for the checkout group
			return redirect('order_confirmation', order_number=order_number)
	else:
		form = ProductOrderForm(mode='checkout')

	return render(
		request,
		'checkout.html',
		{
			'form': form,
			'cart_items': items,
			'cart_subtotal': cart.subtotal(),
		},
	)


@login_required
def order_confirmation(request, order_number):
	orders = list(
		Order.objects.filter(order_number=order_number)
		.select_related('product')
		.order_by('id')
	)
	if not orders:
		return redirect('home')

	# All rows should belong to the same user; still enforce ownership.
	if any(o.user_id != request.user.id for o in orders):
		messages.error(request, 'Nemaš pristup ovoj narudžbi.')
		return redirect('home')

	primary = orders[0]
	total = sum((o.total_price for o in orders), 0)

	return render(
		request,
		'order_confirmation.html',
		{
			'order': primary,
			'order_items': orders,
			'order_total': total,
		},
	)


@login_required
def my_orders(request):
	# One row per checkout group (order_number), newest first.
	orders = (
		Order.objects.filter(user=request.user)
		.order_by('-created_at', '-id')
		.distinct('order_number')
	)
	# distinct('field') radi samo na PostgreSQL-u; za SQLite radimo ručno grupiranje.
	# Fallback: if the DB doesn't support it (e.g., SQLite), do manual grouping.
	try:
		list(orders[:1])
		groups = list(orders)
	except Exception:
		all_orders = (
			Order.objects.filter(user=request.user)
			.select_related('product')
			.order_by('-created_at', '-id')
		)
		seen = set()
		groups = []
		for o in all_orders:
			if o.order_number in seen:
				continue
			seen.add(o.order_number)
			groups.append(o)

	return render(request, 'my_orders.html', {'orders': groups})



def register(request):
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			referral = form.cleaned_data.get('referral_code', '').strip().lower()

			if referral == "vip10":  # ovdje ide koji referall code zelimo
				profile = user.userprofile
				profile.has_discount = True
				profile.save()
				print("IMA POPUST")

			print("--------", repr(referral), "--------------")
			login(request, user)
			messages.success(request, 'Registration successful. You are now logged in.')
			return redirect('home')
	else:
		form = CustomUserCreationForm()

	return render(request, 'register.html', {'form': form})





# Admin (custom) CRUD pages


@admin_required
def admin_product_list(request):
	q = (request.GET.get('q') or '').strip()
	products = Product.objects.all()
	if q:
		products = products.filter(
			Q(title__icontains=q)
			| Q(brand__icontains=q)
			| Q(description__icontains=q)
		)
	products = products.order_by('id')
	return render(request, 'admin/product_list.html', {'products': products, 'q': q})


@admin_required
def admin_product_detail(request, pk: int):
	product = get_object_or_404(Product, pk=pk)
	return render(request, 'admin/product_detail.html', {'product': product})


@admin_required
def admin_product_create(request):
	if request.method == 'POST':
		form = ProductAdminForm(request.POST, request.FILES)
		if form.is_valid():
			product = form.save(commit=False)
			uploaded = request.FILES.get('image')
			if uploaded:
				destination = f"products/{uuid4().hex}_{uploaded.name}"
				product.image_url = upload_fileobj_to_firebase(
					fileobj=uploaded,
					destination_path=destination,
					content_type=getattr(uploaded, 'content_type', None),
				)
				# Prefer Firebase URL going forward.
				product.image = None
			product.save()
			messages.success(request, 'Proizvod je kreiran.')
			return redirect('admin_product_detail', pk=product.pk)
	else:
		form = ProductAdminForm()
	return render(
		request,
		'admin/product_form.html',
		{
			'form': form,
			'title': 'Admin · Novi proizvod',
			'subtitle': 'Kreiraj novi proizvod u katalogu.',
		},
	)


@admin_required
def admin_product_update(request, pk: int):
	product = get_object_or_404(Product, pk=pk)
	if request.method == 'POST':
		form = ProductAdminForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			product = form.save(commit=False)
			uploaded = request.FILES.get('image')
			if uploaded:
				destination = f"products/{uuid4().hex}_{uploaded.name}"
				product.image_url = upload_fileobj_to_firebase(
					fileobj=uploaded,
					destination_path=destination,
					content_type=getattr(uploaded, 'content_type', None),
				)
				product.image = None
			product.save()
			messages.success(request, 'Promjene su spremljene.')
			return redirect('admin_product_detail', pk=product.pk)
	else:
		form = ProductAdminForm(instance=product)
	return render(
		request,
		'admin/product_form.html',
		{
			'form': form,
			'product': product,
			'title': f'Admin · Uredi proizvod #{product.pk}',
			'subtitle': 'Ažuriraj detalje proizvoda.',
		},
	)


@admin_required
def admin_product_delete(request, pk: int):
	product = get_object_or_404(Product, pk=pk)
	if request.method == 'POST':
		title = product.title
		product.delete()
		messages.success(request, f'Proizvod "{title}" je obrisan.')
		return redirect('admin_product_list')
	return render(request, 'admin/product_confirm_delete.html', {'product': product})
