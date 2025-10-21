"""
Nitro Price Comparison Dashboard
Main Streamlit application
"""

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from io import BytesIO
from typing import Optional
from data_handler import DataHandler
from scrapers import ScraperManager
from config import (
    NITRO_ORANGE, NITRO_BLACK, NITRO_GREY, NITRO_LIGHT_GREY,
    COLOR_CHEAPER, COLOR_MORE_EXPENSIVE, COLOR_EQUAL, COLOR_NO_DATA,
    COMPETITORS, EXPORT_FILENAME_PREFIX, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
)


# Page configuration
st.set_page_config(
    page_title="Nitro Price Comparison",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for Nitro branding
def load_custom_css():
    st.markdown(f"""
    <style>
        /* Nitro branding colors */
        :root {{
            --nitro-orange: {NITRO_ORANGE};
            --nitro-black: {NITRO_BLACK};
            --nitro-grey: {NITRO_GREY};
        }}

        /* Main header */
        .main-header {{
            background: linear-gradient(135deg, {NITRO_BLACK} 0%, {NITRO_GREY} 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .main-header h1 {{
            margin: 0;
            color: white;
            font-size: 2.5rem;
        }}

        .main-header .tagline {{
            color: {NITRO_ORANGE};
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }}

        /* Price comparison table */
        .price-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.9rem;
        }}

        .price-table th {{
            background-color: {NITRO_BLACK};
            color: white;
            padding: 12px;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 10;
            border: 1px solid {NITRO_GREY};
        }}

        .price-table td {{
            padding: 10px;
            border: 1px solid {NITRO_LIGHT_GREY};
        }}

        .price-table tr:hover {{
            background-color: #f5f5f5;
        }}

        /* Price cells with color coding */
        .price-cheaper {{
            background-color: {COLOR_CHEAPER};
            color: white;
            font-weight: bold;
            padding: 8px;
            border-radius: 5px;
            text-align: center;
        }}

        .price-more-expensive {{
            background-color: {COLOR_MORE_EXPENSIVE};
            color: white;
            font-weight: bold;
            padding: 8px;
            border-radius: 5px;
            text-align: center;
        }}

        .price-equal {{
            background-color: {COLOR_EQUAL};
            color: white;
            font-weight: bold;
            padding: 8px;
            border-radius: 5px;
            text-align: center;
        }}

        .price-no-data {{
            background-color: {COLOR_NO_DATA};
            color: white;
            padding: 8px;
            border-radius: 5px;
            text-align: center;
        }}

        /* Confidence badges */
        .confidence-high {{
            background-color: {COLOR_CHEAPER};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
        }}

        .confidence-medium {{
            background-color: {COLOR_EQUAL};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
        }}

        .confidence-low {{
            background-color: {COLOR_MORE_EXPENSIVE};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
        }}

        /* Buttons */
        .stButton > button {{
            background-color: {NITRO_ORANGE};
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            transition: all 0.3s;
        }}

        .stButton > button:hover {{
            background-color: {NITRO_BLACK};
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}

        /* Metrics */
        .metric-card {{
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid {NITRO_ORANGE};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}

        /* Sidebar */
        .css-1d391kg {{
            background-color: {NITRO_LIGHT_GREY};
        }}

        /* Data freshness indicator */
        .freshness-recent {{
            color: {COLOR_CHEAPER};
            font-weight: bold;
        }}

        .freshness-stale {{
            color: {COLOR_EQUAL};
            font-weight: bold;
        }}

        .freshness-old {{
            color: {COLOR_MORE_EXPENSIVE};
            font-weight: bold;
        }}

    </style>
    """, unsafe_allow_html=True)


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        diff = now - dt

        if diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min ago", "freshness-recent"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hours ago", "freshness-stale"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days} days ago", "freshness-old"
    except:
        return "Unknown", "freshness-old"


def calculate_price_difference(nitro_price: float, competitor_price: float) -> tuple:
    """Calculate price difference and percentage"""
    if competitor_price is None or nitro_price is None:
        return None, None

    diff = nitro_price - competitor_price
    pct = (diff / nitro_price) * 100
    return diff, pct


def get_price_class(nitro_price: float, competitor_price: Optional[float]) -> str:
    """Get CSS class for price cell based on comparison"""
    if competitor_price is None:
        return "price-no-data"

    diff_pct = ((nitro_price - competitor_price) / nitro_price) * 100

    if abs(diff_pct) < 1:
        return "price-equal"
    elif diff_pct > 0:
        return "price-cheaper"  # We're more expensive (competitor is cheaper)
    else:
        return "price-more-expensive"  # We're cheaper (competitor is more expensive)


