from pathlib import Path
p=Path('outputs/app.R'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('''    support = find_column(headers, "support would help you most", "top_support_priority")
''','')
s=s.replace('''      if (!is.na(row$support) && nzchar(row$support)) paste0("Support=", row$support)
''','')
s=s.replace('''      support = get_text("support"),
''','')
s=s.replace('''          p("This app explores student-reported preparation, confidence, salary expectations, and support preferences when the uploaded form asks about them."),''','''          p("This app explores student-reported preparation, skill confidence, internship experience, placement confidence, and salary expectations."),''')
s=s.replace('''          h4("Support students say they need most"),''','''          h4("Students’ expected salary ranges"),''')
s=s.replace('''          p("It can describe respondents' preparation, confidence, and expectations. It can analyze support preferences only when that question is present in the uploaded file. It can find recurring combinations among the answers that were collected."),''','''          p("It can describe respondents' preparation, confidence, and salary expectations, and find recurring combinations among those answers."),''')
s=s.replace('''    support_count <- sum(!is.na(d$support) & nzchar(d$support))
    salary_count <- sum(!is.na(d$salary) & nzchar(d$salary))''','''    salary_count <- sum(!is.na(d$salary) & nzchar(d$salary))''')
s=s.replace('''    support_status <- if (support_count > 0) paste(support_count, "answers") else "question not included in this CSV"
''','')
s=s.replace('''           "\\nSupport-priority question: ", support_status,
           "\\nSalary expectation answers: ", salary_count)''','''           "\\nSalary expectation answers: ", salary_count)''')
s=s.replace('''    support_answers <- d$support[!is.na(d$support) & nzchar(d$support)]
    if (length(support_answers) > 0) {
      choices <- support_answers
      chart_title <- "Support students say they need most"
    } else {
      choices <- d$salary[!is.na(d$salary) & nzchar(d$salary)]
      chart_title <- "Students’ expected salary ranges"
    }''','''    choices <- d$salary[!is.na(d$salary) & nzchar(d$salary)]
    chart_title <- "Students’ expected salary ranges"''')
s=s.replace('''    validate(need(length(choices) > 0, "No support or salary answers were found in this file."))''','''    validate(need(length(choices) > 0, "No salary expectation answers were found in this file."))''')
s=s.replace('''          p("It can describe respondents' preparation, confidence, expectations, and requested support. It can find recurring combinations among these answers."),''','''          p("It can describe respondents' preparation, confidence, and salary expectations, and find recurring combinations among these answers."),''')
p.write_text(s,encoding='utf-8')

p=Path('outputs/README.md'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('The project mines student survey responses for recurring combinations of preparation, skill confidence, internship experience, placement confidence, and salary expectations. If a form includes a support-priority question, the app can analyze it too.','The project mines student survey responses for recurring combinations of preparation, skill confidence, internship experience, placement confidence, and salary expectations.')
s=s.replace('The app now recognizes the confidence question wording in this export and charts salary expectations when support-priority answers are absent. Do not report support needs from this dataset.','The app recognizes the confidence question wording in this export and charts salary expectations. The pattern mining uses only fields present in this survey.')
s=s.replace('support requests, and confidence averages','salary expectations, and confidence averages')
s=s.replace('salary expectations and requested support.','salary expectations.')
s=s.replace('If a form includes a support-priority question, the app can analyze it too.','')
p.write_text(s,encoding='utf-8')
