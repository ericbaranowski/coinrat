from typing import List, Dict

from coinrat.domain.candle import Candle
from coinrat.domain.order import Order
from coinrat.domain.portfolio import PortfolioSnapshot
from coinrat.domain.strategy import StrategyRun


class EventEmitter:
    def emit_new_candles(self, candle_storage: str, candles: List[Candle]) -> None:
        raise NotImplementedError()

    def emit_new_order(self, order_storage: str, order: Order, portfolio_snapshot: PortfolioSnapshot) -> None:
        raise NotImplementedError()

    def emit_event(self, event: Dict) -> None:
        raise NotImplementedError()

    def emit_new_strategy_run(self, strategy_run: StrategyRun):
        raise NotImplementedError()
