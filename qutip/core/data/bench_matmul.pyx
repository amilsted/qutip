# cython: language_level=3
"""Cython benchmarks for QobjEvo.matmul_data with in-place operations."""
import time

from qutip.core.data.dense cimport Dense
from qutip.core.data cimport dense
from qutip.core.data.mul cimport imul_dense
from qutip.core.cy.qobjevo cimport QobjEvo

cdef double _bench_matmul_data(QobjEvo qevo, Dense state, Dense out, int n_iters):
    """Benchmark QobjEvo.matmul_data with Dense state and pre-allocated output."""
    cdef int i
    for i in range(100):
        qevo.matmul_data(0, state, out)
        imul_dense(out, 0)
    t0 = time.perf_counter()
    for i in range(n_iters):
        qevo.matmul_data(0, state, out)
        imul_dense(out, 0)
    return (time.perf_counter() - t0) / n_iters * 1e6

cdef tuple _bench_interleaved(QobjEvo qevo_dia, QobjEvo qevo_csr, Dense state, Dense out, int n_iters):
    """Benchmark DIA and CSR interleaved to avoid caching artifacts."""
    cdef int i
    cdef double t_dia = 0.0, t_csr = 0.0, t0
    # Warmup
    for i in range(100):
        qevo_dia.matmul_data(0, state, out)
        imul_dense(out, 0)
        qevo_csr.matmul_data(0, state, out)
        imul_dense(out, 0)
    # Interleaved timing
    for i in range(n_iters):
        t0 = time.perf_counter()
        qevo_dia.matmul_data(0, state, out)
        imul_dense(out, 0)
        t_dia += time.perf_counter() - t0
        
        t0 = time.perf_counter()
        qevo_csr.matmul_data(0, state, out)
        imul_dense(out, 0)
        t_csr += time.perf_counter() - t0
    return (t_dia / n_iters * 1e6, t_csr / n_iters * 1e6)

def run_benchmarks(qevo_dia, qevo_csr, psi_dense, rho_dense, int n_iters=10000):
    """
    Run matmul_data benchmarks for DIA/CSR Hamiltonians.
    State is always Dense (as in actual solvers).
    """
    cdef int dim = psi_dense.shape[0]
    cdef QobjEvo qevo_i = qevo_dia
    cdef QobjEvo qevo_c = qevo_csr
    cdef Dense psi = psi_dense.data
    cdef Dense rho = rho_dense.data
    cdef Dense out_vec = dense.zeros(dim, 1, psi.fortran)
    cdef Dense out_mat = dense.zeros(dim, dim, rho.fortran)
    
    return {
        'dia_vec': _bench_matmul_data(qevo_i, psi, out_vec, n_iters),
        'csr_vec': _bench_matmul_data(qevo_c, psi, out_vec, n_iters),
        'dia_mat': _bench_matmul_data(qevo_i, rho, out_mat, n_iters),
        'csr_mat': _bench_matmul_data(qevo_c, rho, out_mat, n_iters),
    }

def run_benchmarks_interleaved(qevo_dia, qevo_csr, psi_dense, rho_dense, int n_iters=10000):
    """
    Run matmul_data benchmarks with DIA/CSR interleaved.
    """
    cdef int dim = psi_dense.shape[0]
    cdef QobjEvo qevo_i = qevo_dia
    cdef QobjEvo qevo_c = qevo_csr
    cdef Dense psi = psi_dense.data
    cdef Dense rho = rho_dense.data
    cdef Dense out_vec = dense.zeros(dim, 1, psi.fortran)
    cdef Dense out_mat = dense.zeros(dim, dim, rho.fortran)
    
    dia_vec, csr_vec = _bench_interleaved(qevo_i, qevo_c, psi, out_vec, n_iters)
    dia_mat, csr_mat = _bench_interleaved(qevo_i, qevo_c, rho, out_mat, n_iters)
    
    return {
        'dia_vec': dia_vec,
        'csr_vec': csr_vec,
        'dia_mat': dia_mat,
        'csr_mat': csr_mat,
    }
