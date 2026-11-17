# College Placement Insights — R + Shiny project

## What the project studies
The project mines student survey responses for recurring combinations of preparation, skill confidence, internship experience, placement confidence, and salary expectations. A separate model uses those answers to estimate the chance that a similar respondent reports **high placement confidence** (score 4 or 5).

That prediction is about reported confidence. The form does not ask whether a student received an offer, so the app does not predict actual hiring or placement success.

## Your uploaded response file
The supplied export has 70 rows and includes year, branch, CGPA range, technical-skill confidence, preparation frequency, internship/project experience, placement confidence, and expected salary range. It does **not** include a support-priority question. The app recognizes the confidence question wording in this export and charts salary expectations. The pattern mining uses only fields present in this survey.

## Files
- `app.R` — interactive Shiny dashboard, association-rule mining, and confidence model.
- `sample_responses.csv` — synthetic example data for trying the app. It is not real survey data.
- `placement_survey_250_mixed_observed_synthetic.csv` — 70 original responses plus 180 generated rows, each labeled by source. The app excludes generated rows by default. The 180 generated rows are simulations sampled from the observed answer distributions, with confidence answers sampled by preparation rating. They are not new respondents or independent evidence; use this mixed file for app demonstration only.
- `google_form_questionnaire.md` — the questions visible in the supplied response export and the fields available for analysis.

## Run the app
You need R and RStudio. In RStudio, open this project folder, open `app.R`, and click **Run App**. Install Shiny once if R asks:

```r
install.packages("shiny")
```

Or run this in the R console after setting the working directory to this folder:

```r
shiny::runApp()
```

The app opens with the synthetic sample and marks it as demo data. Upload the original 70-row Google Forms CSV for your real results. If you upload the 250-row mixed file, the app uses only its 70 observed rows by default; the checkbox can include generated rows for interface demonstration, with a warning that the combined results are synthetic/mixed.

## What the app shows
1. **Overview:** response count, average ratings, salary expectations, and confidence averages by preparation score.
2. **Pattern mining:** recurring pairs of answers, with support, confidence, and lift.
3. **Predict confidence:** enter preparation, technical-skill confidence, and internship status. The model estimates the chance of a high self-reported confidence score.
4. **Data and limits:** sample-size and interpretation notes.

Association-rule measures in plain language:
- **Support:** how many respondents gave both answers in the pattern.
- **Confidence:** among respondents with the first answer, how many also gave the second.
- **Lift:** whether the two answers occur together more often than expected from the second answer's overall frequency. Lift above 1 means they co-occur more often than that baseline.

The app filters rules to patterns seen in at least 3 respondents and 10% of usable responses. If the survey is small, it may show no rules; report that honestly.

## How prediction works
The app uses logistic regression with preparation rating, technical-skill rating, and internship experience (when both internship answers are present) to estimate whether a respondent would rate placement confidence 4 or 5. It enables the model only when there are at least 30 complete records and at least 5 examples in each confidence group. At 40 or more complete responses, it also shows five-fold cross-validation accuracy and a majority-class baseline. If model accuracy is close to that baseline, the model adds little predictive value.

## Important limits
- The survey is self-reported and likely a convenience sample of classmates.
- Association rules show answers that co-occur; they do not prove one answer causes another.
- Confidence is not an actual placement result. Do not label the prediction as a placement probability.
- The synthetic CSV only demonstrates the interface and code. Replace it with the Google Forms export before presenting findings.
- If response counts are low, show counts and averages; do not overstate patterns or prediction quality.

## Suggested explanation to the teacher
“We used association-rule mining to identify answer combinations that recur in the survey, and logistic regression to estimate high self-reported placement confidence from preparation, technical-skill confidence, and internship experience. The app checks the model against held-out responses when the sample is large enough. Since the survey measures confidence rather than actual job offers, our results describe student perceptions and cannot establish what causes placements.”


