import datetime
import dateutil.parser

from decimal import Decimal
from typing import Union, Dict, List
from uuid import UUID

from coinrat.domain.coinrat import ForEndUserException
from coinrat.domain.pair import Pair, deserialize_pair, serialize_pair

ORDER_TYPE_LIMIT = 'limit'
ORDER_TYPE_MARKET = 'market'

DIRECTION_SELL = 'sell'
DIRECTION_BUY = 'buy'

ORDER_STATUS_OPEN = 'open'
ORDER_STATUS_CLOSED = 'closed'
ORDER_STATUS_CANCELED = 'canceled'
POSSIBLE_ORDER_STATUSES = [ORDER_STATUS_OPEN, ORDER_STATUS_CLOSED, ORDER_STATUS_CANCELED]

ORDER_FIELD_ORDER_ID = 'order_id'
ORDER_FIELD_STRATEGY_RUN_ID = 'strategy_run_id'
ORDER_FIELD_MARKET = 'market'
ORDER_FIELD_DIRECTION = 'direction'
ORDER_FIELD_CREATED_AT = 'created_at'
ORDER_FIELD_PAIR = 'pair'
ORDER_FIELD_TYPE = 'type'
ORDER_FIELD_QUANTITY = 'quantity'
ORDER_FIELD_RATE = 'rate'
ORDER_FIELD_ID_ON_MARKET = 'id_on_market'
ORDER_FIELD_STATUS = 'status'
ORDER_FIELD_CLOSED_AT = 'closed_at'
ORDER_FIELD_CANCELED_AT = 'canceled_at'


class NotEnoughBalanceToPerformOrderException(ForEndUserException):
    pass


class Order:
    def __init__(
        self,
        order_id: UUID,
        strategy_run_id: UUID,
        market_name: str,
        direction: str,
        created_at: datetime.datetime,
        pair: Pair,
        order_type: str,
        quantity: Decimal,
        rate: Union[Decimal, None] = None,
        market_id: Union[str, None] = None,
        status: str = ORDER_STATUS_OPEN,
        closed_at: Union[datetime.datetime, None] = None,
        canceled_at: Union[datetime.datetime, None] = None,
    ) -> None:
        assert '+00:00' in created_at.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(created_at.isoformat()))

        assert order_type in [ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET], 'Unknown type of order: "{}".'.format(order_type)
        assert isinstance(quantity, Decimal)

        if order_type == ORDER_TYPE_LIMIT:
            assert isinstance(rate, Decimal)
        if order_type == ORDER_TYPE_MARKET:
            assert rate is None, 'For market orders, rate must be None (does not make sense).'

        assert status in POSSIBLE_ORDER_STATUSES

        assert status == ORDER_STATUS_CLOSED and closed_at is not None or closed_at is None
        assert status == ORDER_STATUS_CANCELED and canceled_at is not None or canceled_at is None

        assert direction in [DIRECTION_SELL, DIRECTION_BUY]

        self._order_id = order_id
        self._strategy_run_id = strategy_run_id
        self._market_name = market_name
        self._created_at = created_at
        self._direction = direction
        self._pair = pair
        self._type = order_type
        self._quantity = quantity
        self._rate = rate
        self._id_on_market = market_id
        self._status = status
        self._closed_at = closed_at
        self._canceled_at = canceled_at

    def is_sell(self) -> bool:
        return self._direction == DIRECTION_SELL

    def is_buy(self) -> bool:
        return self._direction == DIRECTION_BUY

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def strategy_run_id(self) -> UUID:
        return self._strategy_run_id

    @property
    def market_name(self) -> str:
        return self._market_name

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @property
    def pair(self) -> Pair:
        return self._pair

    @property
    def type(self) -> str:
        return self._type

    @property
    def rate(self) -> Union[Decimal, None]:
        """How much BASE CURRENCY I need to buy 1 MARKET CURRENCY"""
        return self._rate

    @property
    def quantity(self) -> Decimal:
        """Always in MARKET CURRENCY"""
        return self._quantity

    @property
    def id_on_market(self) -> Union[str, None]:
        return self._id_on_market

    @property
    def is_open(self) -> bool:
        """Open means, it's placed on the marked, ready to be processed if condition (price, ...) met."""
        return self._status == ORDER_STATUS_OPEN

    @property
    def is_closed(self) -> bool:
        """Closed means, this deal is done. Money transferred. It's SUCCESSFULLY done."""
        return self._status == ORDER_STATUS_CLOSED

    @property
    def closed_at(self) -> Union[datetime.datetime, None]:
        return self._closed_at

    @property
    def is_canceled(self) -> bool:
        """Order was cancelled before it proceeds."""
        return self._status == ORDER_STATUS_CANCELED

    @property
    def canceled_at(self) -> Union[datetime.datetime, None]:
        return self._canceled_at

    def set_id_on_market(self, id_on_market: str) -> None:
        self._id_on_market = id_on_market

    def close(self, closed_at: datetime.datetime) -> None:
        self._status = ORDER_STATUS_CLOSED
        self._closed_at = closed_at

    def cancel(self, canceled_at: datetime.datetime):
        self._status = ORDER_STATUS_CANCELED
        self._canceled_at = canceled_at

    def __repr__(self) -> str:
        return (
            '{0}-{1}, '
            + 'Id: "{2}", '
            + 'Market: "{3}", '
            + 'Created: "{4}", '
            + 'Closed: "{5}", '
            + 'ID on market: "{6}", '
            + 'Pair: [{7}], '
            + 'Type: "{8}", '
            + 'Rate: "{9}", '
            + 'Quantity: "{10:.8f}"'
        ).format(
            self._direction.upper(),
            self._status.upper(),
            self._order_id,
            self._market_name,
            self._created_at.isoformat(),
            self._closed_at.isoformat() if self._closed_at is not None else 'None',
            self._id_on_market,
            self._pair,
            self._type,
            '{0:.8f}'.format(self._rate) if self._rate is not None else 'None',
            self._quantity
        )


