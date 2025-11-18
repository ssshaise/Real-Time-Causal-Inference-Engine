import pandas as pd
import numpy as np

def generate_ecommerce_data(n=1000):
    np.random.seed(42)
    
    ad_spend = np.random.uniform(1000, 10000, n)
    
    seasonality = np.random.beta(2, 2, n)
    
    traffic = (ad_spend * 2.5) + (seasonality * 5000) + np.random.normal(0, 500, n)
    

    discount_pct = np.random.choice([0, 0.10, 0.20, 0.30], n)
    
    base_conversion = 0.03
    conversion_rate = base_conversion + (discount_pct * 0.05) 
    orders = traffic * conversion_rate
    
    avg_order_value = 100 * (1 - discount_pct) 
    
    revenue = orders * avg_order_value + np.random.normal(0, 1000, n)
    
    df = pd.DataFrame({
        'Ad_Spend': ad_spend.round(2),
        'Seasonality': seasonality.round(2),
        'Discount_Pct': discount_pct,
        'Site_Traffic': traffic.round(0),
        'Revenue': revenue.round(2)
    })
    
    return df

if __name__ == "__main__":
    df = generate_ecommerce_data()
    save_path = "data/raw/ecommerce_data.csv"
    df.to_csv(save_path, index=False)
    print(f"✅ Real-world dataset created at: {save_path}")
    print(df.head())