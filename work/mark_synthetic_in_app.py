from pathlib import Path
p=Path('outputs/app.R'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('''      fileInput("file", "Upload Google Forms CSV", accept = ".csv"),
      helpText("No upload? The app uses the labeled synthetic sample file."),''','''      fileInput("file", "Upload Google Forms CSV", accept = ".csv"),
      uiOutput("synthetic_option"),
      helpText("No upload? The app uses the labeled synthetic sample file."),''')
s=s.replace('''  data <- reactive({ clean_survey(raw_data()) })''','''  data <- reactive({
    raw <- raw_data()
    source_column <- which(tolower(names(raw)) == "data_source")
    if (length(source_column) > 0 && !isTRUE(input$include_synthetic)) {
      origin <- tolower(as.character(raw[[source_column[1]]]))
      raw <- raw[!grepl("synthetic", origin), , drop = FALSE]
    }
    clean_survey(raw)
  })''')
old='''  output$data_notice <- renderUI({
    if (is_demo()) {
      div(style = "padding:10px;background:#fff0d9;color:#754c00;margin-bottom:12px;",
          strong("DEMO DATA — SYNTHETIC, NOT REAL STUDENT RESPONSES. Upload your Google Forms CSV for actual results."))
    } else {
      div(style = "padding:10px;background:#e8f5e9;color:#205b25;margin-bottom:12px;",
          strong(paste("Survey file loaded:", nrow(data()), "rows. Results describe these respondents.")))
    }
  })'''
new='''  output$synthetic_option <- renderUI({
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
  })'''
if old not in s:
    raise SystemExit('Could not locate data notice block')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')

p=Path('outputs/README.md'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('- `sample_responses.csv` — synthetic example data for trying the app. It is not real survey data.','- `sample_responses.csv` — synthetic example data for trying the app. It is not real survey data.\n- `placement_survey_250_mixed_observed_synthetic.csv` — 70 original responses plus 180 generated rows, each labeled by source. The app excludes generated rows by default.')
s=s.replace('The app opens with the synthetic sample and marks it as demo data. Use the **Upload Google Forms CSV** control to load your collected responses. The app recognizes the wording in the supplied questionnaire; you should not need to rename the Google Forms columns.','The app opens with the synthetic sample and marks it as demo data. Upload the original 70-row Google Forms CSV for your real results. If you upload the 250-row mixed file, the app uses only its 70 observed rows by default; the checkbox can include generated rows for interface demonstration, with a warning that the combined results are synthetic/mixed.')
p.write_text(s,encoding='utf-8')
