from pathlib import Path
p=Path('outputs/app.R'); s=p.read_text(encoding='utf-8-sig')
s=s.replace('confidence = find_column(headers, "confident that you can secure a suitable placement", "placement_confidence_1_5"),','confidence = find_column(headers, "suitable placement", "placement_confidence_1_5"),')
s=s.replace('''    support_count <- sum(!is.na(d$support) & nzchar(d$support))
    salary_count <- sum(!is.na(d$salary) & nzchar(d$salary))
    paste0("Rows loaded: ", nrow(d),
           "\\nUsable preparation/confidence answers: ", nrow(usable),
           "\\nAverage preparation rating: ", round(mean(usable$preparation), 2), " / 5",
           "\\nAverage placement-confidence rating: ", round(mean(usable$confidence), 2), " / 5",
           "\\nSupport answers recorded: ", support_count,
           "\\nSalary expectation answers recorded: ", salary_count)''','''    support_count <- sum(!is.na(d$support) & nzchar(d$support))
    salary_count <- sum(!is.na(d$salary) & nzchar(d$salary))
    support_status <- if (support_count > 0) paste(support_count, "answers") else "question not included in this CSV"
    paste0("Rows loaded: ", nrow(d),
           "\\nUsable preparation/confidence answers: ", nrow(usable),
           "\\nAverage preparation rating: ", round(mean(usable$preparation), 2), " / 5",
           "\\nAverage placement-confidence rating: ", round(mean(usable$confidence), 2), " / 5",
           "\\nSupport-priority question: ", support_status,
           "\\nSalary expectation answers: ", salary_count)''')
s=s.replace('''    choices <- d$support[!is.na(d$support) & nzchar(d$support)]
    validate(need(length(choices) > 0, "No support answers were found in this file."))
    counts <- sort(table(choices), decreasing = TRUE)
    old_par <- par(mar = c(5, 14, 2, 1))
    on.exit(par(old_par))
    barplot(rev(counts), horiz = TRUE, las = 1,
            col = "#197c7e", border = NA, xlab = "Number of respondents",
            main = "Support students say they need most", cex.names = 0.85)''','''    support_answers <- d$support[!is.na(d$support) & nzchar(d$support)]
    if (length(support_answers) > 0) {
      choices <- support_answers
      chart_title <- "Support students say they need most"
    } else {
      choices <- d$salary[!is.na(d$salary) & nzchar(d$salary)]
      chart_title <- "Students’ expected salary ranges"
    }
    validate(need(length(choices) > 0, "No support or salary answers were found in this file."))
    counts <- sort(table(choices), decreasing = TRUE)
    old_par <- par(mar = c(5, 14, 2, 1))
    on.exit(par(old_par))
    barplot(rev(counts), horiz = TRUE, las = 1,
            col = "#197c7e", border = NA, xlab = "Number of respondents",
            main = chart_title, cex.names = 0.85)''')
s=s.replace('''  output$prep_table <- renderTable({''','''  output$prep_table <- renderTable({''')
p.write_text(s,encoding='utf-8')
