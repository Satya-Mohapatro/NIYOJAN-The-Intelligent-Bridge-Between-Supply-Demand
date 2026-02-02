import pandas as pd

# Load the dataset
df = pd.read_csv('indian_grocery_store_weekly_sales.csv')

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Convert date column
df['week'] = pd.to_datetime(df['week'])

df['weekofyear'] = df['week'].dt.isocalendar().week.astype(int)

weekly_avg = (
    df.groupby(['product_id', 'weekofyear'])['sales_quantity']
    .mean()
    .reset_index(name='weekly_avg_sales')
)

overall_avg = (
    df.groupby('product_id')['sales_quantity']
    .mean()
    .reset_index(name='overall_avg_sales')
)

seasonal_df = weekly_avg.merge(overall_avg, on='product_id')
seasonal_df['seasonal_index'] = (
    seasonal_df['weekly_avg_sales'] / seasonal_df['overall_avg_sales']
)

seasonal_df.to_csv('seasonal_index_per_product.csv', index=False)
