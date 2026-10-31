
import pandas as pd


def evaluate_forecast(data):

    print("\nFORECAST ACCURACY REPORT")
    print("========================")

    # Load original forecast data.
    # This preserves the original probabilities before
    # historical conversion rates are applied in forecast.py.

    original_data = pd.read_csv(
        "data/forecast_snapshots.csv"
    )

    # Get the latest original snapshot for each opportunity

    latest = (
        original_data.sort_values("Snapshot_Date")
        .groupby("Opportunity_ID")
        .tail(1)
        .copy()
    )

    # Load final simulated outcomes

    outcomes = pd.read_csv("data/final_outcomes.csv")

    # Keep completed opportunities only

    resolved = outcomes[
        outcomes["Final_Outcome"].isin(["Won", "Lost"])
    ].copy()

    # Calculate actual sales

    resolved["Actual_Sales"] = resolved["Final_Amount"].where(
        resolved["Final_Outcome"] == "Won",
        0
    )

    # Merge latest predictions with final outcomes

    evaluation = latest.merge(
        resolved[["Opportunity_ID", "Actual_Sales"]],
        on="Opportunity_ID",
        how="inner"
    )

    # Calculate prediction errors

    evaluation["Absolute_Error"] = (
        evaluation["Actual_Sales"]
        - evaluation["Expected_Sales"]
    ).abs()

    # Calculate total predicted and actual sales

    predicted_sales = evaluation["Expected_Sales"].sum()

    actual_sales = evaluation["Actual_Sales"].sum()

    total_error = evaluation["Absolute_Error"].sum()

    # Display evaluation details

    print("Evaluation Snapshot:", latest["Snapshot_Date"].max())

    print("Resolved Opportunities:", len(resolved))

    print(
        "Open Opportunities Excluded:",
        outcomes["Final_Outcome"].eq("Open").sum()
    )

    print("\nFINAL SNAPSHOT EVALUATION")
    print("=========================")

    print(f"Predicted Sales: ₹{predicted_sales:,.2f}")
    print(f"Actual Sales: ₹{actual_sales:,.2f}")
    print(f"Total Absolute Error: ₹{total_error:,.2f}")

    # Calculate WAPE

    if actual_sales > 0:

        wape = (total_error / actual_sales) * 100

        accuracy = 100 - wape

        print("\nOVERALL WAPE:", round(wape, 2), "%")

        print(
            "Forecast Accuracy Indicator:",
            round(accuracy, 2),
            "%"
        )

    else:

        print("\nWAPE cannot be calculated because actual sales are zero.")

    print("\nEvaluation completed!")
