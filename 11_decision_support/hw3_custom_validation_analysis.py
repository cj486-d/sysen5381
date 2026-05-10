import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('/Users/jiangchunlin/dsai_backup_20260329_134433/09_text_analysis/data')
input_csv = base / 'prompt_comparison_scores.csv'
out_dir = Path('/Users/jiangchunlin/Downloads/hw3_outputs')
out_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_csv)

df['evidence_reliability'] = (df['accuracy'] + df['faithfulness']) / 2.0
df['decision_usability'] = (df['clarity'] + df['succinctness'] + df['relevance']) / 3.0
df['institutional_communication'] = df['formality']

df['unsupported_claim_risk'] = (df['accuracy'] <= 3).astype(int)
df['weak_grounding_risk'] = (df['faithfulness'] <= 3).astype(int)
df['risk_penalty'] = df['unsupported_claim_risk'] + df['weak_grounding_risk']

df['custom_total_score'] = (
    0.45 * df['evidence_reliability'] +
    0.35 * df['decision_usability'] +
    0.20 * df['institutional_communication'] -
    0.40 * df['risk_penalty']
)

summary = df.groupby('prompt_id').agg(
    n=('custom_total_score', 'count'),
    custom_mean=('custom_total_score', 'mean'),
    custom_sd=('custom_total_score', 'std'),
    evidence_mean=('evidence_reliability', 'mean'),
    usability_mean=('decision_usability', 'mean'),
    comm_mean=('institutional_communication', 'mean'),
    risk_rate=('risk_penalty', lambda s: float((s > 0).mean()))
).reset_index()

A = df.loc[df['prompt_id'] == 'A', 'custom_total_score']
B = df.loc[df['prompt_id'] == 'B', 'custom_total_score']
C = df.loc[df['prompt_id'] == 'C', 'custom_total_score']

t_ab = stats.ttest_ind(A, B, equal_var=False)
t_ac = stats.ttest_ind(A, C, equal_var=False)
t_bc = stats.ttest_ind(B, C, equal_var=False)

f_abc, p_abc = stats.f_oneway(A, B, C)

scored_path = out_dir / 'hw3_custom_scored_reports.csv'
summary_path = out_dir / 'hw3_custom_prompt_summary.csv'
stats_path = out_dir / 'hw3_statistical_results.txt'
plot_path = out_dir / 'hw3_prompt_comparison_boxplot.png'

df.to_csv(scored_path, index=False)
summary.to_csv(summary_path, index=False)

with open(stats_path, 'w', encoding='utf-8') as f:
    f.write('Homework 3 Statistical Results\n')
    f.write('====================================\n\n')
    f.write('Sample sizes by prompt:\n')
    f.write(str(df['prompt_id'].value_counts().sort_index().to_dict()) + '\n\n')
    f.write('Custom score summary by prompt:\n')
    f.write(summary.to_string(index=False) + '\n\n')
    f.write('Welch t-test (Prompt A vs Prompt B):\n')
    f.write(f't = {t_ab.statistic:.4f}, p = {t_ab.pvalue:.6g}\n\n')
    f.write('Welch t-test (Prompt A vs Prompt C):\n')
    f.write(f't = {t_ac.statistic:.4f}, p = {t_ac.pvalue:.6g}\n\n')
    f.write('Welch t-test (Prompt B vs Prompt C):\n')
    f.write(f't = {t_bc.statistic:.4f}, p = {t_bc.pvalue:.6g}\n\n')
    f.write('One-way ANOVA (A, B, C):\n')
    f.write(f'F = {f_abc:.4f}, p = {p_abc:.6g}\n\n')
    if p_abc < 0.05:
        f.write('Interpretation: Prompt choice significantly affects custom validation score.\n')
    else:
        f.write('Interpretation: No statistically significant difference by prompt.\n')

plt.figure(figsize=(8,5))
df.boxplot(column='custom_total_score', by='prompt_id', grid=False)
plt.title('Custom Validation Score by Prompt')
plt.suptitle('')
plt.xlabel('Prompt')
plt.ylabel('Custom Total Score')
plt.tight_layout()
plt.savefig(plot_path, dpi=180)

print('WROTE', scored_path)
print('WROTE', summary_path)
print('WROTE', stats_path)
print('WROTE', plot_path)
