
import matplotlib.pyplot as plt


def show_sales_chart(data):

    # Calculate total expected sales for each quarter
    quarterly_sales = (
        data.groupby("Snapshot_Date")["Expected_Sales"]
        .sum()
        .sort_index()
    )

    # Create a bar chart
    plt.figure(figsize=(10, 5))

    plt.bar(
        quarterly_sales.index,
        quarterly_sales.values
    )

    # Add chart title and labels
    plt.title("Quarterly Expected Sales Forecast")
    plt.xlabel("Snapshot Date")
    plt.ylabel("Expected Sales (₹)")

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display chart
    plt.show()
