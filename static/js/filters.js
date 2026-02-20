document.addEventListener('DOMContentLoaded', function () {
	const form = document.querySelector('.filter-form');
	const searchInput = document.getElementById('id_q');
	const brandSelect = document.getElementById('id_brand');
	const sortSelect = document.getElementById('id_sort');
	const resetButton = document.getElementById('resetFilters');

	const minInput = document.getElementById('id_price_min');
	const maxInput = document.getElementById('id_price_max');
	const minSummary = document.getElementById('priceMinSummary');
	const maxSummary = document.getElementById('priceMaxSummary');
	const minValueEl = document.getElementById('priceMinValue');
	const maxValueEl = document.getElementById('priceMaxValue');
	const minBubble = document.getElementById('priceMinBubble');
	const maxBubble = document.getElementById('priceMaxBubble');

	const slidersReady = Boolean(minInput && maxInput && minSummary && maxSummary);

	const toEuro = (value) => `${value} €`;
	const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
	const showBubble = (bubble) => {
		if (!bubble) return;
		bubble.classList.remove('opacity-0', 'scale-95');
		bubble.classList.add('opacity-100', 'scale-100');
	};
	const hideBubble = (bubble) => {
		if (!bubble) return;
		bubble.classList.add('opacity-0', 'scale-95');
		bubble.classList.remove('opacity-100', 'scale-100');
	};
	const positionBubble = (input, bubble) => {
		if (!input || !bubble) return;
		const sliderMin = parseFloat(input.min);
		const sliderMax = parseFloat(input.max);
		const value = parseFloat(input.value);
		const pct = sliderMax === sliderMin ? 0 : (value - sliderMin) / (sliderMax - sliderMin);
		bubble.textContent = toEuro(value);

		// Vertical spacing controlled via JS (user preference: not via HTML classes).
		// Negative = move bubble up (more space from the slider).
		const verticalOffsetPx = 12;
		bubble.style.transform = `translateX(-50%) translateY(-${verticalOffsetPx}px)`;

		// Position bubble centered above the thumb.
		// Using real element widths is more stable than CSS calc hacks across browsers.
		const inputRect = input.getBoundingClientRect();
		const bubbleRect = bubble.getBoundingClientRect();
		const x = pct * inputRect.width;
		const leftPx = x - bubbleRect.width / 2;
		bubble.style.left = `${leftPx}px`;
	};
	const pulse = (el) => {
		if (!el) return;
		el.classList.remove('opacity-60', 'scale-[0.98]');
		// force reflow so animation re-triggers even on rapid input
		void el.offsetWidth;
		el.classList.add('opacity-60', 'scale-[0.98]');
		window.clearTimeout(el.__pulseTimeout);
		el.__pulseTimeout = window.setTimeout(() => {
			el.classList.remove('opacity-60', 'scale-[0.98]');
		}, 120);
	};
	// We intentionally don't render a "bubble" on the slider track.

	const syncValues = () => {
		if (!slidersReady) {
			return;
		}
		const sliderMin = parseFloat(minInput.min);
		const sliderMax = parseFloat(minInput.max);
		let minValue = parseFloat(minInput.value);
		let maxValue = parseFloat(maxInput.value);
		minValue = clamp(minValue, sliderMin, sliderMax);
		maxValue = clamp(maxValue, sliderMin, sliderMax);
		if (minValue > maxValue) {
			maxValue = minValue;
			maxInput.value = maxValue;
		}
		if (maxValue < minValue) {
			minValue = maxValue;
			minInput.value = minValue;
		}
		minInput.value = minValue;
		maxInput.value = maxValue;
		if (minValueEl) {
			minValueEl.textContent = toEuro(minValue);
			pulse(minValueEl);
		} else {
			// fallback for older markup
			minSummary.textContent = `Odabrano: ${toEuro(minValue)}`;
			pulse(minSummary);
		}
		if (maxValueEl) {
			maxValueEl.textContent = toEuro(maxValue);
			pulse(maxValueEl);
		} else {
			maxSummary.textContent = `Odabrano: ${toEuro(maxValue)}`;
			pulse(maxSummary);
		}
	};

	const attachBubbleDrag = (input, bubble) => {
		if (!input || !bubble) return;

		const update = () => positionBubble(input, bubble);
		const start = () => {
			update();
			showBubble(bubble);
		};
		const end = () => {
			hideBubble(bubble);
		};

		// Mouse/touch/pen unified
		input.addEventListener('pointerdown', start);
		input.addEventListener('pointerup', end);
		input.addEventListener('pointercancel', end);
		input.addEventListener('blur', end);

		// While dragging
		input.addEventListener('input', () => {
			update();
		});

		// Ensure hidden by default even if CSS cached differently
		end();
	};

	if (slidersReady) {
		minInput.addEventListener('input', syncValues);
		maxInput.addEventListener('input', syncValues);
		minInput.addEventListener('change', syncValues);
		maxInput.addEventListener('change', syncValues);
		syncValues();
		attachBubbleDrag(minInput, minBubble);
		attachBubbleDrag(maxInput, maxBubble);
	}

	if (resetButton && form) {
		resetButton.addEventListener('click', function (event) {
			event.preventDefault();
			if (searchInput) {
				searchInput.value = '';
			}
			if (brandSelect) {
				brandSelect.value = '';
			}
			if (sortSelect) {
				sortSelect.value = 'newest';
			}
			if (slidersReady) {
				minInput.value = minInput.min;
				maxInput.value = maxInput.max;
				syncValues();
			}
			const url = new URL(window.location.href);
			url.search = '';
			window.history.replaceState({}, '', url.toString());
		});
	}
});
