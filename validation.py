
def validate_data(data):

    print("\nFORECAST DATA VALIDATION")
    print("------------------------")

    # Required columns
    required_columns = [
        "Opportunity_ID",
        "Amount",
        "Probability",
        "Seasonality_Factor",
        "Expected_Sales",
        "Stage",
        "Snapshot_Date",
        "Quarter"
    ]

    # Check required columns
    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Check missing values
    missing_count = data[required_columns].isnull().sum().sum()

    # Check valid stages
    valid_stages = [
        "Prospecting",
        "Qualification",
        "Proposal",
        "Negotiation",
        "Closed Won",
        "Closed Lost"
    ]

    valid_rows = (
        (data["Amount"] > 0)
        & data["Probability"].between(0, 1)
        & (data["Seasonality_Factor"] > 0)
        & data["Stage"].isin(valid_stages)
        & data["Quarter"].between(1, 8)
    )

    # Check expected sales calculation
    calculated_sales = (
        data["Amount"]
        * data["Probability"]
        * data["Seasonality_Factor"]
    )

    incorrect_sales = (
        (data["Expected_Sales"] - calculated_sales).abs() > 0.01
    )

    invalid_count = (~valid_rows).sum() + incorrect_sales.sum()

    print("Missing values:", missing_count)
    print("Invalid records:", invalid_count)
    print("Valid records:", len(data) - invalid_count)

    if missing_count > 0 or invalid_count > 0:
        raise ValueError("Forecast data validation failed!")

    print("All forecast data checks passed!")

    return data.copy()
