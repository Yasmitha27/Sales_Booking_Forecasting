
import pandas as pd

# Load existing files
activities = pd.read_csv("data/activity_history.csv")
opportunities = pd.read_csv("data/opportunities.csv")

# Get Opportunity_ID and Rep_ID mapping
rep_mapping = opportunities[
    ["Opportunity_ID", "Rep_ID"]
].drop_duplicates()

# Add Rep_ID to activity records
activities = activities.drop(columns=["Rep_ID"], errors="ignore")

activities = activities.merge(
    rep_mapping,
    on="Opportunity_ID",
    how="left"
)

# Check for missing representative IDs
missing = activities["Rep_ID"].isnull().sum()

print("Missing Rep_ID records:", missing)

if missing > 0:
    raise ValueError("Some activities have no matching sales representative!")

# Save updated activity history
activities.to_csv("data/activity_history.csv", index=False)

print("Activity history updated successfully!")
print(activities.head())
