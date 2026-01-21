"""Run QobjEvo.matmul_data benchmarks in fresh subprocesses."""
import os
import subprocess
import sys

DIMS = [32, 64, 128, 256]
N_RUNS = 3

BENCH_CODE = '''
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import qutip as qt
from qutip.core.data.bench_matmul import run_benchmarks

dim = {dim}
n_iters = {n_iters}

a = qt.destroy(dim)
H = qt.num(dim) + a + a.dag()
psi = qt.basis(dim, 0).to("Dense")
rho = qt.ket2dm(psi).to("Dense")

r = run_benchmarks(
    qt.QobjEvo(H.to("Dia")), qt.QobjEvo(H.to("CSR")),
    psi, rho, n_iters
)
print(",".join(f"{{k}}:{{v:.2f}}" for k, v in r.items()))
'''

ITERS_VEC = {32: 50000, 64: 20000, 128: 5000, 256: 2000}
ITERS_MAT = {32: 20000, 64: 5000, 128: 1000, 256: 200}

def run_bench(pythonpath, dim, n_iters):
    code = BENCH_CODE.format(dim=dim, n_iters=n_iters)
    env = {**os.environ, 'PYTHONPATH': pythonpath, 
           'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}
    r = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return None
    return dict(kv.split(':') for kv in r.stdout.strip().split(','))

def fmt(vals):
    return f"{min(vals):6.2f}-{max(vals):6.2f}"

if __name__ == "__main__":
    import argparse
    import statistics
    parser = argparse.ArgumentParser()
    parser.add_argument('pythonpath', help='PYTHONPATH to qutip (e.g., qutip-repo)')
    parser.add_argument('--csv', help='Output CSV file')
    args = parser.parse_args()
    
    # Get version
    r = subprocess.run([sys.executable, '-c', 
        f'import sys; sys.path.insert(0, "{args.pythonpath}"); import qutip; print(qutip.__version__)'],
        capture_output=True, text=True)
    print(f"QuTiP: {r.stdout.strip()}")
    print(f"Runs per dim: {N_RUNS} (fresh subprocess each)")
    print("H = num(N) + a + a.dag(), State = Dense\n")

    all_results = []

    print("=== MAT-VEC (H @ |psi>) [min-max µs] ===")
    print(f"{'Dim':>6}  {'H=DIA':>14}  {'H=CSR':>14}")
    print("-" * 42)
    
    for dim in DIMS:
        results = {k: [] for k in ['dia_vec', 'csr_vec']}
        for _ in range(N_RUNS):
            r = run_bench(args.pythonpath, dim, ITERS_VEC[dim])
            if r:
                for k in results:
                    results[k].append(float(r[k]))
        print(f"{dim:>6}  {fmt(results['dia_vec']):>14}  {fmt(results['csr_vec']):>14}")
        for k, v in results.items():
            all_results.append(('vec', dim, k.replace('_vec', ''), statistics.mean(v), statistics.stdev(v) if len(v) > 1 else 0))

    print()
    print("=== MAT-MAT (H @ rho) [min-max µs] ===")
    print(f"{'Dim':>6}  {'H=DIA':>14}  {'H=CSR':>14}")
    print("-" * 42)
    
    for dim in DIMS:
        results = {k: [] for k in ['dia_mat', 'csr_mat']}
        for _ in range(N_RUNS):
            r = run_bench(args.pythonpath, dim, ITERS_MAT[dim])
            if r:
                for k in results:
                    results[k].append(float(r[k]))
        print(f"{dim:>6}  {fmt(results['dia_mat']):>14}  {fmt(results['csr_mat']):>14}")
        for k, v in results.items():
            all_results.append(('mat', dim, k.replace('_mat', ''), statistics.mean(v), statistics.stdev(v) if len(v) > 1 else 0))

    if args.csv:
        with open(args.csv, 'w') as f:
            f.write("op,dim,dtype,mean,std\n")
            for r in all_results:
                f.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.4f},{r[4]:.4f}\n")
        print(f"\nResults saved to {args.csv}")
