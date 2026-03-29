from __future__ import annotations

import logging
import os

from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv


TESTNET_BASE_URL = "https://testnet.binancefuture.com/fapi"
LOGGER = logging.getLogger("trading_bot")


def get_futures_client() -> Client:
	"""Create a Binance client configured for USDT-M Futures Testnet."""
	load_dotenv()

	api_key = os.getenv("BINANCE_API_KEY", "").strip()
	api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

	if not api_key or not api_secret:
		raise ValueError(
			"Missing BINANCE_API_KEY or BINANCE_API_SECRET in environment variables."
		)

	client = Client(api_key=api_key, api_secret=api_secret)
	client.FUTURES_URL = TESTNET_BASE_URL

	# Validate connectivity early so CLI fails fast with a clear error.
	try:
		client.futures_ping()
		LOGGER.info("Connected to Binance Futures Testnet successfully.")
	except BinanceAPIException as exc:
		LOGGER.error("Failed to connect to Binance Futures Testnet: %s", exc)
		raise

	return client
