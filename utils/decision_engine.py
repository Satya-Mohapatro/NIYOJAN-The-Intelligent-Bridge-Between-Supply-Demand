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
             return f"⚠️ Critical: Zero sales history! Expected demand: {int(forecast)}."
        else:
             return f"No sales history, and no immediate demand."

    ratio = forecast / current_stock

    if ratio > 1.2:
        return f"🔥 High acceleration ({int(forecast)} vs {int(current_stock)} last week). Potential stock-out risk."
    elif ratio < 0.5:
        return f"💤 Slowing demand. Forecast ({int(forecast)}) is lower than recent sales ({int(current_stock)})."
    elif ratio > 1.05:
         return f"📈 Demand slightly upwards. Monitor."
    else:
        return f"✅ Stable demand pattern."

