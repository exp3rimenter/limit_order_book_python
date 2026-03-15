"""
Interactive CLI for the Limit Order Book.
Usage: python cli/cli.py [--symbol SYM] [--price N] [--seed N]
"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orderbook import LimitOrderBook, Side
from orderbook.simulator import MarketSimulator
from orderbook.display import print_trades, print_stats, print_order_history

HELP = """
+------------------------------------------------------+
|          Limit Order Book  --  Interactive CLI       |
+------------------------------------------------------+
|  buy  <price> <qty>    Place a BUY limit order       |
|  sell <price> <qty>    Place a SELL limit order      |
|  cancel <id>           Cancel an open order          |
|  book [depth]          Display order book            |
|  trades [n]            Show last N trades            |
|  stats                 Market statistics + VWAP      |
|  history [n]           Order history                 |
|  sim [steps]           Run simulation steps          |
|  help                  This menu                     |
|  quit                  Exit                          |
+------------------------------------------------------+
"""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTC/USD")
    p.add_argument("--price",  default=100.0, type=float)
    p.add_argument("--seed",   default=42, type=int)
    args = p.parse_args()

    book = LimitOrderBook(args.symbol)
    sim  = MarketSimulator(book, base_price=args.price, seed=args.seed)
    print(f"\n  Limit Order Book CLI  |  {args.symbol}")
    print("  Seeding book...\n")
    sim.seed_book(levels=5)
    book.display()
    print(HELP)

    while True:
        try:
            raw = input("  >> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break
        if not raw:
            continue
        parts = raw.split()
        cmd   = parts[0].lower()
        try:
            if cmd in ("quit", "exit", "q"):
                print("  Goodbye!"); break
            elif cmd == "help":
                print(HELP)
            elif cmd == "book":
                book.display(int(parts[1]) if len(parts) > 1 else 8)
            elif cmd == "buy":
                if len(parts) < 3: print("  Usage: buy <price> <qty>"); continue
                print(f"  {book.add_limit_order(Side.BUY, float(parts[1]), float(parts[2]))}")
            elif cmd == "sell":
                if len(parts) < 3: print("  Usage: sell <price> <qty>"); continue
                print(f"  {book.add_limit_order(Side.SELL, float(parts[1]), float(parts[2]))}")
            elif cmd == "cancel":
                if len(parts) < 2: print("  Usage: cancel <id>"); continue
                oid = int(parts[1])
                ok  = book.cancel_order(oid)
                print(f"  {'Cancelled' if ok else 'Not found / already closed'}: #{oid}")
            elif cmd == "trades":
                print_trades(book.recent_trades(int(parts[1]) if len(parts) > 1 else 10))
            elif cmd == "stats":
                print_stats(book)
            elif cmd == "history":
                print_order_history(book, int(parts[1]) if len(parts) > 1 else 20)
            elif cmd == "sim":
                steps = int(parts[1]) if len(parts) > 1 else 10
                sim.run(steps=steps)
                print(f"  Done -- {len(book.trades)} total trades.")
                book.display()
            else:
                print(f"  Unknown command '{cmd}'. Type 'help'.")
        except ValueError as e:
            print(f"  Invalid input: {e}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()
