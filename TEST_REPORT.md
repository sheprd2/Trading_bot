# Phase 3 Test Report

Date: 2026-03-28
Environment: Binance USDT-M Futures Testnet

## Summary

All required phase 3 scenarios were executed through the CLI.

## Test Cases

1. MARKET order

Command:

```bash
python bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Result:

- Exit code: 0
- Behavior: order request accepted and success path logged

2. LIMIT order

Command:

```bash
python bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 200000
```

Result:

- Exit code: 0
- Behavior: order created with status NEW in later verified run

3. Invalid side

Command:

```bash
python bot/cli.py --symbol BTCUSDT --side BAD --type MARKET --quantity 0.001
```

Result:

- Exit code: 2
- Validation error: invalid side

4. Missing price for LIMIT

Command:

```bash
python bot/cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
```

Result:

- Exit code: 2
- Validation error: price required for LIMIT

5. Wrong input (quantity <= 0)

Command:

```bash
python bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0
```

Result:

- Exit code: 2
- Validation error: quantity must be greater than 0

## Logging Verification

The file `logs/trading.log` contains:

- validated input records
- API request payloads
- API responses
- validation and execution errors

## Notes

- Local app logs are not shown on Binance website; only exchange orders and fills are shown there.
- After fixing the futures testnet base URL, open orders are visible through API and on testnet UI.