def serialize_order(order: Order) -> Dict[str, Union[str, None]]:
    return {
        ORDER_FIELD_ORDER_ID: str(order.order_id),
        ORDER_FIELD_STRATEGY_RUN_ID: str(order.strategy_run_id),
        ORDER_FIELD_MARKET: order.market_name,
        ORDER_FIELD_DIRECTION: order._direction,
        ORDER_FIELD_CREATED_AT: order.created_at.isoformat(),
        ORDER_FIELD_PAIR: serialize_pair(order.pair),
        ORDER_FIELD_TYPE: order.type,
        ORDER_FIELD_QUANTITY: str(order.quantity),
        ORDER_FIELD_RATE: str(order.rate),
        ORDER_FIELD_ID_ON_MARKET: order.id_on_market,
        ORDER_FIELD_STATUS: order._status,
        ORDER_FIELD_CLOSED_AT: order.closed_at.isoformat() if order.closed_at is not None else None,
        ORDER_FIELD_CANCELED_AT: order.canceled_at.isoformat() if order.canceled_at is not None else None,
    }


def serialize_orders(orders: List[Order]) -> List[Dict[str, Union[str, None]]]:
    return list(map(serialize_order, orders))


def deserialize_order(serialized: Dict) -> Order:
    closed_at = serialized[ORDER_FIELD_CLOSED_AT]
    if closed_at is not None:
        closed_at = dateutil.parser.parse(closed_at).replace(tzinfo=datetime.timezone.utc)

    canceled_at = serialized[ORDER_FIELD_CANCELED_AT]
    if canceled_at is not None:
        canceled_at = dateutil.parser.parse(canceled_at).replace(tzinfo=datetime.timezone.utc)

    return Order(
        UUID(serialized[ORDER_FIELD_ORDER_ID]),
        UUID(serialized[ORDER_FIELD_STRATEGY_RUN_ID]),
        serialized[ORDER_FIELD_MARKET],
        serialized[ORDER_FIELD_DIRECTION],
        dateutil.parser.parse(serialized[ORDER_FIELD_CREATED_AT]).replace(tzinfo=datetime.timezone.utc),
        deserialize_pair(serialized[ORDER_FIELD_PAIR]),
        serialized[ORDER_FIELD_TYPE],
        Decimal(serialized[ORDER_FIELD_QUANTITY]),
        Decimal(serialized[ORDER_FIELD_RATE]),
        serialized[ORDER_FIELD_ID_ON_MARKET],
        serialized[ORDER_FIELD_STATUS],
        closed_at,
        canceled_at
    )


def deserialize_orders(serialized_orders: List[Dict]) -> List[Order]:
    return list(map(deserialize_order, serialized_orders))


class OrderMarketInfo:
    def __init__(
        self,
        order: Order,
        is_open: bool,
        closed_at: Union[datetime.datetime, None],
        quantity_remaining: Decimal
    ) -> None:
        self._order = order
        self._is_open = is_open
        self._closed_at = closed_at
        self._quantity_remaining = quantity_remaining

    @property
    def order(self) -> Order:
        return self._order

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def closed_at(self) -> datetime.datetime:
        return self._closed_at

    @property
    def quantity_remaining(self) -> Decimal:
        return self._quantity_remaining

    def __repr__(self) -> str:
        return (
            'Order Id: "{}", '
            + '{}, '
            + 'Closed at: "{}", '
            + 'Remaining quantity: "{}"'
        ).format(
            self._order.order_id,
            'OPEN' if self._is_open else 'CLOSED',
            self._closed_at.isoformat() if self._closed_at is not None else '',
            self._quantity_remaining
        )
