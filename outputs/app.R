# College Placement Insights — interactive Shiny app
# Run from this folder in RStudio with: shiny::runApp()
# Install the only extra package once with: install.packages("shiny")

library(shiny)

# ---------- Read and standardize the survey CSV ----------

find_column <- function(headers, clue, fallback) {
  found <- which(grepl(clue, tolower(headers), fixed = TRUE))
  if (length(found) > 0) return(headers[found[1]])
  found <- which(tolower(headers) == tolower(fallback))
  if (length(found) > 0) return(headers[found[1]])
  NA_character_
}

clean_survey <- function(raw) {
  names(raw) <- sub("^\\ufeff", "", names(raw))
  headers <- names(raw)
  columns <- list(
    year = find_column(headers, "current year of study", "year"),
    branch = find_column(headers, "broad branch", "branch"),
    cgpa = find_column(headers, "cgpa range", "cgpa_band"),
    skill = find_column(headers, "technical skills", "skill_confidence_1_5"),
    preparation = find_column(headers, "regularly are you preparing", "preparation_1_5"),
    internship = find_column(headers, "internship or substantial industry project", "internship"),
    confidence = find_column(headers, "suitable placement", "placement_confidence_1_5"),
    salary = find_column(headers, "salary range", "expected_salary_band")
  )

  get_text <- function(key) {
    column <- columns[[key]]
    if (is.na(column)) return(rep(NA_character_, nrow(raw)))
    trimws(as.character(raw[[column]]))
  }
  get_number <- function(key) suppressWarnings(as.numeric(get_text(key)))

  data.frame(
    year = get_text("year"),
    branch = get_text("branch"),
    cgpa = get_text("cgpa"),
    skill = get_number("skill"),
    preparation = get_number("preparation"),
    internship = tools::toTitleCase(tolower(get_text("internship"))),
    confidence = get_number("confidence"),
    salary = get_text("salary"),
    stringsAsFactors = FALSE
  )
}

# ---------- Prepare categories for association-rule mining ----------

rating_group <- function(value) {
  if (is.na(value)) return(NA_character_)
  if (value <= 2) return("Low")
  if (value == 3) return("Medium")
  "High"
}

make_transactions <- function(data) {
  lapply(seq_len(nrow(data)), function(i) {
    row <- data[i, ]
    items <- c(
      if (!is.na(row$preparation)) paste0("Preparation=", rating_group(row$preparation)),
      if (!is.na(row$skill)) paste0("Skill=", rating_group(row$skill)),
      if (!is.na(row$confidence)) paste0("Confidence=", rating_group(row$confidence)),
      if (!is.na(row$internship) && nzchar(row$internship)) paste0("Internship=", row$internship),
      if (!is.na(row$salary) && nzchar(row$salary)) paste0("Salary=", row$salary)
    )
    items[!is.na(items)]
  })
}

mine_pair_rules <- function(data) {
  transactions <- make_transactions(data)
  n <- length(transactions)
  minimum_count <- max(3, ceiling(n * 0.10))
  all_items <- unique(unlist(transactions))
  if (length(all_items) < 2 || n == 0) return(data.frame())

  item_count <- vapply(all_items, function(item) {
    sum(vapply(transactions, function(basket) item %in% basket, logical(1)))
  }, numeric(1))
  names(item_count) <- all_items

  rules <- list()
  row_number <- 1
  for (first in all_items) {
    for (second in all_items) {
      # Do not create impossible rules such as Preparation=Low -> Preparation=High.
      first_field <- sub("=.*$", "", first)
      second_field <- sub("=.*$", "", second)
      if (first == second || first_field == second_field) next

      together <- sum(vapply(transactions, function(basket) {
        first %in% basket && second %in% basket
      }, logical(1)))
      if (together < minimum_count) next

      rule_confidence <- together / item_count[first]
      rule_support <- together / n
      rule_lift <- rule_confidence / (item_count[second] / n)
      rules[[row_number]] <- data.frame(
        Pattern = paste(first, "→", second),
        People = together,
        Support = rule_support,
        Confidence = rule_confidence,
        Lift = rule_lift,
        Outcome = second,
        stringsAsFactors = FALSE
      )
      row_number <- row_number + 1
    }
  }

  if (length(rules) == 0) return(data.frame())
  result <- do.call(rbind, rules)
  # Show confidence-related patterns first, then the strongest lift.
  result <- result[order(!grepl("^Confidence=", result$Outcome), -result$Lift, -result$Confidence), ]
  result$Support <- round(100 * result$Support, 1)
  result$Confidence <- round(100 * result$Confidence, 1)
  result$Lift <- round(result$Lift, 2)
  rownames(result) <- NULL
  result[, c("Pattern", "People", "Support", "Confidence", "Lift")]
}

