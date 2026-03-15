from collections import deque
from typing import Optional
import itertools
from .models import Order, Trade, Side, OrderStatus, PriceLevel

class LimitOrderBook:
    def __init__(self, symbol):
        self.symbol = symbol
        self._order_id_gen = itertools.count(1)
        self._trade_id_gen = itertools.count(1)
        self._bids = {}
        self._asks = {}
        self._orders = {}
        self.trades = []

    def add_limit_order(self, side, price, quantity):
        if price <= 0 or quantity <= 0:
            raise ValueError("Price and quantity must be positive.")
        order = Order(order_id=next(self._order_id_gen), side=side,
                      price=round(price, 8), quantity=round(quantity, 8))
        self._orders[order.order_id] = order
        self._match(order)
        if order.is_active:
            book = self._bids if side == Side.BUY else self._asks
            book.setdefault(order.price, deque()).append(order)
        return order

    def cancel_order(self, order_id):
        order = self._orders.get(order_id)
        if order is None or not order.is_active:
            return False
        book = self._bids if order.side == Side.BUY else self._asks
        level = book.get(order.price)
        if level:
            try:
                level.remove(order)
            except ValueError:
                pass
            if not level:
                del book[order.price]
        order.cancel()
        return True

    def get_order(self, order_id):
        return self._orders.get(order_id)

    def best_bid(self):
        return max(self._bids) if self._bids else None

    def best_ask(self):
        return min(self._asks) if self._asks else None

    def spread(self):
        bb, ba = self.best_bid(), self.best_ask()
        return round(ba - bb, 8) if bb is not None and ba is not None else None

    def mid_price(self):
        bb, ba = self.best_bid(), self.best_ask()
        return round((bb + ba) / 2, 8) if bb is not None and ba is not None else None

    def bid_levels(self, depth=10):
        return self._levels(self._bids, reverse=True, depth=depth)

    def ask_levels(self, depth=10):
        return self._levels(self._asks, reverse=False, depth=depth)

    def total_bid_volume(self):
        return sum(o.remaining_quantity for q in self._bids.values() for o in q)

    def total_ask_volume(self):
        return sum(o.remaining_quantity for q in self._asks.values() for o in q)

    def open_orders(self):
        return [o for o in self._orders.values() if o.is_active]

    def order_history(self):
        return list(self._orders.values())

    def recent_trades(self, n=10):
        return self.trades[-n:]

    def vwap(self):
        if not self.trades:
            return None
        tv = sum(t.price * t.quantity for t in self.trades)
        tq = sum(t.quantity for t in self.trades)
        return round(tv / tq, 8)

    def stats(self):
        return {
            "symbol": self.symbol,
            "best_bid": self.best_bid(),
            "best_ask": self.best_ask(),
            "spread": self.spread(),
            "mid_price": self.mid_price(),
            "total_bid_volume": self.total_bid_volume(),
            "total_ask_volume": self.total_ask_volume(),
            "total_trades": len(self.trades),
            "vwap": self.vwap(),
            "open_orders": len(self.open_orders()),
        }

    def _match(self, incoming):
        if incoming.side == Side.BUY:
            opposite = self._asks
            get_sorted = lambda: sorted(opposite.keys())
            price_crosses = lambda best: incoming.price >= best
        else:
            opposite = self._bids
            get_sorted = lambda: sorted(opposite.keys(), reverse=True)
            price_crosses = lambda best: incoming.price <= best

        while incoming.remaining_quantity > 0:
            prices = get_sorted()
            if not prices or not price_crosses(prices[0]):
                break
            bp = prices[0]
            level = opposite[bp]
            while level and incoming.remaining_quantity > 0:
                resting = level[0]
                fq = round(min(incoming.remaining_quantity, resting.remaining_quantity), 8)
                trade = Trade(
                    trade_id=next(self._trade_id_gen),
                    buy_order_id=incoming.order_id if incoming.side == Side.BUY else resting.order_id,
                    sell_order_id=resting.order_id if incoming.side == Side.BUY else incoming.order_id,
                    price=bp, quantity=fq)
                self.trades.append(trade)
                incoming.fill(fq)
                resting.fill(fq)
                if not resting.is_active:
                    level.popleft()
            if not level:
                del opposite[bp]

    def _levels(self, book, reverse, depth):
        prices = sorted(book.keys(), reverse=reverse)[:depth]
        return [PriceLevel(p, sum(o.remaining_quantity for o in book[p]), len(book[p])) for p in prices]

    def display(self, depth=8):
        W = 56
        asks = self.ask_levels(depth)
        bids = self.bid_levels(depth)
        sp = self.spread()
        mid = self.mid_price()
        print(f"\n{'━'*W}")
        print(f"  Order Book -- {self.symbol}".center(W))
        print(f"{'━'*W}")
        print(f"  {'Price':>12}  {'Qty':>12}  {'Side':>6}")
        print(f"  {'─'*12}  {'─'*12}  {'─'*6}")
        for lvl in reversed(asks):
            print(f"  {lvl.price:>12.4f}  {lvl.total_quantity:>12.4f}  {'ASK':>6}  (orders: {lvl.order_count})")
        sp_str = f"Spread: {sp:.4f}  |  Mid: {mid:.4f}" if sp is not None else "No spread"
        print(f"{'─'*W}")
        print(sp_str.center(W))
        print(f"{'─'*W}")
        for lvl in bids:
            print(f"  {lvl.price:>12.4f}  {lvl.total_quantity:>12.4f}  {'BID':>6}  (orders: {lvl.order_count})")
        print(f"{'━'*W}\n")
