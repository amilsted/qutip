#!/usr/bin/env python
"""Compare benchmark CSV files and generate tables."""
import csv
import sys

def load_csv(path):
    data = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            key = (row["solver"], int(row["n_res"]), row["dtype"])
            data[key] = (float(row["mean"]), float(row["std"]))
    return data

def print_table(master, pr, solver):
    keys = sorted([k for k in master if k[0] == solver])
    print(f"{'N_res':>6} {'Dim':>6} {'Type':<4} {'Master':>12} {'PR':>12} {'Change':>8}")
    print("-" * 54)
    for key in keys:
        _, n_res, dtype = key
        m_mean, m_std = master[key]
        p_mean, p_std = pr.get(key, (0, 0))
        m_var_pct = m_std / m_mean * 100 if m_mean else 0
        p_var_pct = p_std / p_mean * 100 if p_mean else 0
        change = (p_mean - m_mean) / m_mean * 100 if m_mean else 0
        sign = "+" if change > 0 else ""
        print(f"{n_res:>6} {2*n_res:>6} {dtype:<4} {m_mean:>7.3f}±{m_var_pct:>3.0f}% {p_mean:>7.3f}±{p_var_pct:>3.0f}% {sign}{change:>6.1f}%")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} master.csv pr.csv")
        sys.exit(1)

    master = load_csv(sys.argv[1])
    pr = load_csv(sys.argv[2])

    print("=== SESOLVE ===\n")
    print_table(master, pr, "sesolve")
    print("\n=== MESOLVE ===\n")
    print_table(master, pr, "mesolve")

if __name__ == "__main__":
    main()
