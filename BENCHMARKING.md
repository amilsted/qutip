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
     4      8 CSR    0.109±  4%   0.111±  4% +   1.9%
     4      8 Dia    0.101±  4%   0.116±  7% +  14.7%
     8     16 CSR    0.104±  1%   0.107±  0% +   2.6%
     8     16 Dia    0.108±  2%   0.110±  1% +   1.3%
    16     32 CSR    0.096±  1%   0.097±  1% +   1.6%
    16     32 Dia    0.100±  1%   0.100±  1%   -0.3%
    32     64 CSR    0.099± 10%   0.094±  1%   -5.1%
    32     64 Dia    0.099±  1%   0.095±  0%   -4.1%
    64    128 CSR    0.095±  3%   0.092±  2%   -3.1%
    64    128 Dia    0.094±  1%   0.088±  0%   -6.6%
   128    256 CSR    0.098±  2%   0.093±  1%   -4.9%
   128    256 Dia    0.102±  1%   0.093±  1%   -8.1%
   256    512 CSR    0.095±  1%   0.092±  1%   -3.7%
   256    512 Dia    0.099±  1%   0.093±  1%   -6.4%
   512   1024 CSR    0.100±  1%   0.096±  2%   -3.3%
   512   1024 Dia    0.104±  1%   0.097±  1%   -6.9%
  1024   2048 CSR    0.081±  3%   0.075±  1%   -7.7%
  1024   2048 Dia    0.082±  1%   0.077±  2%   -5.6%
  2048   4096 CSR    0.090±  1%   0.087±  2%   -3.7%
  2048   4096 Dia    0.095±  2%   0.089±  3%   -5.5%
  4096   8192 CSR    0.093±  0%   0.088±  1%   -5.4%
  4096   8192 Dia    0.097±  2%   0.089±  1%   -8.4%
  5000  10000 CSR    0.080±  1%   0.077±  1%   -4.1%
  5000  10000 Dia    0.084±  1%   0.078±  6%   -7.0%
```

### MESOLVE
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.085±  1%   0.089±  1% +   4.3%
     4      8 Dia    0.100±  2%   0.093±  1%   -7.5%
     8     16 CSR    0.085±  1%   0.080±  2%   -6.3%
     8     16 Dia    0.101±  2%   0.081±  1%  -19.6%
    16     32 CSR    0.090±  1%   0.083±  1%   -7.4%
    16     32 Dia    0.101±  1%   0.086±  1%  -14.9%
    32     64 CSR    0.096±  1%   0.092±  2%   -4.7%
    32     64 Dia    0.107±  1%   0.094±  1%  -12.1%
    64    128 CSR    0.091±  4%   0.087±  1%   -5.1%
    64    128 Dia    0.103±  0%   0.090±  2%  -12.4%
   128    256 CSR    0.121±  5%   0.107±  4%  -11.0%
   128    256 Dia    0.151±  6%   0.119±  7%  -21.0%
```

## Full solve results: Linux, c8i.4xlarge

Compiler: GCC 14.3.0 (x86_64-linux-gnu)

SESOLVE:
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.122±  1%   0.121±  1%   -1.5%
     4      8 Dia    0.126±  4%   0.124±  2%   -1.9%
     8     16 CSR    0.121±  1%   0.120±  1%   -0.8%
     8     16 Dia    0.121±  1%   0.120±  1%   -0.7%
    16     32 CSR    0.114±  0%   0.112±  0%   -1.3%
    16     32 Dia    0.112±  0%   0.111±  0%   -1.0%
    32     64 CSR    0.114±  0%   0.114±  0%   -0.2%
    32     64 Dia    0.112±  0%   0.113±  0% +   0.4%
    64    128 CSR    0.115±  1%   0.115±  1%   -0.3%
    64    128 Dia    0.113±  0%   0.113±  0% +   0.0%
   128    256 CSR    0.118±  0%   0.117±  0%   -0.7%
   128    256 Dia    0.114±  0%   0.114±  0% +   0.2%
   256    512 CSR    0.115±  0%   0.114±  0%   -1.1%
   256    512 Dia    0.110±  0%   0.113±  4% +   2.4%
   512   1024 CSR    0.119±  3%   0.119±  5%   -0.3%
   512   1024 Dia    0.112±  0%   0.112±  0%   -0.5%
  1024   2048 CSR    0.095±  0%   0.094±  0%   -1.1%
  1024   2048 Dia    0.091±  1%   0.091±  1%   -0.2%
  2048   4096 CSR    0.098±  0%   0.098±  2% +   0.2%
  2048   4096 Dia    0.094±  1%   0.096±  2% +   2.5%
  4096   8192 CSR    0.107±  1%   0.106±  1%   -1.1%
  4096   8192 Dia    0.103±  1%   0.105±  3% +   1.9%
  5000  10000 CSR    0.097±  1%   0.096±  1%   -1.6%
  5000  10000 Dia    0.093±  2%   0.093±  1% +   0.0%
