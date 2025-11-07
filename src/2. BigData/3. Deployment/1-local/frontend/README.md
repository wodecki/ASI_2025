# Frontend Streamlit - Local Development

## 📚 Educational Purpose

This module demonstrates building an interactive frontend for ML API:

1. **Separation of Concerns** - UI separated from business logic (backend)
2. **HTTP Client** - Communication with REST API via requests
3. **User Experience** - Loading states, error handling, visualizations
4. **Configuration Management** - Environment variables for different environments

## 🏗️ Architecture

```
┌─────────────────────────┐
│   Streamlit Frontend    │
│   (app.py, port 8501)   │
│                         │
│   User Interface:       │
│   - Item selector       │
│   - Predict button      │
│   - Results table       │
│   - Chart visualization │
└────────┬────────────────┘
         │ HTTP GET
         │ requests.get(f"{API_URL}/predict/{item}")
         ↓
┌─────────────────────────┐
│   FastAPI Backend       │
│   (main.py, port 8003)  │
│                         │
│   Returns JSON:         │
│   {                     │
│     "item": "...",      │
│     "predictions": [...] │
│   }                     │
└─────────────────────────┘
```

## 🔑 Key Code Patterns

### 1. Environment-Based Configuration
```python
API_URL = os.getenv("API_URL", "http://localhost:8003")
```

**Why:**
- Easy URL change without code modification
- Different environments: local (localhost), Docker (container name), Cloud (HTTPS URL)

**Usage:**
```bash
# Default (localhost)
uv run streamlit run app.py

# Custom URL (e.g., Docker or Cloud)
API_URL="http://backend:8003" uv run streamlit run app.py
API_URL="https://iowa-xyz.run.app" uv run streamlit run app.py
```

### 2. Graceful Error Handling
```python
try:
    response = requests.get(url, timeout=10)
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to backend...")
```

**Why:**
- User-friendly error messages
- Troubleshooting hints displayed in UI
- Prevents app crashes on network errors

### 3. Loading States
```python
with st.spinner('Generating forecast...'):
    result = get_predictions(item_name)
```

**Why:**
- Visual feedback for the user
- Better UX during I/O operations
- Communicates that the app hasn't frozen

### 4. Data Transformation Layer
```python
def format_predictions_df(predictions_data: list) -> pd.DataFrame:
    # Separate data transformation from UI
```

**Why:**
- Separation of concerns
- Reusable transformation logic
- Easier testing

## ⚙️ Installation and Running

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run backend (in a separate terminal)
```bash
cd ../backend
uv run uvicorn main:app --host 0.0.0.0 --port 8003
```

### 3. Run frontend
```bash
# Default (connection to localhost:8003)
uv run streamlit run app.py

# With custom URL
API_URL="http://10.0.0.5:8003" uv run streamlit run app.py
```

### 4. Open in Browser
```
http://localhost:8501
```

## 🎨 User Interface

### Main Components

1. **Header**
   - Application title
   - API URL information
   - Forecast horizon

2. **Connection Tester** (expander)
   - Button for connection testing
   - Backend health check
   - JSON response preview

3. **Main Interface**
   - Dropdown with product list
   - "Generate Forecast" button
   - Loading spinner during request

4. **Results Display**
   - Success message
   - Table with forecasts (7 days)
   - Line chart visualization
   - Raw JSON (expander for advanced users)

5. **Footer**
   - Architecture diagram
   - Data flow explanation

## 🛠️ File Structure

```
frontend/
├── app.py                       # Streamlit application
├── pyproject.toml               # Dependencies (uv format)
└── README.md                    # This file
```

## 📊 Data Flow

```
1. User selects item → "BLACK VELVET"
2. User clicks "Generate Forecast" button
3. Frontend calls: GET http://localhost:8003/predict/BLACK%20VELVET
4. Backend returns JSON:
   {
     "item": "BLACK VELVET",
     "predictions": [
       {"date": "2024-01-01", "mean": 1234.56},
       {"date": "2024-01-02", "mean": 1256.78},
       ...
     ],
     "forecast_horizon": 7
   }
5. Frontend transforms JSON → pandas DataFrame
6. Display:
   - Table with dates and values
   - Line chart visualization
```

## 🎓 What You Will Learn

### Basics
1. How to build simple UI with Streamlit
2. How to call REST API from Python (requests)
3. How to handle network errors
4. How to transform JSON → DataFrame

### Intermediate
1. Environment-based configuration
2. User experience patterns (loading, errors)
3. Data visualization (charts)
4. Separation of concerns (UI vs logic)

### Advanced
1. Cross-environment compatibility (local/Docker/cloud)
2. Timeout handling
3. HTTP status code interpretation
4. Structured error messaging

## 🔍 Troubleshooting

### Problem: Connection refused
```
❌ Cannot connect to backend at `http://localhost:8003`
```

**Solution:**
1. Check if backend is running:
   ```bash
   curl http://localhost:8003/
   ```
2. If not, start the backend:
   ```bash
   cd ../backend && uv run uvicorn main:app --host 0.0.0.0 --port 8003
   ```

### Problem: Timeout error
```
⏱️ Request timed out. Backend might be overloaded.
```

**Possible causes:**
- Model is still loading (first backend startup)
- Backend has frozen
- Network latency too high

**Solution:**
1. Wait 10-15 seconds and try again
2. Check backend logs
3. Restart backend if necessary

### Problem: Item not found
```
❌ Item 'XYZ' not found in the system.
```

**Solution:** Product doesn't exist in the model. Available products:
- BLACK VELVET
- FIREBALL CINNAMON WHISKEY
- HAWKEYE VODKA
- TITOS HANDMADE VODKA
- FIVE O'CLOCK VODKA

### Problem: Streamlit won't start
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
uv sync  # Installs all dependencies
```

## 🎨 Customization

### Changing Product List
Edit in `app.py`:
```python
ITEMS = [
    'BLACK VELVET',
    'YOUR_NEW_PRODUCT',
    # ...
]
```

### Adding New Visualizations
```python
# Bar chart instead of line chart
st.bar_chart(predictions_df.set_index('Date'))

# Area chart
st.area_chart(predictions_df.set_index('Date'))

# Metric card
st.metric(
    label="Average Forecast",
    value=f"{predictions_df['Predicted Sales'].mean():.2f}"
)
```

### Changing UI Language
The UI is already in English. Column names:
```python
df = df.rename(columns={
    'date': 'Date',
    'mean': 'Predicted Sales'
})
```

## 📈 Performance Tips

1. **Caching:** Use `@st.cache_data` for expensive operations
   ```python
   @st.cache_data(ttl=3600)  # Cache for 1 hour
   def get_predictions(item_name: str):
       ...
   ```

2. **Lazy Loading:** Load data only when needed (already implemented)

3. **Timeout:** Adjust timeout in `requests.get()` to match your infrastructure

## 🔗 Next Steps

After mastering local deployment:
1. **Module 2 (Docker):** Containerize frontend + backend → single compose
2. **Module 3 (Cloud):** Deploy frontend pointing to Cloud Run backend
3. **Advanced:** Add authentication, caching, monitoring

## 💡 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Requests Library](https://docs.python-requests.org/)
- [REST API Calls from Python](https://realpython.com/api-integration-in-python/)
- [Streamlit Components Gallery](https://streamlit.io/components)
