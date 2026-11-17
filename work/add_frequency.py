from pathlib import Path
p=Path('outputs/placement_analysis.py'); s=p.read_text(encoding='utf-8-sig')
helper='''\n\ndef print_frequency(title, answers):\n    """Print the number and percentage for each answer to a choice question."""\n    answers = [answer for answer in answers if answer]\n    print(f"\\n{title} (n={len(answers)})")\n    for answer, count in Counter(answers).most_common():\n        percent = count / len(answers) * 100\n        print(f"{answer}: {count} people ({percent:.1f}%)")\n'''
s=s.replace('\ndef main():', helper+'\n\ndef main():')
needle='''    if usable:
        print(f"Average preparation rating: {average(prep_scores):.2f}/5")
        print(f"Average placement-confidence rating: {average(confidence_scores):.2f}/5")

    # Association-rule mining'''
replacement='''    if usable:
        print(f"Average preparation rating: {average(prep_scores):.2f}/5")
        print(f"Average placement-confidence rating: {average(confidence_scores):.2f}/5")

    print_frequency("Support requested", [row.get(columns["support"], "").strip() for row in rows])
    print_frequency("Expected salary range", [row.get(columns["salary"], "").strip() for row in rows])

    # Association-rule mining'''
s=s.replace(needle,replacement)
s=s.replace('rules.sort(reverse=True)', 'rules.sort(key=lambda rule: (not rule[5].startswith("Confidence="), -rule[0], -rule[1]))')
p.write_text(s,encoding='utf-8')
