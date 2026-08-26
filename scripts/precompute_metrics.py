import os
import json
import pandas as pd
import numpy as np

# File Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYTICAL_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "tables", "analytical_dataset.csv")
HOLIDAYS_CSV = os.path.join(PROJECT_ROOT, "data", "raw", "tabular", "uk_bank_holidays.csv")
METRICS_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "metrics")

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

def convert_to_serializable(val):
    if isinstance(val, (np.integer, int)):
        return int(val)
    elif isinstance(val, (np.floating, float)):
        return float(val) if not np.isnan(val) else None
    elif isinstance(val, (np.ndarray, list)):
        return [convert_to_serializable(x) for x in val]
    elif isinstance(val, dict):
        return {k: convert_to_serializable(v) for k, v in val.items()}
    else:
        return str(val) if pd.notnull(val) else None

def precompute_all_metrics():
    os.makedirs(METRICS_DIR, exist_ok=True)
    print("🚀 Loading analytical dataset (selecting optimized columns)...")

    usecols = [
        "LCLid", "day", "energy_median", "energy_mean", "energy_max", 
        "energy_std", "energy_sum", "energy_min", "stdorToU", 
        "Acorn", "Acorn_grouped", "temperatureMax", "temperatureMin", 
        "humidity", "windSpeed", "summary", "precipType"
    ]

    df = pd.read_csv(ANALYTICAL_CSV, usecols=usecols)
    print(f"✅ Dataset Loaded! Shape: {df.shape}")

    # Ensure date parsing
    df["day_dt"] = pd.to_datetime(df["day"])
    df["month"] = df["day_dt"].dt.month
    df["season"] = df["month"].apply(get_season)

    # -------------------------------------------------------------
    # 1. HOUSEHOLD STATISTICS
    # -------------------------------------------------------------
    print("\n📊 1. Calculating Household Statistics...")
    total_households = int(df["LCLid"].nunique())
    tariff_counts = df.groupby("stdorToU")["LCLid"].nunique().to_dict()
    acorn_counts = df.groupby("Acorn_grouped")["LCLid"].nunique().to_dict()
    acorn_detail_counts = df.groupby("Acorn")["LCLid"].nunique().to_dict()

    hh_avg_energy = df.groupby("LCLid")["energy_sum"].agg(["mean", "max", "min"]).reset_index()

    household_stats = {
        "total_households": total_households,
        "tariff_distribution": tariff_counts,
        "acorn_grouped_distribution": acorn_counts,
        "acorn_detail_distribution": acorn_detail_counts,
        "household_daily_energy_summary": {
            "mean_daily_per_household_kwh": float(hh_avg_energy["mean"].mean()),
            "max_daily_per_household_kwh": float(hh_avg_energy["max"].max()),
            "min_daily_per_household_kwh": float(hh_avg_energy["min"].min())
        }
    }
    with open(os.path.join(METRICS_DIR, "household_stats.json"), "w") as f:
        json.dump(convert_to_serializable(household_stats), f, indent=2)
    print("  💾 Saved household_stats.json")

    # -------------------------------------------------------------
    # 2. WEATHER STATISTICS
    # -------------------------------------------------------------
    print("🌤️ 2. Calculating Weather Statistics...")
    daily_weather = df.drop_duplicates(subset=["day"])
    
    weather_stats = {
        "total_weather_days": int(len(daily_weather)),
        "temperature_celsius": {
            "mean_max_temp": float(daily_weather["temperatureMax"].mean()),
            "mean_min_temp": float(daily_weather["temperatureMin"].mean()),
            "highest_recorded_temp": float(daily_weather["temperatureMax"].max()),
            "lowest_recorded_temp": float(daily_weather["temperatureMin"].min())
        },
        "atmospheric": {
            "mean_humidity": float(daily_weather["humidity"].mean()),
            "mean_wind_speed": float(daily_weather["windSpeed"].mean())
        },
        "summary_counts": daily_weather["summary"].value_counts().head(10).to_dict(),
        "precip_type_counts": daily_weather["precipType"].value_counts(dropna=False).to_dict(),
        "temp_energy_correlation": float(df[["temperatureMax", "energy_sum"]].corr().iloc[0, 1])
    }
    with open(os.path.join(METRICS_DIR, "weather_stats.json"), "w") as f:
        json.dump(convert_to_serializable(weather_stats), f, indent=2)
    print("  💾 Saved weather_stats.json")

    # -------------------------------------------------------------
    # 3. CONSUMPTION STATISTICS
    # -------------------------------------------------------------
    print("⚡ 3. Calculating Consumption Statistics...")
    percentiles = df["energy_sum"].quantile([0.25, 0.50, 0.75, 0.90, 0.99]).to_dict()
    
    # Top dates by citywide total consumption
    top_dates = df.groupby("day")["energy_sum"].sum().nlargest(5).to_dict()
    top_households = df.groupby("LCLid")["energy_sum"].mean().nlargest(5).to_dict()

    consumption_stats = {
        "total_dataset_rows": int(len(df)),
        "total_daily_consumption_records": int(len(df)),
        "total_aggregate_energy_sum_kwh": float(df["energy_sum"].sum()),
        "daily_mean_kwh": float(df["energy_sum"].mean()),
        "daily_median_kwh": float(df["energy_sum"].median()),
        "daily_std_kwh": float(df["energy_sum"].std()),
        "daily_min_kwh": float(df["energy_sum"].min()),
        "daily_max_kwh": float(df["energy_sum"].max()),
        "percentiles_kwh": {f"p{int(k*100)}": float(v) for k, v in percentiles.items()},
        "top_5_highest_citywide_consumption_dates": {str(k): float(v) for k, v in top_dates.items()},
        "top_5_highest_consuming_households_avg_kwh": {str(k): float(v) for k, v in top_households.items()}
    }
    with open(os.path.join(METRICS_DIR, "consumption_stats.json"), "w") as f:
        json.dump(convert_to_serializable(consumption_stats), f, indent=2)
    print("  💾 Saved consumption_stats.json")

    # -------------------------------------------------------------
    # 4. SEASONAL STATISTICS
    # -------------------------------------------------------------
    print("🍂 4. Calculating Seasonal Statistics...")
    seasonal_grp = df.groupby("season").agg(
        avg_daily_energy_kwh=("energy_sum", "mean"),
        max_daily_energy_kwh=("energy_sum", "max"),
        avg_temp_max=("temperatureMax", "mean"),
        avg_temp_min=("temperatureMin", "mean"),
        record_count=("energy_sum", "count")
    ).to_dict(orient="index")

    with open(os.path.join(METRICS_DIR, "seasonal_stats.json"), "w") as f:
        json.dump(convert_to_serializable(seasonal_grp), f, indent=2)
    print("  💾 Saved seasonal_stats.json")

    # -------------------------------------------------------------
    # 5. HOLIDAY STATISTICS
    # -------------------------------------------------------------
    print("🎉 5. Calculating Holiday Statistics...")
    holiday_stats = {}
    if os.path.exists(HOLIDAYS_CSV):
        holidays_df = pd.read_csv(HOLIDAYS_CSV)
        # Parse holiday dates (actual column name is 'Bank holidays')
        holidays_df["clean_date"] = pd.to_datetime(holidays_df["Bank holidays"]).dt.strftime("%Y-%m-%d")
        holiday_date_set = set(holidays_df["clean_date"])

        df["is_holiday"] = df["day"].isin(holiday_date_set)

        holiday_comparison = df.groupby("is_holiday")["energy_sum"].agg(["mean", "median", "std", "count"]).to_dict(orient="index")
        
        # Breakdown by specific holiday title ('Type' column)
        df_holidays_only = df.merge(holidays_df, left_on="day", right_on="clean_date", how="inner")
        specific_holiday_stats = df_holidays_only.groupby("Type")["energy_sum"].agg(["mean", "median", "count"]).to_dict(orient="index") if "Type" in df_holidays_only.columns else {}

        holiday_stats = {
            "bank_holiday_vs_regular": {
                "bank_holiday": holiday_comparison.get(True, {}),
                "regular_day": holiday_comparison.get(False, {})
            },
            "specific_holidays": specific_holiday_stats
        }
    else:
        holiday_stats = {"note": "Bank holidays CSV not found."}

    with open(os.path.join(METRICS_DIR, "holiday_stats.json"), "w") as f:
        json.dump(convert_to_serializable(holiday_stats), f, indent=2)
    print("  💾 Saved holiday_stats.json")

    # -------------------------------------------------------------
    # 6. TARIFF STATISTICS
    # -------------------------------------------------------------
    print("💡 6. Calculating Tariff Statistics...")
    tariff_grp = df.groupby("stdorToU").agg(
        avg_daily_energy_kwh=("energy_sum", "mean"),
        median_daily_energy_kwh=("energy_sum", "median"),
        std_daily_energy_kwh=("energy_sum", "std"),
        max_daily_energy_kwh=("energy_sum", "max"),
        total_records=("energy_sum", "count")
    ).to_dict(orient="index")

    with open(os.path.join(METRICS_DIR, "tariff_stats.json"), "w") as f:
        json.dump(convert_to_serializable(tariff_grp), f, indent=2)
    print("  💾 Saved tariff_stats.json")

    # -------------------------------------------------------------
    # 7. ACORN STATISTICS
    # -------------------------------------------------------------
    print("🏘️ 7. Calculating ACORN Statistics...")
    acorn_grp = df.groupby("Acorn_grouped").agg(
        avg_daily_energy_kwh=("energy_sum", "mean"),
        median_daily_energy_kwh=("energy_sum", "median"),
        std_daily_energy_kwh=("energy_sum", "std"),
        total_records=("energy_sum", "count")
    ).to_dict(orient="index")

    acorn_detail_grp = df.groupby("Acorn").agg(
        avg_daily_energy_kwh=("energy_sum", "mean"),
        median_daily_energy_kwh=("energy_sum", "median"),
        total_records=("energy_sum", "count")
    ).to_dict(orient="index")

    acorn_stats = {
        "acorn_grouped": acorn_grp,
        "acorn_detailed": acorn_detail_grp
    }

    with open(os.path.join(METRICS_DIR, "acorn_stats.json"), "w") as f:
        json.dump(convert_to_serializable(acorn_stats), f, indent=2)
    print("  💾 Saved acorn_stats.json")

    print("\n" + "=" * 50)
    print(f"🎉 ALL METRICS PRECOMPUTED AND SAVED TO: {METRICS_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    precompute_all_metrics()
