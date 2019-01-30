import time
import logging
import logging.config
from decimal import Decimal

import config


logging.config.dictConfig(config.log_config)
logger = logging.getLogger(__name__)


class Order():

  def __init__(self, pair, side, size, price, test=False):
    self.pair = pair
    self.side = side
    self.size = Decimal(size)
    self.price = Decimal(price)
    self.status = "created"
    self.id = ""
    self.history = []
    self.responses = []
    self.test = test
    self.post_only = True
    self.filled = Decimal()

    self.update_history("Created")

  @property
  def pair(self):
    return self._pair

  @pair.setter
  def pair(self, value):

    self._pair = value
    self.base_pair = self.pair[:3]
    self.quote_pair = self.pair[4:]

    # Set Price rounding for USD pairs and non USD pairs
    if self.quote_pair == 'USD':
      self.price_decimals = 2
    else:
      self.price_decimals = 5

  @property
  def side(self):
    return self._side

  @side.setter
  def side(self, value):
    if value not in ["buy", "sell"]:
      raise ValueError("side must be 'buy' or 'sell'.")

    self._side = value

  @property
  def size(self):
    return self._size

  @size.setter
  def size(self, value):
    self._size = Decimal(value)

  @property
  def price(self):
    return self._price

  @price.setter
  def price(self, value):
    if type(value) not in [float, int, Decimal]:
      raise TypeError("{} is not a number".format(value))

    self._price = Decimal(round(value, self.price_decimals))

  def update_history(self, message):
    self.history.append(
      {"time": time.time(), "status": message}
    )

  def allow_market_trade(self):
    self.post_only = False

  def __str__(self):
    return (
      "pair: {}\n"
      "side: {}\n"
      "price: {}\n"
      "size: {}\n"
      "filled: {}\n"
      "status: {}\n"
      "id: {}\n"
      "test: {}\n"
      "history: {}\n"
      "responses: {}"
    ).format(
      self.pair,
      self.side,
      self.price,
      self.size,
      self.filled,
      self.status,
      self.id,
      self.test,
      self.history,
      self.responses
    )