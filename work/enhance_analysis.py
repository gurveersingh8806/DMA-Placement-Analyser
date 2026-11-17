from pathlib import Path
p=Path('outputs/placement_analysis.py')
s=p.read_text(encoding='utf-8-sig')
insert='''\n\ndef ranks(numbers):\n    """Give each number a rank; tied numbers receive the average tied rank."""\n    ordered = sorted(enumerate(numbers), key=lambda pair: pair[1])\n    result = [0] * len(numbers)\n    start = 0\n    while start < len(ordered):\n        end = start + 1\n        while end < len(ordered) and ordered[end][1] == ordered[start][1]:\n            end += 1\n        average_rank = (start + 1 + end) / 2\n        for position in range(start, end):\n            original_index = ordered[position][0]\n            result[original_index] = average_rank\n        start = end\n    return result\n\n\ndef correlation(first, second):\n    """Return Pearson correlation for two lists (used on ranks for Spearman)."""\n    if len(first) < 2:\n        return None\n    first_mean = average(first)\n    second_mean = average(second)\n    top = sum((a - first_mean) * (b - second_mean) for a, b in zip(first, second))\n    first_size = sum((a - first_mean) ** 2 for a in first)\n    second_size = sum((b - second_mean) ** 2 for b in second)\n    if first_size == 0 or second_size == 0:\n        return None\n    return top / (first_size * second_size) ** 0.5\n'''
s=s.replace('\ndef print_counts(title, answers, total):', insert+'\n\ndef print_counts(title, answers, total):')
s=s.replace('''    # Cross-tab: for each preparation score, count low and high confidence answers.
    # This helps us see whether the two answers appear together in this survey.
    confidence_by_preparation = defaultdict(Counter)
    for preparation, confidence in valid_rows:
        confidence_by_preparation[preparation][confidence] += 1

    print("\\nPreparation rating compared with placement confidence")
    print("Prep score | Confidence scores 1, 2, 3, 4, 5 | High confidence (4 or 5)")
    for preparation in sorted(confidence_by_preparation):
        counts = confidence_by_preparation[preparation]
        score_counts = [counts[score] for score in range(1, 6)]
        people = sum(score_counts)
        high = counts[4] + counts[5]
        high_percent = high / people * 100
        print(f"     {preparation}     | {score_counts} | {high}/{people} people ({high_percent:.1f}%)")

    print("\\nHow to explain this:")
    print("The table compares two survey answers. It can show a pattern in these respondents,")
    print("but it cannot prove that preparation causes placement success.")
''','''    # Group answers by preparation rating so the average confidence at each
    # preparation level is easy to compare.
    confidence_by_preparation = defaultdict(list)
    confidence_counts = defaultdict(Counter)
    for preparation, confidence in valid_rows:
        confidence_by_preparation[preparation].append(confidence)
        confidence_counts[preparation][confidence] += 1

    print("\\nPreparation rating compared with placement confidence")
    print("Prep | People | Average confidence | High confidence (4 or 5)")
    for preparation in sorted(confidence_by_preparation):
        confidence_list = confidence_by_preparation[preparation]
        counts = confidence_counts[preparation]
        people = len(confidence_list)
        high = counts[4] + counts[5]
        high_percent = high / people * 100
        print(f"  {preparation}  |   {people:>3}  |       {average(confidence_list):.2f}/5      | {high}/{people} ({high_percent:.1f}%)")

    # Spearman rank correlation checks whether higher preparation ratings
    # generally go with higher confidence ratings. It ranges from -1 to +1.
    rho = correlation(ranks(preparation_scores), ranks(confidence_scores))
    print("\\nPreparation-confidence association (Spearman rank correlation)")
    if rho is None:
        print("Not enough variation or responses to calculate a correlation.")
    else:
        print(f"rho = {rho:.2f} (closer to +1 means the two ratings tend to rise together)")

    print("\\nHow to explain this:")
    print("These results show association between self-reported preparation and confidence.")
    print("They do not show that preparation causes an actual placement: the form measures")
    print("confidence, not placement outcomes, and does not compare a controlled intervention.")
''')
p.write_text(s,encoding='utf-8')
