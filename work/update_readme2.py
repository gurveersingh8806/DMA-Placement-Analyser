from pathlib import Path
p=Path('outputs/README.md'); s=p.read_text(encoding='utf-8-sig')
start=s.index('## What the code does')
end=s.index('## Explain the method to your teacher')
s=s[:start]+'''## What the code does
- Shows response counts and averages for the preparation and placement-confidence ratings.
- Counts salary expectations and requested support.
- Groups ratings into Low, Medium, and High.
- Mines repeated pairs of answers, such as `Preparation=High -> Confidence=High`.
- Reports **support** (how many respondents show both answers), **confidence** (how often the second answer appears when the first does), and **lift** (whether the pair appears together more often than the second answer appears overall).
- Shows the most requested support inside each preparation group.

The rule search is a small, beginner-readable pairwise association analysis. Rules must appear in at least 3 responses and at least 10% of usable responses. With a small sample, it may find no repeated rules; that is a result to report honestly. Association rules describe recurring answer combinations; they do not show cause or actual placement success.

'''+s[end:]
start=s.index('## Explain the method to your teacher')
s=s[:start]+'''## Explain the method to your teacher
“We summarized the answers with counts and averages, then used pairwise association-rule mining to find combinations of answers that recur. For each rule we report support, confidence, and lift. For example, a rule can show how often high placement confidence appears among students reporting high preparation. The survey measures self-reported confidence rather than actual placement offers, so the patterns do not establish cause and effect.”
'''
p.write_text(s,encoding='utf-8')
