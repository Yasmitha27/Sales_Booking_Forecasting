
import pandas as pd

folder = "data"

reps = pd.read_csv(f"{folder}/sales_reps.csv")
accounts = pd.read_csv(f"{folder}/accounts.csv")
opportunities = pd.read_csv(f"{folder}/opportunities.csv")
snapshots = pd.read_csv(f"{folder}/forecast_snapshots.csv")
activities = pd.read_csv(f"{folder}/activity_history.csv")
territories = pd.read_csv(f"{folder}/territory_history.csv")

errors = 0

print("\nCOMPLETE DATA VALIDATION")
print("=" * 40)

# 1. Record counts
print("\n1. RECORD COUNTS")
print("Sales representatives:", len(reps))
print("Accounts:", len(accounts))
print("Opportunities:", len(opportunities))
print("Forecast snapshots:", len(snapshots))
print("Activity records:", len(activities))
print("Territory changes:", len(territories))

# 2. Missing values
print("\n2. MISSING VALUE CHECK")

all_data = {
    "Sales reps": reps,
    "Accounts": accounts,
    "Opportunities": opportunities,
    "Snapshots": snapshots,
    "Activities": activities,
    "Territories": territories
}

for name, df in all_data.items():
    missing = df.isnull().sum().sum()
    print(f"{name}: {missing} missing values")
    errors += missing

# 3. Account and representative relationships
print("\n3. RELATIONSHIP CHECK")

invalid_accounts = (
    ~opportunities["Account_ID"].isin(accounts["Account_ID"])
).sum()

invalid_reps = (
    ~opportunities["Rep_ID"].isin(reps["Rep_ID"])
).sum()

print("Invalid account IDs:", invalid_accounts)
print("Invalid rep IDs:", invalid_reps)

errors += invalid_accounts + invalid_reps

# 4. Eight snapshots per opportunity
print("\n4. SNAPSHOT CHECK")

snapshot_counts = snapshots.groupby("Opportunity_ID").size()

wrong_snapshots = (
    snapshot_counts.reindex(
        opportunities["Opportunity_ID"],
        fill_value=0
    ) != 8
).sum()

print("Opportunities without exactly 8 snapshots:", wrong_snapshots)
errors += wrong_snapshots

# 5. Stage progression
print("\n5. STAGE CHECK")

print(snapshots["Stage"].value_counts())

required_stages = {
    "Prospecting",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost"
}

missing_stages = required_stages - set(snapshots["Stage"].unique())

print("Missing stages:", missing_stages)

errors += len(missing_stages)

# 6. Seasonality
print("\n6. SEASONALITY CHECK")

expected_factors = {
    1: 0.90,
    2: 1.00,
    3: 1.10,
    4: 1.20
}

for quarter, expected in expected_factors.items():

    rows = snapshots[
        snapshots["Quarter"] % 4 == quarter
    ]

    wrong = (
        rows["Seasonality_Factor"] != expected
    ).sum()

    print(f"Quarter {quarter}: Incorrect factors = {wrong}")
    errors += wrong

# 7. Deal slippage
print("\n7. DEAL SLIPPAGE CHECK")

merged = snapshots.merge(
    opportunities[["Opportunity_ID", "Original_Close_Date"]],
    on="Opportunity_ID"
)

merged["Original_Close_Date"] = pd.to_datetime(
    merged["Original_Close_Date"]
)

merged["Close_Date"] = pd.to_datetime(
    merged["Close_Date"]
)

calculated_slippage = (
    merged["Close_Date"] - merged["Original_Close_Date"]
).dt.days

wrong_slippage = (
    merged["Slippage_Days"] != calculated_slippage
).sum()

print("Incorrect slippage records:", wrong_slippage)
errors += wrong_slippage

# 8. Stale opportunities
print("\n8. STALE OPPORTUNITY CHECK")

expected_stale = snapshots["Days_Since_Activity"] > 90

actual_stale = (
    snapshots["Is_Stale"]
    .astype(str)
    .str.lower()
    .isin(["true", "1"])
)

wrong_stale = (
    expected_stale != actual_stale
).sum()

print("Incorrect stale flags:", wrong_stale)
errors += wrong_stale

# 9. Expected sales calculation
print("\n9. EXPECTED SALES CHECK")

calculated_sales = (
    snapshots["Amount"]
    * snapshots["Probability"]
    * snapshots["Seasonality_Factor"]
)

wrong_sales = (
    (snapshots["Expected_Sales"] - calculated_sales).abs() > 0.01
).sum()

print("Incorrect expected sales records:", wrong_sales)
errors += wrong_sales

# 10. Territory changes
print("\n10. TERRITORY CHECK")

territory_errors = 0

for _, change in territories.iterrows():

    if change["Entity_Type"] == "Account":

        rows = snapshots[
            snapshots["Account_ID"] == change["Entity_ID"]
        ]

        actual_column = "Account_Territory"

    elif change["Entity_Type"] == "SalesRep":

        rows = snapshots[
            snapshots["Rep_ID"] == change["Entity_ID"]
        ]

        actual_column = "Rep_Territory"

    else:
        territory_errors += 1
        continue

    before = rows[
        rows["Quarter"] < change["Effective_Quarter"]
    ]

    after = rows[
        rows["Quarter"] >= change["Effective_Quarter"]
    ]

    territory_errors += (
        before[actual_column] != change["Old_Territory"]
    ).sum()

    territory_errors += (
        after[actual_column] != change["New_Territory"]
    ).sum()

print("Incorrect territory records:", territory_errors)
errors += territory_errors

# Final result
print("\n" + "=" * 40)
print("TOTAL VALIDATION ERRORS:", errors)

if errors == 0:
    print("ALL VALIDATION CHECKS PASSED!")
else:
    print("SOME CHECKS FAILED. REVIEW THE RESULTS.")

print("=" * 40)
