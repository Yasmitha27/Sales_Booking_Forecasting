
import sqlite3
import pandas as pd
import os


def save_to_database(data):

    connection = sqlite3.connect("sales.db")

    files = {
        "sales_reps": "data/sales_reps.csv",
        "accounts": "data/accounts.csv",
        "opportunities": "data/opportunities.csv",
        "territory_history": "data/territory_history.csv",
        "forecast_snapshots": "data/forecast_snapshots.csv",
        "activity_history": "data/activity_history.csv",
        "final_outcomes": "data/final_outcomes.csv",
        "historical_bookings": "data/historical_bookings.csv",
        "sales_quotas": "data/sales_quotas.csv"
    }

    for table_name, file_path in files.items():

        if os.path.exists(file_path):

            csv_data = pd.read_csv(file_path)

            csv_data.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False
            )

            print(f"{table_name} table saved successfully!")

    data.to_sql(
        "forecast_results",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()

    print("\nAll project data saved to database!")


def view_database():

    connection = sqlite3.connect("sales.db")

    tables = [
        "sales_reps",
        "accounts",
        "opportunities",
        "forecast_snapshots",
        "historical_bookings",
        "sales_quotas",
        "final_outcomes",
        "forecast_results"
    ]

    print("\nDATABASE TABLE SUMMARY")
    print("----------------------")

    for table in tables:

        result = pd.read_sql_query(
            f"SELECT COUNT(*) AS Total_Records FROM {table}",
            connection
        )

        print(table, ":", result.iloc[0, 0])

    connection.close()
