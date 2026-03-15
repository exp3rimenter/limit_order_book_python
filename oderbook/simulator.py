import random
import time
from .book import LimitOrderBook
from .models import Side

class MarketSimulator:
    """Simulates random market participants placing limit orders."""

    def __init__(self, book, base_price=100.0, tick_size=0.01,
                 spread_ticks=4, volatility=0.05, seed=None):
        self.book = book
        self.base_price = base_price
        self.tick_size = tick_size
        self.spread_ticks = spread_ticks
        self.volatility = volatility
        self._rng = random.Random(seed)

    def seed_book(self, levels=5, qty_range=(1, 10)):
        """Populate both sides of the book with resting orders."""
        half = self.spread_ticks * self.tick_size / 2
        bb = round(self.base_price - half, 8)
        ba = round(self.base_price + half, 8)
        for i in range(levels):
            self.book.add_limit_order(Side.BUY,  round(bb - i * self.tick_size, 8),
                                      round(self._rng.uniform(*qty_range), 2))
            self.book.add_limit_order(Side.SELL, round(ba + i * self.tick_size, 8),
                                      round(self._rng.uniform(*qty_range), 2))

    def step(self):
        """Simulate one market event (passive 70%, aggressive 30%)."""
        mid = self.book.mid_price() or self.base_price
        mid = round(mid + self._rng.gauss(0, self.volatility), 8)
        side = self._rng.choice([Side.BUY, Side.SELL])
        qty  = round(self._rng.uniform(0.5, 5.0), 2)
        aggr = self._rng.random() < 0.3
        if aggr:
            if side == Side.BUY:
                p = round((self.book.best_ask() or mid) + self._rng.uniform(0, 0.5), 4)
            else:
                p = round((self.book.best_bid() or mid) - self._rng.uniform(0, 0.5), 4)
        else:
            off = self._rng.uniform(0.01, 1.0)
            p = round(mid - off if side == Side.BUY else mid + off, 4)
        if p > 0:
            self.book.add_limit_order(side, p, qty)

    def run(self, steps=20, delay=0.0):
        """Run N simulation steps."""
        for _ in range(steps):
            self.step()
            if delay:
                time.sleep(delay)
