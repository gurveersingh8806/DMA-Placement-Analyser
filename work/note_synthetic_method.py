from pathlib import Path
p=Path('outputs/README.md'); s=p.read_text(encoding='utf-8-sig')
needle='The app excludes generated rows by default.'
insert='The 180 generated rows are simulations sampled from the observed answer distributions, with confidence answers sampled by preparation rating. They are not new respondents or independent evidence; use this mixed file for app demonstration only.'
s=s.replace(needle, needle+' '+insert)
p.write_text(s,encoding='utf-8')
