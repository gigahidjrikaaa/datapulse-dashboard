"""Views package for dashboard page layouts."""

from src.views.data_explorer import render_data_explorer_view
from src.views.eda import render_eda_view
from src.views.executive_summary import render_executive_summary_view
from src.views.overview import render_overview_view
from src.views.revival_strategy import render_revival_strategy_view
from src.views.trends import render_trends_view

__all__ = [
    "render_data_explorer_view",
    "render_eda_view",
    "render_executive_summary_view",
    "render_overview_view",
    "render_revival_strategy_view",
    "render_trends_view",
]