```

MESOLVE:
```
 N_res    Dim Type       Master           PR   Change
------------------------------------------------------
     4      8 CSR    0.112±  0%   0.112±  1%   -0.2%
     4      8 Dia    0.115±  0%   0.115±  1% +   0.3%
     8     16 CSR    0.104±  0%   0.103±  0%   -1.3%
     8     16 Dia    0.105±  0%   0.104±  0%   -0.4%
    16     32 CSR    0.101±  0%   0.100±  0%   -1.3%
    16     32 Dia    0.099±  0%   0.099±  0%   -0.4%
    32     64 CSR    0.102±  1%   0.100±  0%   -1.5%
    32     64 Dia    0.100±  1%   0.100±  0%   -0.5%
    64    128 CSR    0.117±  1%   0.117±  1%   -0.2%
    64    128 Dia    0.116±  1%   0.116±  1% +   0.6%
   128    256 CSR    0.189±  1%   0.189±  1%   -0.3%
   128    256 Dia    0.206±  3%   0.210±  3% +   2.0%
```
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

Using interleaved benchmarks to avoid caching artifacts.

MAT-VEC (H @ |ψ⟩) - tridiagonal H, Dense state:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         0.25± 0%    0.19± 0%  -24.0%
    32 dia         0.28± 0%    0.21± 0%  -25.0%
    64 csr         0.38± 0%    0.30± 0%  -21.1%
    64 dia         0.41± 0%    0.28± 0%  -31.7%
   128 csr         0.63± 0%    0.47± 0%  -25.4%
   128 dia         0.66± 0%    0.40± 0%  -39.4%
   256 csr         1.16± 0%    0.83± 0%  -28.4%
   256 dia         1.23± 0%    0.69± 0%  -43.9%
```

MAT-MAT (H @ ρ) - tridiagonal H, Dense state:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         3.39± 0%    2.89± 0%  -14.7%
    32 dia         4.14± 0%    2.60± 0%  -37.2%
    64 csr        13.69± 0%   11.30± 0%  -17.5%
    64 dia        17.15± 0%   17.01± 0%   -0.8%
   128 csr        61.18± 0%   45.99± 0%  -24.8%
   128 dia        72.36± 0%   50.09± 0%  -30.8%
   256 csr       227.24± 0%  176.94± 0%  -22.1%
   256 dia       294.77± 0%  204.17± 0%  -30.7%
```

### Microbenchmark Results (c8i.4xlarge)

Compiler: GCC 14.3.0 (x86_64-linux-gnu)

Using interleaved benchmarks to avoid caching artifacts.

MAT-VEC (H @ |ψ⟩) - tridiagonal H, Dense state:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         0.26± 0%    0.25± 0%   -3.8%
    32 dia         0.20± 0%    0.21± 0% +   5.0%
    64 csr         0.41± 0%    0.39± 0%   -4.9%
    64 dia         0.29± 0%    0.29± 0%    0.0%
   128 csr         0.70± 0%    0.67± 0%   -4.3%
   128 dia         0.46± 0%    0.48± 0% +   4.3%
   256 csr         1.33± 0%    1.22± 0%   -8.3%
   256 dia         0.86± 0%    0.83± 0%   -3.5%
```

MAT-MAT (H @ ρ) - tridiagonal H, Dense state:
```
   Dim Type           Master           PR   Change
--------------------------------------------------
    32 csr         4.24± 0%    2.99± 0%  -29.5%
    32 dia         2.84± 0%    2.84± 0%    0.0%
    64 csr        16.74± 0%   12.26± 0%  -26.8%
    64 dia        11.42± 0%   11.52± 0% +   0.9%
   128 csr        68.14± 0%   48.64± 0%  -28.6%
   128 dia        46.59± 0%   46.94± 0% +   0.8%
   256 csr       295.14± 0%  221.18± 0%  -25.1%
   256 dia       214.50± 0%  219.45± 0% +   2.3%
```