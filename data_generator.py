
import os
import numpy as np
import pandas as pd

SEED = 20261022

TERRITORIES = ["North", "South", "East", "West", "Central"]

PRODUCTS = [
    "CRM Software",
    "Analytics Platform",
    "Cloud Services",
    "AI Solutions",
    "Cybersecurity"
]

STAGES = [
    "Prospecting",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost"
]

STAGE_PROBABILITIES = {
    "Prospecting": 0.10,
    "Qualification": 0.25,
    "Proposal": 0.50,
    "Negotiation": 0.75,
    "Closed Won": 1.00,
    "Closed Lost": 0.00
}

SEASONALITY = {
    1: 0.90,
    2: 1.00,
    3: 1.10,
    4: 1.20
}

QUARTER_DATES = [
    "2025-03-31",
    "2025-06-30",
    "2025-09-30",
    "2025-12-31",
    "2026-03-31",
    "2026-06-30",
    "2026-09-30",
    "2026-12-31"
]


def generate_data(scale=1.0, seed=SEED, output_folder="data"):

    rng = np.random.default_rng(seed)

    os.makedirs(output_folder, exist_ok=True)

    rep_count = round(2000 * scale)
    account_count = round(2000 * scale)
    opportunity_count = round(20000 * scale)

    if min(rep_count, account_count, opportunity_count) < 1:
        raise ValueError("Scale must generate at least one record.")

    snapshot_dates = [
        pd.Timestamp(date) for date in QUARTER_DATES
    ]

    # 1. Generate sales representatives

    rep_ids = [
        f"R{i:04d}" for i in range(1, rep_count + 1)
    ]

    rep_territories = rng.choice(
        TERRITORIES, size=rep_count
    )

    sales_reps = pd.DataFrame({
        "Rep_ID": rep_ids,
        "Rep_Name": [
            f"Rep_{i:04d}" for i in range(1, rep_count + 1)
        ],
        "Territory": rep_territories
    })

    # 2. Generate customer accounts

    account_ids = [
        f"A{i:05d}" for i in range(1, account_count + 1)
    ]

    account_territories = rng.choice(
        TERRITORIES, size=account_count
    )

    account_rep_ids = rng.choice(
        rep_ids, size=account_count
    )

    accounts = pd.DataFrame({
        "Account_ID": account_ids,
        "Account_Name": [
            f"Company_{i:05d}"
            for i in range(1, account_count + 1)
        ],
        "Territory": account_territories,
        "Rep_ID": account_rep_ids
    })

    # 3. Generate territory changes

    territory_history = []

    rep_changes = rng.choice(
        rep_ids,
        size=max(1, round(rep_count * 0.10)),
        replace=False
    )

    account_changes = rng.choice(
        account_ids,
        size=max(1, round(account_count * 0.05)),
        replace=False
    )

    rep_change_lookup = {}
    account_change_lookup = {}

    for rep_id in rep_changes:

        old_territory = sales_reps.loc[
            sales_reps["Rep_ID"] == rep_id,
            "Territory"
        ].iloc[0]

        new_territory = rng.choice([
            t for t in TERRITORIES if t != old_territory
        ])

        effective_quarter = int(rng.integers(2, 9))

        territory_history.append({
            "Entity_Type": "SalesRep",
            "Entity_ID": rep_id,
            "Old_Territory": old_territory,
            "New_Territory": new_territory,
            "Effective_Quarter": effective_quarter
        })

        rep_change_lookup[rep_id] = (
            new_territory, effective_quarter
        )

    for account_id in account_changes:

        old_territory = accounts.loc[
            accounts["Account_ID"] == account_id,
            "Territory"
        ].iloc[0]

        new_territory = rng.choice([
            t for t in TERRITORIES if t != old_territory
        ])

        effective_quarter = int(rng.integers(2, 9))

        territory_history.append({
            "Entity_Type": "Account",
            "Entity_ID": account_id,
            "Old_Territory": old_territory,
            "New_Territory": new_territory,
            "Effective_Quarter": effective_quarter
        })

        account_change_lookup[account_id] = (
            new_territory, effective_quarter
        )

    territory_df = pd.DataFrame(territory_history)

    # 4. Generate opportunities with products

    opportunities = []

    for i in range(1, opportunity_count + 1):

        account_index = int(rng.integers(0, account_count))

        account_id = account_ids[account_index]

        rep_id = account_rep_ids[account_index]

        amount = int(rng.integers(20000, 500001))

        initial_stage = rng.choice(STAGES[:4])

        product = rng.choice(PRODUCTS)

        created_date = (
            pd.Timestamp("2024-01-01")
            + pd.Timedelta(days=int(rng.integers(0, 426)))
        )

        original_close_date = (
            pd.Timestamp("2025-04-01")
            + pd.Timedelta(days=int(rng.integers(0, 640)))
        )

        opportunities.append({
            "Opportunity_ID": f"O{i:06d}",
            "Account_ID": account_id,
            "Rep_ID": rep_id,
            "Product": product,
            "Amount": amount,
            "Stage": initial_stage,
            "Created_Date": created_date,
            "Original_Close_Date": original_close_date
        })

    opportunities_df = pd.DataFrame(opportunities)

    # 5. Generate quarterly snapshots

    forecast_snapshots = []
    activity_history = []
    final_outcomes = []

    for _, opportunity in opportunities_df.iterrows():

        opportunity_id = opportunity["Opportunity_ID"]
        account_id = opportunity["Account_ID"]
        rep_id = opportunity["Rep_ID"]
        product = opportunity["Product"]

        amount = opportunity["Amount"]
        stage = opportunity["Stage"]

        original_close_date = opportunity["Original_Close_Date"]
        close_date = original_close_date

        created_date = opportunity["Created_Date"]

        last_activity_date = (
            created_date
            + pd.Timedelta(days=int(rng.integers(1, 91)))
        )

        for quarter_index, snapshot_date in enumerate(
            snapshot_dates, start=1
        ):

            # Stage progression

            if stage not in ["Closed Won", "Closed Lost"]:

                if stage == "Negotiation":

                    result = rng.random()

                    if result < 0.15:
                        stage = "Closed Won"

                    elif result < 0.25:
                        stage = "Closed Lost"

                else:

                    if rng.random() < 0.35:

                        current_stage = STAGES.index(stage)

                        stage = STAGES[
                            min(current_stage + 1, 4)
                        ]

            # Deal slippage

            if (
                stage not in ["Closed Won", "Closed Lost"]
                and close_date <= snapshot_date
            ):

                delay_days = int(rng.integers(30, 91))

                close_date += pd.Timedelta(
                    days=delay_days
                )

            slippage_days = (
                close_date - original_close_date
            ).days

            # Update activity date

            if rng.random() < 0.65:

                previous_date = (
                    snapshot_dates[quarter_index - 2]
                    if quarter_index > 1
                    else created_date
                )

                available_days = max(
                    1,
                    (snapshot_date - previous_date).days
                )

                activity_day = int(
                    rng.integers(1, available_days + 1)
                )

                last_activity_date = (
                    previous_date
                    + pd.Timedelta(days=activity_day)
                )

            days_since_activity = (
                snapshot_date - last_activity_date
            ).days

            is_stale = days_since_activity > 90

            # Territory updates

            account_territory = accounts.loc[
                accounts["Account_ID"] == account_id,
                "Territory"
            ].iloc[0]

            rep_territory = sales_reps.loc[
                sales_reps["Rep_ID"] == rep_id,
                "Territory"
            ].iloc[0]

            if account_id in account_change_lookup:

                new_territory, effective_quarter = (
                    account_change_lookup[account_id]
                )

                if quarter_index >= effective_quarter:
                    account_territory = new_territory

            if rep_id in rep_change_lookup:

                new_territory, effective_quarter = (
                    rep_change_lookup[rep_id]
                )

                if quarter_index >= effective_quarter:
                    rep_territory = new_territory

            # Seasonality and expected sales

            quarter_number = ((quarter_index - 1) % 4) + 1

            seasonality_factor = SEASONALITY[
                quarter_number
            ]

            probability = STAGE_PROBABILITIES[stage]

            expected_sales = (
                amount
                * probability
                * seasonality_factor
            )

            # Save forecast snapshot

            forecast_snapshots.append({

                "Snapshot_ID": (
                    f"S{len(forecast_snapshots) + 1:07d}"
                ),

                "Snapshot_Date": snapshot_date,
                "Quarter": quarter_index,
                "Opportunity_ID": opportunity_id,
                "Account_ID": account_id,
                "Rep_ID": rep_id,
                "Product": product,
                "Account_Territory": account_territory,
                "Rep_Territory": rep_territory,
                "Stage": stage,
                "Amount": amount,
                "Probability": probability,
                "Seasonality_Factor": seasonality_factor,
                "Expected_Sales": expected_sales,
                "Close_Date": close_date,
                "Slippage_Days": slippage_days,
                "Last_Activity_Date": last_activity_date,
                "Days_Since_Activity": days_since_activity,
                "Is_Stale": is_stale
            })

            # Save activity record

            activity_history.append({

                "Opportunity_ID": opportunity_id,
                "Quarter": quarter_index,
                "Last_Activity_Date": last_activity_date,
                "Days_Since_Activity": days_since_activity

            })

        # Save final outcome

        final_outcomes.append({

            "Opportunity_ID": opportunity_id,
            "Account_ID": account_id,
            "Rep_ID": rep_id,
            "Product": product,
            "Final_Stage": stage,

            "Final_Outcome": (
                "Won" if stage == "Closed Won"
                else "Lost" if stage == "Closed Lost"
                else "Open"
            ),

            "Final_Amount": amount,
            "Final_Close_Date": close_date,
            "Outcome_Snapshot_Date": snapshot_dates[-1]

        })

    final_outcomes_df = pd.DataFrame(final_outcomes)

    # 6. Generate historical bookings

    won_opportunities = final_outcomes_df[
        final_outcomes_df["Final_Outcome"] == "Won"
    ].copy()

    historical_bookings = won_opportunities[[

        "Opportunity_ID",
        "Account_ID",
        "Rep_ID",
        "Product",
        "Final_Amount"

    ]].copy()

    historical_bookings = historical_bookings.rename(
        columns={"Final_Amount": "Booking_Amount"}
    )

    historical_bookings["Booking_Date"] = (
        won_opportunities["Outcome_Snapshot_Date"].values
    )

    historical_bookings["Booking_Quarter"] = (
        pd.to_datetime(
            historical_bookings["Booking_Date"]
        ).dt.to_period("Q").astype(str)
    )

    # 7. Generate quarterly sales quotas

    quota_records = []

    for rep_id in rep_ids:

        for quarter_index, snapshot_date in enumerate(
            snapshot_dates, start=1
        ):

            quota_amount = int(
                rng.integers(1500000, 2500001)
            )

            quota_records.append({

                "Rep_ID": rep_id,
                "Quarter": quarter_index,
                "Quarter_End_Date": snapshot_date,
                "Quota_Amount": quota_amount

            })

    sales_quotas = pd.DataFrame(quota_records)

    # 8. Save all CSV files

    sales_reps.to_csv(
        f"{output_folder}/sales_reps.csv",
        index=False
    )

    accounts.to_csv(
        f"{output_folder}/accounts.csv",
        index=False
    )

    opportunities_df.to_csv(
        f"{output_folder}/opportunities.csv",
        index=False
    )

    territory_df.to_csv(
        f"{output_folder}/territory_history.csv",
        index=False
    )

    pd.DataFrame(forecast_snapshots).to_csv(
        f"{output_folder}/forecast_snapshots.csv",
        index=False
    )

    pd.DataFrame(activity_history).to_csv(
        f"{output_folder}/activity_history.csv",
        index=False
    )

    final_outcomes_df.to_csv(
        f"{output_folder}/final_outcomes.csv",
        index=False
    )

    historical_bookings.to_csv(
        f"{output_folder}/historical_bookings.csv",
        index=False
    )

    sales_quotas.to_csv(
        f"{output_folder}/sales_quotas.csv",
        index=False
    )

    # 9. Display generation results

    print("\nDATA GENERATION COMPLETED")
    print("-------------------------")

    print("Sales Representatives:", len(sales_reps))
    print("Accounts:", len(accounts))
    print("Opportunities:", len(opportunities_df))
    print("Products:", opportunities_df["Product"].nunique())
    print("Territory Changes:", len(territory_df))
    print("Forecast Snapshots:", len(forecast_snapshots))
    print("Activity Records:", len(activity_history))
    print("Final Outcome Records:", len(final_outcomes_df))
    print("Historical Booking Records:", len(historical_bookings))
    print("Sales Quota Records:", len(sales_quotas))

    print("-------------------------")


# Run data generation

if __name__ == "__main__":

    generate_data(
        scale=1.0,
        seed=SEED,
        output_folder="data"
    )
