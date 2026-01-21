#!/usr/bin/env python
"""Compare matmul microbenchmark CSV files."""
import csv
import sys

def load_csv(path):
    data = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            key = (row["op"], int(row["dim"]), row["dtype"])
            data[key] = (float(row["mean"]), float(row["std"]))
    return data

def print_table(master, pr, op):
    keys = sorted([k for k in master if k[0] == op])
    print(f"{'Dim':>6} {'Type':<8} {'Master':>12} {'PR':>12} {'Change':>8}")
    print("-" * 50)
    for key in keys:
        _, dim, dtype = key
        m_mean, m_std = master[key]
        p_mean, p_std = pr.get(key, (0, 0))
        m_var_pct = m_std / m_mean * 100 if m_mean else 0
        p_var_pct = p_std / p_mean * 100 if p_mean else 0
        change = (p_mean - m_mean) / m_mean * 100 if m_mean else 0
        sign = "+" if change > 0 else ""
        print(f"{dim:>6} {dtype:<8} {m_mean:>7.2f}±{m_var_pct:>2.0f}% {p_mean:>7.2f}±{p_var_pct:>2.0f}% {sign}{change:>6.1f}%")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} master.csv pr.csv")
        sys.exit(1)

    master = load_csv(sys.argv[1])
    pr = load_csv(sys.argv[2])

    print("=== MAT-VEC (H @ |psi>) [µs] ===\n")
    print_table(master, pr, "vec")
    print("\n=== MAT-MAT (H @ rho) [µs] ===\n")
    print_table(master, pr, "mat")

if __name__ == "__main__":
    main()
