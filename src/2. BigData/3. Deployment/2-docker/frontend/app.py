"""
Streamlit frontend for Iowa alcohol sales prediction.

Educational Purpose:
- Demonstrates clean separation between UI and API
- Shows environment-based configuration
- Implements user-friendly error handling and loading states
"""

import os
import streamlit as st
import requests
import pandas as pd
from typing import Optional, Dict, Any

# Configuration from environment variable (for flexibility across deployments)
API_URL = os.getenv("API_URL", "http://localhost:8003")

# Available items for dropdown (could be fetched from API in production)
ITEMS = [
    'BLACK VELVET',
    'FIREBALL CINNAMON WHISKEY',
    'HAWKEYE VODKA',
    'TITOS HANDMADE VODKA',
    "FIVE O'CLOCK VODKA"
]


def get_predictions(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch predictions from FastAPI backend.

    Educational Note:
    - Uses requests library for HTTP client
    - Returns None on error (graceful degradation)
    - Logs errors for debugging

    Args:
        item_name: Product name to forecast

    Returns:
        Prediction dict or None if request failed
    """
    try:
        response = requests.get(
            f"{API_URL}/predict/{item_name}",
            timeout=10  # Prevent hanging on slow responses
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error(f"❌ Item '{item_name}' not found in the system.")
            return None
        elif response.status_code == 503:
            st.warning("⏳ Backend is starting up. Please try again in a few seconds.")
            return None
        else:
            st.error(f"❌ Server error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        st.error(
            f"❌ Cannot connect to backend at `{API_URL}`\n\n"
            "**Troubleshooting:**\n"
            "1. Is the FastAPI backend running?\n"
            "2. Run: `cd ../backend && uv run uvicorn main:app --host 0.0.0.0 --port 8003`\n"
            "3. Check if API_URL environment variable is set correctly"
        )
        return None

    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Backend might be overloaded.")
        return None

    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


def format_predictions_df(predictions_data: list) -> pd.DataFrame:
    """
    Convert API response to formatted DataFrame for display.

    Educational Note:
    - Separates data transformation from UI logic
    - Makes data presentation cleaner

    Args:
        predictions_data: List of prediction dicts from API

    Returns:
        Formatted DataFrame ready for display
    """
    df = pd.DataFrame(predictions_data)

    # Extract just the date part (not full timestamp)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    # Round mean to 2 decimal places for readability
    df['mean'] = df['mean'].round(2)

    # Rename columns for better readability
    df = df[['date', 'mean']].rename(columns={
        'date': 'Date',
        'mean': 'Predicted Sales'
    })

    return df


def main():
    """
    Main Streamlit application.

    Educational Note:
    - Structured UI flow: title → inputs → action → results
    - Uses Streamlit session state for interactivity
    - Implements loading indicators for UX
    """

    # Page configuration
    st.set_page_config(
        page_title="Iowa Sales Predictor",
        page_icon="📊",
        layout="centered"
    )

    # Header
    st.title('📊 Iowa Alcohol Sales Forecast')
    st.markdown(
        f"""
        **Backend API:** `{API_URL}`
        **Forecast Horizon:** 7 days
        """
    )

    # Show API connection status
    with st.expander("🔍 Check API Connection"):
        if st.button("Test Connection"):
            try:
                response = requests.get(f"{API_URL}/", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Backend is running!")
                    st.json(response.json())
                else:
                    st.error(f"❌ Backend returned status: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

    st.markdown("---")

    # Main interface
    st.subheader("Select Product")

    item_name = st.selectbox(
        label='Product',
        options=ITEMS,
        help="Select an alcohol product for sales forecasting"
    )

    # Action button with loading state
    if st.button('🔮 Generate Forecast', type="primary"):
        with st.spinner('Generating forecast...'):
            # Fetch predictions from API
            result = get_predictions(item_name)

            if result:
                # Success! Display results
                st.success(f"✅ Forecast generated for: **{result['item']}**")

                # Display predictions table
                st.subheader("📈 7-Day Forecast")

                predictions_df = format_predictions_df(result['predictions'])
                st.dataframe(
                    predictions_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Optional: Chart visualization
                st.subheader("📊 Visualization")
                st.line_chart(
                    predictions_df.set_index('Date')['Predicted Sales']
                )

                # Show raw JSON for educational purposes
                with st.expander("🔍 View Raw API Response"):
                    st.json(result)

    # Footer with educational info
    st.markdown("---")
    st.markdown(
        """
        ### 💡 How It Works

        1. **Frontend (Streamlit)** - This user interface
        2. **HTTP Request** - Send GET request to `/predict/{item_name}`
        3. **Backend (FastAPI)** - Process request and invoke the model
        4. **AutoGluon Model** - Generate 7-day forecast
        5. **HTTP Response** - Return results in JSON format
        6. **Presentation** - Display table and chart

        **Architecture:** Microservices (frontend ↔ backend via HTTP API)
        """
    )


if __name__ == '__main__':
    main()
