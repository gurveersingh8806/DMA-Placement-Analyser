from pathlib import Path
p=Path('outputs/app.R'); lines=p.read_text(encoding='utf-8-sig').splitlines()
new=[]
for line in lines:
    if 'salary = find_column(headers, "salary range"' in line:
        line=line.rstrip(',')
    if 'support = get_text("support")' in line:
        continue
    if 'paste0("Salary=", row$salary),' in line:
        line=line.rstrip(',')
    if 'This app explores student-reported preparation, confidence, salary expectations, and support preferences' in line:
        line='      p("This app explores student-reported preparation, skill confidence, internship experience, placement confidence, and salary expectations."),'
    if 'output$support_plot <- renderPlot' in line:
        line=line.replace('output$support_plot','output$salary_plot')
    if 'h4("Support students say they need most")' in line:
        line=line.replace('Support students say they need most','Students’ expected salary ranges')
    new.append(line)
s='\n'.join(new)+'\n'
p.write_text(s,encoding='utf-8')
