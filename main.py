
import pandas as pd

from validation import validate_data
from forecast import generate_forecast
from database import save_to_database, view_database
from evaluation import evaluate_forecast
from charts import show_sales_chart


print("STEP 1: Loading forecast snapshots", flush=True)

data = pd.read_csv("data/forecast_snapshots.csv")

print("\nSTEP 2: Validating data", flush=True)
data = validate_data(data)

print("\nSTEP 3: Generating forecast", flush=True)
result = generate_forecast(data)

print("\nSTEP 4: Evaluating forecast", flush=True)
evaluate_forecast(result)

print("\nSTEP 5: Saving forecast to database", flush=True)
save_to_database(result)

view_database()

print("\nSTEP 6: Displaying chart", flush=True)
show_sales_chart(result)

print("\nPROJECT EXECUTION COMPLETED!", flush=True)
