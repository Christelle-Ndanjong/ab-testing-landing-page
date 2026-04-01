# %% [markdown]
# # A/B Testing Analysis — Landing Page Experiment
# **Dataset:** A/B Testing (Kaggle)
# 
# Statistical analysis to determine whether a new landing page design
# increases conversion rates compared to the existing page.

# %% [markdown]
# ## Setup & Data Loading

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

df = pd.read_csv('ab_data.csv')
print(f"Raw dataset: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nSample data:")
df.head()

# %% [markdown]
# ## Data Cleaning

# %%
# Check for mismatched groups
print("=== GROUP-PAGE ALIGNMENT ===")
print(pd.crosstab(df['group'], df['landing_page']))

# %%
# Remove mismatched rows (control seeing new_page or treatment seeing old_page)
before = len(df)
df = df[~((df['group'] == 'control') & (df['landing_page'] == 'new_page'))]
df = df[~((df['group'] == 'treatment') & (df['landing_page'] == 'old_page'))]
print(f"Removed {before - len(df)} mismatched rows")

# Remove duplicate users — keep first visit
before = len(df)
df = df.drop_duplicates(subset='user_id', keep='first')
print(f"Removed {before - len(df)} duplicate user rows")
print(f"\nClean dataset: {df.shape}")

# %%
# Verify clean data
print("=== CLEAN DATA VERIFICATION ===")
print(pd.crosstab(df['group'], df['landing_page']))

# %% [markdown]
# ## Question 1: Conversion Rate by Group

# %%
conversion = df.groupby('group').agg(
    users=('user_id', 'count'),
    conversions=('converted', 'sum')
).reset_index()
conversion['conversion_rate'] = round(conversion['conversions'] / conversion['users'] * 100, 2)

print("=== CONVERSION RATES ===")
print(conversion)
print(f"\nDifference: {conversion.loc[conversion['group']=='treatment', 'conversion_rate'].values[0] - conversion.loc[conversion['group']=='control', 'conversion_rate'].values[0]:.2f} percentage points")

# %%
plt.figure(figsize=(8, 5))
colors = ['#3498db', '#e74c3c']
bars = plt.bar(conversion['group'], conversion['conversion_rate'], color=colors)
plt.title('Conversion Rate: Control vs Treatment', fontsize=14, fontweight='bold')
plt.ylabel('Conversion Rate (%)')
plt.ylim(0, 15)

# Add value labels on bars
for bar, rate in zip(bars, conversion['conversion_rate']):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{rate}%', ha='center', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('conversion_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# **Insight:** Control (old page) converts at 12.04% vs Treatment (new page) at 11.88%.
# The old page actually performs slightly better, but is this difference statistically significant?

# %% [markdown]
# ## Question 2: Daily Conversion Rate Trend

# %%
df['date'] = pd.to_datetime(df['timestamp']).dt.date

daily = (df.groupby(['date', 'group'])
         .agg(visitors=('user_id', 'count'),
              conversions=('converted', 'sum'))
         .reset_index())
daily['conversion_rate'] = round(daily['conversions'] / daily['visitors'] * 100, 2)

# %%
fig, ax = plt.subplots(figsize=(14, 5))

for group, color in [('control', '#3498db'), ('treatment', '#e74c3c')]:
    group_data = daily[daily['group'] == group]
    ax.plot(range(len(group_data)), group_data['conversion_rate'],
            marker='o', label=group, color=color, linewidth=2)

