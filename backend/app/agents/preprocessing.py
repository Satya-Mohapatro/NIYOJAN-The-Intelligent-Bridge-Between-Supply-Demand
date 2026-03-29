import pandas as pd
import numpy as np
import io

DEFAULT_LEAD_TIME  = 2
DEFAULT_STOCK_MULT = 2
Z_SCORE = 1.65

def preprocess_forecast(csv_bytes: bytes) -> tuple:
    """
    Accepts raw CSV bytes (from file upload).
    Returns (products_list, warnings_list).
    Works with ANY product IDs and ANY number of weeks.
    """
    df = pd.read_csv(io.BytesIO(csv_bytes))

    # Validate required column
    if "Product_ID" not in df.columns:
        raise ValueError("Missing required column: 'Product_ID'. Upload the Niyojan forecast CSV.")

    forecast_cols = [c for c in df.columns if c.startswith("Week_") and c.endswith("_Forecast")]
    if not forecast_cols:
        raise ValueError("No 'Week_N_Forecast' columns found. Upload the Niyojan forecast CSV.")

    warnings = [
        f"lead_time defaulted to {DEFAULT_LEAD_TIME} weeks (not in CSV)",
        f"current_stock defaulted to {DEFAULT_STOCK_MULT}x mean forecast (not in CSV)",
        "Simulation results are directionally correct, not warehouse-precise."
    ]

    products = []
    for _, row in df.iterrows():
        pid = str(row["Product_ID"])
        weekly_forecasts = [float(row[c]) for c in forecast_cols if pd.notna(row[c])]
        if not weekly_forecasts:
            continue

        mean_demand     = float(np.mean(weekly_forecasts))
        week1_forecast  = weekly_forecasts[0]
        last_week_sales = float(row["Last_Week_Sales"]) if "Last_Week_Sales" in row and pd.notna(row["Last_Week_Sales"]) else mean_demand
        std_dev = float(np.std(weekly_forecasts)) if len(weekly_forecasts) > 1 else mean_demand * 0.10
        if std_dev == 0:
            std_dev = mean_demand * 0.05

        lead_time     = DEFAULT_LEAD_TIME
        current_stock = round(mean_demand * DEFAULT_STOCK_MULT)

        volatility    = round(std_dev / mean_demand, 4) if mean_demand > 0 else 0
        safety_stock  = round(Z_SCORE * std_dev * np.sqrt(lead_time), 2)
        reorder_point = round((mean_demand * lead_time) + safety_stock, 2)
        inv_gap       = round(reorder_point - current_stock, 2)

        ratio = week1_forecast / current_stock if current_stock > 0 else 999
        if ratio > 1.2:
            base_risk = "High"
        elif ratio < 0.5:
            base_risk = "Medium (Overstock)"
        else:
            base_risk = "Low"

        trend_pct = round(
            ((weekly_forecasts[-1] - weekly_forecasts[0]) / weekly_forecasts[0]) * 100, 2
        ) if len(weekly_forecasts) >= 2 else 0.0

        products.append({
            "product_id":       pid,
            "product_name":     str(row["Product_Name"]) if "Product_Name" in row and pd.notna(row.get("Product_Name")) else pid,
            "category":         str(row["Category"]) if "Category" in row and pd.notna(row.get("Category")) else "Unknown",
            "last_week_sales":  last_week_sales,
            "week1_forecast":   week1_forecast,
            "weekly_forecasts": weekly_forecasts,
            "mean_demand":      round(mean_demand, 2),
            "std_dev":          round(std_dev, 2),
            "lead_time":        lead_time,
            "current_stock":    current_stock,
            "using_defaults":   True,
            "volatility":       volatility,
            "safety_stock":     safety_stock,
            "reorder_point":    reorder_point,
            "inv_gap":          inv_gap,
            "base_risk":        base_risk,
            "trend_pct":        trend_pct,
        })

    return products, warnings
