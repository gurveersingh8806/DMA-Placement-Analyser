import csv, random
from pathlib import Path
out=Path('outputs'); out.mkdir(exist_ok=True)
random.seed(17)
rows=[]
for i in range(1,41):
    year=random.choice(['2nd year','3rd year','Final year'])
    branch=random.choice(['Computer/IT','Electronics','Mechanical','Civil','Other'])
    skill=random.randint(1,5); prep=random.randint(1,5); internship=random.choice(['Yes','No']); cgpa=random.choice(['Below 6.0','6.0–6.9','7.0–7.9','8.0+'])
    confidence=max(1,min(5,round((skill+prep+random.uniform(-1.3,1.3))/2)))
    expectation=random.choice(['₹3–5 LPA','₹5–8 LPA','₹8–12 LPA','₹12+ LPA','Not sure'])
    priority=random.choice(['More companies','Higher salary','Role matching skills','Internships','Aptitude/interview training'])
    rows.append({'response_id':i,'year':year,'branch':branch,'cgpa_band':cgpa,'skill_confidence_1_5':skill,'preparation_1_5':prep,'internship':internship,'placement_confidence_1_5':confidence,'expected_salary_band':expectation,'top_support_priority':priority})
with (out/'illustrative_sample.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
