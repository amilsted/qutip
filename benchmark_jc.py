"""Benchmark Jaynes-Cummings model - single process, careful ordering."""
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time
import statistics
import qutip as qt

N_RES_SESOLVE = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 5000]
N_RES_MESOLVE = [4, 8, 16, 32, 64, 128]
N_RUNS = 5

# t_end tuned for ~0.1s per run based on measured performance
T_END_SESOLVE = {4: 10683, 8: 8778, 16: 7335, 32: 5462, 64: 3426, 128: 1984, 256: 1106, 512: 589, 1024: 250, 2048: 140, 4096: 75, 5000: 55}
T_END_MESOLVE = {4: 24509, 8: 8333, 16: 2349, 32: 589, 64: 170, 128: 42}

def jc_system(N_res, dtype):
    wc, wa, g = 1.0, 1.0, 0.1
    a = qt.tensor(qt.destroy(N_res), qt.qeye(2)).to(dtype)
    sm = qt.tensor(qt.qeye(N_res), qt.destroy(2)).to(dtype)
    H = (wc * a.dag() * a + wa * sm.dag() * sm + g * (a.dag() * sm + a * sm.dag())).to(dtype)
    psi0 = qt.tensor(qt.basis(N_res, 1), qt.basis(2, 0)).to(dtype)
    return H, psi0

def bench_sesolve(n_res, dtype, n_runs):
    H, psi0 = jc_system(n_res, dtype)
    t_end = T_END_SESOLVE[n_res]
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        qt.sesolve(H, psi0, [0, t_end], options={"nsteps": 1000000})
        times.append(time.perf_counter() - t0)
    return times

def bench_mesolve(n_res, dtype, n_runs):
    H, psi0 = jc_system(n_res, "Dense")
    H = H.to(dtype)
    rho0 = qt.ket2dm(psi0).to(dtype)
    t_end = T_END_MESOLVE[n_res]
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        qt.mesolve(H, rho0, [0, t_end], c_ops=[], options={"nsteps": 1000000})
        times.append(time.perf_counter() - t0)
    return times

def fmt(vals):
    m = statistics.mean(vals)
    s = statistics.stdev(vals) if len(vals) > 1 else 0
    return f"{m:.3f}±{s:.3f}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Output CSV file")
    args = parser.parse_args()

    print(f"QuTiP: {qt.__version__}")
    print(f"Runs: {N_RUNS} (mean±std, seconds)\n")

    results = []

    print("=== SESOLVE (ket) ===")
    print(f"{'N_res':>6} {'Dim':>5} {'DIA':>14} {'CSR':>14}")
    print("-" * 42)
    
    for n_res in N_RES_SESOLVE:
        times = {d: bench_sesolve(n_res, d, N_RUNS) for d in ["Dia", "CSR"]}
        print(f"{n_res:>6} {2*n_res:>5} {fmt(times['Dia']):>14} {fmt(times['CSR']):>14}")
        for dtype, t in times.items():
            results.append(("sesolve", n_res, dtype, statistics.mean(t), statistics.stdev(t) if len(t) > 1 else 0))

    print()
    print("=== MESOLVE (density matrix, no c_ops) ===")
    print(f"{'N_res':>6} {'Dim':>5} {'DIA':>14} {'CSR':>14}")
    print("-" * 42)
    
    for n_res in N_RES_MESOLVE:
        times = {d: bench_mesolve(n_res, d, N_RUNS) for d in ["Dia", "CSR"]}
        print(f"{n_res:>6} {2*n_res:>5} {fmt(times['Dia']):>14} {fmt(times['CSR']):>14}")
        for dtype, t in times.items():
            results.append(("mesolve", n_res, dtype, statistics.mean(t), statistics.stdev(t) if len(t) > 1 else 0))

    if args.csv:
        with open(args.csv, "w") as f:
            f.write("solver,n_res,dtype,mean,std\n")
            for r in results:
                f.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.6f},{r[4]:.6f}\n")
        print(f"\nResults saved to {args.csv}")
