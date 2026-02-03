import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"

def test_insight_engine():
    # 1. Login
    print("Logging in...")
    try:
        resp = requests.post(f"{API_URL}/auth/login", data={
            "username": "admin@niyojan.ai",
            "password": "admin123"
        })
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()["access_token"]
        print("Login successful.")

        # 2. Call Insight Endpoint
        print("Testing Insight Engine...")
        payload = {
            "product_name": "Test Product A",
            "current_stock": 50,
            "forecast_next_week": 120,
            "trend": "Increasing"
        }
        
        try:
            insight_resp = requests.post(
                f"{API_URL}/insight",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60 # Add timeout to prevent hanging
            )
            
            if insight_resp.status_code == 200:
                data = insight_resp.json()
                print("\n✅ Insight Generation Successful!")
                print("Raw Response keys:", data.keys())
                if 'english' in data:
                    print(f"English Summary: {data['english']['summary']}")
                    print(f"Risk: {data['english']['risk']}")
                    print(f"Action: {data['english']['action']}")
                if 'hindi' in data:
                    print(f"Hindi Summary: {data['hindi']['summary']}")
            else:
                print(f"❌ Insight Generation Failed: SC={insight_resp.status_code}")
                print(f"Response: {insight_resp.text}")

        except requests.exceptions.Timeout:
            print("❌ Request Timed Out! Backend or LLM is taking too long.")
        except Exception as e:
            print(f"❌ Request Error: {e}")

    except Exception as e:
        print(f"Error during login or setup: {e}")

if __name__ == "__main__":
    test_insight_engine()
