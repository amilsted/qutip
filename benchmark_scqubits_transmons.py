"""
Benchmark: Matrix-form vs Superoperator Lindblad solver for coupled transmons.

This script uses scqubits to create a system of N charge-coupled transmons,
adds a charge drive and photon loss dissipation on one transmon, and compares
the performance of qutip's mesolve with and without the matrix_form option.
"""

import numpy as np
import time
import scqubits as scq
import qutip

# Suppress scqubits warnings
import warnings
warnings.filterwarnings('ignore')


def create_coupled_transmons(n_transmons, ncut=5, EJ=15.0, EC=0.3, ng=0.0, g=0.05,
                             truncated_dim=3):
    """
    Create a system of N charge-coupled transmons using scqubits.
    
    Parameters
    ----------
    n_transmons : int
        Number of transmons
    ncut : int
        Charge basis cutoff for each transmon
    EJ : float
        Josephson energy (GHz)
    EC : float
        Charging energy (GHz)
    ng : float
        Offset charge
    g : float
        Coupling strength between adjacent transmons (GHz)
    truncated_dim : int
        Number of levels to keep per transmon
    
    Returns
    -------
    hilbertspace : scqubits.HilbertSpace
        The composite Hilbert space
    transmons : list
        List of Transmon objects
    """
    # Create individual transmons
    transmons = []
    for i in range(n_transmons):
        tmon = scq.Transmon(
            EJ=EJ,
            EC=EC,
            ng=ng,
            ncut=ncut,
            truncated_dim=truncated_dim
        )
        transmons.append(tmon)
    
    # Create Hilbert space
    hilbertspace = scq.HilbertSpace(transmons)
    
    # Add capacitive coupling between adjacent transmons
    for i in range(n_transmons - 1):
        hilbertspace.add_interaction(
            g_strength=g,
            op1=(transmons[i].n_operator, transmons[i]),
            op2=(transmons[i+1].n_operator, transmons[i+1])
        )
    
    return hilbertspace, transmons


def get_qutip_hamiltonian_and_ops(hilbertspace, transmons):
    """
    Extract qutip Hamiltonian and operators from the scqubits Hilbert space.
    All operators are converted to CSR representation.
    
    Returns
    -------
    H : qutip.Qobj
        System Hamiltonian (includes interactions)
    n_op : qutip.Qobj
        Charge operator for first transmon in energy eigenbasis
    a_op : qutip.Qobj
        Annihilation operator for first transmon
    omega_q : float
        Qubit frequency (E1 - E0) for first transmon
    """
    # Get full Hamiltonian (bare + interactions)
    H = hilbertspace.hamiltonian().to("CSR")
    
    # Get annihilation operator for first transmon using scqubits
    tmon = transmons[0]
    a_op = hilbertspace.annihilate(tmon).to("CSR")
    
    # Create charge operator for first transmon in energy eigenbasis
    # using scqubits identity_wrap with op_in_eigenbasis=False
    # (the operator is in the charge basis, transform to energy eigenbasis)
    n_op = scq.identity_wrap(
        tmon.n_operator(), tmon, hilbertspace.subsystem_list,
        op_in_eigenbasis=False
    ).to("CSR")
    
    # Get qubit frequency (transition frequency between ground and first excited)
    evals = tmon.eigenvals(evals_count=2)
    omega_q = evals[1] - evals[0]
    
    return H, n_op, a_op, omega_q


