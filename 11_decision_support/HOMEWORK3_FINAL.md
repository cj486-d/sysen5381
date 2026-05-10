# Homework 3: AI Report Validation System

Name: Chunlin Jiang  
Course: SYSEN 5381  

## Writing Component

My validation system is designed to evaluate AI-generated policy reports for decision-support quality, not just general writing quality. I built a customized framework that emphasizes whether a report is reliable enough for policy use: evidence reliability, decision usability, institutional communication quality, and explicit risk flags. This differs from the Module 9 LAB rubric because I did not reuse the fixed overall Likert setup as-is. Instead, I defined a weighted custom score and added risk penalties for low-confidence reporting behaviors.

The customized framework uses five derived components and a final weighted score. First, **Evidence Reliability** is computed from accuracy and faithfulness, because factual correctness and source alignment are primary for policy validation. Second, **Decision Usability** is computed from clarity, succinctness, and relevance, because staff need outputs that are actionable and readable. Third, **Institutional Communication** uses formality as a governance-oriented quality dimension for official communication contexts. I then add two binary risk controls: `unsupported_claim_risk` and `weak_grounding_risk` (triggered when accuracy or faithfulness are low). The final **custom_total_score** is: `0.45*evidence_reliability + 0.35*decision_usability + 0.20*institutional_communication - 0.40*risk_penalty`.

For the experiment, I used the prompt comparison dataset from Module 9 and evaluated three prompt groups (A, B, C), each with 30 reports (N=90). I implemented a reproducible analysis script that computes custom scores per report, summary statistics by prompt, pairwise Welch t-tests, and one-way ANOVA. The custom-score means were: Prompt A = 4.2283, Prompt B = 3.5583, Prompt C = 3.2417. Pairwise Welch tests were all significant (A vs B: t=8.2104, p=8.29e-11; A vs C: t=12.0909, p=2.08e-16; B vs C: t=3.2679, p=0.00182). ANOVA confirmed prompt-level differences overall (F=67.0532, p=2.39e-18), so I reject the null hypothesis that prompts perform equally under this customized validator.

The main challenge was designing a validator that is strict enough to penalize risky outputs but stable enough for batch scoring. I solved this by keeping the scoring formula deterministic and separating quality dimensions from risk penalties. Another challenge is that prompt style can trade off between formality and succinctness; the weighted design makes these tradeoffs visible instead of hiding them in one broad score. Overall, this system works as a practical validation layer: it ranks prompt quality, quantifies uncertainty-related risks, and provides statistically defensible comparisons for prompt selection.

## Git Repository Links

- Validation system script/code:  
  [hw3_custom_validation_analysis.py](https://github.com/cj486-d/sysen5381/blob/main/11_decision_support/hw3_custom_validation_analysis.py)
- Validation criteria/rubric definition (in code + writeup):  
  [HOMEWORK3_FINAL.md](https://github.com/cj486-d/sysen5381/blob/main/11_decision_support/HOMEWORK3_FINAL.md)
- Example validation outputs/results:  
  [hw3_custom_prompt_summary.csv](https://github.com/cj486-d/sysen5381/blob/main/11_decision_support/hw3_outputs/hw3_custom_prompt_summary.csv)  
  [hw3_statistical_results.txt](https://github.com/cj486-d/sysen5381/blob/main/11_decision_support/hw3_outputs/hw3_statistical_results.txt)
- Reports/scores validated (source data from prior module work):  
  [prompt_comparison_scores.csv](https://github.com/cj486-d/sysen5381/blob/main/09_text_analysis/data/prompt_comparison_scores.csv)

## Documentation

### Validation Criteria Table

| Dimension | Description | Scale/Method | Benchmark |
|---|---|---|---|
| Evidence Reliability | Factual and source alignment quality | Mean of `accuracy` and `faithfulness` (1-5) | >=4.0 target |
| Decision Usability | Actionability/readability for staff decisions | Mean of `clarity`, `succinctness`, `relevance` (1-5) | >=3.7 target |
| Institutional Communication | Suitability for formal policy communication | `formality` (1-5) | >=3.5 target |
| Unsupported Claim Risk | Risk flag when low factual rigor appears | Binary (`accuracy<=3`) | 0 preferred |
| Weak Grounding Risk | Risk flag when grounding appears weak | Binary (`faithfulness<=3`) | 0 preferred |
| Custom Total Score | Final weighted evaluation score | `0.45*ER + 0.35*DU + 0.20*IC - 0.40*risk_penalty` | Higher is better |

This differs from the LAB because it introduces domain-specific weighting and explicit penalty flags, rather than only using a flat generic Likert aggregate.

### Experimental Design

- Prompt groups: A, B, C
- Reports per prompt: 30
- Total sample size: 90
- Same scoring procedure applied to all reports

### Statistical Analysis

- Hypothesis: Mean custom validation scores are equal across prompt groups
- Tests used: Welch t-tests (pairwise) and one-way ANOVA
- Key results: All pairwise differences significant; ANOVA significant (p < 0.001)
- Conclusion: Prompt choice significantly affects validation performance under this custom rubric

### System Design

The pipeline has four steps: (1) load report-level score data, (2) compute custom criteria and risk flags, (3) aggregate and test group differences, and (4) export outputs for review and plotting. The AI reviewer role is represented through the original module’s report scoring dimensions, then transformed through a policy-focused evaluation layer.

### Technical Details

- Runtime: Python (`/opt/anaconda3/bin/python`)
- Packages: `pandas`, `numpy`, `scipy`, `matplotlib`
- Input data: `09_text_analysis/data/prompt_comparison_scores.csv`
- Generated outputs:
  - `hw3_custom_scored_reports.csv`
  - `hw3_custom_prompt_summary.csv`
  - `hw3_statistical_results.txt`
  - `hw3_prompt_comparison_boxplot.png`

### Usage Instructions

1. Run: `python hw3_custom_validation_analysis.py`
2. Confirm output files are generated in `hw3_outputs/`
3. Use `hw3_statistical_results.txt` for test statistics and p-values
4. Use `hw3_prompt_comparison_boxplot.png` as the prompt-comparison screenshot
5. Insert screenshots and this writeup into one `.docx` and submit on Canvas

## Screenshot/Output Checklist (4-5 images)

1. Validation system in action: script execution terminal output  
2. Example evaluated output: `hw3_custom_scored_reports.csv` rows  
3. Validation criteria/rubric: criteria table from this document  
4. Statistical output: `hw3_statistical_results.txt`  
5. Prompt comparison visualization: `hw3_prompt_comparison_boxplot.png`
