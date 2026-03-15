def print_trades(trades, title="Recent Trades"):
    W = 60
    print(f"\n{'━'*W}")
    print(f"  {title}".center(W))
    print(f"{'━'*W}")
    if not trades:
        print("  (no trades yet)".center(W))
    else:
        print(f"  {'ID':>4}  {'Buy#':>6}  {'Sell#':>6}  {'Price':>10}  {'Qty':>10}")
        print(f"  {'─'*4}  {'─'*6}  {'─'*6}  {'─'*10}  {'─'*10}")
        for t in trades:
            print(f"  {t.trade_id:>4}  {t.buy_order_id:>6}  {t.sell_order_id:>6}  "
                  f"{t.price:>10.4f}  {t.quantity:>10.4f}")
    print(f"{'━'*W}\n")


def print_stats(book):
    s = book.stats()
    W = 50
    print(f"\n{'━'*W}")
    print(f"  Stats -- {s['symbol']}".center(W))
    print(f"{'━'*W}")
    for label, val, fmt in [
        ("Best Bid",     s["best_bid"],         ".4f"),
        ("Best Ask",     s["best_ask"],         ".4f"),
        ("Spread",       s["spread"],           ".4f"),
        ("Mid Price",    s["mid_price"],        ".4f"),
        ("VWAP",         s["vwap"],             ".4f"),
        ("Bid Volume",   s["total_bid_volume"], ".4f"),
        ("Ask Volume",   s["total_ask_volume"], ".4f"),
        ("Open Orders",  s["open_orders"],      "d"),
        ("Total Trades", s["total_trades"],     "d"),
    ]:
        val_str = f"{val:{fmt}}" if val is not None else "N/A"
        print(f"  {label:<18} {val_str:>14}")
    print(f"{'━'*W}\n")


def print_order_history(book, limit=20):
    orders = book.order_history()[-limit:]
    W = 72
    print(f"\n{'━'*W}")
    print(f"  Order History (last {limit})".center(W))
    print(f"{'━'*W}")
    print(f"  {'ID':>4}  {'Side':<5}  {'Price':>10}  {'Qty':>8}  {'Filled':>8}  Status")
    print(f"  {'─'*4}  {'─'*5}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*16}")
    for o in orders:
        print(f"  {o.order_id:>4}  {o.side.value:<5}  {o.price:>10.4f}  "
              f"{o.quantity:>8.4f}  {o.filled_quantity:>8.4f}  {o.status.value}")
    print(f"{'━'*W}\n")