def run_benchmark(n_transmons_list, truncated_dim=3, n_times=100, kappa=0.01,
                  drive_amp=0.1, target_time=1.0):
    """
    Run benchmark comparing matrix-form and superoperator solvers.
    
    Parameters
    ----------
    n_transmons_list : list of int
        List of transmon counts to benchmark
    truncated_dim : int
        Number of levels to keep per transmon (default: 3)
    n_times : int
        Number of time points
    kappa : float
        Photon loss rate (GHz)
    drive_amp : float
        Drive amplitude (GHz)
    target_time : float
        Target total time per solver (seconds). Number of repeats is adjusted
        to achieve this, with a minimum of 2 repeats.
    """
    results = []
    
    for n_transmons in n_transmons_list:
        print(f"\n{'='*60}")
        print(f"Benchmarking {n_transmons} coupled transmons ({truncated_dim} levels each)")
        print(f"{'='*60}")
        
        # Create system
        hilbertspace, transmons = create_coupled_transmons(
            n_transmons, truncated_dim=truncated_dim
        )
        H, n_op, a_op, omega_q = get_qutip_hamiltonian_and_ops(hilbertspace, transmons)
        
        dim = H.shape[0]
        print(f"Hilbert space dimension: {dim}")
        print(f"Density matrix size: {dim}x{dim} = {dim**2} elements")
        print(f"Liouvillian size: {dim**2}x{dim**2} = {dim**4} elements")
        print(f"Qubit frequency: {omega_q:.3f} GHz")
        
        # Time-dependent drive on first transmon (charge drive at qubit frequency)
        # H_drive(t) = drive_amp * cos(omega_q * t) * n_op
        # Use interpolated coefficient for efficiency
        t_coeff = np.linspace(0, 10, 1001)
        drive_coeff_vals = drive_amp * np.cos(omega_q * t_coeff)
        drive_coeff = qutip.coefficient(drive_coeff_vals, tlist=t_coeff)
        
        H_td = qutip.QobjEvo([H, [n_op, drive_coeff]])
        
        # Collapse operator: photon loss on first transmon
        c_ops = [np.sqrt(kappa) * a_op]
        
        # Print operator representations
        print(f"\nOperator representations (all CSR):")
        print(f"  H:       {type(H.data).__name__}")
        print(f"  n_op:    {type(n_op.data).__name__}")
        print(f"  c_op:    {type(c_ops[0].data).__name__}")
        
        # Initial state: ground state (tensor product basis)
        dims = [t.truncated_dim for t in transmons]
        psi0 = qutip.basis(dims, [0] * n_transmons)
        rho0 = qutip.ket2dm(psi0)
        
        # Time evolution
        tlist = np.linspace(0, 10, n_times)
        
        # Expectation operators
        e_ops = [n_op]  # Charge on first transmon
        
        # First run to estimate time and determine number of repeats
        print("\nRunning superoperator form...")
        t_start = time.perf_counter()
        result_super = qutip.mesolve(
            H_td, rho0, tlist, c_ops, e_ops=e_ops,
            options={"matrix_form": False}
        )
        t_first_super = time.perf_counter() - t_start
        
        # Determine number of repeats (minimum 2)
        n_repeats = max(2, int(target_time / t_first_super))
        print(f"  First run: {t_first_super:.3f} s, doing {n_repeats} repeats")
        
        # Run remaining repeats for superoperator
        times_super = [t_first_super]
        for _ in range(n_repeats - 1):
            t_start = time.perf_counter()
            qutip.mesolve(
                H_td, rho0, tlist, c_ops, e_ops=e_ops,
                options={"matrix_form": False}
            )
            times_super.append(time.perf_counter() - t_start)
        t_super = np.mean(times_super)
        print(f"  Mean time: {t_super:.3f} s (std: {np.std(times_super):.3f} s)")
        
        # Benchmark matrix form with same number of repeats
        print("Running matrix form...")
        times_matrix = []
        for i in range(n_repeats):
            t_start = time.perf_counter()
            result_matrix = qutip.mesolve(
                H_td, rho0, tlist, c_ops, e_ops=e_ops,
                options={"matrix_form": True}
            )
            times_matrix.append(time.perf_counter() - t_start)
            if i == 0:
                print(f"  First run: {times_matrix[0]:.3f} s")
        t_matrix = np.mean(times_matrix)
        print(f"  Mean time: {t_matrix:.3f} s (std: {np.std(times_matrix):.3f} s)")
        
        # Verify results match
        max_diff = np.max(np.abs(
            np.array(result_super.expect[0]) - np.array(result_matrix.expect[0])
        ))
        print(f"\nMax difference in expectation values: {max_diff:.2e}")
        
        # Speedup
        speedup = t_super / t_matrix
        print(f"Speedup (matrix form vs superoperator): {speedup:.2f}x")
        
        results.append({
            'n_transmons': n_transmons,
            'dim': dim,
            't_super': t_super,
            't_matrix': t_matrix,
            'speedup': speedup,
            'max_diff': max_diff,
            'n_repeats': n_repeats
        })
    
    return results


def print_summary(results, truncated_dim=3):
    """Print a summary table of benchmark results."""
    print("\n" + "="*70)
    print(f"BENCHMARK SUMMARY ({truncated_dim} levels/transmon, times in seconds)")
    print("="*70)
    print(f"{'N':>2} {'Dim':>4} {'Super':>8} {'Matrix':>8} {'Speedup':>8}")
    print("-"*70)
    for r in results:
        print(f"{r['n_transmons']:>2} {r['dim']:>4} {r['t_super']:>8.3f} "
              f"{r['t_matrix']:>8.3f} {r['speedup']:>7.2f}x")
    print("="*70)


if __name__ == "__main__":
    print("Matrix-form vs Superoperator Lindblad Solver Benchmark")
    print("System: Charge-coupled transmons with drive and dissipation")
    
    # Benchmark with 3 levels per transmon (dim = 3^N)
    print("\n" + "#"*70)
    print("# 3 LEVELS PER TRANSMON")
    print("#"*70)
    n_transmons_list_3 = [2, 3, 4, 5]
    results_3 = run_benchmark(n_transmons_list_3, truncated_dim=3)
    print_summary(results_3, truncated_dim=3)
    
    # Benchmark with 4 levels per transmon (dim = 4^N)
    print("\n" + "#"*70)
    print("# 4 LEVELS PER TRANSMON")
    print("#"*70)
    n_transmons_list_4 = [2, 3, 4]
    results_4 = run_benchmark(n_transmons_list_4, truncated_dim=4)
    print_summary(results_4, truncated_dim=4)
