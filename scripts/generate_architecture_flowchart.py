"""
generate_architecture_flowchart.py
==================================
Generates a publication-grade, high-resolution end-to-end architecture flowchart
for ClearPay (AWS Serverless Liquidity-Aware Settlement Engine).
Output: docs/report_figures/clearpay_architecture_flowchart.png
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_flowchart():
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Color Palette - Professional Black/Slate/Charcoal Theme
    c_bg = "#F8F9FA"
    c_box_bg = "#FFFFFF"
    c_box_border = "#2B2B2B"
    c_header_bg = "#212529"
    c_accent_dark = "#343A40"
    c_accent_light = "#E9ECEF"
    c_badge_bg = "#495057"
    c_arrow = "#212529"
    c_cloud_border = "#6C757D"

    fig.patch.set_facecolor(c_bg)

    # Title Banner
    ax.text(9, 11.5, "ClearPay: End-to-End Serverless Architecture & Execution Flowchart", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#111827', fontfamily='DejaVu Sans')
    ax.text(9, 11.15, "Event-Driven Liquidity-Aware Clearing, Netting Optimization & Atomic Ledger Settlement on AWS", 
            ha='center', va='center', fontsize=11, fontstyle='italic', color='#4B5563', fontfamily='DejaVu Sans')

    # AWS Cloud Container Boundary
    cloud_box = patches.FancyBboxPatch((2.8, 0.4), 14.8, 10.3, boxstyle="round,pad=0.2,rounding_size=0.3",
                                       linewidth=1.8, edgecolor=c_cloud_border, facecolor="#F1F3F5", linestyle="--")
    ax.add_patch(cloud_box)
    ax.text(3.1, 10.4, "AWS Cloud Boundary (Region: ap-south-1 / Mumbai)", fontsize=11, fontweight='bold', color='#495057')

    # Helper function for drawing rounded process boxes
    def draw_box(x, y, w, h, step_num, title, subtitle, items=None, is_db=False):
        # Outer box
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                                     linewidth=1.5, edgecolor=c_box_border, facecolor=c_box_bg)
        ax.add_patch(box)

        # Header badge / stripe
        header_h = 0.45
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                        boxstyle="round,pad=0.1,rounding_size=0.1",
                                        linewidth=1.2, edgecolor=c_box_border, facecolor=c_header_bg)
        ax.add_patch(header)

        # Step badge & title
        header_text = f"Step {step_num}: {title}" if step_num else title
        ax.text(x + w/2, y + h - header_h/2, header_text, ha='center', va='center', 
                color='#FFFFFF', fontweight='bold', fontsize=9.5)

        # Subtitle
        ax.text(x + w/2, y + h - 0.7, subtitle, ha='center', va='center', 
                color='#343A40', fontweight='bold', fontsize=8.5)

        # Detail bullet items
        if items:
            start_y = y + h - 0.95
            for i, itm in enumerate(items):
                ax.text(x + 0.15, start_y - (i * 0.22), f"• {itm}", 
                        ha='left', va='center', color='#495057', fontsize=7.5)

    # Helper for drawing connection arrows
    def draw_arrow(x1, y1, x2, y2, label="", label_pos=0.5, label_offset=(0, 0.15)):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=c_arrow, lw=1.8, shrinkA=3, shrinkB=3))
        if label:
            lx = x1 + (x2 - x1) * label_pos + label_offset[0]
            ly = y1 + (y2 - y1) * label_pos + label_offset[1]
            ax.text(lx, ly, label, ha='center', va='center', fontsize=7.5, 
                    fontweight='bold', color='#1F2937', 
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#CED4DA", lw=0.8))

    # --- COLUMN 1: CLIENT & INGESTION TIER ---
    # Client Tier Container
    client_box = patches.FancyBboxPatch((0.3, 3.8), 2.2, 6.9, boxstyle="round,pad=0.2,rounding_size=0.2",
                                        linewidth=1.4, edgecolor="#ADB5BD", facecolor="#FFFFFF", linestyle=":")
    ax.add_patch(client_box)
    ax.text(1.4, 10.4, "Client / Participant Tier", fontsize=10, fontweight='bold', ha='center', color='#495057')

    draw_box(0.4, 7.8, 2.0, 2.3, "1A", "Streamlit UI", "Operator Dashboard",
             ["Local & Cloud App", "Interactive Controls", "Portfolio Monitor", "Trigger Settl. Window"])
    
    draw_box(0.4, 4.4, 2.0, 2.5, "1B", "Participant Banks", "REST API Clients",
             ["Direct Batch Pay Orders", "Payload Normalization", "STAN Sign-off", "ISO 20022 Schema"])

    # --- AWS ENTRY POINT: API GATEWAY ---
    draw_box(3.2, 6.0, 2.2, 2.5, "2", "API Gateway", "REST Ingestion Endpoint",
             ["POST /payments", "API Key / IAM Auth", "Schema Validation", "CORS & Throttling"])

    # --- INGESTION LAMBDA & SQS ---
    draw_box(5.8, 6.0, 2.3, 2.5, "3", "IngestFunction", "Serverless Ingest (Lambda)",
             ["Validates JSON Body", "Enforces Idempotency", "Assigns PENDING Status", "Dead-Letter Buffering"])

    # --- DYNAMODB PAYMENTS TABLE ---
    draw_box(8.5, 6.0, 2.4, 2.5, "4", "PaymentsTable", "DynamoDB (Staging)",
             ["PK: payment_id", "GSI: status-index", "Stores Status: PENDING", "Point-in-Time Recovery"])

    # --- ROW 2: ORCHESTRATION & NETTING (STEP FUNCTIONS) ---
    # State Machine boundary box
    sm_box = patches.FancyBboxPatch((3.2, 0.8), 14.0, 4.4, boxstyle="round,pad=0.2,rounding_size=0.25",
                                    linewidth=1.2, edgecolor="#495057", facecolor="#E9ECEF", alpha=0.6)
    ax.add_patch(sm_box)
    ax.text(3.4, 4.9, "AWS Step Functions: ClearPay Settlement Orchestration State Machine (SettlementStateMachine)", 
            fontsize=10.5, fontweight='bold', color='#212529')

    # Step Functions sub-tasks
    draw_box(3.5, 1.2, 2.3, 3.2, "5", "Preflight & Collect", "CollectFunction",
             ["Settlement Window Open", "Scan PENDING Status", "Acquire Window Lease", "Lock Payment Queue", "Build Graph Adjacency"])

    draw_box(6.2, 1.2, 2.7, 3.2, "6", "Netting Engine", "NetFunction (Lambda)",
             ["Compute Bilateral Net", "Form Net Matrix N(i,j)", "Greedy Liquidity Pass", "Removal Heuristic", "BCGR Cycle Repair", "Output Approved Plan"])

    draw_box(9.3, 1.2, 2.4, 3.2, "7", "S3 Plan Freeze", "Amazon S3 DataBucket",
             ["Bucket: clearpay-data", "Key: windows/{id}/plan", "SHA-256 Hash Digest", "Zero Plan Tampering", "Audit Trail Snapshot"])

    draw_box(12.1, 1.2, 2.4, 3.2, "8", "PosterFunction", "Atomic Ledger Posting",
             ["Two-Phase Commit (2PC)", "DynamoDB TransactWrite", "Conditional Balance >= A", "Post Debit / Credit", "Write Immutable Ledger"])

    draw_box(14.8, 1.2, 2.2, 3.2, "9", "FinalizeFunction", "Window Close",
             ["Mark SETTLED / DEFERRED", "Release Lease Locks", "Notify SQS / SNS", "Emit CloudWatch Metrics", "Next Window Transition"])

    # --- TOP ROW: PERSISTENCE & AUDIT (DYNAMODB & S3 RECONCILIATION) ---
    draw_box(11.3, 6.0, 2.7, 2.5, "10", "Accounts & Ledger", "DynamoDB Tables",
             ["AccountsTable (Balances)", "LedgerTable (Double-Entry)", "Conditional Integrity", "Zero Double-Debit Proof"])

    draw_box(14.4, 6.0, 2.8, 2.5, "11", "Reconcile Tier", "S3 & ReconcileFunction",
             ["External Bank Statements", "S3 PutObject Trigger", "Automatic Reconciliation", "Flag Amount Discrepancy", "Zero Unsettled Drift"])

    # --- CONNECTING ARROWS ---
    # Streamlit & Banks -> API Gateway
    draw_arrow(2.4, 8.5, 3.2, 7.5, "Submit Batch")
    draw_arrow(2.4, 5.5, 3.2, 6.8, "API POST")

    # API Gateway -> Ingest Lambda -> PaymentsTable
    draw_arrow(5.4, 7.25, 5.8, 7.25, "Invoke")
    draw_arrow(8.1, 7.25, 8.5, 7.25, "PutItem")

    # Step Functions Trigger
    ax.annotate("", xy=(4.6, 4.4), xytext=(4.6, 5.5),
                arrowprops=dict(arrowstyle="->", color=c_arrow, lw=1.8, linestyle=":"))
    ax.text(4.6, 5.0, "Trigger Window\n(EventBridge/Cron)", ha='center', va='center', 
            fontsize=7, fontweight='bold', bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFF", edgecolor="#CED4DA"))

    # Inside Step Functions Chain: 5 -> 6 -> 7 -> 8 -> 9
    draw_arrow(5.8, 2.8, 6.2, 2.8, "Graph Data")
    draw_arrow(8.9, 2.8, 9.3, 2.8, "Opt Plan")
    draw_arrow(11.7, 2.8, 12.1, 2.8, "SHA-256 Plan")
    draw_arrow(14.5, 2.8, 14.8, 2.8, "Commit Ok")

    # PosterFunction <-> AccountsTable/LedgerTable
    draw_arrow(13.3, 4.4, 12.7, 6.0, "TransactWriteItems\n(Atomic 2PC)", label_pos=0.5, label_offset=(-0.3, -0.2))

    # Accounts & Ledger -> Reconcile Tier
    draw_arrow(14.0, 7.25, 14.4, 7.25, "Audit Match")

    # FinalizeFunction -> Reconcile / SettlementsTable
    draw_arrow(15.9, 4.4, 15.8, 6.0, "Settlement\nLog", label_pos=0.5, label_offset=(0.3, -0.2))

    # Bottom legend / summary ribbon
    legend_box = patches.FancyBboxPatch((0.5, 0.4), 2.0, 3.0, boxstyle="round,pad=0.1,rounding_size=0.15",
                                        linewidth=1.2, edgecolor="#ADB5BD", facecolor="#FFFFFF")
    ax.add_patch(legend_box)
    ax.text(1.5, 3.1, "ClearPay Legend", fontsize=8.5, fontweight='bold', ha='center', color='#212529')
    ax.text(0.6, 2.7, "──> Synchronous REST / Lambda", fontsize=7.2, color='#212529')
    ax.text(0.6, 2.3, "- - > EventBridge / Scheduled", fontsize=7.2, color='#212529')
    ax.text(0.6, 1.9, "==> DynamoDB TransactWrite", fontsize=7.2, color='#212529')
    ax.text(0.6, 1.5, "[SHA] Cryptographic Plan Lock", fontsize=7.2, color='#212529')
    ax.text(0.6, 1.1, "BCGR Cycle Gridlock Repair", fontsize=7.2, color='#212529')
    ax.text(0.6, 0.7, "Zero-Overdraft Guarantee", fontsize=7.2, color='#212529')

    # Save outputs
    out_dir = os.path.abspath("docs/report_figures")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "clearpay_architecture_flowchart.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Flowchart successfully generated at: {out_path}")

if __name__ == "__main__":
    generate_flowchart()
