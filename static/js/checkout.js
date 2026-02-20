document.addEventListener('DOMContentLoaded', function () {
	const form = document.getElementById('orderForm');
	if (!form) return;

	const paymentSelect = document.getElementById('id_payment_method');
	const paypalFields = document.getElementById('paypalFields');
	const cardFields = document.getElementById('cardFields');
	const paypalEmailInput = document.getElementById('id_paypal_email');
	const cardholderInput = document.getElementById('id_cardholder_name');
	const cardNumberInput = document.getElementById('id_card_number');
	const cardExpiryInput = document.getElementById('id_card_expiry');
	const cardCvvInput = document.getElementById('id_card_cvv');

	const digitsOnly = (value) => (value || '').replace(/\D/g, '');

	const setRequired = (el, required) => {
		if (!el) return;
		if (required) el.setAttribute('required', 'required');
		else el.removeAttribute('required');
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

	const formatExpiry = (value) => {
		const digits = digitsOnly(value).slice(0, 4);
		if (digits.length <= 2) return digits;
		return `${digits.slice(0, 2)}/${digits.slice(2)}`;
	};

	const formatCardNumber = (value) => {
		const digits = digitsOnly(value).slice(0, 16);
		return digits.replace(/(.{4})/g, '$1 ').trim();
	};

	if (paymentSelect) {
		paymentSelect.addEventListener('change', updatePaymentFields);
		updatePaymentFields();
	}

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
});
