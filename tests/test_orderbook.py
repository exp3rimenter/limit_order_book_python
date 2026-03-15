import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from orderbook import LimitOrderBook, Side
from orderbook.models import OrderStatus

@pytest.fixture
def book():
    return LimitOrderBook("TEST/USD")

class TestOrderPlacement:
    def test_bid_rests(self, book):
        o = book.add_limit_order(Side.BUY, 100.0, 5.0)
        assert o.status == OrderStatus.OPEN and book.best_bid() == 100.0
    def test_ask_rests(self, book):
        o = book.add_limit_order(Side.SELL, 105.0, 3.0)
        assert o.status == OrderStatus.OPEN and book.best_ask() == 105.0
    def test_invalid_price(self, book):
        with pytest.raises(ValueError): book.add_limit_order(Side.BUY, -1.0, 5.0)
    def test_invalid_qty(self, book):
        with pytest.raises(ValueError): book.add_limit_order(Side.BUY, 100.0, 0)

class TestSpread:
    def test_spread(self, book):
        book.add_limit_order(Side.BUY, 100.0, 5)
        book.add_limit_order(Side.SELL, 104.0, 5)
        assert book.spread() == 4.0
    def test_mid(self, book):
        book.add_limit_order(Side.BUY, 100.0, 5)
        book.add_limit_order(Side.SELL, 104.0, 5)
        assert book.mid_price() == 102.0
    def test_spread_none(self, book):
        book.add_limit_order(Side.BUY, 100.0, 5)
        assert book.spread() is None

class TestMatching:
    def test_full_match(self, book):
        book.add_limit_order(Side.SELL, 100.0, 5)
        buy = book.add_limit_order(Side.BUY, 100.0, 5)
        assert buy.status == OrderStatus.FILLED and len(book.trades) == 1
    def test_partial_match(self, book):
        book.add_limit_order(Side.SELL, 100.0, 3)
        buy = book.add_limit_order(Side.BUY, 100.0, 5)
        assert buy.status == OrderStatus.PARTIALLY_FILLED and buy.remaining_quantity == 2.0
    def test_no_match(self, book):
        book.add_limit_order(Side.BUY, 99.0, 5)
        book.add_limit_order(Side.SELL, 101.0, 5)
        assert len(book.trades) == 0
    def test_multi_level(self, book):
        book.add_limit_order(Side.SELL, 100.0, 2)
        book.add_limit_order(Side.SELL, 101.0, 3)
        book.add_limit_order(Side.SELL, 102.0, 4)
        buy = book.add_limit_order(Side.BUY, 102.0, 9)
        assert buy.status == OrderStatus.FILLED and len(book.trades) == 3
    def test_resting_price(self, book):
        book.add_limit_order(Side.SELL, 100.0, 5)
        book.add_limit_order(Side.BUY, 105.0, 5)
        assert book.trades[0].price == 100.0

class TestFIFO:
    def test_price_priority(self, book):
        o_low  = book.add_limit_order(Side.BUY, 99.0,  5)
        o_high = book.add_limit_order(Side.BUY, 101.0, 5)
        book.add_limit_order(Side.SELL, 99.0, 5)
        assert o_high.status == OrderStatus.FILLED and o_low.status == OrderStatus.OPEN
    def test_time_priority(self, book):
        o1 = book.add_limit_order(Side.BUY, 100.0, 3)
        o2 = book.add_limit_order(Side.BUY, 100.0, 3)
        book.add_limit_order(Side.SELL, 100.0, 3)
        assert o1.status == OrderStatus.FILLED and o2.status == OrderStatus.OPEN

class TestCancellation:
    def test_cancel(self, book):
        o = book.add_limit_order(Side.BUY, 100.0, 5)
        assert book.cancel_order(o.order_id) is True and o.status == OrderStatus.CANCELLED
    def test_cancel_missing(self, book):
        assert book.cancel_order(9999) is False
    def test_cancel_filled_fails(self, book):
        book.add_limit_order(Side.SELL, 100.0, 5)
        buy = book.add_limit_order(Side.BUY, 100.0, 5)
        assert book.cancel_order(buy.order_id) is False
    def test_cancelled_not_matched(self, book):
        o = book.add_limit_order(Side.BUY, 100.0, 5)
        book.cancel_order(o.order_id)
        book.add_limit_order(Side.SELL, 100.0, 5)
        assert len(book.trades) == 0

class TestStats:
    def test_vwap_single(self, book):
        book.add_limit_order(Side.SELL, 100.0, 4)
        book.add_limit_order(Side.BUY,  100.0, 4)
        assert book.vwap() == 100.0
    def test_vwap_multi(self, book):
        book.add_limit_order(Side.SELL, 100.0, 2)
        book.add_limit_order(Side.SELL, 110.0, 2)
        book.add_limit_order(Side.BUY,  110.0, 4)
        assert book.vwap() == pytest.approx(105.0)
    def test_vwap_none(self, book):
        assert book.vwap() is None