def get_confidence_badge(confidence: float) -> str:
    """Get HTML badge for confidence score"""
    if confidence >= CONFIDENCE_HIGH:
        return f'<span class="confidence-high">High ({confidence:.0%})</span>'
    elif confidence >= CONFIDENCE_MEDIUM:
        return f'<span class="confidence-medium">Med ({confidence:.0%})</span>'
    else:
        return f'<span class="confidence-low">Low ({confidence:.0%})</span>'


def render_header():
    """Render the main header with branding"""
    st.markdown("""
    <div class="main-header">
        <h1>🔧 Nitro Price Comparison</h1>
        <div class="tagline">Real-time competitor pricing intelligence</div>
    </div>
    """, unsafe_allow_html=True)


def export_to_excel(df: pd.DataFrame, data_handler: DataHandler) -> BytesIO:
    """Export comparison data to Excel with formatting"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write main comparison data
        df.to_excel(writer, sheet_name='Price Comparison', index=False)

        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Price Comparison']

        # Add formatting
        from openpyxl.styles import Font, PatternFill, Alignment

        # Header formatting
        header_fill = PatternFill(start_color=NITRO_BLACK.replace('#', ''),
                                 end_color=NITRO_BLACK.replace('#', ''),
                                 fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')

        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Add metadata sheet
        cache_stats = data_handler.get_cache_stats()
        metadata_df = pd.DataFrame([
            ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Products', len(df)],
            ['Total Cached Prices', cache_stats['total_entries']],
            ['', ''],
            ['Competitor', 'Cached Entries'],
        ] + [[comp, count] for comp, count in cache_stats['by_competitor'].items()])

        metadata_df.to_excel(writer, sheet_name='Metadata', index=False, header=False)

    output.seek(0)
    return output


def main():
    """Main application"""

    # Load custom CSS
    load_custom_css()

    # Render header
    render_header()

    # Initialize session state
    if 'data_handler' not in st.session_state:
        st.session_state.data_handler = DataHandler()

    if 'scraper_manager' not in st.session_state:
        st.session_state.scraper_manager = ScraperManager()

    if 'comparison_df' not in st.session_state:
        st.session_state.comparison_df = None

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1A1A1A/FF6B35?text=NITRO",
                caption="Nitro Industrial Supply")

        st.markdown("---")
        st.header("Data Source")

        # CSV file upload
        uploaded_file = st.file_uploader("Upload Parts CSV", type=['csv'])

        if uploaded_file:
            try:
                # Save uploaded file temporarily
                temp_path = "temp_parts.csv"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                # Load data
                parts_df = st.session_state.data_handler.load_csv(temp_path)
                st.success(f"✅ Loaded {len(parts_df)} parts")

            except Exception as e:
                st.error(f"❌ Error loading CSV: {str(e)}")

        st.markdown("---")
        st.header("Filters & Settings")

        # Search box
        search_term = st.text_input("🔍 Search Parts", "")

        # Price difference filter
        price_filter = st.selectbox(
            "Filter by Price Difference",
            ["All", "Competitors 10%+ Cheaper", "Competitors 20%+ Cheaper",
             "We're 10%+ Cheaper", "Equal Pricing (±5%)"]
        )

        # Sort options
        sort_by = st.selectbox(
            "Sort By",
            ["Part Number", "Part Description", "Nitro Price",
             "Max Price Difference", "Min Competitor Price"]
        )

        st.markdown("---")
        st.header("Processing Options")

        # Sample size limiter
        enable_limit = st.checkbox("Limit items to process", value=False,
                                   help="Process only a subset of items (recommended for large datasets)")

        if enable_limit:
            max_items = st.number_input(
                "Max items to process",
                min_value=10,
                max_value=10000,
                value=100,
                step=10,
                help="Process only the first N items (after filters)"
            )
        else:
            max_items = None

        # Cache usage option
        use_cache_only = st.checkbox(
            "Show cached data only (no new scraping)",
            value=True,
            help="Display cached prices without scraping. Uncheck to force update."
        )

        # Competitor selection
        st.markdown("---")
        st.header("Competitors")
        selected_competitors = []
        for competitor in COMPETITORS.keys():
            if st.checkbox(competitor, value=True, key=f"comp_{competitor}"):
                selected_competitors.append(competitor)

        st.markdown("---")

        # Cache management
        st.header("Cache Management")
        cache_stats = st.session_state.data_handler.get_cache_stats()
        st.metric("Cached Prices", cache_stats['total_entries'])

        if st.button("🗑️ Clear All Cache"):
            st.session_state.data_handler.clear_cache()
            st.success("Cache cleared!")
            st.rerun()

    # Main content area
    if st.session_state.data_handler.parts_data is None:
        st.info("👆 Please upload a CSV file to get started")
        st.markdown("### Expected CSV Format")
        st.markdown("""
        - **Column L**: Part Number
        - **Column M**: Part Description
        - **Column Y**: Nitro Price (CAD)
        """)
        return

    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 6])

    with col1:
        scrape_button = st.button("🔄 Force Update Prices", use_container_width=True,
                                 help="Scrape fresh prices for displayed items")

    with col2:
        export_button = st.button("📊 Export to Excel", use_container_width=True)

    # Load parts data
    parts_df = st.session_state.data_handler.parts_data

    # Apply search filter
    if search_term:
        mask = (
            parts_df['part_number'].str.contains(search_term, case=False, na=False) |
            parts_df['part_description'].str.contains(search_term, case=False, na=False)
        )
        parts_df = parts_df[mask]

    # Apply item limit
    original_count = len(parts_df)
    if max_items and len(parts_df) > max_items:
        parts_df = parts_df.head(max_items)
        st.warning(f"⚠️ Processing limited to {max_items} of {original_count} items. "
                  f"Adjust limit in sidebar or disable to process all.")

    # Calculate cache statistics
    items_with_cache = 0
    items_without_cache = 0
    for _, row in parts_df.iterrows():
        part_num = row['part_number']
        has_any_cache = False
        for competitor in selected_competitors:
            cached = st.session_state.data_handler.get_cached_price(part_num, competitor)
            if cached and cached.get('price'):
                has_any_cache = True
                break
        if has_any_cache:
            items_with_cache += 1
        else:
            items_without_cache += 1

    # Show cache statistics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total Items", len(parts_df))
    with col_stat2:
        st.metric("Items with Cached Prices", items_with_cache)
    with col_stat3:
        st.metric("Items Need Scraping", items_without_cache)

    # Show what will be processed
    if scrape_button and not use_cache_only:
        st.info(f"🔄 Scraping prices for {len(parts_df)} items across {len(selected_competitors)} competitors. "
               f"This may take several minutes...")
    elif use_cache_only and items_without_cache > 0:
        st.info(f"ℹ️ Showing cached data only. {items_without_cache} items don't have cached prices. "
               f"Uncheck 'Show cached data only' and click 'Force Update Prices' to scrape them.")

    # Build comparison dataframe
    comparison_data = []

    # Progress tracking for scraping
    if scrape_button and not use_cache_only:
        progress_bar = st.progress(0)
        status_text = st.empty()
        eta_text = st.empty()
        total_items = len(parts_df)
        start_time = time.time()

    for item_idx, (idx, row) in enumerate(parts_df.iterrows()):
        part_num = row['part_number']
        part_desc = row['part_description']
        nitro_price = row['nitro_price']

        row_data = {
            'Part Number': part_num,
            'Description': part_desc,
            'Nitro Price': f"${nitro_price:.2f}" if pd.notna(nitro_price) else "N/A"
        }

        # Update progress
        if scrape_button and not use_cache_only:
            progress = (item_idx + 1) / total_items
            progress_bar.progress(progress)
            status_text.text(f"Processing item {item_idx + 1} of {total_items}: {part_num}")

            # Calculate ETA
            if item_idx > 0:
                elapsed = time.time() - start_time
                avg_time_per_item = elapsed / (item_idx + 1)
                remaining_items = total_items - (item_idx + 1)
                eta_seconds = avg_time_per_item * remaining_items
                eta_minutes = int(eta_seconds / 60)
                eta_secs = int(eta_seconds % 60)
                eta_text.text(f"⏱️ Estimated time remaining: {eta_minutes}m {eta_secs}s")

        # Get competitor prices
        for competitor in selected_competitors:
            cached = st.session_state.data_handler.get_cached_price(part_num, competitor)

            # Only scrape if Force Update is clicked AND cache-only mode is off
            should_scrape = scrape_button and not use_cache_only and (cached is None or True)

            if should_scrape:
                # Scrape fresh data
                result = st.session_state.scraper_manager.scrape_competitor(
                    competitor, part_num, part_desc
                )

                st.session_state.data_handler.cache_price(
                    part_num, competitor, result['price'],
                    result.get('url'), result.get('confidence', 0.0),
                    result['status'], result.get('error_message', '')
                )
                cached = st.session_state.data_handler.get_cached_price(part_num, competitor)

            if cached and cached.get('price'):
                comp_price = cached['price']
                diff, pct = calculate_price_difference(nitro_price, comp_price)

                row_data[f"{competitor} Price"] = f"${comp_price:.2f}"
                row_data[f"{competitor} Diff"] = f"{pct:+.1f}%" if pct else "N/A"
                row_data[f"{competitor} Status"] = "✓"

                # Store for filtering
                row_data[f"_{competitor}_pct"] = pct
            else:
                row_data[f"{competitor} Price"] = "N/A"
                row_data[f"{competitor} Diff"] = "N/A"
                row_data[f"{competitor} Status"] = "✗"
                row_data[f"_{competitor}_pct"] = None

        comparison_data.append(row_data)

    # Clear progress indicators
    if scrape_button and not use_cache_only:
        progress_bar.empty()
        status_text.empty()
        eta_text.empty()
        total_time = time.time() - start_time
        st.success(f"✅ Completed processing {len(parts_df)} items in {int(total_time/60)}m {int(total_time%60)}s!")

    # Save comparison data
    st.session_state.data_handler.save_cache()

    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)

        # Apply price filter
        if price_filter != "All":
            filtered_indices = []
            for idx, row in comparison_df.iterrows():
                pct_values = [row[col] for col in row.index if col.startswith('_') and col.endswith('_pct')]
                pct_values = [v for v in pct_values if v is not None]

                if not pct_values:
                    continue

                if price_filter == "Competitors 10%+ Cheaper":
                    if any(pct > 10 for pct in pct_values):
                        filtered_indices.append(idx)
                elif price_filter == "Competitors 20%+ Cheaper":
                    if any(pct > 20 for pct in pct_values):
                        filtered_indices.append(idx)
                elif price_filter == "We're 10%+ Cheaper":
                    if any(pct < -10 for pct in pct_values):
                        filtered_indices.append(idx)
                elif price_filter == "Equal Pricing (±5%)":
                    if any(-5 <= pct <= 5 for pct in pct_values):
                        filtered_indices.append(idx)

            comparison_df = comparison_df.loc[filtered_indices]

        # Remove hidden columns used for filtering
        display_df = comparison_df[[col for col in comparison_df.columns if not col.startswith('_')]]

        # Display metrics
        st.markdown("### Summary Metrics")
        metric_cols = st.columns(4)

        with metric_cols[0]:
            st.metric("Total Parts", len(display_df))

        with metric_cols[1]:
            # Calculate average price difference across all competitors
            avg_diffs = []
            for col in comparison_df.columns:
                if col.startswith('_') and col.endswith('_pct'):
                    values = comparison_df[col].dropna()
                    if len(values) > 0:
                        avg_diffs.extend(values.tolist())

            if avg_diffs:
                avg_diff = sum(avg_diffs) / len(avg_diffs)
                st.metric("Avg Price Difference", f"{avg_diff:+.1f}%")
            else:
                st.metric("Avg Price Difference", "N/A")

        with metric_cols[2]:
            # Count how many we're cheaper
            cheaper_count = 0
            for idx, row in comparison_df.iterrows():
                pct_values = [row[col] for col in row.index if col.startswith('_') and col.endswith('_pct')]
                pct_values = [v for v in pct_values if v is not None]
                if any(pct < 0 for pct in pct_values):
                    cheaper_count += 1

            st.metric("We're Cheaper", cheaper_count)

        with metric_cols[3]:
            # Count how many competitors are cheaper
            expensive_count = 0
            for idx, row in comparison_df.iterrows():
                pct_values = [row[col] for col in row.index if col.startswith('_') and col.endswith('_pct')]
                pct_values = [v for v in pct_values if v is not None]
                if any(pct > 0 for pct in pct_values):
                    expensive_count += 1

            st.metric("Competitors Cheaper", expensive_count)

        st.markdown("---")

        # Display comparison table
        st.markdown(f"### Price Comparison Table ({len(display_df)} parts)")

        # Use Streamlit's dataframe with highlighting
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600
        )

        # Export to Excel
        if export_button:
            try:
                excel_data = export_to_excel(display_df, st.session_state.data_handler)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{EXPORT_FILENAME_PREFIX}{timestamp}.xlsx"

                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success(f"✅ Excel file ready for download: {filename}")
            except Exception as e:
                st.error(f"❌ Error creating Excel file: {str(e)}")

    else:
        st.warning("No data to display. Try adjusting your filters.")

    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: {NITRO_GREY}; padding: 1rem;">
        <small>Nitro Price Comparison Tool v1.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
