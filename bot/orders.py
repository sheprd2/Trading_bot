from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException


@dataclass
class OrderRequest:
	symbol: str
	side: str
	order_type: str
	quantity: float
	price: float | None = None


LOGGER = logging.getLogger("trading_bot")


def place_market_order(client: Client, symbol: str, side: str, quantity: float) -> dict[str, Any]:
	"""Place a MARKET order on Binance USDT-M futures."""
	payload = {
		"symbol": symbol,
		"side": side,
		"type": "MARKET",
		"newOrderRespType": "RESULT",
		"quantity": quantity,
	}
	LOGGER.info("API request | futures_create_order | payload=%s", payload)
	try:
		response = client.futures_create_order(**payload)
		LOGGER.info("API response | futures_create_order | %s", response)
		return response
	except (BinanceAPIException, BinanceOrderException) as exc:
		LOGGER.exception("Binance order error for MARKET order: %s", exc)
		raise


def place_limit_order(
	client: Client,
	symbol: str,
	side: str,
	quantity: float,
	price: float,
) -> dict[str, Any]:
	"""Place a LIMIT order on Binance USDT-M futures."""
	payload = {
		"symbol": symbol,
		"side": side,
		"type": "LIMIT",
		"timeInForce": "GTC",
		"newOrderRespType": "RESULT",
		"quantity": quantity,
		"price": price,
	}
	LOGGER.info("API request | futures_create_order | payload=%s", payload)
	try:
		response = client.futures_create_order(**payload)
		LOGGER.info("API response | futures_create_order | %s", response)
		return response
	except (BinanceAPIException, BinanceOrderException) as exc:
		LOGGER.exception("Binance order error for LIMIT order: %s", exc)
		raise
