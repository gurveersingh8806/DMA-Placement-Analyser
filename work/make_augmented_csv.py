import csv, random
from collections import defaultdict
from pathlib import Path
src=Path('outputs/Dma lab  - Form responses 1.csv')
out=Path('outputs/placement_survey_250_mixed_observed_synthetic.csv')
random.seed(73017)
with src.open('r',encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f)
    headers=reader.fieldnames
    observed=list(reader)
if len(observed)!=70:
    raise SystemExit(f'Expected 70 source rows, found {len(observed)}')
source_fields=[h for h in headers if h!='Timestamp']
# Create additional rows by sampling from the observed marginal answer distributions.
# Confidence is sampled conditional on preparation to preserve that broad pattern.
prep_h=next(h for h in headers if 'regularly are you preparing' in h.lower())
conf_h=next(h for h in headers if 'suitable placement' in h.lower())
options={h:[r[h] for r in observed if r[h].strip()] for h in source_fields}
confidence_by_prep=defaultdict(list)
for row in observed:
    if row[prep_h].strip() and row[conf_h].strip():
        confidence_by_prep[row[prep_h]].append(row[conf_h])
augmented=[]
for row in observed:
    new=dict(row); new['Data_Source']='Observed original response'; augmented.append(new)
for i in range(180):
    new={h:random.choice(options[h]) if options[h] else '' for h in source_fields}
    # Simulated placement-confidence rating follows an observed conditional answer distribution.
    new[conf_h]=random.choice(confidence_by_prep[new[prep_h]]) if confidence_by_prep[new[prep_h]] else random.choice(options[conf_h])
    new['Timestamp']=''
    new['Data_Source']='Synthetic generated row'
    augmented.append(new)
with out.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=headers+['Data_Source'])
    writer.writeheader(); writer.writerows(augmented)
print(f'Wrote {len(augmented)} rows: 70 observed + 180 synthetic -> {out}')
