
import pandas as pd


def generate_forecast(data):

    data = data.copy()

    # --------------------------------------------------
    # 1. HISTORICAL STAGE CONVERSION ANALYSIS
    # --------------------------------------------------

    print("\nHISTORICAL STAGE CONVERSION ANALYSIS")
    print("====================================")

    outcomes = pd.read_csv("data/final_outcomes.csv")

    resolved = outcomes[
        outcomes["Final_Outcome"].isin(["Won", "Lost"])
    ][["Opportunity_ID", "Final_Outcome"]]

    stage_history = data[
        ["Opportunity_ID", "Stage"]
    ].drop_duplicates()

    stage_history = stage_history.merge(
        resolved,
        on="Opportunity_ID",
        how="inner"
    )

    conversion_rates = stage_history.groupby("Stage").agg(
        Total_Opportunities=("Opportunity_ID", "nunique"),
        Won_Opportunities=(
            "Final_Outcome",
            lambda x: (x == "Won").sum()
        )
    ).reset_index()

    conversion_rates["Conversion_Rate"] = (
        conversion_rates["Won_Opportunities"]
        / conversion_rates["Total_Opportunities"]
    )

    print(conversion_rates.to_string(index=False))

    probability_lookup = dict(
        zip(
            conversion_rates["Stage"],
            conversion_rates["Conversion_Rate"]
        )
    )

    data["Probability"] = data["Stage"].map(
        probability_lookup
    )

    data["Probability"] = data["Probability"].fillna(0)

    # Recalculate expected sales

    data["Expected_Sales"] = (
        data["Amount"]
        * data["Probability"]
        * data["Seasonality_Factor"]
    )

    # --------------------------------------------------
    # 2. LATEST SNAPSHOT
    # --------------------------------------------------

    latest = (
        data.sort_values("Snapshot_Date")
        .groupby("Opportunity_ID")
        .tail(1)
        .copy()
    )

    # --------------------------------------------------
    # 3. SCENARIO-BASED FORECASTING
    # --------------------------------------------------

    print("\nSCENARIO-BASED FORECAST")
    print("=======================")

    total_forecast = latest["Expected_Sales"].sum()

    best_case = total_forecast * 1.15
    base_case = total_forecast
    worst_case = total_forecast * 0.80

    scenarios = pd.DataFrame({
        "Scenario": [
            "Best Case",
            "Base Case",
            "Worst Case"
        ],
        "Forecast_Amount": [
            best_case,
            base_case,
            worst_case
        ]
    })

    print(scenarios.to_string(index=False))

    # --------------------------------------------------
    # 4. SCENARIO UNCERTAINTY ANALYSIS
    # --------------------------------------------------

    print("\nSCENARIO-BASED UNCERTAINTY ANALYSIS")
    print("===================================")

    best_difference = best_case - base_case
    worst_difference = base_case - worst_case

    uncertainty_range = best_case - worst_case

    uncertainty_percentage = (
        uncertainty_range / base_case * 100
        if base_case != 0 else 0
    )

    print(f"Best Case Forecast: ₹{best_case:,.2f}")
    print(f"Base Case Forecast: ₹{base_case:,.2f}")
    print(f"Worst Case Forecast: ₹{worst_case:,.2f}")
    print(f"Best Case Difference: ₹{best_difference:,.2f}")
    print(f"Worst Case Difference: ₹{worst_difference:,.2f}")
    print(f"Total Uncertainty Range: ₹{uncertainty_range:,.2f}")
    print(f"Uncertainty Percentage: {uncertainty_percentage:.2f}%")

    # --------------------------------------------------
    # 5. QUARTERLY FORECAST
    # --------------------------------------------------

    print("\nQUARTERLY FORECAST")
    print("==================")

    quarterly_forecast = (
        data.groupby("Snapshot_Date")["Expected_Sales"]
        .sum()
        .sort_index()
    )

    print(quarterly_forecast)

    # --------------------------------------------------
    # 6. SALES REPRESENTATIVE PERFORMANCE
    # --------------------------------------------------

    print("\nSALES REPRESENTATIVE PERFORMANCE")
    print("=================================")

    if "Rep_ID" in latest.columns:

        rep_performance = latest.groupby("Rep_ID").agg(
            Total_Opportunities=("Opportunity_ID", "nunique"),
            Expected_Sales=("Expected_Sales", "sum")
        ).reset_index()

        print(rep_performance.head(10).to_string(index=False))

    # --------------------------------------------------
    # 7. TERRITORY FORECAST
    # --------------------------------------------------

    print("\nTERRITORY FORECAST")
    print("==================")

    if "Account_Territory" in latest.columns:

        territory_forecast = latest.groupby(
            "Account_Territory"
        ).agg(
            Total_Opportunities=("Opportunity_ID", "nunique"),
            Expected_Sales=("Expected_Sales", "sum")
        ).reset_index()

        print(territory_forecast.to_string(index=False))

    # --------------------------------------------------
    # 8. STALE OPPORTUNITY ANALYSIS
    # --------------------------------------------------

    print("\nSTALE OPPORTUNITY ANALYSIS")
    print("==========================")

    if "Is_Stale" in latest.columns:

        stale_count = latest["Is_Stale"].sum()

        active_count = len(latest) - stale_count

        print("Stale Opportunities:", stale_count)
        print("Active Opportunities:", active_count)

    # --------------------------------------------------
    # 9. OPPORTUNITY SLIPPAGE ANALYSIS
    # --------------------------------------------------

    print("\nOPPORTUNITY SLIPPAGE ANALYSIS")
    print("=============================")

    if "Slippage_Days" in latest.columns:

        delayed = latest[
            latest["Slippage_Days"] > 0
        ]

        on_time = latest[
            latest["Slippage_Days"] <= 0
        ]

        average_delay = (
            delayed["Slippage_Days"].mean()
            if len(delayed) > 0 else 0
        )

        print("Delayed Opportunities:", len(delayed))
        print("On-time Opportunities:", len(on_time))
        print(f"Average Delay: {average_delay:.2f} days")

    # --------------------------------------------------
    # 10. SALES REP ACTIVITY ANALYSIS
    # --------------------------------------------------

    print("\nSALES REP ACTIVITY ANALYSIS")
    print("===========================")

    try:

        activity = pd.read_csv("data/activity_history.csv")

        if "Rep_ID" in activity.columns:

            activity_report = activity.groupby("Rep_ID").size()

            print("Total Activity Records:", len(activity))
            print("Sales Representatives with Activity:",
                  activity["Rep_ID"].nunique())

            print("\nTop 10 Representatives by Activity:")

            print(
                activity_report
                .sort_values(ascending=False)
                .head(10)
                .to_string()
            )

    except FileNotFoundError:

        print("Activity history file not found.")

    # --------------------------------------------------
    # 11. PRODUCT-WISE SALES FORECASTING
    # --------------------------------------------------

    print("\nPRODUCT-WISE SALES FORECAST")
    print("===========================")

    if "Product" in latest.columns:

        product_forecast = (
            latest.groupby("Product").agg(
                Total_Opportunities=(
                    "Opportunity_ID", "nunique"
                ),
                Total_Amount=("Amount", "sum"),
                Expected_Sales=("Expected_Sales", "sum")
            ).reset_index()
        )

        product_forecast = product_forecast.sort_values(
            by="Expected_Sales",
            ascending=False
        )

        print(
            product_forecast.to_string(index=False)
        )

        print("\nProduct-wise forecasting completed!")

    else:

        print("Product column not found in forecast data.")

    # --------------------------------------------------
    # 12. RETURN FORECAST RESULTS
    # --------------------------------------------------

    return data
    print("\nSALES REPRESENTATIVE QUOTA ACHIEVEMENT")
    print("======================================")

    bookings = pd.read_csv("data/historical_bookings.csv")
    quotas = pd.read_csv("data/sales_quotas.csv")

    # Calculate Q4 bookings for each representative
    rep_bookings = (
        bookings[bookings["Booking_Quarter"] == "2026Q4"]
        .groupby("Rep_ID")["Booking_Amount"]
        .sum()
        .reset_index()
    )

    # Select Q4 quotas (Quarter 8)
    q4_quotas = quotas[quotas["Quarter"] == 8][
        ["Rep_ID", "Quota_Amount"]
    ]

    # Combine bookings and quotas
    quota_analysis = rep_bookings.merge(
        q4_quotas,
        on="Rep_ID",
        how="right"
    )

    quota_analysis["Booking_Amount"] = (
        quota_analysis["Booking_Amount"].fillna(0)
    )

    # Calculate achievement percentage
    quota_analysis["Achievement_Percentage"] = (
        quota_analysis["Booking_Amount"]
        / quota_analysis["Quota_Amount"]
    ) * 100

    quota_analysis["Quota_Status"] = (
        quota_analysis["Achievement_Percentage"]
        .apply(
            lambda x: "Achieved" if x >= 100 else "Not Achieved"
        )
    )

    quota_analysis = quota_analysis.sort_values(
        by="Achievement_Percentage",
        ascending=False
    )

    print(
        quota_analysis.head(10).to_string(index=False)
    )

    print("\nQuota achievement analysis completed!")