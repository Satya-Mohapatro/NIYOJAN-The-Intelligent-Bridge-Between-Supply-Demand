import requests
import pandas as pd
import io

BASE_URL = "http://127.0.0.1:8000"

def test_workflow():
    print("1. Logging in as Default Admin...")
    login_data = {
        "username": "admin@niyojan.ai",
        "password": "admin123",
        "grant_type": "password"
    }
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code != 200:
        print("Login Failed:", resp.text)
        return
    token = resp.json()["access_token"]
    print("Login Successful. Token obtained.")

    print("3. Uploading CSV with Prices...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create dummy CSV
    data = {
        "Product_ID": ["P100", "P101"],
        "Product_Name": ["Test Product A", "Test Product B"],
        "Category": ["TestCat", "TestCat"],
        "Week": ["01-01-2024", "08-01-2024"],
        "Sales_Quantity": [100, 120],
        "Price": [15.50, 20.00]
    }
    df = pd.DataFrame(data)
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    
    files = {"file": ("test.csv", csv_buf, "text/csv")}
    resp = requests.post(f"{BASE_URL}/forecast", headers=headers, data={"horizon": 4}, files=files)
    
    if resp.status_code != 200:
        print("Forecast Failed:", resp.text)
        return
    
    result = resp.json()
    print(f"Forecast Successful. Products: {result['products']}")
    
    # Check Revenue and Trend
    first_item = result['data'][0]
    if "Forecasted_Revenue" in first_item:
        print(f"✅ Revenue Data Present: {first_item['Forecasted_Revenue']}")
    else:
        print("❌ Revenue Data Missing")

    if "Trend_Symbol" in first_item:
        print(f"✅ Trend Symbol Present: {first_item['Trend_Symbol']}")
    else:
        print("❌ Trend Symbol Missing")

    print("4. Checking Alerts...")
    resp = requests.get(f"{BASE_URL}/alerts", headers=headers)
    alerts = resp.json()
    print(f"Alerts Count: {len(alerts['data'])}")
    if len(alerts['data']) > 0:
        print(f"Sample Alert: {alerts['data'][0]['alert']}")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"Test crashed: {e}")
