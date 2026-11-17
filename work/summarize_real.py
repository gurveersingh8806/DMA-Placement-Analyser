import csv, statistics, collections
p='outputs/Dma lab  - Form responses 1.csv'
with open(p,encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
print('rows',len(rows))
for i,h in enumerate(rows[0]): print(i,repr(h))
for key in [list(rows[0])[0],list(rows[0])[1],list(rows[0])[2],list(rows[0])[3],list(rows[0])[5],list(rows[0])[6],list(rows[0])[7],list(rows[0])[8]]:
 c=collections.Counter(r[key].strip() for r in rows); print('\n',key, c)
for key in [list(rows[0])[4],list(rows[0])[5],list(rows[0])[7]]:
 vals=[int(r[key]) for r in rows if r[key].strip()]; print('avg',key,round(statistics.mean(vals),2), 'counts',collections.Counter(vals))
prep=list(rows[0])[5]; conf=list(rows[0])[7]
print('\nPREP CONF')
for p in sorted(set(r[prep] for r in rows)):
 vals=[int(r[conf]) for r in rows if r[prep]==p]; print(p,len(vals),collections.Counter(vals),'mean',round(statistics.mean(vals),2),'high%',round(sum(x>=4 for x in vals)/len(vals)*100,1))
