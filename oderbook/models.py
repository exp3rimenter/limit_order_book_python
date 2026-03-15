from dataclasses import dataclass, field
from enum import Enum
import time

class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

@dataclass
class Order:
    order_id: int
    side: Side
    price: float
    quantity: float
    timestamp: float = field(default_factory=time.time)
    filled_quantity: float = field(default=0.0)
    status: OrderStatus = field(default=OrderStatus.OPEN)

    @property
    def remaining_quantity(self):
        return self.quantity - self.filled_quantity

    @property
    def is_active(self):
        return self.status in (OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED)

    def fill(self, qty):
        self.filled_quantity += qty
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED

    def cancel(self):
        self.status = OrderStatus.CANCELLED

    def __repr__(self):
        return (f"Order(id={self.order_id}, {self.side.value}, price={self.price:.2f}, "
                f"qty={self.quantity}, filled={self.filled_quantity}, status={self.status.value})")

@dataclass
class Trade:
    trade_id: int
    buy_order_id: int
    sell_order_id: int
    price: float
    quantity: float
    timestamp: float = field(default_factory=time.time)

    def __repr__(self):
        return (f"Trade(id={self.trade_id}, buy#{self.buy_order_id} x sell#{self.sell_order_id}, "
                f"price={self.price:.2f}, qty={self.quantity})")

@dataclass
class PriceLevel:
    price: float
    total_quantity: float
    order_count: int
