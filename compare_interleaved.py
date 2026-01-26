#!/usr/bin/env python
"""Compare interleaved benchmark results from two QuTiP builds."""
import sys
import subprocess
import re

def run_bench(path):
    """Run test_interleaved.py and parse results."""
    out = subprocess.check_output([sys.executable, "test_interleaved.py", path], text=True)
    results = {}
    for line in out.split('\n'):
        m = re.match(r'Dim (\d+):', line)
        if m:
            dim = int(m.group(1))
        if 'Interleaved:' in line:
            nums = re.findall(r'(\w+ \w+)=([\d.]+)', line)
            for name, val in nums:
                results[(dim, name)] = float(val)
    return results

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <master_path> <pr_path>")
        sys.exit(1)
    
    master = run_bench(sys.argv[1])
    pr = run_bench(sys.argv[2])
    
    print("MAT-VEC (H @ |ψ⟩):")
    print(f"{'Dim':>5} {'Type':<4} {'Master':>12} {'PR':>12} {'Change':>8}")
    print("-" * 45)
    for dim in [32, 64, 128, 256]:
        for typ in ['DIA vec', 'CSR vec']:
            m, p = master[(dim, typ)], pr[(dim, typ)]
            chg = (p - m) / m * 100
            sign = '+' if chg > 0 else ''
            print(f"{dim:5} {typ.split()[0].lower():<4} {m:10.2f}±0% {p:10.2f}±0% {sign:>1}{chg:6.1f}%")
    
    print("\nMAT-MAT (H @ ρ):")
    print(f"{'Dim':>5} {'Type':<4} {'Master':>12} {'PR':>12} {'Change':>8}")
    print("-" * 45)
    for dim in [32, 64, 128, 256]:
        for typ in ['DIA mat', 'CSR mat']:
            m, p = master[(dim, typ)], pr[(dim, typ)]
            chg = (p - m) / m * 100
            sign = '+' if chg > 0 else ''
            print(f"{dim:5} {typ.split()[0].lower():<4} {m:10.2f}±0% {p:10.2f}±0% {sign:>1}{chg:6.1f}%")

if __name__ == "__main__":
    main()
