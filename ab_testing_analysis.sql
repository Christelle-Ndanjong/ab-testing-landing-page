-- ============================================================
-- A/B Testing Analysis — Landing Page Experiment
-- Dataset: A/B Testing (Kaggle)
-- Database: SQL Server (T-SQL)
-- ============================================================

USE ABTesting;
GO


-- ============================================================
-- DATA VALIDATION
-- Verify data integrity before analysis
-- ============================================================

-- Total row count
SELECT COUNT(*) AS total_rows FROM ab_data;
-- Result: 294,478 rows


-- ============================================================
-- DATA CLEANING
-- Fix mismatched groups and remove duplicates
-- ============================================================

-- Check for mismatched data (control seeing new page or treatment seeing old page)
SELECT [group], landing_page, COUNT(*) AS count
FROM ab_data
GROUP BY [group], landing_page;
-- Result: 1,965 treatment users saw old_page, 1,928 control users saw new_page

-- Count mismatched rows
SELECT COUNT(*) AS mismatched_rows
FROM ab_data
WHERE ([group] = 'control' AND landing_page = 'new_page')
   OR ([group] = 'treatment' AND landing_page = 'old_page');
-- Result: 3,893 mismatched rows

-- Remove mismatched rows
DELETE FROM ab_data
WHERE ([group] = 'control' AND landing_page = 'new_page')
   OR ([group] = 'treatment' AND landing_page = 'old_page');

-- Check for duplicate users
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT user_id) AS unique_users
FROM ab_data;

-- Remove duplicate users — keep only first visit
WITH duplicates AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY [timestamp]) AS rn
    FROM ab_data
)
DELETE FROM duplicates WHERE rn > 1;

-- Verify clean data
SELECT [group], landing_page, COUNT(*) AS count
FROM ab_data
GROUP BY [group], landing_page;
-- Result: control/old_page 145,274 | treatment/new_page 145,310


-- ============================================================
-- QUESTION 1: Overall Conversion Rate by Group
-- Business Context: Compare conversion performance between
-- the control (old page) and treatment (new page) groups.
-- ============================================================

SELECT
    [group],
    SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) AS total_conversions,
    COUNT(DISTINCT user_id) AS total_visitors,
    ROUND(
        CAST(SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) AS FLOAT) /
        NULLIF(COUNT(DISTINCT user_id), 0) * 100, 2
    ) AS conversion_rate
FROM ab_data
GROUP BY [group];
-- Result: Control 12.04%, Treatment 11.88%


-- ============================================================
-- QUESTION 2: Daily Conversion Rate Trend
-- Business Context: Check if the conversion difference is
-- consistent over time or driven by specific days.
-- ============================================================

SELECT
    CAST([timestamp] AS DATE) AS test_date,
    [group],
    COUNT(*) AS daily_visitors,
    SUM(converted) AS daily_conversions,
    ROUND(
        CAST(SUM(converted) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 2
    ) AS daily_conversion_rate
FROM ab_data
GROUP BY CAST([timestamp] AS DATE), [group]
ORDER BY test_date, [group];


-- ============================================================
-- QUESTION 3: Conversion Summary Statistics
-- Business Context: Provide key metrics for the executive summary
-- ============================================================

SELECT
    COUNT(DISTINCT user_id) AS total_users,
    SUM(converted) AS total_conversions,
    ROUND(CAST(SUM(converted) AS FLOAT) / COUNT(*) * 100, 2) AS overall_conversion_rate,
    SUM(CASE WHEN [group] = 'control' THEN converted ELSE 0 END) AS control_conversions,
    SUM(CASE WHEN [group] = 'treatment' THEN converted ELSE 0 END) AS treatment_conversions,
    ROUND(
        CAST(SUM(CASE WHEN [group] = 'control' THEN converted ELSE 0 END) AS FLOAT) /
        NULLIF(SUM(CASE WHEN [group] = 'control' THEN 1 ELSE 0 END), 0) * 100, 2
    ) AS control_rate,
    ROUND(
        CAST(SUM(CASE WHEN [group] = 'treatment' THEN converted ELSE 0 END) AS FLOAT) /
        NULLIF(SUM(CASE WHEN [group] = 'treatment' THEN 1 ELSE 0 END), 0) * 100, 2
    ) AS treatment_rate
FROM ab_data;


-- ============================================================
-- QUESTION 4: Test Duration and Sample Size
-- Business Context: Verify the test ran long enough with
-- sufficient sample size for statistical validity.
-- ============================================================

SELECT
    MIN(CAST([timestamp] AS DATE)) AS test_start,
    MAX(CAST([timestamp] AS DATE)) AS test_end,
    DATEDIFF(day, MIN(CAST([timestamp] AS DATE)), MAX(CAST([timestamp] AS DATE))) AS test_duration_days,
    COUNT(DISTINCT user_id) AS total_sample_size,
    SUM(CASE WHEN [group] = 'control' THEN 1 ELSE 0 END) AS control_size,
    SUM(CASE WHEN [group] = 'treatment' THEN 1 ELSE 0 END) AS treatment_size
FROM ab_data;


-- ============================================================
-- QUESTION 5: Conversion by Day of Week
-- Business Context: Check if certain days perform differently
-- for control vs treatment groups.
-- ============================================================

SELECT
    DATENAME(WEEKDAY, CAST([timestamp] AS DATE)) AS day_of_week,
    DATEPART(WEEKDAY, CAST([timestamp] AS DATE)) AS day_number,
    [group],
    COUNT(*) AS visitors,
    SUM(converted) AS conversions,
    ROUND(
        CAST(SUM(converted) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 2
    ) AS conversion_rate
FROM ab_data
GROUP BY DATENAME(WEEKDAY, CAST([timestamp] AS DATE)),
         DATEPART(WEEKDAY, CAST([timestamp] AS DATE)),
         [group]
ORDER BY day_number, [group];
