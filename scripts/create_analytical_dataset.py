import pandas as pd

print("Loading datasets...")

energy = pd.read_csv(
    "data/raw/tabular/daily_dataset.csv"
)

households = pd.read_csv(
    "data/raw/tabular/informations_households.csv"
)

weather = pd.read_csv(
    "data/raw/tabular/weather_daily_darksky.csv"
)

print("Converting dates...")

energy["day"] = pd.to_datetime(energy["day"])

weather["time"] = pd.to_datetime(weather["time"])

weather["day"] = weather["time"].dt.date

energy["day"] = energy["day"].dt.date

print("Merging energy and household data...")

merged = energy.merge(
    households,
    on="LCLid",
    how="left"
)

print("Merging weather data...")

merged = merged.merge(
    weather,
    on="day",
    how="left"
)

print(merged.shape)

print(merged.head())

merged.to_csv(
    "data/processed/tables/analytical_dataset.csv",
    index=False
)

print("Dataset saved successfully!")