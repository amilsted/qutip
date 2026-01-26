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
     4      8 CSR    0.107±  1%   0.110±  1% +   2.9%
     4      8 Dia    0.104±  1%   0.115±  1% +  10.8%
     8     16 CSR    0.101±  1%   0.102±  1% +   0.7%
     8     16 Dia    0.109±  1%   0.107±  1%   -2.3%
    16     32 CSR    0.094±  2%   0.095±  1% +   0.7%
    16     32 Dia    0.099±  2%   0.099±  2% +   0.2%
    32     64 CSR    0.094±  1%   0.092±  1%   -2.5%
    32     64 Dia    0.098±  2%   0.100± 15% +   2.2%
    64    128 CSR    0.093±  1%   0.095±  5% +   1.7%
    64    128 Dia    0.095±  2%   0.091±  2%   -4.3%
   128    256 CSR    0.097±  1%   0.089±  2%   -8.4%
   128    256 Dia    0.103±  1%   0.092±  1%  -11.2%
   256    512 CSR    0.097±  1%   0.091±  1%   -5.9%
   256    512 Dia    0.100±  1%   0.092±  2%   -8.1%
   512   1024 CSR    0.101±  1%   0.095±  1%   -5.9%
   512   1024 Dia    0.106±  1%   0.099±  6%   -6.2%
  1024   2048 CSR    0.080±  2%   0.079±  1%   -1.2%
  1024   2048 Dia    0.085±  2%   0.078±  2%   -7.7%
  2048   4096 CSR    0.090±  1%   0.086±  1%   -4.1%
  2048   4096 Dia    0.094±  1%   0.086±  1%   -8.2%
  4096   8192 CSR    0.093±  1%   0.086±  3%   -7.5%
  4096   8192 Dia    0.096±  2%   0.083±  1%  -13.4%
  5000  10000 CSR    0.080±  1%   0.075±  1%   -6.3%
  5000  10000 Dia    0.084±  1%   0.076±  1%   -9.7%
```

### MESOLVE
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.085±  2%   0.087±  1% +   2.0%
     4      8 Dia    0.102±  2%   0.091±  1%  -11.2%
     8     16 CSR    0.085±  1%   0.081±  0%   -5.0%
     8     16 Dia    0.100±  4%   0.085±  0%  -15.4%
    16     32 CSR    0.090±  1%   0.082±  3%   -8.4%
    16     32 Dia    0.102±  1%   0.087±  1%  -14.5%
    32     64 CSR    0.097±  1%   0.095±  4%   -2.7%
    32     64 Dia    0.107±  1%   0.092±  4%  -14.8%
    64    128 CSR    0.092±  5%   0.086±  1%   -6.6%
    64    128 Dia    0.109± 13%   0.089±  1%  -18.5%
   128    256 CSR    0.124±  4%   0.108±  2%  -13.0%
   128    256 Dia    0.135±  3%   0.114±  1%  -16.0%
```

## Full solve results: Linux, c8i.4xlarge

Compiler: GCC 14.3.0 (x86_64-linux-gnu)

SESOLVE:
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.121±  1%   0.121±  1% +   0.7%
     4      8 Dia    0.121±  0%   0.122±  1% +   1.2%
     8     16 CSR    0.119±  0%   0.119±  0% +   0.6%
     8     16 Dia    0.118±  0%   0.120±  0% +   1.3%
    16     32 CSR    0.112±  0%   0.114±  0% +   1.4%
    16     32 Dia    0.111±  0%   0.113±  0% +   1.8%
    32     64 CSR    0.115±  1%   0.115±  0%   -0.0%
    32     64 Dia    0.111±  0%   0.112±  1% +   0.7%
    64    128 CSR    0.115±  1%   0.114±  1%   -0.4%
    64    128 Dia    0.112±  0%   0.113±  0% +   0.5%
   128    256 CSR    0.118±  0%   0.117±  0%   -0.9%
   128    256 Dia    0.114±  0%   0.114±  0% +   0.0%
   256    512 CSR    0.116±  0%   0.114±  0%   -1.7%
   256    512 Dia    0.110±  0%   0.110±  0%   -0.0%
   512   1024 CSR    0.118±  0%   0.116±  0%   -1.4%
   512   1024 Dia    0.113±  0%   0.112±  0%   -0.4%
  1024   2048 CSR    0.095±  0%   0.094±  0%   -1.5%
  1024   2048 Dia    0.091±  0%   0.091±  0%   -0.0%
  2048   4096 CSR    0.098±  0%   0.097±  0%   -1.3%
  2048   4096 Dia    0.094±  1%   0.094±  1%   -0.3%
  4096   8192 CSR    0.108±  2%   0.106±  1%   -1.4%
  4096   8192 Dia    0.103±  1%   0.103±  0% +   0.3%
  5000  10000 CSR    0.097±  0%   0.096±  0%   -0.9%
  5000  10000 Dia    0.093±  1%   0.093±  0% +   0.5%
