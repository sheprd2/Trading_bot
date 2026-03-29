from __future__ import annotations

import argparse
import sys
from typing import Callable

from client import get_futures_client
from logging_config import configure_logging
from orders import place_limit_order, place_market_order, place_stop_limit_order
from validators import (
	validate_order_type,
	validate_price,
	validate_quantity,
	validate_side,
	validate_stop_price,
	validate_symbol,
)


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="CLI trading bot for Binance Futures Testnet"
	)
	parser.add_argument("--interactive", action="store_true", help="Launch guided prompt mode")
	parser.add_argument("--symbol", help="Trading pair symbol (e.g. BTCUSDT)")
	parser.add_argument("--side", help="Order side: BUY or SELL")
	parser.add_argument(
		"--type",
		dest="order_type",
		required=False,
		help="MARKET, LIMIT, or STOP_LIMIT",
	)
	parser.add_argument("--quantity", type=float, help="Order quantity")
	parser.add_argument("--price", type=float, help="Required when --type LIMIT or STOP_LIMIT")
	parser.add_argument(
		"--stop-price",
		type=float,
		help="Required when --type STOP_LIMIT",
	)
	return parser


def _prompt_until_valid(prompt_text: str, parser_fn: Callable[[str], object]) -> object:
	while True:
		try:
			raw = input(prompt_text).strip()
			return parser_fn(raw)
		except ValueError as exc:
			print(f"Invalid input: {exc}")


def _prompt_choice(prompt_text: str, choices: tuple[str, ...]) -> str:
	while True:
		raw = input(prompt_text).strip().upper()
		if raw in choices:
			return raw
		print(f"Invalid input. Choose one of: {', '.join(choices)}")


def _parse_positive_float(raw: str) -> float:
	value = float(raw)
	if value <= 0:
		raise ValueError("value must be greater than 0")
	return value


def _prompt_yes_no(prompt_text: str) -> bool:
	while True:
		raw = input(prompt_text).strip().lower()
		if raw in {"y", "yes"}:
			return True
		if raw in {"n", "no"}:
			return False
		print("Invalid input. Enter y or n.")


def _collect_interactive_args() -> argparse.Namespace:
	print("Interactive mode enabled. Enter order details below.")
	symbol = _prompt_until_valid(
		"Symbol (example BTCUSDT): ",
		lambda raw: validate_symbol(raw),
	)
	side = _prompt_choice("Side (BUY/SELL): ", ("BUY", "SELL"))
	order_type = _prompt_choice("Type (MARKET/LIMIT/STOP_LIMIT): ", ("MARKET", "LIMIT", "STOP_LIMIT"))
	quantity = _prompt_until_valid(
		"Quantity (> 0): ",
		lambda raw: validate_quantity(_parse_positive_float(raw)),
	)

	price = None
	if order_type in {"LIMIT", "STOP_LIMIT"}:
		price = _prompt_until_valid(
			"Price (> 0): ",
			lambda raw: _parse_positive_float(raw),
		)

	stop_price = None
	if order_type == "STOP_LIMIT":
		stop_price = _prompt_until_valid(
			"Stop price (> 0): ",
			lambda raw: _parse_positive_float(raw),
		)

	print("\nOrder Summary")
	print(f"- symbol: {symbol}")
	print(f"- side: {side}")
	print(f"- type: {order_type}")
	print(f"- quantity: {quantity}")
	print(f"- price: {price}")
	print(f"- stop_price: {stop_price}")

	if not _prompt_yes_no("Submit this order? (y/n): "):
		print("Order submission cancelled.")
		raise SystemExit(0)

	return argparse.Namespace(
		symbol=symbol,
		side=side,
		order_type=order_type,
		quantity=quantity,
		price=price,
		stop_price=stop_price,
	)


def main() -> None:
	logger = configure_logging()
	parser = build_parser()

	try:
		args = parser.parse_args()

		if args.interactive:
			args = _collect_interactive_args()
		else:
			missing: list[str] = []
			for field in ("symbol", "side", "order_type", "quantity"):
				if getattr(args, field) is None:
					missing.append(field)
			if missing:
				parser.error(
					"Missing required arguments in non-interactive mode: "
					+ ", ".join(f"--{name.replace('_', '-')}" for name in missing)
				)

		symbol = validate_symbol(args.symbol)
		side = validate_side(args.side)
		order_type = validate_order_type(args.order_type)
		quantity = validate_quantity(args.quantity)
		price = validate_price(order_type, args.price)
		stop_price = validate_stop_price(order_type, args.stop_price)

		logger.info(
			"Validated input | symbol=%s side=%s type=%s quantity=%s price=%s stop_price=%s",
			symbol,
			side,
			order_type,
			quantity,
			price,
			stop_price,
		)

		client = get_futures_client()

		if order_type == "MARKET":
			result = place_market_order(
				client=client,
				symbol=symbol,
				side=side,
				quantity=quantity,
			)
		elif order_type == "LIMIT":
			result = place_limit_order(
				client=client,
				symbol=symbol,
				side=side,
				quantity=quantity,
				price=price,  # Guaranteed by validation for LIMIT orders.
			)
		else:
			result = place_stop_limit_order(
				client=client,
				symbol=symbol,
				side=side,
				quantity=quantity,
				price=price,  # Guaranteed by validation for STOP_LIMIT orders.
				stop_price=stop_price,  # Guaranteed by validation for STOP_LIMIT orders.
			)

		logger.info("Order created successfully | orderId=%s", result.get("orderId"))
		print(
			"Order placed successfully "
			f"(id={result.get('orderId')}, status={result.get('status')}, symbol={result.get('symbol')})"
		)
	except (KeyboardInterrupt, EOFError):
		logger.warning("Interactive session interrupted by user.")
		print("Input cancelled. No order submitted.")
		sys.exit(0)
	except ValueError as exc:
		logger.error("Validation error: %s", exc)
		print(f"Validation error: {exc}")
		sys.exit(2)
	except Exception as exc:
		logger.error("Failed to place order: %s", exc)
		print(f"Execution error: {exc}")
		sys.exit(1)


if __name__ == "__main__":
	main()
