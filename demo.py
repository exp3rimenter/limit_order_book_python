"""demo.py -- Full walkthrough. Run: python demo.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orderbook import LimitOrderBook, Side
from orderbook.simulator import MarketSimulator
from orderbook.display import print_trades, print_stats, print_order_history

def section(t):
    print(f"\n{'='*56}\n  {t}\n{'='*56}")

def main():
    book = LimitOrderBook("BTC/USD")
    sim  = MarketSimulator(book, base_price=100.0, spread_ticks=4, seed=1)

    section("1. Seed book with resting orders")
    sim.seed_book(levels=5, qty_range=(1, 8))
    book.display()

    section("2. Place manual limit orders")
    o1 = book.add_limit_order(Side.BUY,  98.0, 5)
    o2 = book.add_limit_order(Side.SELL, 104.0, 3)
    print(f"  {o1}\n  {o2}")
    book.display()

    section("3. Aggressive BUY crosses spread -> trades fire")
    ba = book.best_ask()
    print(f"  Best ask: {ba:.4f}")
    ag = book.add_limit_order(Side.BUY, ba + 1.0, 10)
    print(f"  Aggressive order: {ag}")
    book.display()
    print_trades(book.recent_trades(5))

    section("4. Cancel an open order")
    oo = book.open_orders()
    if oo:
        t = oo[0]
        print(f"  Cancelling #{t.order_id} ({t.side.value} @ {t.price})")
        book.cancel_order(t.order_id)
        book.display()

    section("5. Run 30 simulation steps")
    sim.run(steps=30)
    book.display()

    section("6. Market statistics")
    print_stats(book)

    section("7. Order history (last 15)")
    print_order_history(book, limit=15)

    section(f"8. All trades ({len(book.trades)} total)")
    print_trades(book.trades)

if __name__ == "__main__":
    main()