# ---------- Fit and check a simple confidence model ----------

fit_confidence_model <- function(data) {
  usable <- data[complete.cases(data[, c("preparation", "skill", "confidence", "internship")]), ]
  usable$high_confidence <- as.integer(usable$confidence >= 4)
  usable$internship <- factor(usable$internship)
  class_counts <- table(usable$high_confidence)

  # Small samples or a class with too few examples make a prediction model unreliable.
  if (nrow(usable) < 30 || length(class_counts) < 2 || min(class_counts) < 5) {
    return(list(ok = FALSE, reason = "Need at least 30 complete responses and at least 5 examples of both lower and higher confidence."))
  }

  # If everyone answered the same way about internships, that variable cannot
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
  )
  if (is.null(fit) || !isTRUE(fit$converged)) {
    return(list(ok = FALSE, reason = "The model could not fit these responses reliably. Show the descriptive and pattern results instead."))
  }

  # Five-fold cross-validation estimates how often the model classifies a held-out
  # response correctly. This is a rough check, not proof the model will generalize.
  cv_accuracy <- NA_real_
  baseline_accuracy <- NA_real_
  if (nrow(usable) >= 40) {
    set.seed(42)
    folds <- sample(rep(1:5, length.out = nrow(usable)))
    predictions <- rep(NA_real_, nrow(usable))
    for (fold in 1:5) {
      train <- usable[folds != fold, ]
      test_rows <- which(folds == fold)
      if (length(unique(train$high_confidence)) < 2) next
      fold_formula <- if (nlevels(droplevels(train$internship)) > 1) {
        high_confidence ~ preparation + skill + internship
      } else {
        high_confidence ~ preparation + skill
      }
      fold_fit <- tryCatch(
        suppressWarnings(glm(fold_formula, data = train, family = binomial())),
        error = function(e) NULL
      )
      if (!is.null(fold_fit) && isTRUE(fold_fit$converged)) {
        predictions[test_rows] <- tryCatch(
          predict(fold_fit, newdata = usable[test_rows, ], type = "response"),
          error = function(e) NA_real_
        )
      }
    }
    scored <- !is.na(predictions)
    if (sum(scored) >= 20) {
      predicted_class <- as.integer(predictions[scored] >= 0.5)
      cv_accuracy <- mean(predicted_class == usable$high_confidence[scored]) * 100
      baseline_accuracy <- max(prop.table(table(usable$high_confidence))) * 100
    }
  }

  list(ok = TRUE, fit = fit, data = usable, uses_internship = uses_internship,
       cv_accuracy = cv_accuracy, baseline_accuracy = baseline_accuracy)
}

# ---------- Shiny page ----------

ui <- fluidPage(
  titlePanel("College Placement Insights"),
  sidebarLayout(
    sidebarPanel(
      h4("Load your survey"),
      fileInput("file", "Upload Google Forms CSV", accept = ".csv"),
      uiOutput("synthetic_option"),
      helpText("No upload? The app uses the labeled synthetic sample file."),
      tags$hr(),
      h4("About this project"),
      p("This app explores student-reported preparation, skill confidence, internship experience, placement confidence, and salary expectations."),
      p(strong("Confidence is not an actual placement result."))
    ),
    mainPanel(
      uiOutput("data_notice"),
      tabsetPanel(
        tabPanel("Overview",
          h3("Survey snapshot"),
          verbatimTextOutput("summary"),
          plotOutput("salary_plot", height = 300),
          h4("Average confidence by preparation rating"),
          tableOutput("prep_table")
        ),
        tabPanel("Pattern mining",
          h3("Recurring answer combinations"),
          p("Association rules show which answers appear together in the responses."),
          tableOutput("rules_table"),
          h4("How to read the measures"),
          p("Support = respondents with both answers. Confidence = among people with the first answer, the share who also gave the second. Lift above 1 means the pair occurs together more often than the second answer occurs overall."),
          p("These are patterns, not causes. Rules need at least 3 respondents and 10% of all uploaded responses to appear.")
        ),
        tabPanel("Predict confidence",
          h3("Estimate high placement confidence"),
          p("The estimate is the model's probability that a similar respondent would report confidence of 4 or 5. It does not predict whether someone will actually get hired."),
          uiOutput("model_status"),
          uiOutput("model_controls"),
          h4("Estimated probability"),
          verbatimTextOutput("prediction"),
          h4("Model check"),
          verbatimTextOutput("model_check")
        ),
        tabPanel("Data and limits",
          h3("What this survey can answer"),
          p("It can describe respondents' preparation, confidence, and salary expectations, and find recurring combinations among those answers."),
          h3("What it cannot establish"),
          p("The survey does not ask whether respondents received job offers, and it does not assign students to different preparation programs. It cannot establish causes or official placement rates."),
          h3("Sample size"),
          verbatimTextOutput("limitations")
        )
      )
    )
  )
)

