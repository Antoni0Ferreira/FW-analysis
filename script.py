import pandas as pd
import numpy as np
from pytrends.request import TrendReq
import time
import os
from datetime import datetime, timedelta

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

pd.set_option('future.no_silent_downcasting', True)

FASHION_WEEKS = {
    "S/S 2025": (datetime(2025, 9, 29), datetime(2025, 10, 7)),
    "A/W 2025": (datetime(2025, 3, 23), datetime(2025, 3, 11)),
    "S/S 2024": (datetime(2024, 9, 23), datetime(2024, 10, 1)),
    "A/W 2024": (datetime(2024, 2, 26), datetime(2024, 3, 5)),
    "S/S 2023": (datetime(2023, 9, 25), datetime(2023, 10, 3)),
    "A/W 2023": (datetime(2023, 2, 27), datetime(2023, 3, 7)),
    "S/S 2022": (datetime(2022, 9, 26), datetime(2022, 10, 4)),
    "A/W 2022": (datetime(2022, 2, 28), datetime(2022, 3, 8)),
}

def read_fashion_houses(file_path="data/paris_fashion_houses.csv"):
    try:
        df = pd.read_csv(file_path, header=None)
        fashion_houses = df[0].tolist()
        return fashion_houses
    except Exception as e:
        print(f"Error reading fashion houses from file: {e}")
        return []
    
def collect_trends_data(brands, timeframe="today 12-m", geo=''):

    try:
        pytrends.build_payload(brands, cat=0, timeframe=timeframe, geo=geo)
        data = pytrends.interest_over_time()

        if not data.empty:
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])
        
        return data
    
    except Exception as e:
        print(f"Error collecting trends data: {e}")
        return pd.DataFrame()

def collect_related_queries(brand):

    try:
        pytrends.build_payload([brand], cat=0, timeframe='today 12-m', geo='')
        related_queries = pytrends.related_queries()
        return related_queries.get(brand, {})
    except Exception as e:
        print(f"Error collecting related queries for {brand}: {e}")
        return {}
    
def batch_colldect_trends_data(brands, batch_size=5, timeframe="today 12-m", geo=''):
    all_data = []

    for i in range(0, len(brands),batch_size):

        batch = brands[i:i+batch_size]
        print(f"Collecting data for : {', '.join(batch)}")

        data = collect_trends_data(batch, timeframe, geo)

        if not data.empty:
            all_data.append(data)

        time.sleep(2)  # To respect rate limits

    if all_data:
        combined_data = pd.concat(all_data, axis=1)
        # Remove duplicate columns
        combined_data = combined_data.loc[:,~combined_data.columns.duplicated()]
        return combined_data
    
    return pd.DataFrame()

def analyze_fw_trends(brands, fw_periods=FASHION_WEEKS):


    for season, (start_date, end_date) in fw_periods.items():
        print(f"Analyzing trends for {season} ({start_date.date()} to {end_date.date()})")

        # Format dates for pytrends
        timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"

        data = batch_colldect_trends_data(brands, batch_size=5, timeframe=timeframe)

        if not data.empty:
            
            avg_interest = data.mean().sort_values(ascending=False)
            top_brands = avg_interest.head(10).index.tolist()
            print(f"Top brands for {season}: {', '.join(top_brands)}")

            return data, avg_interest, top_brands

    return None, None, None

def save_trends_data(data, filename="fashion_trends_data.csv"):

    try:
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        data.to_csv(filepath)
        print(f"Trends data saved to {filepath}")
    except Exception as e:
        print(f"Error saving trends data to file: {e}")

def main():
    print("=" * 60)
    print("Paris' Fashion Week Trends Analysis")
    print("=" * 60)

    fashion_houses = read_fashion_houses()
    if not fashion_houses:
        print("No fashion houses to analyze. Exiting.")
        return
    
    # #1 Collect overall trends data (last 12 months)
    overall_data = batch_colldect_trends_data(fashion_houses, batch_size=5, timeframe="today 12-m")

    if not overall_data.empty:
        save_trends_data(overall_data, filename="overall_fashion_trends_data.csv")

        print("\nOverall Average Interest (over last 12 months):")
        overall_avg = overall_data.mean().sort_values(ascending=False)
        print(overall_avg)

    # # #2 Analyze trends during Fashion Weeks
    # fw_data, fw_avg, top_brands = analyze_fw_trends(fashion_houses)

    # if fw_data is not None and not fw_data.empty:
    #     save_trends_data(fw_data, filename="fw_fashion_trends_data.csv")

    #     print("\nFashion Week Average Interest:")
    #     print(fw_avg)

    #     print("\nTop Brands During Fashion Weeks:")
    #     for brand in top_brands:
    #         print(f"- {brand}")
    
    # # #3 Collect related queries for top brands
    # print("\nCollecting related queries for top brands...")
    # for brand in top_brands:
    #     related = collect_related_queries(brand)
    #     if related is not None:
    #         top_related = related.get('top', pd.DataFrame())
    #         rising_related = related.get('rising', pd.DataFrame())

    #         if not top_related.empty:
    #             print(f"\nTop related queries for {brand}:")
    #             print(top_related.head(5))

    #         if not rising_related.empty:
    #             print(f"\nRising related queries for {brand}:")
    #             print(rising_related.head(5))
    #     else:
    #         print(f"No related queries found for {brand}.")

    # print("\n" + "=" * 60)
    # print("Analysis Complete.")


if __name__ == "__main__":
    main()