from pathlib import Path
p=Path('outputs/app.R'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('''          uiOutput("model_status"),
          conditionalPanel("output.model_ready == true",
            sliderInput("prep_input", "Placement preparation (1 = not currently, 5 = very regularly)", min = 1, max = 5, value = 3, step = 1),
            sliderInput("skill_input", "Technical skill confidence (1 = low, 5 = high)", min = 1, max = 5, value = 3, step = 1),
            uiOutput("internship_input"),
            h4("Estimated probability"),
            verbatimTextOutput("prediction"),
            h4("Model check"),
            verbatimTextOutput("model_check")
          )''','''          uiOutput("model_status"),
          uiOutput("model_controls"),
          h4("Estimated probability"),
          verbatimTextOutput("prediction"),
          h4("Model check"),
          verbatimTextOutput("model_check")''')
s=s.replace('''  output$model_ready <- reactive({ isTRUE(model()$ok) })
  outputOptions(output, "model_ready", suspendWhenHidden = FALSE)

  output$internship_input <- renderUI({
    fitted <- model()
    if (!fitted$ok) return(NULL)
    selectInput("internship_input", "Completed an internship or substantial industry project?",
                choices = levels(fitted$data$internship),
                selected = levels(fitted$data$internship)[1])
  })''','''  output$model_controls <- renderUI({
    fitted <- model()
    if (!fitted$ok) return(NULL)
    tagList(
      sliderInput("prep_input", "Placement preparation (1 = not currently, 5 = very regularly)", min = 1, max = 5, value = 3, step = 1),
      sliderInput("skill_input", "Technical skill confidence (1 = low, 5 = high)", min = 1, max = 5, value = 3, step = 1),
      selectInput("internship_input", "Completed an internship or substantial industry project?",
                  choices = levels(fitted$data$internship),
                  selected = levels(fitted$data$internship)[1])
    )
  })''')
p.write_text(s,encoding='utf-8')
