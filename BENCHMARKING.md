# QuTiP matmul Benchmarks

Benchmarks for comparing `QobjEvo.matmul_data` performance across branches.

## Setup

Clone QuTiP and check out the PR branch:
```bash
git clone https://github.com/amilsted/qutip.git qutip-repo
cd qutip-repo
git checkout matrix_mesolve_pr
```

Use git worktrees for easy branch comparison:
```bash
git worktree add ../qutip-master master
```

Ensure single-threaded BLAS:
```bash
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
```

Build both:
```bash
source .venv/bin/activate
cd qutip-repo && python setup.py build_ext --inplace
cd ../qutip-master && python setup.py build_ext --inplace
```

## End-to-End: Jaynes-Cummings Model

**File:** `benchmark_jc.py`

**Run:**
```bash
PYTHONPATH=qutip-master python benchmark_jc.py --csv master.csv
PYTHONPATH=qutip-repo python benchmark_jc.py --csv pr.csv
python compare_benchmarks.py master.csv pr.csv
```

**What it tests:**
- `sesolve` with ket initial state (DIA/CSR Hamiltonians)
- `mesolve` with density matrix initial state, no collapse operators (DIA/CSR)
- Jaynes-Cummings Hamiltonian: `H = ωc a†a + ωa σ†σ + g(a†σ + aσ†)`
- Resonator dimensions: 4 to 5000 (sesolve), 4 to 128 (mesolve)
- Evolution times tuned for ~0.1s per run
- Reports mean±std over 5 runs
- Both `sesolve` and `mesolve` are testing matrix-vector operations

## Full solve results: MacOS, Apple Silicon

Compiler: Apple clang 17.0.0 (arm64-apple-darwin24.6.0)

### SESOLVE
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.105±  2%   0.112±  1% +   6.5%
     4      8 Dia    0.105±  1%   0.118±  3% +  12.3%
     8     16 CSR    0.109± 12%   0.105±  1%   -3.7%
     8     16 Dia    0.107±  2%   0.108±  1% +   0.9%
    16     32 CSR    0.096±  1%   0.096±  1%   -0.0%
    16     32 Dia    0.100±  1%   0.097±  1%   -3.2%
    32     64 CSR    0.096±  1%   0.112± 36% +  16.4%
    32     64 Dia    0.098±  0%   0.094±  1%   -4.2%
    64    128 CSR    0.095±  1%   0.092±  1%   -2.9%
    64    128 Dia    0.102±  1%   0.092±  1%   -9.5%
   128    256 CSR    0.096±  1%   0.092±  1%   -3.8%
   128    256 Dia    0.102±  2%   0.100± 14%   -1.5%
   256    512 CSR    0.095±  2%   0.090±  1%   -6.2%
   256    512 Dia    0.100±  1%   0.091±  1%   -8.7%
   512   1024 CSR    0.102±  6%   0.097±  2%   -5.0%
   512   1024 Dia    0.105±  2%   0.097±  3%   -7.7%
  1024   2048 CSR    0.081±  1%   0.078±  1%   -4.5%
  1024   2048 Dia    0.085±  1%   0.079±  2%   -7.5%
  2048   4096 CSR    0.092±  2%   0.088±  1%   -4.3%
  2048   4096 Dia    0.093±  1%   0.089±  2%   -4.7%
  4096   8192 CSR    0.097±  2%   0.088±  2%   -9.1%
  4096   8192 Dia    0.102±  3%   0.091±  4%  -11.1%
  5000  10000 CSR    0.080±  1%   0.076±  3%   -5.7%
  5000  10000 Dia    0.086±  3%   0.075±  2%  -13.4%
```

### MESOLVE
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.094± 10%   0.088±  0%   -6.4%
     4      8 Dia    0.100±  1%   0.093±  1%   -7.1%
     8     16 CSR    0.085±  1%   0.081±  1%   -4.8%
     8     16 Dia    0.102±  1%   0.084±  0%  -18.0%
    16     32 CSR    0.092±  2%   0.084±  2%   -9.0%
    16     32 Dia    0.104±  1%   0.086±  1%  -17.7%
    32     64 CSR    0.096±  2%   0.095±  4%   -0.7%
    32     64 Dia    0.109±  1%   0.095±  2%  -13.1%
    64    128 CSR    0.093±  2%   0.093±  4%   -0.6%
    64    128 Dia    0.108±  3%   0.097±  2%  -10.1%
   128    256 CSR    0.133±  6%   0.119±  7%  -10.8%
   128    256 Dia    0.155±  5%   0.168± 24% +   8.0%
```

## Full solve results: Linux, c8i.4xlarge

Compiler: GCC 14.3.0 (x86_64-linux-gnu)

