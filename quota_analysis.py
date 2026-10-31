
import pandas as pd


def analyze_quota_achievement():

    print("\nSALES REPRESENTATIVE QUOTA ACHIEVEMENT")
    print("======================================")

    # Load booking and quota data
    bookings = pd.read_csv("data/historical_bookings.csv")
    quotas = pd.read_csv("data/sales_quotas.csv")

    # Calculate Q4 booking totals
    rep_bookings = (
        bookings[bookings["Booking_Quarter"] == "2026Q4"]
        .groupby("Rep_ID")["Booking_Amount"]
        .sum()
        .reset_index()
    )

    # Select Q4 quotas (Quarter 8)
    q4_quotas = quotas[
        quotas["Quarter"] == 8
    ][["Rep_ID", "Quota_Amount"]]

    # Combine bookings and quotas
    quota_analysis = q4_quotas.merge(
        rep_bookings,
        on="Rep_ID",
        how="left"
    )

    # Replace missing bookings with zero
    quota_analysis["Booking_Amount"] = (
        quota_analysis["Booking_Amount"].fillna(0)
    )

    # Calculate quota achievement percentage
    quota_analysis["Achievement_Percentage"] = (
        quota_analysis["Booking_Amount"]
        / quota_analysis["Quota_Amount"]
    ) * 100

    # Identify quota status
    quota_analysis["Quota_Status"] = (
        quota_analysis["Achievement_Percentage"].apply(
            lambda x: "Achieved" if x >= 100 else "Not Achieved"
        )
    )

    # Sort by achievement percentage
    quota_analysis = quota_analysis.sort_values(
        by="Achievement_Percentage",
        ascending=False
    )

    # Display top 10 representatives
    print("\nTOP 10 REPRESENTATIVES")
    print("----------------------")

    print(
        quota_analysis.head(10).to_string(index=False)
    )

    # Overall quota summary
    total_bookings = quota_analysis["Booking_Amount"].sum()
    total_quota = quota_analysis["Quota_Amount"].sum()

    overall_achievement = (
        total_bookings / total_quota
    ) * 100

    achieved_count = (
        quota_analysis["Quota_Status"] == "Achieved"
    ).sum()

    print("\nOVERALL QUOTA SUMMARY")
    print("---------------------")

    print(f"Total Representatives: {len(quota_analysis)}")
    print(f"Total Bookings: ₹{total_bookings:,.2f}")
    print(f"Total Quota: ₹{total_quota:,.2f}")
    print(f"Overall Achievement: {overall_achievement:.2f}%")
    print(f"Representatives Achieving Quota: {achieved_count}")
    print(
        f"Representatives Not Achieving Quota: "
        f"{len(quota_analysis) - achieved_count}"
    )

    print("\nQuota achievement analysis completed!")

    # Save results
    quota_analysis.to_csv(
        "data/quota_achievement.csv",
        index=False
    )

    print("Quota analysis saved successfully!")


if __name__ == "__main__":
    analyze_quota_achievement()
