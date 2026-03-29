from __future__ import annotations

import argparse
import sys

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
	parser.add_argument("--symbol", required=True, help="Trading pair symbol (e.g. BTCUSDT)")
	parser.add_argument("--side", required=True, help="Order side: BUY or SELL")
	parser.add_argument(
		"--type",
		dest="order_type",
		required=True,
		help="MARKET, LIMIT, or STOP_LIMIT",
	)
	parser.add_argument("--quantity", type=float, required=True, help="Order quantity")
	parser.add_argument("--price", type=float, help="Required when --type LIMIT or STOP_LIMIT")
	parser.add_argument(
		"--stop-price",
		type=float,
		help="Required when --type STOP_LIMIT",
	)
	return parser


def main() -> None:
	logger = configure_logging()
	parser = build_parser()

	try:
		args = parser.parse_args()

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
	except ValueError as exc:
		logger.error("Validation error: %s", exc)
		print(f"Validation error: {exc}")
		sys.exit(2)
	except Exception as exc:
		logger.exception("Failed to place order: %s", exc)
		print(f"Execution error: {exc}")
		sys.exit(1)


if __name__ == "__main__":
	main()