SESOLVE:
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.120±  2%   0.126±  0% +   4.8%
     4      8 Dia    0.123±  1%   0.130±  3% +   5.4%
     8     16 CSR    0.119±  1%   0.122±  1% +   3.0%
     8     16 Dia    0.121±  1%   0.122±  0% +   1.1%
    16     32 CSR    0.111±  0%   0.115±  0% +   4.2%
    16     32 Dia    0.112±  0%   0.114±  0% +   1.9%
    32     64 CSR    0.114±  0%   0.117±  1% +   2.7%
    32     64 Dia    0.112±  0%   0.113±  1% +   1.1%
    64    128 CSR    0.114±  1%   0.115±  1% +   1.2%
    64    128 Dia    0.112±  0%   0.113±  0% +   0.8%
   128    256 CSR    0.118±  0%   0.117±  0%   -0.4%
   128    256 Dia    0.113±  0%   0.113±  0% +   0.1%
   256    512 CSR    0.115±  0%   0.114±  0%   -0.7%
   256    512 Dia    0.110±  0%   0.110±  0%   -0.2%
   512   1024 CSR    0.118±  0%   0.118±  0%   -0.6%
   512   1024 Dia    0.113±  0%   0.113±  1% +   0.2%
  1024   2048 CSR    0.095±  0%   0.094±  0%   -0.5%
  1024   2048 Dia    0.091±  1%   0.091±  0%   -0.6%
  2048   4096 CSR    0.099±  2%   0.097±  0%   -1.6%
  2048   4096 Dia    0.093±  0%   0.093±  0%   -0.1%
  4096   8192 CSR    0.108±  0%   0.106±  0%   -1.8%
  4096   8192 Dia    0.103±  0%   0.103±  1%   -0.2%
  5000  10000 CSR    0.097±  1%   0.095±  0%   -2.1%
  5000  10000 Dia    0.093±  0%   0.093±  0%   -0.3%
```

MESOLVE:
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.111±  0%   0.114±  0% +   2.3%
     4      8 Dia    0.114±  0%   0.115±  0% +   0.6%
     8     16 CSR    0.104±  0%   0.102±  0%   -1.5%
     8     16 Dia    0.104±  0%   0.103±  0%   -0.4%
    16     32 CSR    0.102±  0%   0.100±  1%   -1.9%
    16     32 Dia    0.101±  1%   0.100±  0%   -0.4%
    32     64 CSR    0.101±  0%   0.100±  0%   -1.5%
    32     64 Dia    0.100±  0%   0.100±  1% +   0.5%
    64    128 CSR    0.120±  1%   0.115±  0%   -4.0%
    64    128 Dia    0.116±  1%   0.115±  0%   -1.1%
   128    256 CSR    0.192±  1%   0.185±  1%   -3.5%
   128    256 Dia    0.211±  3%   0.206±  2%   -2.3%
```

## Microbenchmarks: `QobjEvo.matmul_data`

These test matrix-matrix operations as well as matrix-vector.

**Files:**
- `qutip/core/data/bench_matmul.pyx` - Cython benchmark module
- `run_matmul_bench.py` - Runner script
- `compare_matmul.py` - Comparison script

Copy the Cython benchmark to both worktrees and rebuild before running:
```bash
cp qutip-repo/qutip/core/data/bench_matmul.pyx qutip-master/qutip/core/data/
```

**Run:**
```bash
python run_matmul_bench.py qutip-master --csv matmul_master.csv
python run_matmul_bench.py qutip-repo --csv matmul_pr.csv
python compare_matmul.py matmul_master.csv matmul_pr.csv
```

### Microbenchmark Results (macOS Apple Silicon)

Compiler: Apple clang 17.0.0 (arm64-apple-darwin24.6.0)

MAT-VEC:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         0.19± 0%    0.17± 7%  -12.3%
    32 dia         0.22± 5%    0.18±10%  -18.2%
    64 csr         0.32± 3%    0.28± 4%  -13.5%
    64 dia         0.37± 9%    0.25± 2%  -32.1%
   128 csr         0.59± 1%    0.45± 2%  -23.3%
   128 dia         0.62± 0%    0.38± 4%  -38.2%
   256 csr         1.10± 1%    0.81± 4%  -25.8%
   256 dia         1.17± 1%    0.68± 2%  -42.0%
```

MAT-MAT:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         3.23± 2%    2.86± 2%  -11.6%
    32 dia         3.98± 1%    2.56± 1%  -35.8%
    64 csr        13.22± 1%   11.11± 1%  -16.0%
    64 dia        16.50± 1%   15.54± 2%   -5.9%
   128 csr        60.51± 0%   44.68± 1%  -26.2%
   128 dia        72.66± 4%   48.03± 1%  -33.9%
   256 csr       219.79± 1%  171.99± 1%  -21.7%
   256 dia       286.31± 1%  202.60± 5%  -29.2%
```

### Microbenchmark Results (c8i.4xlarge)

Compiler: GCC 14.3.0 (x86_64-linux-gnu)

MAT-VEC (H @ |ψ⟩) - tridiagonal H, Dense state:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         0.20± 0%    0.19± 3%   -3.4%
    32 dia         0.14± 0%    0.16± 0% +  14.3%
    64 csr         0.34± 0%    0.34± 2%   -1.0%
    64 dia         0.23± 0%    0.24± 2% +   5.8%
   128 csr         0.64± 0%    0.62± 0%   -3.1%
   128 dia         0.41± 1%    0.42± 1% +   2.5%
   256 csr         1.23± 0%    1.18± 0%   -4.3%
   256 dia         0.75± 1%    0.77± 0% +   2.7%
```

MAT-MAT (H @ ρ) - tridiagonal H, Dense state:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         4.16± 1%    2.97± 1%  -28.7%
    32 dia         2.75± 0%    2.74± 1%   -0.2%
    64 csr        16.58± 0%   12.62± 1%  -23.9%
    64 dia        11.26± 1%   11.31± 0% +   0.4%
   128 csr        66.60± 1%   48.48± 0%  -27.2%
   128 dia        46.50± 1%   46.16± 0%   -0.7%
   256 csr       286.77± 2%  219.86± 4%  -23.3%
   256 dia       216.43± 1%  218.50± 4% +   1.0%
```