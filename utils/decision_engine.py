def analyze_forecast(product, forecast, current_stock):
    """
    Compare forecasted demand and current stock
    to generate an inventory alert message.
    """
    if forecast > current_stock * 1.1:
        return f" High demand expected for {product}. Consider restocking."
    elif forecast < current_stock * 0.5:
        return f" Demand drop expected for {product}. Stock might be too high."
    else:
        return f" Stock level for {product} looks balanced."