```

MESOLVE:
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.112±  1%   0.112±  0%   -0.3%
     4      8 Dia    0.114±  0%   0.115±  0% +   0.8%
     8     16 CSR    0.104±  0%   0.103±  0%   -1.6%
     8     16 Dia    0.105±  0%   0.104±  0%   -0.3%
    16     32 CSR    0.101±  0%   0.099±  0%   -2.0%
    16     32 Dia    0.099±  0%   0.098±  0%   -0.7%
    32     64 CSR    0.102±  2%   0.100±  0%   -2.0%
    32     64 Dia    0.101±  3%   0.100±  1%   -0.8%
    64    128 CSR    0.119±  1%   0.117±  1%   -1.5%
    64    128 Dia    0.116±  1%   0.117±  1% +   0.3%
   128    256 CSR    0.191±  1%   0.189±  1%   -0.9%
   128    256 Dia    0.209±  2%   0.210±  3% +   0.5%
```

## Microbenchmarks: `QobjEvo.matmul_data`

These test matrix-matrix operations as well as matrix-vector.

**Files:**
- `qutip/core/data/bench_matmul.pyx` - Cython benchmark module
- `test_interleaved.py` - Interleaved benchmark script (recommended)
- `compare_interleaved.py` - Comparison script for interleaved benchmarks

Copy the Cython benchmark to both worktrees and rebuild before running:
```bash
cp qutip-repo/qutip/core/data/bench_matmul.pyx qutip-master/qutip/core/data/
```

**Run (interleaved, recommended):**
```bash
python compare_interleaved.py qutip-master qutip-repo
```

The interleaved benchmark alternates DIA/CSR operations to avoid CPU cache artifacts.

### Microbenchmark Results (macOS Apple Silicon)

Compiler: Apple clang 17.0.0 (arm64-apple-darwin24.6.0)

Using interleaved benchmarks to avoid caching artifacts.

MAT-VEC (H @ |ψ⟩) - tridiagonal H, Dense state:
```
  Dim Type       Master           PR   Change
---------------------------------------------
   32 dia        0.28±0%       0.21±0%   -25.0%
   32 csr        0.25±0%       0.19±0%   -24.0%
   64 dia        0.40±0%       0.29±0%   -27.5%
   64 csr        0.37±0%       0.31±0%   -16.2%
  128 dia        0.66±0%       0.43±0%   -34.8%
  128 csr        0.63±0%       0.50±0%   -20.6%
  256 dia        1.22±0%       0.72±0%   -41.0%
  256 csr        1.17±0%       0.85±0%   -27.4%
```

MAT-MAT (H @ ρ) - tridiagonal H, Dense state:
```
  Dim Type       Master           PR   Change
---------------------------------------------
   32 dia        4.12±0%       2.61±0%   -36.7%
   32 csr        3.38±0%       2.90±0%   -14.2%
   64 dia       17.08±0%      17.19±0% +   0.6%
   64 csr       13.58±0%      11.39±0%   -16.1%
  128 dia       70.78±0%      48.79±0%   -31.1%
  128 csr       59.81±0%      45.75±0%   -23.5%
  256 dia      291.91±0%     200.77±0%   -31.2%
  256 csr      225.79±0%     174.94±0%   -22.5%
```

### Microbenchmark Results (c8i.4xlarge)

Compiler: GCC 14.3.0 (x86_64-linux-gnu)

Using interleaved benchmarks to avoid caching artifacts.

MAT-VEC (H @ |ψ⟩) - tridiagonal H, Dense state:
```
  Dim Type       Master           PR   Change
--------------------------------------------------
   32 dia        0.21±0%       0.21±0%     0.0%
   32 csr        0.26±0%       0.25±0%    -3.8%
   64 dia        0.29±0%       0.29±0%     0.0%
   64 csr        0.42±0%       0.39±0%    -7.1%
  128 dia        0.48±0%       0.48±0%     0.0%
  128 csr        0.72±0%       0.66±0%    -8.3%
  256 dia        0.83±0%       0.84±0% +   1.2%
  256 csr        1.31±0%       1.25±0%    -4.6%
```

MAT-MAT (H @ ρ) - tridiagonal H, Dense state:
```
  Dim Type       Master           PR   Change
--------------------------------------------------
   32 dia        2.77±0%       2.86±0% +   3.2%
   32 csr        4.18±0%       3.02±0%   -27.8%
   64 dia       11.57±0%      11.51±0%    -0.5%
   64 csr       17.00±0%      12.36±0%   -27.3%
  128 dia       46.68±0%      46.96±0% +   0.6%
  128 csr       68.28±0%      48.95±0%   -28.3%
  256 dia      226.34±0%     216.76±0%    -4.2%
  256 csr      305.26±0%     210.71±0%   -31.0%
```