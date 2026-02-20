document.addEventListener('DOMContentLoaded', function () {
	const form = document.getElementById('orderForm');
	if (!form) {
		return;
	}

	// If user clicked "checkout" button, we allow normal POST+redirect.
	const checkoutFlag = document.getElementById('checkoutFlag');

	// Elements
	const quantityInput = document.getElementById('id_quantity');
	const totalElement = document.getElementById('orderTotal');
	const sizeDisplay = document.getElementById('selectedSize');
	const colorSelect = document.getElementById('id_color');
	const colorDisplay = document.getElementById('selectedColor');
	const unitPrice = totalElement ? parseFloat(totalElement.dataset.unitPrice) : 0;

	// Payment fields (checkout page only)
	const paymentSelect = document.getElementById('id_payment_method');
	const paypalFields = document.getElementById('paypalFields');
	const cardFields = document.getElementById('cardFields');
	const paypalEmailInput = document.getElementById('id_paypal_email');
	const cardholderInput = document.getElementById('id_cardholder_name');
	const cardNumberInput = document.getElementById('id_card_number');
	const cardExpiryInput = document.getElementById('id_card_expiry');
	const cardCvvInput = document.getElementById('id_card_cvv');

	// Utility functions
	const digitsOnly = (value) => (value || '').replace(/\D/g, '');
	const formatEuro = (value) => `${value.toFixed(2)} €`;

	const formatExpiry = (value) => {
		const digits = digitsOnly(value).slice(0, 4);
		if (digits.length <= 2) return digits;
		return `${digits.slice(0, 2)}/${digits.slice(2)}`;
	};

	const formatCardNumber = (value) => {
		const digits = digitsOnly(value).slice(0, 16);
		return digits.replace(/(.{4})/g, '$1 ').trim();
	};

	// ========== SIZE SELECTION ==========
	const updateSizeDisplay = () => {
		const checkedInput = document.querySelector('input[name="size"]:checked');
		if (sizeDisplay) {
			sizeDisplay.textContent = checkedInput ? checkedInput.value : '-';
		}
		// Update active class on labels
		document.querySelectorAll('.size-option').forEach((label) => {
			const inputId = label.getAttribute('for');
			const input = inputId ? document.getElementById(inputId) : null;
			if (input && input.checked) {
				label.classList.add('active');
			} else {
				label.classList.remove('active');
			}
		});
	};

	const initSizeSelection = () => {
		// With proper <label for="..."> association, the browser will toggle
		// the radio automatically. We just keep the UI state in sync.
		// Listen for change events on inputs.
		document.querySelectorAll('input[name="size"]').forEach((input) => {
			input.addEventListener('change', updateSizeDisplay);
		});

		// Extra robustness: in case dynamic nodes are added or labels are clicked in a
		// way that doesn't trigger per-input listeners, listen on the container too.
		const container = document.getElementById('sizeOptions');
		if (container) {
			container.addEventListener('change', (e) => {
				const target = e.target;
				if (target && target.matches && target.matches('input[name="size"]')) {
					updateSizeDisplay();
				}
			});
		}

		// Initial update
		updateSizeDisplay();
	};

	// ========== COLOR SELECTION ==========
	const updateColorDisplay = () => {
		if (!colorSelect || !colorDisplay) return;
		const selectedOption = colorSelect.options[colorSelect.selectedIndex];
		colorDisplay.textContent = selectedOption ? selectedOption.text : '-';
	};

	// ========== TOTAL CALCULATION ==========
	const updateTotal = () => {
		if (!quantityInput || !totalElement) return;
		let qty = parseInt(quantityInput.value, 10);
		if (isNaN(qty) || qty < 1) {
			qty = 1;
			quantityInput.value = qty;
		}
		const maxQty = parseInt(quantityInput.max || '10', 10);
		if (qty > maxQty) {
			qty = maxQty;
			quantityInput.value = qty;
		}
		totalElement.textContent = formatEuro(unitPrice * qty);
	};

	// ========== PAYMENT FIELDS (checkout) ==========
	const setRequired = (el, required) => {
		if (!el) return;
		if (required) {
			el.setAttribute('required', 'required');
		} else {
			el.removeAttribute('required');
		}
	};

	const updatePaymentFields = () => {
		if (!paymentSelect) return;
		const method = paymentSelect.value;

		if (paypalFields) paypalFields.style.display = method === 'paypal' ? '' : 'none';
		if (cardFields) cardFields.style.display = method === 'card' ? '' : 'none';

		setRequired(paypalEmailInput, method === 'paypal');
		setRequired(cardholderInput, method === 'card');
		setRequired(cardNumberInput, method === 'card');
		setRequired(cardExpiryInput, method === 'card');
		setRequired(cardCvvInput, method === 'card');
	};

	// ========== INITIALIZATION ==========

	// ========== IMAGE LIGHTBOX (product detail) ==========
	const imageBtn = document.getElementById('productImageBtn');
	const imageModal = document.getElementById('imageModal');
	const imageModalClose = document.getElementById('imageModalClose');

	const openImageModal = () => {
		if (!imageModal) return;
		imageModal.classList.remove('hidden');
		imageModal.classList.add('flex');
		// Prevent background scroll
		document.body.style.overflow = 'hidden';
	};

	const closeImageModal = () => {
		if (!imageModal) return;
		imageModal.classList.add('hidden');
		imageModal.classList.remove('flex');
		document.body.style.overflow = '';
	};

	if (imageBtn && imageModal) {
		imageBtn.addEventListener('click', openImageModal);
	}
	if (imageModalClose) {
		imageModalClose.addEventListener('click', closeImageModal);
	}
	if (imageModal) {
		// Click outside image closes
		imageModal.addEventListener('click', (e) => {
			if (e.target === imageModal) {
				closeImageModal();
			}
		});
		// Escape closes
		document.addEventListener('keydown', (e) => {
			if (e.key === 'Escape' && !imageModal.classList.contains('hidden')) {
				closeImageModal();
			}
		});
	}
	
	// Size selection
	initSizeSelection();

	// Color selection
	if (colorSelect) {
		colorSelect.addEventListener('change', updateColorDisplay);
		updateColorDisplay();
	}

	// Quantity & total
	if (quantityInput) {
		quantityInput.addEventListener('input', updateTotal);
		quantityInput.addEventListener('blur', updateTotal);
	}
	updateTotal();

	// Payment method toggle (checkout page)
	if (paymentSelect) {
		paymentSelect.addEventListener('change', updatePaymentFields);
		updatePaymentFields();
	}

	// Card input formatting
	if (cardExpiryInput) {
		cardExpiryInput.addEventListener('input', () => {
			const formatted = formatExpiry(cardExpiryInput.value);
			if (cardExpiryInput.value !== formatted) {
				cardExpiryInput.value = formatted;
			}
		});
		cardExpiryInput.setAttribute('inputmode', 'numeric');
		cardExpiryInput.setAttribute('maxlength', '5');
		cardExpiryInput.setAttribute('placeholder', 'MM/YY');
	}

	if (cardNumberInput) {
		cardNumberInput.addEventListener('input', () => {
			const formatted = formatCardNumber(cardNumberInput.value);
			if (cardNumberInput.value !== formatted) {
				cardNumberInput.value = formatted;
			}
		});
		cardNumberInput.setAttribute('inputmode', 'numeric');
		cardNumberInput.setAttribute('autocomplete', 'cc-number');
		cardNumberInput.setAttribute('maxlength', '19');
		cardNumberInput.setAttribute('placeholder', '1234 5678 9012 3456');
	}

	if (cardCvvInput) {
		cardCvvInput.addEventListener('input', () => {
			const digits = digitsOnly(cardCvvInput.value).slice(0, 3);
			if (cardCvvInput.value !== digits) {
				cardCvvInput.value = digits;
			}
		});
		cardCvvInput.setAttribute('maxlength', '3');
		cardCvvInput.setAttribute('placeholder', '123');
	}

	// ========== AJAX ADD TO CART (product page) ==========
	const ensureCartBadge = () => {
		const link = document.getElementById('cartLink');
		if (!link) return null;
		let badge = link.querySelector('.badge');
		if (!badge) {
			badge = document.createElement('span');
			badge.className = 'badge absolute -top-1 -right-1';
			link.appendChild(badge);
		}
		return badge;
	};

	const showToast = (text, type = 'success') => {
		const container = document.getElementById('toastContainer');
		if (!container) return;
		const el = document.createElement('div');
		el.className = 'card px-5 py-4';
		el.innerHTML = `<div class="text-sm ${type === 'error' ? 'text-red-700' : 'text-slate-700'}"></div>`;
		el.querySelector('div').textContent = text;
		container.prepend(el);
		window.setTimeout(() => el.remove(), 3500);
	};

	form.addEventListener('submit', async (e) => {
		// If checkout was requested, allow normal server redirect.
		if (checkoutFlag && checkoutFlag.value) {
			return;
		}

		// Otherwise, do AJAX add-to-cart to keep user on the product page.
		e.preventDefault();

		// Primary submit button feedback
		const submitBtn = form.querySelector('button[type="submit"].btn-primary');
		const originalBtnText = submitBtn ? submitBtn.textContent : '';
		if (submitBtn) {
			submitBtn.disabled = true;
			submitBtn.textContent = 'Dodajem...';
		}

		try {
			const resp = await fetch(form.action, {
				method: 'POST',
				headers: {
					'X-Requested-With': 'XMLHttpRequest',
					'Accept': 'application/json',
				},
				body: new FormData(form),
			});

			const data = await resp.json().catch(() => null);
			if (!resp.ok || !data || !data.ok) {
				showToast('Nešto nije u redu. Provjeri odabir veličine/količine.', 'error');
				if (submitBtn) {
					submitBtn.disabled = false;
					submitBtn.textContent = originalBtnText;
				}
				return;
			}

			showToast(data.message || 'Dodano u košaricu.');
			const badge = ensureCartBadge();
			if (badge) {
				badge.textContent = String(data.cartItemCount ?? '');
				if (!data.cartItemCount || Number(data.cartItemCount) <= 0) {
					badge.remove();
				}
			}

			if (submitBtn) {
				submitBtn.textContent = 'Dodano';
				window.setTimeout(() => {
					submitBtn.disabled = false;
					submitBtn.textContent = originalBtnText;
				}, 1500);
			}
		} catch (err) {
			showToast('Greška mreže. Pokušaj ponovo.', 'error');
			if (submitBtn) {
				submitBtn.disabled = false;
				submitBtn.textContent = originalBtnText;
			}
		}
	});
});
