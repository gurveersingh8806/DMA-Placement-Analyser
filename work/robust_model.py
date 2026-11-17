from pathlib import Path
p=Path('outputs/app.R'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('''  fit <- tryCatch(
    suppressWarnings(glm(high_confidence ~ preparation + skill + internship,
                         data = usable, family = binomial())),
    error = function(e) NULL
  )''','''  # If everyone answered the same way about internships, that variable cannot
  # help distinguish respondents, so leave it out of the model.
  uses_internship <- nlevels(droplevels(usable$internship)) > 1
  model_formula <- if (uses_internship) {
    high_confidence ~ preparation + skill + internship
  } else {
    high_confidence ~ preparation + skill
  }
  fit <- tryCatch(
    suppressWarnings(glm(model_formula, data = usable, family = binomial())),
    error = function(e) NULL
  )''')
s=s.replace('''      fold_fit <- tryCatch(
        suppressWarnings(glm(high_confidence ~ preparation + skill + internship,
                             data = train, family = binomial())),
        error = function(e) NULL
      )''','''      fold_formula <- if (nlevels(droplevels(train$internship)) > 1) {
        high_confidence ~ preparation + skill + internship
      } else {
        high_confidence ~ preparation + skill
      }
      fold_fit <- tryCatch(
        suppressWarnings(glm(fold_formula, data = train, family = binomial())),
        error = function(e) NULL
      )''')
s=s.replace('''  list(ok = TRUE, fit = fit, data = usable,
       cv_accuracy = cv_accuracy, baseline_accuracy = baseline_accuracy)''','''  list(ok = TRUE, fit = fit, data = usable, uses_internship = uses_internship,
       cv_accuracy = cv_accuracy, baseline_accuracy = baseline_accuracy)''')
s=s.replace('''      selectInput("internship_input", "Completed an internship or substantial industry project?",
                  choices = levels(fitted$data$internship),
                  selected = levels(fitted$data$internship)[1])''','''      if (fitted$uses_internship) {
        selectInput("internship_input", "Completed an internship or substantial industry project?",
                    choices = levels(fitted$data$internship),
                    selected = levels(fitted$data$internship)[1])
      } else {
        helpText("Internship experience was the same for all usable responses, so the model leaves it out.")
      }''')
s=s.replace('''    req(fitted$ok, input$internship_input)
    new_profile <- data.frame(
      preparation = input$prep_input,
      skill = input$skill_input,
      internship = factor(input$internship_input, levels = levels(fitted$data$internship))
    )''','''    req(fitted$ok)
    new_profile <- data.frame(preparation = input$prep_input, skill = input$skill_input)
    if (fitted$uses_internship) {
      req(input$internship_input)
      new_profile$internship <- factor(input$internship_input, levels = levels(fitted$data$internship))
    }''')
p.write_text(s,encoding='utf-8')
