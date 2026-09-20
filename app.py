"""Main application entry point for the Global Superstore Strategic Performance Evaluation."""

import streamlit as st

from src.components.filters import render_sidebar_filters
from src.config import APP_LAYOUT, APP_SUBTITLE, APP_TITLE, APP_VERSION
from src.services.analyzer import filter_data
from src.services.data_loader import load_sales_data
from src.views.eda import render_eda_view
from src.views.executive_summary import render_executive_summary_view
from src.views.overview import render_overview_view
from src.views.revival_strategy import render_revival_strategy_view
from src.views.trends import render_trends_view


def main() -> None:
    """Initialize application layout, global state, navigation routing, and views."""
    st.set_page_config(
        page_title="Global Superstore | Strategic Diagnostic",
        page_icon=None,
        layout=APP_LAYOUT,
        initial_sidebar_state="expanded",
    )

    # Sidebar Header & Branding
    st.sidebar.title(APP_TITLE)
    st.sidebar.caption(f"{APP_SUBTITLE} | Version {APP_VERSION}")
    st.sidebar.markdown("---")

    # Data Source Selection
    st.sidebar.markdown("### Data Source Selection")
    data_source_mode = st.sidebar.radio(
        "Data Ingestion Mode",
        options=["Global Superstore Master File", "Upload Custom Dataset (CSV / Excel)"],
        label_visibility="collapsed",
    )

    raw_data_source = None
    if data_source_mode == "Upload Custom Dataset (CSV / Excel)":
        uploaded_file = st.sidebar.file_uploader(
            "Upload Transaction File",
            type=["csv", "xlsx", "xls"],
            help="Select an updated corporate transaction ledger.",
        )
        if uploaded_file is not None:
            raw_data_source = uploaded_file
        else:
            st.sidebar.info("Awaiting file upload. Reverting to primary Global Superstore ledger.")
            st.stop()

    # Load and Preprocess Data
    try:
        base_df = load_sales_data(raw_data_source)
    except Exception as exc:
        st.error(f"Data ingestion failure: {exc}")
        return

    # Render Filters
    filters = render_sidebar_filters(base_df)

    # Filter Data according to user criteria
    filtered_df = filter_data(
        df=base_df,
        date_range=filters.get("date_range"),
        markets=filters.get("markets"),
        categories=filters.get("categories"),
        segments=filters.get("segments"),
        years=filters.get("years"),
    )

    # Store filtered dataframe in session state for navigation views
    st.session_state["filtered_df"] = filtered_df
    st.session_state["raw_df"] = base_df

    # Define Navigation Pages mapped directly to the Advisory Deliverables
    def view_executive_summary() -> None:
        render_executive_summary_view(st.session_state["filtered_df"])

    def view_task1() -> None:
        render_overview_view(st.session_state["filtered_df"])

    def view_task2() -> None:
        render_eda_view(st.session_state["filtered_df"])

    def view_task3() -> None:
        render_trends_view(st.session_state["filtered_df"])

    def view_task4_5() -> None:
        render_revival_strategy_view(st.session_state["filtered_df"])

    # Streamlit Navigation Router (Strictly professional, zero emojis)
    page_nav = st.navigation(
        [
            st.Page(
                view_executive_summary,
                title="Executive Memorandum: Strategic Diagnostic",
                default=True,
            ),
            st.Page(
                view_task1,
                title="Section 1: Multi-Year Financial Performance Audit",
            ),
            st.Page(
                view_task2,
                title="Section 2: Geographic & Product Margin Variance",
            ),
            st.Page(
                view_task3,
                title="Section 3: Root Cause Diagnostic: Pricing & Logistics",
            ),
            st.Page(
                view_task4_5,
                title="Section 4: Strategic Turnaround Framework & Action Plan",
            ),
        ]
    )

    page_nav.run()


if __name__ == "__main__":
    main()
