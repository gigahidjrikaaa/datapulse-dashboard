"""Application configuration and constants for Global Superstore Analytics."""

from pathlib import Path
from typing import Final, Optional

# Directory Paths
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
DATA_DIR: Final[Path] = BASE_DIR / "data"
DEFAULT_DATASET_PATH: Final[Path] = DATA_DIR / "Global_Superstore2.csv"

# Dashboard Metadata
APP_TITLE: Final[str] = "Global Superstore: Strategic Performance Evaluation & Turnaround Plan"
APP_SUBTITLE: Final[str] = "Board of Directors Diagnostic: Commercial Governance, Unit Economics & Margin Optimization"
APP_ICON: Final[Optional[str]] = None
APP_LAYOUT: Final[str] = "wide"
APP_VERSION: Final[str] = "2.2.0"

# Visualization Color Palette (Restrained institutional executive palette)
PRIMARY_COLOR: Final[str] = "#2563EB"      # Enterprise Blue
SUCCESS_COLOR: Final[str] = "#059669"      # Forest Green
WARNING_COLOR: Final[str] = "#D97706"      # Muted Amber
DANGER_COLOR: Final[str] = "#DC2626"       # Crimson Red
ACCENT_PURPLE: Final[str] = "#7C3AED"      # Slate Purple
ACCENT_CYAN: Final[str] = "#0891B2"        # Slate Cyan

CHART_COLORWAY: Final[list[str]] = [
    PRIMARY_COLOR,
    SUCCESS_COLOR,
    ACCENT_PURPLE,
    WARNING_COLOR,
    ACCENT_CYAN,
    DANGER_COLOR,
]

CHART_TEMPLATE: Final[str] = "plotly_dark"

# Expected Schema Columns for Global Superstore
REQUIRED_COLUMNS: Final[list[str]] = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "City",
    "State",
    "Country",
    "Market",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
    "Shipping Cost",
    "Order Priority",
]