server <- function(input, output, session) {
  is_demo <- reactive({ is.null(input$file) })

  raw_data <- reactive({
    if (is.null(input$file)) {
      read.csv("sample_responses.csv", check.names = FALSE, stringsAsFactors = FALSE,
               fileEncoding = "UTF-8-BOM")
    } else {
      read.csv(input$file$datapath, check.names = FALSE, stringsAsFactors = FALSE,
               fileEncoding = "UTF-8-BOM")
    }
  })

  data <- reactive({
    raw <- raw_data()
    source_column <- which(tolower(names(raw)) == "data_source")
    if (length(source_column) > 0 && !isTRUE(input$include_synthetic)) {
      origin <- tolower(as.character(raw[[source_column[1]]]))
      raw <- raw[!grepl("synthetic", origin), , drop = FALSE]
    }
    clean_survey(raw)
  })
  model <- reactive({ fit_confidence_model(data()) })
  rules <- reactive({ mine_pair_rules(data()) })

  output$synthetic_option <- renderUI({
    if (is_demo()) return(NULL)
    raw <- raw_data()
    source_column <- which(tolower(names(raw)) == "data_source")
    if (length(source_column) == 0) return(NULL)
    origin <- tolower(as.character(raw[[source_column[1]]]))
    if (!any(grepl("synthetic", origin))) return(NULL)
    checkboxInput("include_synthetic", "Include generated rows for app demonstration only", value = FALSE)
  })

  output$data_notice <- renderUI({
    if (is_demo()) {
      div(style = "padding:10px;background:#fff0d9;color:#754c00;margin-bottom:12px;",
          strong("DEMO DATA — SYNTHETIC, NOT REAL STUDENT RESPONSES. Upload your Google Forms CSV for actual results."))
    } else {
      raw <- raw_data()
      source_column <- which(tolower(names(raw)) == "data_source")
      if (length(source_column) > 0) {
        origin <- tolower(as.character(raw[[source_column[1]]]))
        synthetic_count <- sum(grepl("synthetic", origin), na.rm = TRUE)
        observed_count <- nrow(raw) - synthetic_count
        if (synthetic_count > 0 && isTRUE(input$include_synthetic)) {
          return(div(style = "padding:10px;background:#fff0d9;color:#754c00;margin-bottom:12px;",
                     strong(paste0("MIXED DEMO DATA: ", observed_count, " observed + ", synthetic_count,
                                   " synthetic rows. All results combine both; do not present them as survey findings."))))
        }
        if (synthetic_count > 0) {
          return(div(style = "padding:10px;background:#e8f5e9;color:#205b25;margin-bottom:12px;",
                     strong(paste0("Analyzing ", observed_count, " observed responses. Excluded ", synthetic_count,
                                   " synthetic rows; use the checkbox only to demonstrate the app."))))
        }
      }
      div(style = "padding:10px;background:#e8f5e9;color:#205b25;margin-bottom:12px;",
          strong(paste("Survey file loaded:", nrow(data()), "rows. Results describe these respondents.")))
    }
  })

  output$summary <- renderText({
    d <- data()
    usable <- d[!is.na(d$preparation) & !is.na(d$confidence), ]
    if (nrow(usable) == 0) return("No usable preparation and confidence ratings found. Check the CSV headings.")
    salary_count <- sum(!is.na(d$salary) & nzchar(d$salary))
    paste0("Rows loaded: ", nrow(d),
           "\nUsable preparation/confidence answers: ", nrow(usable),
           "\nAverage preparation rating: ", round(mean(usable$preparation), 2), " / 5",
           "\nAverage placement-confidence rating: ", round(mean(usable$confidence), 2), " / 5",
           "\nSalary expectation answers: ", salary_count)
  })

  output$salary_plot <- renderPlot({
    d <- data()
    choices <- d$salary[!is.na(d$salary) & nzchar(d$salary)]
    chart_title <- "Students’ expected salary ranges"
    validate(need(length(choices) > 0, "No salary expectation answers were found in this file."))
    counts <- sort(table(choices), decreasing = TRUE)
    old_par <- par(mar = c(5, 14, 2, 1))
    on.exit(par(old_par))
    barplot(rev(counts), horiz = TRUE, las = 1,
            col = "#197c7e", border = NA, xlab = "Number of respondents",
            main = chart_title, cex.names = 0.85)
  })

  output$prep_table <- renderTable({
    d <- data()
    d <- d[!is.na(d$preparation) & !is.na(d$confidence), ]
    if (nrow(d) == 0) return(data.frame(Note = "No usable ratings found."))
    groups <- split(d$confidence, d$preparation)
    data.frame(
      Preparation_rating = as.numeric(names(groups)),
      Respondents = vapply(groups, length, integer(1)),
      Average_confidence = round(vapply(groups, mean, numeric(1)), 2),
      High_confidence_percent = round(vapply(groups, function(x) mean(x >= 4) * 100, numeric(1)), 1),
      check.names = FALSE
    )
  }, rownames = FALSE)

  output$rules_table <- renderTable({
    result <- rules()
    if (nrow(result) == 0) return(data.frame(Note = "No recurring rules met the minimum count. Show descriptive summaries and collect more responses."))
    head(result, 15)
  }, rownames = FALSE)

  output$model_status <- renderUI({
    fitted <- model()
    if (!fitted$ok) {
      return(div(style = "padding:10px;background:#fff0d9;color:#754c00;", strong(fitted$reason)))
    }
    div(style = "padding:10px;background:#e8f5e9;color:#205b25;",
        strong("Model available. It estimates high self-reported confidence, not actual hiring."))
  })

  output$model_controls <- renderUI({
    fitted <- model()
    if (!fitted$ok) return(NULL)
    tagList(
      sliderInput("prep_input", "Placement preparation (1 = not currently, 5 = very regularly)", min = 1, max = 5, value = 3, step = 1),
      sliderInput("skill_input", "Technical skill confidence (1 = low, 5 = high)", min = 1, max = 5, value = 3, step = 1),
      if (fitted$uses_internship) {
        selectInput("internship_input", "Completed an internship or substantial industry project?",
                    choices = levels(fitted$data$internship),
                    selected = levels(fitted$data$internship)[1])
      } else {
        helpText("Internship experience was the same for all usable responses, so the model leaves it out.")
      }
    )
  })

  output$prediction <- renderText({
    fitted <- model()
    req(fitted$ok)
    new_profile <- data.frame(preparation = input$prep_input, skill = input$skill_input)
    if (fitted$uses_internship) {
      req(input$internship_input)
      new_profile$internship <- factor(input$internship_input, levels = levels(fitted$data$internship))
    }
    probability <- predict(fitted$fit, newdata = new_profile, type = "response")
    paste0(round(probability * 100, 1),
           "% estimated chance of reporting high placement confidence (4 or 5), based on the survey model.")
  })

  output$model_check <- renderText({
    fitted <- model()
    req(fitted$ok)
    if (is.na(fitted$cv_accuracy)) {
      return("Cross-validation needs at least 40 complete survey responses. Treat profile estimates as very tentative.")
    }
    paste0("Five-fold cross-validation accuracy: ", round(fitted$cv_accuracy, 1),
           "%\nMajority-class baseline accuracy: ", round(fitted$baseline_accuracy, 1),
           "%\nCompare these values: if model accuracy is close to baseline, its predictions add little information.")
  })

  output$limitations <- renderText({
    d <- data()
    usable <- d[complete.cases(d[, c("preparation", "skill", "confidence", "internship")]), ]
    paste0("Complete records for prediction: ", nrow(usable),
           "\nThe model is enabled only with at least 30 complete records and at least 5 low-confidence and 5 high-confidence responses.",
           "\nThe answers are self-reported and the sample may not represent all students.")
  })
}

shinyApp(ui = ui, server = server)



