import pandas as pd

energy = pd.read_csv(
    "data/raw/tabular/daily_dataset.csv"
)

households = pd.read_csv(
    "data/raw/tabular/informations_households.csv"
)

weather = pd.read_csv(
    "data/raw/tabular/weather_daily_darksky.csv"
)

print(energy.shape)
print(households.shape)
print(weather.shape)

print("\nEnergy columns:")
print(energy.columns.tolist())

print("\nHousehold columns:")
print(households.columns.tolist())

print("\nWeather columns:")
print(weather.columns.tolist())