from collections import Counter, defaultdict

from ._data import load_clean_data


def analyze_all():
    return analyze_records(load_clean_data())


def analyze_records(records):
    letter_counts = Counter()
    letter_values = defaultdict(list)
    month_counts = Counter()
    metric_values = defaultdict(list)
    letters_by_value = defaultdict(list)
    metric_counts = Counter()
    row_summaries = []
    code_value_totals = Counter()
    letter_metric_totals = Counter()

    for record in records:
        letter = record["letter"]
        value = record["value"]
        codes = record["codes"]
        metrics = record["metrics"]

        letter_counts[letter] += 1
        letter_values[letter].append(value)
        month_counts[f"{record['month']:02d}"] += 1
        letters_by_value[value].append(letter)
        row_summaries.append((letter, len(codes), len(metrics)))

        for code in codes:
            code_value_totals[code] += value
        for key, metric_value in metrics:
            metric_values[key].append(metric_value)
            metric_counts[key] += 1
            letter_metric_totals[letter] += metric_value

    return {
        "01": sum(record["value"] for record in records),
        "02": sorted(letter_counts.items()),
        "03": sorted(
            (letter, sum(values)) for letter, values in letter_values.items()
        ),
        "04": sorted(month_counts.items()),
        "05": [
            (letter, max(values), min(values))
            for letter, values in sorted(letter_values.items())
        ],
        "06": [
            (key, min(values), max(values))
            for key, values in sorted(metric_values.items())
        ],
        "07": sorted(letters_by_value.items()),
        "08": [
            (value, sorted(set(letters)))
            for value, letters in sorted(letters_by_value.items())
        ],
        "09": dict(sorted(metric_counts.items())),
        "10": row_summaries,
        "11": dict(sorted(code_value_totals.items())),
        "12": dict(sorted(letter_metric_totals.items())),
    }
