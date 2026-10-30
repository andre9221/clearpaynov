"""
generate_scaling_benchmark_graph.py
===================================
Generates a new, high-resolution empirical results figure explaining:
1. Liquidity Stress Sensitivity Curves (Settled % vs Liquidity Ratio Alpha: 0.1 to 1.2)
2. Algorithmic Scalability & Runtime Complexity (Log-Log Plot: N=10 to 10,000 payments)
3. Optimality Gap vs Exact MILP Solver (Distribution across 20 stochastic seeds)

Output: docs/report_figures/clearpay_scaling_liquidity_results.png
"""
import json
import os
import matplotlib.pyplot as plt
import numpy as np

def generate_graph():
    # Load data from benchmark_results.json
    results_path = os.path.abspath("benchmark/results/benchmark_results.json")
    with open(results_path, "r") as f:
        data = json.load(f)

    # 1. Liquidity Stress Data
    liquidity_levels = [float(k) for k in data["settled_value_pct"]["all_or_nothing"].keys()]
    liquidity_pct = [x * 100 for x in liquidity_levels]
    aon_vals = list(data["settled_value_pct"]["all_or_nothing"].values())
    greedy_vals = list(data["settled_value_pct"]["greedy_cumulative"].values())
    rh_vals = list(data["settled_value_pct"]["removal_heuristic"].values())

    # 2. Execution Time Scaling Data (N = 10 to 10,000)
    sizes = [int(k) for k in data["exec_time_ms"]["greedy_cumulative"].keys()]
    greedy_times = list(data["exec_time_ms"]["greedy_cumulative"].values())
    rh_times = list(data["exec_time_ms"]["removal_heuristic"].values())

    # 3. Optimality Gaps
    gaps = [item["gap_pct"] for item in data["optimality_gaps"]]

    # Styling setup: Academic monochrome/charcoal palette
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#343A40'
    plt.rcParams['axes.linewidth'] = 1.2

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    # -------------------------------------------------------------
    # PANEL A: Liquidity Stress Response Curve
    # -------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_facecolor("#F8F9FA")
    ax1.plot(liquidity_pct, aon_vals, marker='s', markersize=6, linewidth=2.0, color='#868E96', 
             linestyle='--', label='All-or-Nothing (Baseline)')
    ax1.plot(liquidity_pct, greedy_vals, marker='^', markersize=6, linewidth=2.0, color='#495057', 
             linestyle='-.', label='Greedy Cumulative')
    ax1.plot(liquidity_pct, rh_vals, marker='o', markersize=6, linewidth=2.5, color='#212529', 
             linestyle='-', label='ClearPay Removal Heuristic')

    ax1.axvspan(10, 40, color='#CED4DA', alpha=0.3, label='Severe Liquidity Deficit (Stress Zone)')
    ax1.set_title("(A) Settlement Yield Under Liquidity Stress", fontsize=12, fontweight='bold', pad=12, color='#212529')
    ax1.set_xlabel("Bank Available Liquidity Quota (% of Gross Outflow)", fontsize=10, fontweight='bold', color='#343A40')
    ax1.set_ylabel("Settled Transaction Value (%)", fontsize=10, fontweight='bold', color='#343A40')
    ax1.set_ylim(-5, 105)
    ax1.set_xlim(8, 122)
    ax1.grid(True, linestyle=':', alpha=0.6, color='#ADB5BD')
    ax1.legend(loc='lower right', fontsize=8.5, framealpha=0.95, edgecolor='#CED4DA')

    # Annotate dead-lock at alpha=0.1
    ax1.annotate('AON 0.0% (Dead-lock)', xy=(10, 0), xytext=(20, 15),
                 arrowprops=dict(arrowstyle="->", color='#212529', lw=1.2),
                 fontsize=8.5, fontweight='bold', color='#495057',
                 bbox=dict(boxstyle="round,pad=0.2", facecolor='#FFFFFF', edgecolor='#CED4DA'))
    ax1.annotate(f'ClearPay: {rh_vals[0]:.1f}% Cleared', xy=(10, rh_vals[0]), xytext=(22, 70),
                 arrowprops=dict(arrowstyle="->", color='#212529', lw=1.2),
                 fontsize=8.5, fontweight='bold', color='#212529',
                 bbox=dict(boxstyle="round,pad=0.2", facecolor='#FFFFFF', edgecolor='#CED4DA'))

    # -------------------------------------------------------------
    # PANEL B: Algorithmic Complexity & Execution Time (Log-Log)
    # -------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_facecolor("#F8F9FA")
    ax2.plot(sizes, greedy_times, marker='^', markersize=6, linewidth=2.2, color='#495057', 
             linestyle='--', label=r'Greedy Cumulative ($O(N^2)$)')
    ax2.plot(sizes, rh_times, marker='o', markersize=6, linewidth=2.5, color='#212529', 
             linestyle='-', label=r'ClearPay Removal Heuristic ($O(N \log N)$)')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title("(B) Computational Scalability (Runtime vs Queue Size)", fontsize=12, fontweight='bold', pad=12, color='#212529')
    ax2.set_xlabel("Payment Queue Size N (Obligations)", fontsize=10, fontweight='bold', color='#343A40')
    ax2.set_ylabel("Execution Latency (milliseconds, Log Scale)", fontsize=10, fontweight='bold', color='#343A40')
    ax2.grid(True, which="both", linestyle=':', alpha=0.6, color='#ADB5BD')
    ax2.legend(loc='upper left', fontsize=9, framealpha=0.95, edgecolor='#CED4DA')

    # Annotate speedup at N=10,000
    speedup = greedy_times[-1] / rh_times[-1]
    ax2.annotate(f'N=10,000:\nGreedy: 10,031 ms\nClearPay: 6.44 ms\n({speedup:.0f}x Speedup)',
                 xy=(sizes[-1], rh_times[-1]), xytext=(700, 3.0),
                 arrowprops=dict(arrowstyle="->", color='#212529', lw=1.2),
                 fontsize=8.5, fontweight='bold', color='#212529',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFFFFF', edgecolor='#CED4DA'))

    # -------------------------------------------------------------
    # PANEL C: Heuristic Optimality Gap vs MILP Optimal Solver
    # -------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_facecolor("#F8F9FA")
    
    # Histogram of gaps across the 20 seeds
    bins = [0, 0.01, 4, 8, 12, 16, 20]
    zero_gaps = sum(1 for g in gaps if g == 0.0)
    zero_pct = (zero_gaps / len(gaps)) * 100

    n_counts, bin_edges, patches_bars = ax3.hist(gaps, bins=bins, color='#495057', edgecolor='#212529', 
                                                 linewidth=1.2, rwidth=0.85)
    patches_bars[0].set_facecolor('#212529')  # Highlight 0% gap

    ax3.set_title("(C) Optimality Gap vs Exact MILP Solver", fontsize=12, fontweight='bold', pad=12, color='#212529')
    ax3.set_xlabel("Optimality Gap % = (MILP - Heuristic) / MILP", fontsize=10, fontweight='bold', color='#343A40')
    ax3.set_ylabel("Number of Trials (20 Random Seeds)", fontsize=10, fontweight='bold', color='#343A40')
    ax3.set_xticks([0, 4, 8, 12, 16, 20])
    ax3.set_xticklabels(['0% (Exact)', '4%', '8%', '12%', '16%', '20%'])
    ax3.grid(True, linestyle=':', alpha=0.6, color='#ADB5BD')

    # Annotate exact optimum percentage
    ax3.annotate(f'{zero_pct:.0f}% of Trials Achieve\nExact 0.0% Optimality Gap\n(Matches MILP Provable Optimum)',
                 xy=(0.5, zero_gaps), xytext=(4, 9),
                 arrowprops=dict(arrowstyle="->", color='#212529', lw=1.2),
                 fontsize=8.5, fontweight='bold', color='#212529',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFFFFF', edgecolor='#CED4DA'))

    plt.suptitle("ClearPay Extended Empirical Evaluation: Liquidity Stress, Runtime Complexity & Mathematical Optimality", 
                 fontsize=14, fontweight='bold', y=1.02, color='#111827')
    plt.tight_layout()

    out_dir = os.path.abspath("docs/report_figures")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "clearpay_extended_empirical_analysis.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Extended results graph successfully generated at: {out_path}")

if __name__ == "__main__":
    generate_graph()