ax.set_title('Daily Conversion Rate Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Day')
ax.set_ylabel('Conversion Rate (%)')
ax.legend(title='Group')
ax.set_ylim(10, 14)
plt.tight_layout()
plt.savefig('daily_trend.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# **Insight:** Both groups fluctuate around the same range (11-13%) with no clear
# separation. Neither group consistently outperforms the other over the test period.

# %% [markdown]
# ## Statistical Test: Z-Test for Two Proportions

# %% [markdown]
# ### Hypothesis Setup
# - **H₀ (Null):** p_new = p_old (no difference in conversion rates)
# - **H₁ (Alternative):** p_new ≠ p_old (there is a difference)
# - **Significance Level:** α = 0.05

# %%
# Extract values for the test
control = df[df['group'] == 'control']
treatment = df[df['group'] == 'treatment']

control_conversions = control['converted'].sum()
treatment_conversions = treatment['converted'].sum()
control_size = len(control)
treatment_size = len(treatment)

print("=== TEST INPUTS ===")
print(f"Control: {control_conversions} conversions out of {control_size} ({control_conversions/control_size*100:.2f}%)")
print(f"Treatment: {treatment_conversions} conversions out of {treatment_size} ({treatment_conversions/treatment_size*100:.2f}%)")

# %%
# Perform Z-test for two proportions
from statsmodels.stats.proportion import proportions_ztest

count = np.array([treatment_conversions, control_conversions])
nobs = np.array([treatment_size, control_size])

z_stat, p_value = proportions_ztest(count, nobs, alternative='two-sided')

print("=== Z-TEST RESULTS ===")
print(f"Z-statistic: {z_stat:.4f}")
print(f"P-value: {p_value:.4f}")
print(f"Significance level (α): 0.05")
print(f"\nDecision: {'REJECT null hypothesis ✓' if p_value < 0.05 else 'FAIL TO REJECT null hypothesis ✗'}")
print(f"\nInterpretation: {'The difference IS statistically significant.' if p_value < 0.05 else 'The difference is NOT statistically significant.'}")

# %% [markdown]
# ### Result: P-value = 0.19
# Since 0.19 > 0.05 (our significance level), we **fail to reject the null hypothesis**.
# There is no statistically significant difference between the old and new landing pages.
# The observed 0.16% difference is likely due to random chance.

# %% [markdown]
# ## Confidence Interval

# %%
from statsmodels.stats.proportion import confint_proportions_2indep

# Calculate 95% confidence interval for the difference
ci_low, ci_high = confint_proportions_2indep(
    treatment_conversions, treatment_size,
    control_conversions, control_size,
    method='wald'
)

observed_diff = (treatment_conversions/treatment_size) - (control_conversions/control_size)

print("=== CONFIDENCE INTERVAL ===")
print(f"Observed difference: {observed_diff*100:.4f} percentage points")
print(f"95% CI: [{ci_low*100:.4f}%, {ci_high*100:.4f}%]")
print(f"\nThe CI includes 0, confirming no significant difference.")

# %%
# Visualize the confidence interval
fig, ax = plt.subplots(figsize=(10, 4))
ax.errorbar(observed_diff*100, 0, xerr=[[abs(observed_diff*100 - ci_low*100)], [abs(ci_high*100 - observed_diff*100)]],
            fmt='o', color='#e74c3c', markersize=10, capsize=10, linewidth=2)
ax.axvline(x=0, color='black', linestyle='--', linewidth=1, label='No difference')
ax.set_xlabel('Difference in Conversion Rate (percentage points)')
ax.set_title('95% Confidence Interval for Treatment - Control Difference', fontsize=14, fontweight='bold')
ax.set_yticks([])
ax.legend()
plt.tight_layout()
plt.savefig('confidence_interval.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# **Insight:** The 95% confidence interval includes 0, meaning the true difference
# could be zero — confirming there is no significant effect of the new page.

# %% [markdown]
# ## Executive Dashboard

# %%
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('A/B Testing Analysis — Landing Page Experiment', fontsize=18, fontweight='bold')

# 1. Conversion rate comparison
colors = ['#3498db', '#e74c3c']
bars = axes[0,0].bar(['Control\n(Old Page)', 'Treatment\n(New Page)'],
                      [control_conversions/control_size*100, treatment_conversions/treatment_size*100],
                      color=colors)
axes[0,0].set_title('Conversion Rate by Group', fontweight='bold')
axes[0,0].set_ylabel('Conversion Rate (%)')
axes[0,0].set_ylim(0, 15)
for bar, rate in zip(bars, [control_conversions/control_size*100, treatment_conversions/treatment_size*100]):
    axes[0,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                   f'{rate:.2f}%', ha='center', fontsize=12, fontweight='bold')

# 2. Daily trend
for group, color in [('control', '#3498db'), ('treatment', '#e74c3c')]:
    group_data = daily[daily['group'] == group]
    axes[0,1].plot(range(len(group_data)), group_data['conversion_rate'],
                   marker='o', label=group, color=color, linewidth=2, markersize=4)
axes[0,1].set_title('Daily Conversion Rate Trend', fontweight='bold')
axes[0,1].set_xlabel('Day')
axes[0,1].set_ylabel('Conversion Rate (%)')
axes[0,1].legend(title='group')
axes[0,1].set_ylim(10, 14)

# 3. Sample size comparison
axes[1,0].bar(['Control', 'Treatment'], [control_size, treatment_size], color=colors)
axes[1,0].set_title('Sample Size per Group', fontweight='bold')
axes[1,0].set_ylabel('Number of Users')
for i, (count, label) in enumerate(zip([control_size, treatment_size], ['Control', 'Treatment'])):
    axes[1,0].text(i, count + 1000, f'{count:,}', ha='center', fontsize=11, fontweight='bold')

# 4. Statistical test result
axes[1,1].axis('off')
result_text = f"""
    STATISTICAL TEST RESULTS

    Test: Z-Test for Two Proportions
    
    Control Rate:     {control_conversions/control_size*100:.2f}%
    Treatment Rate:   {treatment_conversions/treatment_size*100:.2f}%
    Difference:       {observed_diff*100:.2f} pp
    
    Z-statistic:      {z_stat:.4f}
    P-value:          {p_value:.4f}
    Significance (α): 0.05
    
    DECISION: Do Not Launch New Page
    
    The p-value ({p_value:.2f}) exceeds our significance
    threshold (0.05). There is no evidence that
    the new page improves conversions.
"""
axes[1,1].text(0.1, 0.5, result_text, transform=axes[1,1].transAxes,
               fontsize=12, verticalalignment='center', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#dee2e6'))

plt.subplots_adjust(hspace=0.35, wspace=0.3)
plt.savefig('ab_testing_dashboard.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# ## Executive Summary
# 
# ### Finding
# The A/B test of 290,584 users over 23 days shows **no statistically significant 
# difference** between the old and new landing pages. The old page converts at 12.04% 
# versus 11.88% for the new page (p-value = 0.19).
# 
# ### Recommendation: Do Not Launch the New Page
# 1. **Keep the current page** — it performs at least as well as the new design
# 2. **Test individual elements** — instead of a full redesign, A/B test specific 
#    components (button color, headline, CTA text) one at a time
# 3. **Segment the analysis** — check if the new page works better for specific 
#    audiences (mobile vs desktop, new vs returning users)
# 4. **Consider other metrics** — examine bounce rate, time on site, and revenue 
#    per visitor in addition to conversion rate
# 
# ### Statistical Details
# - **Test:** Two-proportion Z-test (two-sided)
# - **Sample size:** 145,274 control + 145,310 treatment
# - **P-value:** 0.19 (threshold: 0.05)
# - **95% CI for difference:** includes 0
# - **Conclusion:** Fail to reject null hypothesis — no significant difference
