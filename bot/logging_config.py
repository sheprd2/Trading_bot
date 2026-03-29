from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_file: str = "logs/trading.log") -> logging.Logger:
	"""Configure and return the bot logger used across modules."""
	log_path = Path(log_file)
	log_path.parent.mkdir(parents=True, exist_ok=True)

	logger = logging.getLogger("trading_bot")
	logger.setLevel(logging.INFO)

	# Avoid duplicate handlers when the CLI is invoked multiple times in-process.
	if logger.handlers:
		return logger

	file_handler = logging.FileHandler(log_path, encoding="utf-8")
	stream_handler = logging.StreamHandler()

	formatter = logging.Formatter(
		"%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)

	file_handler.setFormatter(formatter)
	stream_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)
	logger.propagate = False

	logger.info("Logging configured. Output file: %s", log_path)
	return logger
