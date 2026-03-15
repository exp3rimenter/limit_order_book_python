# Limit Order Book -- Python Project

A fully-tested Limit Order Book with price-time (FIFO) priority matching,
market simulator, interactive CLI, and pytest unit tests.

## Structure
```
orderbook_project/
├── orderbook/
│   ├── __init__.py
│   ├── models.py       # Order, Trade, Side, OrderStatus, PriceLevel
│   ├── book.py         # LimitOrderBook -- core matching engine
│   ├── simulator.py    # MarketSimulator
│   └── display.py      # Pretty-printing helpers
├── cli/
│   └── cli.py          # Interactive CLI
├── tests/
│   └── test_orderbook.py
├── demo.py
├── requirements.txt
└── README.md
```

## Quickstart
```bash
pip install -r requirements.txt
python demo.py            # full walkthrough
python cli/cli.py         # interactive CLI
pytest tests/ -v          # run all tests
```

## CLI Options
```bash
python cli/cli.py --symbol ETH/USD --price 2000 --seed 7
```

## CLI Commands
| Command          | Description                  |
|------------------|------------------------------|
| buy <p> <q>      | Place BUY limit order        |
| sell <p> <q>     | Place SELL limit order       |
| cancel <id>      | Cancel open order            |
| book [depth]     | Display order book           |
| trades [n]       | Show last N trades           |
| stats            | Market stats + VWAP          |
| history [n]      | Order history                |
| sim [steps]      | Run simulation steps         |
| help / quit      |                              |

## Key Concepts
- **Price-Time Priority (FIFO)**: best price matched first; FIFO within same price
- **Spread**: gap between best bid and best ask; crossing it triggers trades
- **VWAP**: volume-weighted average price of all executed trades
- **Order lifecycle**: OPEN -> PARTIALLY_FILLED -> FILLED | CANCELLED
