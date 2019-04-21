import logging
import logging.config

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from . import trading
from .order import Order
import config
from ..database.manager import (
  BaseWrapper, Engine, Test_Engine, test_session, session
)
logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)
JOIN_STRING = "and_(Book.id==Order.book_id, Order._status=={})"


class Book(BaseWrapper):

  pair = Column("pair", String(15))
  orders = relationship(Order, lazy="dynamic", collection_class=set)

  # dynamic_loader()
  # collection_class=attribute_mapped_collection('exchange_id')
  # ready_orders = orders.filter(Order.status == "ready")
  # open_orders = orders.filter(Order.status == "open")
  # filled_orders = orders.filter(Order.status == "filled")
  # rejected_orders = orders.filter(Order.status == "rejected")
  # cancel_orders = orders.filter(Order.status == "canceled")

  def __init__(self, pair, persist=True, test=True):

    self.pair = pair
    self.ready_orders = []
    self.open_orders = []
    self.filled_orders = []
    self.canceled_orders = []
    self.persist = persist
    self.test = test
    logger.debug("Book.test: {}".format(self.test))

  def add_order(self, side, size, price, post_only=True):
    order = Order(
      self.pair, side, size, price, post_only=post_only,
      persist=self.persist, test=self.test
    )
    self.ready_orders.append(order)
    if self.persist:
      order.save()

  def send_orders(self):
    while len(self.ready_orders) > 0:
      order = self.ready_orders.pop()
      trading.send_order(order)
      order.status = "pending"
      trading.confirm_order(order)
      order.status = "open"
      self.open_orders.append(order)

  def cancel_all_orders(self):
    self.cancel_order_list(self.open_orders)

  def cancel_order_list(self, order_list):
    while len(self.open_orders) > 0:
      order = self.open_orders.pop()
      trading.cancel_order(order)
      order.status = "canceled"
      self.canceled_orders.append(order)

  def order_filled(self, order_id):
    filled_order = next(
      order for order in self.open_orders if order.exchange_id == order_id
    )
    self.open_orders.remove(filled_order)
    self.filled_orders.append(filled_order)

    filled_order.status = "filled"
    if self.persist:
      filled_order.save()
      filled_order.session.commit()

    return filled_order
