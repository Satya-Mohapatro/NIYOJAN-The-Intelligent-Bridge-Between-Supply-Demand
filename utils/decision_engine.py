def analyze_forecast(product, forecast, current_stock):
    """
    Compare forecasted demand and current stock to generate an inventory alert message.
    Refined logic:
    - High Demand: Forecast > 1.2 * Stock
    - Low Demand: Forecast < 0.5 * Stock (and stock > 0)
    - Balanced: Stock is within reasonable range
    """
    if current_stock <= 0:
        # If stock is 0, any forecast > 0 is urgent
        if forecast > 0:
             return {
                 "message": f"⚠️ Critical: Zero sales history! Expected demand: {int(forecast)}.",
                 "decision": "RESTOCK",
                 "risk_level": "HIGH"
             }
        else:
             return {
                 "message": f"No sales history, and no immediate demand.",
                 "decision": "HOLD",
                 "risk_level": "LOW"
             }

    ratio = forecast / current_stock

    if ratio > 1.2:
        return {
            "message": f"🔥 High acceleration ({int(forecast)} vs {int(current_stock)} last week). Potential stock-out risk.",
            "decision": "RESTOCK",
            "risk_level": "HIGH"
        }
    elif ratio < 0.5:
        return {
            "message": f"💤 Slowing demand. Forecast ({int(forecast)}) is lower than recent sales ({int(current_stock)}).",
            "decision": "REDUCE",
            "risk_level": "MEDIUM"
        }
    elif ratio > 1.05:
         return {
             "message": f"📈 Demand slightly upwards. Monitor.",
             "decision": "HOLD",
             "risk_level": "LOW"
         }
    else:
        return {
            "message": f"✅ Stable demand pattern.",
            "decision": "HOLD",
            "risk_level": "LOW"
        }

