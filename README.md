# A/B Testing Analysis — Landing Page Experiment

## Overview
Statistical analysis of an A/B test conducted by an e-commerce company to determine whether a new landing page design increases conversion rates compared to the existing page. The project applies hypothesis testing, p-value analysis, and confidence intervals to make a data-driven recommendation using SQL Server, Python (scipy, pandas, seaborn), and Power BI.

## Dataset
**Source:** [Kaggle - A/B Testing](https://www.kaggle.com/datasets/zhangluyuan/ab-testing)

- **294,478 raw records** (290,584 after cleaning)
- **Control group:** 145,274 users → old landing page
- **Treatment group:** 145,310 users → new landing page
- Columns: user_id, timestamp, group, landing_page, converted

## Tools Used
- **SQL Server (SSMS)** — data cleaning, exploration, conversion rate analysis
- **Python (pandas, scipy, matplotlib, seaborn)** — statistical testing, visualizations
- **Power BI** — interactive executive dashboard with test results
- **Statistical Methods** — Z-test for proportions, confidence intervals, p-value analysis

## Key Findings

### 1. The New Page Did NOT Improve Conversions
| Group | Users | Conversions | Conversion Rate |
|-------|-------|-------------|----------------|
| Control (old page) | 145,274 | 17,489 | 12.04% |
| Treatment (new page) | 145,310 | 17,264 | 11.88% |

The old page actually performed slightly better than the new page.

### 2. The Difference is NOT Statistically Significant
| Metric | Value |
|--------|-------|
| Observed difference | -0.16% |
| P-value | 0.19 |
| Significance level (α) | 0.05 |
| Result | **Fail to reject null hypothesis** |

With a p-value of 0.19 (far above the 0.05 threshold), we cannot conclude that the new page performs differently from the old page. The observed difference is likely due to random chance.

### 3. Daily Conversion Rates Show No Consistent Pattern
The daily conversion rate trend shows both groups fluctuating around the same range (11-13%) with no clear separation between control and treatment. Neither group consistently outperforms the other over the 23-day test period.

### 4. Data Quality Issues Found and Resolved
- **3,893 mismatched rows** — control users seeing new_page and vice versa (removed)
- **3,894 duplicate users** — users appearing multiple times (deduplicated, kept first visit)
- Clean dataset: 290,584 unique users with correct group-page assignments

## Statistical Methodology

### Hypothesis Setup
- **Null Hypothesis (H₀):** The new page has the same conversion rate as the old page (p_new = p_old)
- **Alternative Hypothesis (H₁):** The new page has a different conversion rate than the old page (p_new ≠ p_old)
- **Significance Level:** α = 0.05

### Test Used: Z-Test for Two Proportions
Chosen because:
- Large sample sizes (>100,000 per group)
- Binary outcome (converted: yes/no)
- Independent groups
- Normal approximation is valid at this sample size

### Interpretation
- **P-value = 0.19** → Greater than α (0.05)
- **Decision:** Fail to reject the null hypothesis
- **Conclusion:** There is no statistically significant difference between the old and new landing pages

## Recommendation
**Do not launch the new page.** The data shows no evidence that it improves conversions, and it may actually perform slightly worse. Recommendations:

1. **Keep the current page** — it performs at least as well as the new design
2. **Investigate specific elements** — instead of a full page redesign, test individual elements (button color, headline, CTA text) one at a time
3. **Run longer or targeted tests** — segment by device type, traffic source, or user demographics to find if the new page works better for specific audiences
4. **Consider other metrics** — conversion rate isn't the only metric; check if the new page affects time on site, bounce rate, or revenue per visitor

## Project Structure
```
├── README.md
├── sql_queries/
│   └── ab_testing_analysis.sql
├── python/
│   └── ab_testing_analysis.ipynb
├── powerbi/
│   └── ab_testing_dashboard.pbix
└── images/
    ├── conversion_comparison.png
    ├── daily_trend.png
    └── powerbi_dashboard.png
```

## SQL Techniques Used
- Data validation and quality checks
- DELETE with compound WHERE conditions for cleaning mismatched rows
- ROW_NUMBER() with CTE for deduplication
- Conditional aggregation for conversion rates
- CAST/CONVERT for date extraction from timestamps
- Reserved keyword handling with square brackets ([group])

## Python Techniques Used
- **scipy.stats** — proportions_ztest for hypothesis testing
- **statsmodels** — confidence interval calculation
- **pandas** — data cleaning, groupby, daily aggregation
- **seaborn/matplotlib** — comparison charts, daily trend visualization
- Statistical interpretation and business recommendation

## Statistical Concepts Applied
- Hypothesis testing (null vs alternative)
- P-value interpretation
- Statistical significance (α = 0.05)
- Z-test for two proportions
- Confidence intervals
- Type I and Type II errors
- Sample size considerations

## How to Reproduce
1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/zhangluyuan/ab-testing)
2. **SQL Server:** Create database `ABTesting`, import `ab_data.csv`, run cleaning queries first
3. **Python:** Install pandas, scipy, statsmodels, matplotlib, seaborn. Run the notebook
4. **Power BI:** Open the .pbix file or load cleaned data into Power BI Desktop

## Author
Built as part of a self-taught Data Analyst portfolio. Third project in a series demonstrating SQL, Python, Power BI, and statistical analysis skills applied to real business problems.
