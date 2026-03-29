from __future__ import annotations

import re

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{6,20}$")

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def normalize_upper(value: str) -> str:
	return value.strip().upper()


def validate_side(side: str) -> str:
	normalized = normalize_upper(side)
	if normalized not in VALID_SIDES:
		raise ValueError(f"Invalid side '{side}'. Expected one of: {sorted(VALID_SIDES)}")
	return normalized


def validate_order_type(order_type: str) -> str:
	normalized = normalize_upper(order_type)
	if normalized not in VALID_ORDER_TYPES:
		raise ValueError(
			f"Invalid order type '{order_type}'. Expected one of: {sorted(VALID_ORDER_TYPES)}"
		)
	return normalized


def validate_symbol(symbol: str) -> str:
	normalized = normalize_upper(symbol)
	if not SYMBOL_PATTERN.match(normalized):
		raise ValueError(
			"Invalid symbol format. Expected uppercase alphanumeric pair like BTCUSDT."
		)
	return normalized


def validate_quantity(quantity: float) -> float:
	if quantity <= 0:
		raise ValueError("Quantity must be greater than 0.")
	return quantity


def validate_price(order_type: str, price: float | None) -> float | None:
	if order_type == "LIMIT":
		if price is None:
			raise ValueError("Price is required for LIMIT orders.")
		if price <= 0:
			raise ValueError("Price must be greater than 0 for LIMIT orders.")
		return price
	return None
