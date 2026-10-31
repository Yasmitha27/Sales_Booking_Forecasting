# Sales Booking Forecasting System

## 1. Project Overview

The Sales Booking Forecasting System is a Python-based project that forecasts future sales bookings using opportunity stages, historical conversion rates, sales representative activities, and scenario-based uncertainty.

It helps analyze sales performance, identify delayed opportunities, compare sales targets, and estimate expected revenue.

## 2. Project Objectives

- Forecast expected sales bookings.
- Analyze historical stage conversion rates.
- Generate best-case, base-case, and worst-case forecasts.
- Identify stale and delayed opportunities.
- Analyze sales representative performance and activities.
- Compare product-wise and territory-wise sales.
- Evaluate forecast performance using error metrics.
- Store project data in an SQLite database.

## 3. Technologies Used

- **Programming Language:** Python
- **Libraries:** Pandas, NumPy, Matplotlib
- **Database:** SQLite
- **Development Environment:** Visual Studio Code
- **Data Format:** CSV

## 4. Project Features

### Data Generation
Generates synthetic sales representatives, accounts, opportunities, sales activities, historical bookings, and sales quotas.

### Data Validation
Checks missing values, invalid records, sales probabilities, and forecast calculations.

### Historical Stage Conversion Analysis
Calculates conversion rates based on historical opportunity outcomes.

### Scenario-Based Forecasting
Generates three forecasting scenarios:
- Best Case
- Base Case
- Worst Case

### Quarterly Forecasting
Estimates expected sales across different quarters.

### Sales Representative Performance
Analyzes opportunities and expected sales for each representative.

### Territory-Wise Forecasting
Compares expected sales across different sales territories.

### Stale Opportunity Analysis
Identifies opportunities with no recent activity.

### Opportunity Slippage Analysis
Identifies delayed opportunities and calculates average delay.

### Sales Representative Activity Analysis
Analyzes sales activities performed by representatives.

### Product-Wise Forecasting
Compares expected sales across different products.

### Forecast Evaluation
Compares predicted sales with actual synthetic outcomes using WAPE.




