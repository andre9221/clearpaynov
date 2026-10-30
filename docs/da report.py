import os
import sys
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_report():
    doc = docx.Document()

    # Standard academic publication margins (1.0 inch all sides)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # Base Normal style configured to Times New Roman 12pt Black
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # Styling helpers for XML tables and borders
    def set_cell_background(cell, hex_color):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        cell._tc.get_or_add_tcPr().append(tcMar)

    def set_table_borders(table, color="888888", sz="6", val="single"):
        tblBorders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="{val}" w:sz="4" w:space="0" w:color="CCCCCC"/>'
            f'<w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        table._tbl.tblPr.append(tblBorders)

    # Journal Heading Formats (Main = 16pt, Sub = 14pt, Sub-sub = 12pt)
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(30, 30, 30)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(50, 50, 50)
        return p

    def add_p(text, bold_prefix=None, space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = align
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(12)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(0, 0, 0)
        r_txt = p.add_run(text)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(12)
        r_txt.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(12)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(0, 0, 0)
        r_txt = p.add_run(text)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(12)
        r_txt.font.color.rgb = RGBColor(0, 0, 0)
        return p

    # Resolve image directory robustly
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(curr_dir, "report_figures"),
        os.path.join(curr_dir, "..", "report_figures"),
        os.path.abspath("report_figures")
    ]
    report_figures_dir = next((c for c in candidates if os.path.isdir(c)), os.path.abspath("report_figures"))

    def add_figure(img_filename, caption_text, width_inches=5.9):
        img_path = os.path.join(report_figures_dir, img_filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            run_img = p_img.add_run()
            run_img.add_picture(img_path, width=Inches(width_inches))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(11)
            p_cap.paragraph_format.keep_with_next = False
            
            # Format caption cleanly: "Figure X. " in Bold, followed by description in Italic
            parts = caption_text.split(". ", 1)
            if len(parts) == 2:
                r1 = p_cap.add_run(parts[0] + ". ")
                r1.font.name = 'Times New Roman'
                r1.font.size = Pt(10.5)
                r1.font.bold = True
                r1.font.color.rgb = RGBColor(30, 30, 30)

                r2 = p_cap.add_run(parts[1])
                r2.font.name = 'Times New Roman'
                r2.font.size = Pt(10.5)
                r2.font.italic = True
                r2.font.color.rgb = RGBColor(40, 40, 40)
            else:
                r = p_cap.add_run(caption_text)
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 30, 30)
        else:
            print(f"Warning: Image {img_path} not found!")

    # =========================================================================
    # FRONT COVER PAGE
    # =========================================================================
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(20)
    p_logo.paragraph_format.space_after = Pt(10)
    logo_path = os.path.join(report_figures_dir, "vit_logo.png")
    if os.path.exists(logo_path):
        run_l = p_logo.add_run()
        run_l.add_picture(logo_path, width=Inches(3.3))

    p_sch = doc.add_paragraph()
    p_sch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sch.paragraph_format.space_after = Pt(3)
    r_sch = p_sch.add_run("School of Computer Science and Engineering")
    r_sch.font.name = 'Times New Roman'
    r_sch.font.size = Pt(16)
    r_sch.font.bold = True
    r_sch.font.color.rgb = RGBColor(0, 0, 0)

    p_crse = doc.add_paragraph()
    p_crse.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_crse.paragraph_format.space_after = Pt(3)
    r_crse = p_crse.add_run("Course code:BCSE355L Course Name: Cloud Architecture Design")
    r_crse.font.name = 'Times New Roman'
    r_crse.font.size = Pt(13)
    r_crse.font.bold = True
    r_crse.font.color.rgb = RGBColor(40, 40, 40)

    p_da = doc.add_paragraph()
    p_da.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_da.paragraph_format.space_after = Pt(26)
    r_da = p_da.add_run("Direct Assessment III: Max Marks: 10")
    r_da.font.name = 'Times New Roman'
    r_da.font.size = Pt(14)
    r_da.font.bold = True
    r_da.font.color.rgb = RGBColor(0, 0, 0)

    # Title block
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_after = Pt(6)
    r_tit = p_tit.add_run("ClearPay")
    r_tit.font.name = 'Times New Roman'
    r_tit.font.size = Pt(28)
    r_tit.font.bold = True
    r_tit.font.color.rgb = RGBColor(0, 0, 0)

    p_subtit = doc.add_paragraph()
    p_subtit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subtit.paragraph_format.space_after = Pt(32)
    r_subtit = p_subtit.add_run("Liquidity-Aware, Fault-Tolerant Payment Clearing and Settlement on AWS Serverless")
    r_subtit.font.name = 'Times New Roman'
    r_subtit.font.size = Pt(15)
    r_subtit.font.bold = True
    r_subtit.font.color.rgb = RGBColor(50, 50, 50)

    # Team members reg Id, Name:
    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_after = Pt(5)
    r_by = p_by.add_run("Team members reg Id, Name:")
    r_by.font.name = 'Times New Roman'
    r_by.font.size = Pt(13)
    r_by.font.bold = True
    r_by.font.color.rgb = RGBColor(60, 60, 60)

    p_mem1 = doc.add_paragraph()
    p_mem1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mem1.paragraph_format.space_after = Pt(2)
    r_mem1 = p_mem1.add_run("24BCE1142, Andrea A")
    r_mem1.font.name = 'Times New Roman'
    r_mem1.font.size = Pt(14)
    r_mem1.font.bold = True
    r_mem1.font.color.rgb = RGBColor(0, 0, 0)

    p_mem2 = doc.add_paragraph()
    p_mem2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mem2.paragraph_format.space_after = Pt(22)
    r_mem2 = p_mem2.add_run("24BCE1400, Viswanadham Venkata Mrinalini")
    r_mem2.font.name = 'Times New Roman'
    r_mem2.font.size = Pt(14)
    r_mem2.font.bold = True
    r_mem2.font.color.rgb = RGBColor(0, 0, 0)

    p_fac = doc.add_paragraph()
    p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fac.paragraph_format.space_after = Pt(3)
    r_fac = p_fac.add_run("Faculty Guide: Dr. S. Vigneshwari")
    r_fac.font.name = 'Times New Roman'
    r_fac.font.size = Pt(13)
    r_fac.font.bold = True
    r_fac.font.color.rgb = RGBColor(40, 40, 40)

    p_dt = doc.add_paragraph()
    p_dt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dt.paragraph_format.space_after = Pt(12)
    r_dt = p_dt.add_run("October - 2026")
    r_dt.font.name = 'Times New Roman'
    r_dt.font.size = Pt(12)
    r_dt.font.color.rgb = RGBColor(80, 80, 80)

    doc.add_page_break()

    # Configure running headers from page 2 onwards
    section_body = doc.sections[0]
    section_body.different_first_page_header_footer = True
    header = section_body.header
    p_head = header.paragraphs[0]
    p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_h = p_head.add_run("BCSE355L: Cloud Architecture Design | Direct Assessment III | ClearPay")
    r_h.font.name = 'Times New Roman'
    r_h.font.size = Pt(9)
    r_h.font.color.rgb = RGBColor(120, 120, 120)

    # =========================================================================
    # EXECUTIVE DOCUMENT INDEX / TABLE OF CONTENTS
    # =========================================================================
    add_h1("Report Structure & Table of Contents")
    add_p("This report is structured according to the official VIT BCSE355L Direct Assessment III reporting specifications, indexed and numbered sequentially as follows:")

    toc_items = [
        ("Section Number & Title", "Content & Technical Coverage"),
        ("1. Title", "Formal project nomenclature, scope, and cloud architecture domain."),
        ("2. Abstract", "Executive technical summary: problem context, AWS serverless design, algorithmic novelty, and empirical findings."),
        ("3. Problem statement:", "Systemic challenges in RTGS and multilateral netting: all-or-nothing failure, cycle deadlocks, and retry hazards."),
        ("4. Highlights of your project/Novelty:", "10 distinct engineering contributions spanning BCGR, HSC, starvation-free aging, and deterministic AWS persistence."),
        ("5. Dataset Link:", "Stanford SNAP Bitcoin OTC, Bitcoin Alpha, and Ethereum Stablecoin ERC-20 transfer network specifications and citations."),
        ("6. Project demo link:", "Live Streamlit interactive fintech dashboard, hosted deployment guide, and operational instructions."),
        ("7. GitHub repository link:", "Public GitHub repository, formal citations, and architectural directory layout."),
        ("8. Architecture Diagram:", "Six-tier AWS serverless event-driven architecture (Figure 1) and persistence data model (Table 1)."),
        ("9. Screenshots:", "Sequential live execution proofs across 3 production scenarios on AWS ap-south-1 (Figures 2 through 31)."),
        ("10. Results:", "Algorithmic benchmarks on Stanford SNAP data (Table 2, Figure 32), live AWS validation (Table 3), and Free Tier cost analysis."),
        ("11. Conclusion:", "Summary of research outcomes, operational guarantees, limitations, and future research directions."),
        ("12. References (with DOI or weblink):", "30 formally formatted academic and engineering citations with active DOIs and web links."),
        ("13. Appendix: Research Paper link:", "Links to complete research papers, supplementary Word document, and 170 automated test suite breakdown.")
    ]

    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_toc)

    for r_idx, row in enumerate(toc_items):
        for c_idx, val in enumerate(row):
            cell = t_toc.cell(r_idx, c_idx)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            if r_idx == 0:
                set_cell_background(cell, "2B2B2B")
                run.font.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                bg = "F9F9F9" if r_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(0, 0, 0)
                if c_idx == 0:
                    run.font.bold = True

    t_toc.columns[0].width = Inches(2.6)
    t_toc.columns[1].width = Inches(3.9)

    doc.add_page_break()

    # =========================================================================
    # SECTION 1: TITLE
    # =========================================================================
    add_h1("1. Title")
    add_p("ClearPay: Liquidity-Aware, Fault-Tolerant Payment Clearing and Settlement on AWS Serverless", bold_prefix="Project Title: ")

    # =========================================================================
    # SECTION 2: ABSTRACT
    # =========================================================================
    add_h1("2. Abstract")
    add_p(
        "Modern interbank financial systems process millions of payment transactions daily through high-value Real-Time Gross Settlement (RTGS) networks and scheduled multilateral netting batches. In conventional settlement designs, batch multilateral netting enforces an all-or-nothing execution rule: if even a single participating financial institution lacks the liquidity deposit to back its net debit obligation, the entire batch is halted and aborted. This structural vulnerability leads to systemic gridlock, cascades liquidity friction across unaffected banks, and delays counterparty settlements. Furthermore, circular payment chains (where Bank A pays Bank B, Bank B pays Bank C, and Bank C pays Bank A) deadlock under conventional heuristics because each payment appears individually infeasible when judged in isolation, despite netting to zero net debit in aggregate. In addition, distributed cloud execution during network partitions or compute retries introduces the severe operational risk of duplicate debits on the ledger."
    )
    add_p(
        "To resolve these foundational vulnerabilities, this project presents ClearPay, a production-grade, fault-tolerant, liquidity-aware payment clearing and settlement engine engineered entirely on Amazon Web Services (AWS) serverless architecture. ClearPay couples event-driven microservices—implemented using AWS Lambda (Python 3.12, arm64 Graviton architecture), Amazon API Gateway HTTP API, Amazon DynamoDB, Amazon Simple Queue Service (SQS) with Dead-Letter Queues (DLQ), Amazon S3, and AWS Step Functions state machines—with five rigorous settlement optimization algorithms: All-or-Nothing baseline, Greedy Cumulative baseline, Removal Heuristic (RH) baseline, and two novel contributions: Bounded-Cycle Gridlock Repair (BCGR) and Topology Hub-Spoke Clearing (HSC)."
    )
    add_p(
        "ClearPay freezes every approved settlement plan with an immutable SHA-256 cryptographic hash and writes ledger entries using deterministic composite primary keys, ensuring strict idempotency and zero double-debit risk during cloud retries. Automated ledger-to-bank statement reconciliation is achieved through an event-driven S3 Lambda that instantaneously detects duplicate entries, amount mismatches, and counterparty omissions. Validated on real-world transaction graphs from the Stanford Network Analysis Project (SNAP)—including the Bitcoin OTC network (5,881 traders, 35,592 edges), Bitcoin Alpha network (3,783 traders, 24,186 edges), and Ethereum Stablecoin ERC-20 transfer network ($1.03B gross volume across USDT, USDC, and DAI)—under extreme liquidity stress (alpha = 0.10), All-or-Nothing completely deadlocked (clearing 0 payments, 0.0% value), while RH cleared 233 payments and BCGR cleared 236 payments (62.3% value) in just 27.5 milliseconds. ClearPay was deployed in AWS Asia Pacific (Mumbai, ap-south-1) and comprehensively verified through an interactive Streamlit operator dashboard across three production scenarios: normal settlement, insufficient liquidity protection, and circular gridlock release. All 170 automated test suites pass, zero balance overdrafts occur, and the deployment incurs $0.00 cloud cost, operating entirely within the AWS Free Tier."
    )

    # =========================================================================
    # SECTION 3: PROBLEM STATEMENT
    # =========================================================================
    add_h1("3. Problem statement:")
    add_p(
        "Interbank clearinghouses and central banking infrastructures face critical computational and architectural bottlenecks in processing high-throughput payment batches under tight intraday liquidity constraints. Specifically, standard clearing engines suffer from four systemic points of failure:"
    )
    add_bullet(
        " Conventional multilateral netting schemes operate on an all-or-nothing policy. If any single bank experiences a liquidity shortfall (e.g., Bank A owes INR 100 but possesses only INR 10 in central clearing deposits), the entire batch must be deferred. Consequently, hundreds of completely solvent banks with offsetting claims are penalized and blocked. On real-world financial transaction data, all-or-nothing netting settles 0.0% of the total transaction value under tight liquidity conditions.",
        bold_prefix="3.1 The All-or-Nothing Batch Netting Dilemma: "
    )
    add_bullet(
        " In heavy financial networks, transactions frequently form circular dependency cycles (e.g., Bank A owes Bank B INR 1,120, Bank B owes Bank C INR 1,120, and Bank C owes Bank A INR 1,120). The net cash required to settle this entire cycle is exactly zero. However, because each bank’s standalone balance is lower than INR 1,120, conventional greedy or single-pass clearing engines judge every leg of the cycle as infeasible and reject all three payments, causing unnecessary payment gridlock.",
        bold_prefix="3.2 Circular Dependency Deadlocks in Interbank Obligations: "
    )
    add_bullet(
        " Order-dependent greedy heuristic algorithms settle payments sequentially based on queue arrival or gross amount. Under constrained liquidity, greedy admission settles only 16.8% of value because early large payments prematurely exhaust deposits. Although the removal heuristic performs better (settling 60.2%), it lacks graph-topological awareness and is incapable of extracting and executing circular credit cycles.",
        bold_prefix="3.3 Myopic Heuristic Degradation & Suboptimality: "
    )
    add_bullet(
        " In modern distributed cloud environments, transient network failures, step timeouts, and Lambda retries create the hazard of double-debiting bank accounts. If a settlement transaction fails midway, retrying without deterministic idempotency keys can debit an account twice or corrupt financial balances. Furthermore, manual reconciliation between clearing ledgers and external bank statements remains slow, error-prone, and labor-intensive.",
        bold_prefix="3.4 Distributed Cloud Execution Hazards and Reconciliation Bottlenecks: "
    )
    add_p(
        "The clear research and engineering gap addressed by ClearPay is the absence of an ultra-lightweight, serverless-native payment clearing engine that dynamically selects the maximal feasible subset of payments, automatically repairs circular deadlocks without extra cash injections, guarantees mathematical balance conservation, and enforces idempotent fault tolerance across transient cloud failures."
    )

    # =========================================================================
    # SECTION 4: HIGHLIGHTS OF YOUR PROJECT / NOVELTY
    # =========================================================================
    add_h1("4. Highlights of your project/Novelty:")
    add_p("The ClearPay system introduces fundamental architectural and algorithmic innovations over legacy clearing systems:")
    add_bullet(
        " Unlike conventional batch netting that aborts completely when a bank falls short, ClearPay implements a remove-and-add-back heuristic that extracts the largest mathematically feasible subset of payments within each bank’s available deposit balance, allowing solvent obligations to settle immediately.",
        bold_prefix="4.1 Liquidity-Aware Partial Settlement Engine: "
    )
    add_bullet(
        " ClearPay implements a novel cycle-detection and resolution pass that analyzes the set of deferred/rejected payments, identifies closed credit loops (2-bank bilateral cycles and 3-bank multilateral triangles), and clears them atomically with zero additional cash requirement. On the Bitcoin OTC network under tight liquidity, BCGR rescued 3 additional payments (+2.1 percentage points of settled value) and executed faster (27.5 ms vs 29.7 ms) than standard removal heuristics.",
        bold_prefix="4.2 Bounded-Cycle Gridlock Repair (BCGR - Novel Contribution): "
    )
    add_bullet(
        " ClearPay introduces an adaptive k-core graph decomposition algorithm with automatic elbow detection to partition the interbank transaction network into high-degree core hub banks and peripheral spoke banks. Clearing hub-to-hub payment volume in an isolated fast-path stage executes in only 4.12 ms, making it an ideal pre-processing filter for high-frequency clearing windows.",
        bold_prefix="4.3 Topology-Aware Hub-Spoke Clearing (HSC - Novel Contribution): "
    )
    add_bullet(
        " To prevent smaller community banks or low-value payments from being chronically starved by high-volume institutions, ClearPay introduces a multi-objective dynamic utility function U(p) = w(p) * (1 + lambda * deferral_count). Every deferred payment gains escalating priority weight across subsequent windows, guaranteeing starvation-free fairness.",
        bold_prefix="4.4 Starvation-Free Aging Priority Multi-Objective Optimization: "
    )
    add_bullet(
        " Every calculated settlement plan is cryptographically fingerprinted using a SHA-256 hash and stored in Amazon S3 as an immutable record. All DynamoDB double-entry ledger rows use deterministic composite primary keys (window_id#payment_id#D/C), and payment_id serves as an idempotency token. Any AWS Step Functions retry executes safely without duplicate ledger postings.",
        bold_prefix="4.5 Double-Debit Immune Settlement and Deterministic Ledger Keys: "
    )
    add_bullet(
        " ClearPay deploys an automated reconciliation Lambda function connected to S3 object-creation events. Uploading external bank statements triggers an automated three-way audit that flags duplicate debits, transaction value discrepancies, and un-netted obligations. Testing with intentionally injected anomalies confirmed 100% anomaly detection.",
        bold_prefix="4.6 Event-Driven Automated Three-Way Cloud Reconciliation: "
    )
    add_bullet(
        " Supports both real-time individual payment posting via Amazon SQS with DLQ isolation (Mode 0) and scheduled batch multilateral netting via AWS Step Functions (Mode 1), catering to both retail micro-transfers and wholesale interbank clearing.",
        bold_prefix="4.7 Dual-Mode Operational Engine (Real-Time + Scheduled Batch): "
    )
    add_bullet(
        " ClearPay was benchmarked exclusively on real-world transaction data from the Stanford Network Analysis Project (SNAP)—Bitcoin OTC, Bitcoin Alpha, and Ethereum Stablecoin ERC-20 transfers ($1.03 Billion gross volume)—without any artificial or synthetic assumptions.",
        bold_prefix="4.8 100% Real-World Dataset Validation (Zero Synthetic Data): "
    )
    add_bullet(
        " Full production deployment in AWS Asia Pacific (Mumbai, ap-south-1) region using AWS SAM and CloudFormation. All services (Lambda, DynamoDB, API Gateway, SQS, S3, Step Functions) operate completely within the AWS Free Tier, achieving a projected ongoing operational cost of $0.00/month.",
        bold_prefix="4.9 Production AWS Serverless Deployment with Free Tier Compliance: "
    )
    add_bullet(
        " All financial amounts are processed as exact integer paise (1 INR = 100 paise) to eliminate IEEE 754 floating-point rounding errors. A comprehensive test harness of 170 automated test suites (with 66 core liquidity & novel engine tests) guarantees 100% code coverage, zero balance overdrafts, and formal balance conservation across all nodes.",
        bold_prefix="4.10 Exact Integer Arithmetic and 100% Test Coverage Suite: "
    )

    # =========================================================================
    # SECTION 5: DATASET LINK
    # =========================================================================
    add_h1("5. Dataset Link:(create DOI in zenodo if you got your own Dataset)-citation (Team member names followed by faculty name)")
    add_p(
        "To guarantee empirical validity and simulate real-world financial liquidity dynamics, ClearPay was validated exclusively against large-scale public financial transaction datasets provided by the Stanford Network Analysis Project (SNAP) at Stanford University. Because this investigation leverages established, open-access research benchmark networks rather than proprietary newly collected data, no external Zenodo DOI was created. Complete dataset links, properties, ingestion procedures, and formal citations are detailed below."
    )
    
    add_h2("5.1 Stanford SNAP Financial Benchmark Datasets")
    add_bullet(
        " A weighted signed transaction and trust network among users trading on Bitcoin OTC. Contains 5,881 unique trader accounts and 35,592 directed transaction edges spanning from November 2010 to January 2016. Each record contains source node, target node, edge rating/weight, and POSIX epoch timestamp. Link: https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html",
        bold_prefix="• Stanford SNAP Bitcoin OTC Network: "
    )
    add_bullet(
        " A weighted signed transaction network from the Bitcoin Alpha trading exchange. Contains 3,783 verified trader accounts and 24,186 directed financial edges. Link: https://snap.stanford.edu/data/soc-sign-bitcoin-alpha.html",
        bold_prefix="• Stanford SNAP Bitcoin Alpha Network: "
    )
    add_bullet(
        " High-value real-world smart contract transaction logs capturing token transfers for the top three decentralized stablecoins: Tether (USDT), USD Coin (USDC), and Dai (DAI). Encompasses 13,308 account addresses, 16,093 payment obligations, and over $1.03 Billion in gross transfer volume, accessed via the Stanford SNAP financial network collection. Link: https://snap.stanford.edu/data",
        bold_prefix="• Stanford SNAP Ethereum Stablecoin ERC-20 Transfer Network: "
    )

    add_h2("5.2 Dataset Ingestion & Liquidity Formulation in ClearPay")
    add_p(
        "The project repository incorporates these datasets directly under the 'data set/' directory (including 'soc-sign-bitcoinotc.csv.gz' and 'soc-sign-bitcoinalpha.csv.gz'). The ingestion adapter module 'src/common/dataset_adapter.py' translates these raw graph edges into ClearPay's native JSON payment queue schema:"
    )
    add_bullet(
        " Each directed edge (u -> v with rating/weight w and timestamp t) is normalized to a valid payment order: payment_id = OTC-{source}-{target}-{timestamp}, from_account = BANK_{source}, to_account = BANK_{target}, amount_paise = int(abs(weight) * 10000), currency = 'INR', status = 'PENDING'.",
        bold_prefix="• Payment Normalization: "
    )
    add_bullet(
        " To rigorously simulate tight liquidity stress in an interbank environment, the initial deposit balance of each participating bank is initialized as a fractional multiplier alpha of its gross outgoing payment obligations: Balance(i) = max(10000, int(alpha * sum(Amount(i -> j)))). Setting alpha = 0.10 establishes an extreme liquidity stress scenario where total bank deposits equal only 10% of gross obligations, triggering severe settlement competition.",
        bold_prefix="• Liquidity Multiplier Formulation: "
    )

    add_h2("5.3 Authentic Dataset Citation")
    add_p(
        "Because ClearPay evaluates performance on established open-access scientific benchmark networks created by Stanford University researchers rather than an internally generated dataset, external Zenodo DOI registration is not applicable. The official primary citations for the datasets used in this work are:",
        bold_prefix="Dataset Attribution Note: "
    )
    add_bullet(
        " S. Kumar, F. Spezzano, V. S. Subrahmanian, and C. Faloutsos, 'Edge weight prediction in weighted signed networks,' in 2016 IEEE 16th International Conference on Data Mining (ICDM), Barcelona, Spain, 2016, pp. 221-230. DOI: 10.1109/ICDM.2016.0033. (Official publication for the Stanford SNAP Bitcoin-OTC and Bitcoin-Alpha networks).",
        bold_prefix="Primary Dataset Research Citation: "
    )
    add_bullet(
        " J. Leskovec and A. Krevl, 'SNAP Datasets: Stanford Large Network Dataset Collection,' Stanford University, 2014. Available: https://snap.stanford.edu/data",
        bold_prefix="Dataset Repository Citation: "
    )
    add_p(
        "Experimental data pipeline adaptation, liquidity stress parameterization (alpha = 0.10 to 1.20), and benchmark execution conducted by: Andrea A (24BCE1142), Viswanadham Venkata Mrinalini (24BCE1400), under the academic supervision of Dr. S. Vigneshwari (Faculty), School of Computer Science and Engineering, VIT Chennai.",
        bold_prefix="Project Experimental Evaluation: "
    )

    # =========================================================================
    # SECTION 6: PROJECT DEMO LINK
    # =========================================================================
    add_h1("6. Project demo link:(if any)")
    add_p(
        "ClearPay features a fully integrated, interactive web-based operator dashboard built with Streamlit ('app.py') that connects directly to the live AWS Asia Pacific (Mumbai, ap-south-1) cloud environment."
    )
    add_bullet(
        " The Streamlit dashboard can be launched locally in a single command using: 'streamlit run app.py'. The web application initializes at 'http://localhost:8503' and connects seamlessly to the live AWS cloud stack using AWS IAM credentials (configured via 'clearpay-andrea' AWS CLI profile).",
        bold_prefix="6.1 Local Live Dashboard Host: "
    )
    add_bullet(
        " Project demonstration video walk-through and hosted dashboard documentation link: https://github.com/Mrinalini10/clearpay_novel_final/blob/main/docs/DEPLOYMENT.md (hosted web deployment available via Streamlit Community Cloud).",
        bold_prefix="6.2 Demonstration Video & Hosted Guide: "
    )
    add_bullet(
        " The entire execution sequence—spanning client preflight checks, batch payment submission to API Gateway, DynamoDB status transitions, Step Functions workflow execution, S3 plan verification, and balance conservation audits—is thoroughly documented with step-by-step visual proofs in the Screenshots section of this report.",
        bold_prefix="6.3 Complete Cloud Traceability: "
    )

    # =========================================================================
    # SECTION 7: GITHUB REPOSITORY LINK
    # =========================================================================
    add_h1("7. GitHub repository link: (with citation (Team member names followed by faculty name, Title of the project))")
    add_p("https://github.com/Mrinalini10/clearpay_novel_final", bold_prefix="Repository URL: ")
    add_p(
        "Citation: Andrea A, Viswanadham Venkata Mrinalini, Dr. S. Vigneshwari, ClearPay: Liquidity-Aware, Fault-Tolerant Payment Clearing and Settlement on AWS Serverless, GitHub repository, 2026. Available: https://github.com/Mrinalini10/clearpay_novel_final",
        bold_prefix="Formal Citation: "
    )
    add_p(
        "The ClearPay repository is structured as a production-grade AWS serverless codebase containing complete source code, automated test harnesses, benchmark pipelines, and deployment templates:"
    )
    add_bullet(
        " Ingestion Lambda (ingest.py), payment status reader (get_payment.py), real-time ledger poster (poster.py), pending payment collector (collect.py), netting and liquidity optimizer (net.py), settlement committer (finalize.py), and automated reconciliation auditor (reconcile.py).",
        bold_prefix="• src/handlers/: "
    )
    add_bullet(
        " Core mathematical settlement algorithms including liquidity-aware removal heuristic (liquidity.py), novel BCGR and HSC algorithms (topology_liquidity.py), Stanford SNAP real-world dataset adapter (dataset_adapter.py), multilateral netting matrix engine (netting.py), three-way reconciliation (recon.py), and data validation utilities (validation.py).",
        bold_prefix="• src/common/: "
    )
    add_bullet(
        " Automated empirical benchmarking suites (benchmark_suite.py) and matplotlib visualization generators (plot_results.py) comparing execution latency, cleared payment counts, and settled values across varying liquidity alphas.",
        bold_prefix="• benchmark/: "
    )
    add_bullet(
        " 170 comprehensive automated test suites (with 66 core liquidity and novel engine tests) covering unit tests, property-based tests, failure-recovery simulations, and integration checks.",
        bold_prefix="• tests/: "
    )
    add_bullet(
        " Interactive Streamlit dashboard for real-time AWS stack orchestration and verification.",
        bold_prefix="• app.py: "
    )
    add_bullet(
        " Complete Infrastructure-as-Code (IaC) templates for automated CloudFormation stack provisioning in AWS ap-south-1.",
        bold_prefix="• template.yaml & template-liquidity-workflow.yaml: "
    )

    # =========================================================================
    # SECTION 8: ARCHITECTURE DIAGRAM
    # =========================================================================
    add_h1("8. Architecture Diagram:")
    add_p(
        "ClearPay is engineered on AWS serverless services in the Asia Pacific (Mumbai, ap-south-1) region. The architecture implements an event-driven, decoupled design that isolates payment ingestion, real-time single payments, scheduled multilateral batch netting, and automated statement reconciliation."
    )
    add_figure("Figure_1.png", "Figure 1. ClearPay serverless architecture on AWS (ap-south-1).", width_inches=6.1)
    
    add_p(
        "The deployed architecture operates through six coordinated tiers as depicted in Figure 1:"
    )
    add_bullet(
        " Clients and bank operators submit payments via POST /payments and query payment status via GET /payments/{payment_id}. The API Gateway is throttled to 50 requests per second and protected by an API key header (x-api-key). IngestFunction validates schemas, verifies positive integer paise, enforces idempotency, and persists the payment into DynamoDB PaymentsTable with status PENDING.",
        bold_prefix="8.1 Ingestion Tier (API Gateway + Ingest Lambda): "
    )
    add_bullet(
        " For high-priority retail payments requiring immediate real-time posting, payments pass through an Amazon SQS standard queue (visibility timeout 180s, maxReceiveCount 3) to PosterFunction. PosterFunction executes atomic DynamoDB TransactWriteItems to debit the sender, credit the receiver, and update payment status to SETTLED. Persistent failures are automatically isolated into a Dead-Letter Queue (DLQ) with 14-day retention.",
        bold_prefix="8.2 Real-Time Posting Tier (SQS + DLQ + Poster Lambda): "
    )
    add_bullet(
        " Interbank batch netting is coordinated by an AWS Step Functions state machine (LiquiditySettlementStateMachine). The workflow executes in distinct phases: (a) CollectPending Lambda snapshots all pending payments and active bank balances, (b) AnyPending? Choice state verifies whether eligible payments exist, (c) SettlePending Lambda runs the liquidity-aware optimization engine (Removal Heuristic + BCGR / HSC), generates a deterministic settlement plan, and computes net debit positions, and (d) FinalizeSettlement executes atomic balance updates and commits ledger entries.",
        bold_prefix="8.3 Batch Settlement State Machine Tier (AWS Step Functions): "
    )
    add_bullet(
        " S3DataBucket maintains complete audit immutability. The window snapshot is saved under 'windows/{window_id}/payments.json', and the approved plan is frozen under 'windows/{window_id}/approved_plan.json' with a SHA-256 plan hash.",
        bold_prefix="8.4 Immutable Plan Storage Tier (Amazon S3): "
    )
    add_bullet(
        " External bank statements uploaded to 'statements/' automatically trigger ReconcileFunction via S3 ObjectCreated events. The function performs a three-way reconciliation against the DynamoDB ledger, flagging duplicate transactions, missing entries, and amount discrepancies.",
        bold_prefix="8.5 Automated Reconciliation Tier (S3 Event Notifications + Reconcile Lambda): "
    )
    add_bullet(
        " Structured around four purpose-built DynamoDB tables configured with on-demand capacity and server-side encryption.",
        bold_prefix="8.6 Persistent Database Tier (Amazon DynamoDB): "
    )

    # Table 1: Data model
    add_h2("8.7 ClearPay Cloud Data Model")
    add_p("The schema, primary keys, and roles of the DynamoDB tables and S3 resources are summarized in Table 1:")

    table_data = [
        ("Resource", "Partition Key (PK)", "Sort Key (SK) / Details", "Purpose & Architectural Role"),
        ("PaymentsTable", "payment_id (String)", "GSI: StatusPostedIndex", "Maintains payment lifecycle status (PENDING, SETTLED, DEFERRED) and payment metadata."),
        ("AccountsTable", "account_id (String)", "None", "Stores authoritative bank liquidity balances held as integer paise (balance_paise)."),
        ("LedgerTable", "account_id (String)", "entry_id = window#payment#D|C", "Double-entry accounting ledger recording atomic debit and credit rows for every transfer."),
        ("SettlementsTable", "window_id (String)", "None", "Per-window settlement execution state, algorithm parameters, and summary statistics."),
        ("S3 DataBucket", "S3 Bucket: clearpay-data-134748918128", "windows/{id}/*, statements/*", "Stores window snapshots, cryptographic SHA-256 plans, and external reconciliation statements."),
        ("SQS + DLQ", "Amazon SQS Queues", "Visibility 180s, DLQ 3 retries", "Buffers real-time payment ingestion and isolates corrupted or failing messages.")
    ]

    t1 = doc.add_table(rows=len(table_data), cols=4)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = t1.cell(r_idx, c_idx)
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            if r_idx == 0:
                set_cell_background(cell, "2B2B2B")
                run.font.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                bg = "F9F9F9" if r_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(0, 0, 0)

    col_widths = [Inches(1.4), Inches(1.5), Inches(1.6), Inches(2.0)]
    for row in t1.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    p_cap_t1 = doc.add_paragraph()
    p_cap_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_t1.paragraph_format.space_before = Pt(4)
    p_cap_t1.paragraph_format.space_after = Pt(14)
    r_ct1_label = p_cap_t1.add_run("Table 1. ")
    r_ct1_label.font.name = 'Times New Roman'
    r_ct1_label.font.size = Pt(10.5)
    r_ct1_label.font.bold = True
    r_ct1_label.font.color.rgb = RGBColor(30, 30, 30)
    r_ct1_desc = p_cap_t1.add_run("Data model and persistence layout of the ClearPay AWS serverless stack.")
    r_ct1_desc.font.name = 'Times New Roman'
    r_ct1_desc.font.size = Pt(10.5)
    r_ct1_desc.font.italic = True
    r_ct1_desc.font.color.rgb = RGBColor(40, 40, 40)

    # =========================================================================
    # SECTION 9: SCREENSHOTS
    # =========================================================================
    add_h1("9. Screenshots:")
    add_p(
        "This section presents the complete live cloud execution traces captured directly from the deployed AWS stack in Asia Pacific (Mumbai, ap-south-1). The screenshots follow every stage of transaction processing across API Gateway, Lambda, DynamoDB, SQS, Step Functions, S3, and the Streamlit operator dashboard across three distinct production scenarios:"
    )
    add_bullet("Scenario 1: Normal Payments Execution (Three solvent interbank transfers settled and balanced atomically).")
    add_bullet("Scenario 2: Insufficient Liquidity Protection (A payment exceeding sender's balance is safely deferred with zero overdraft).")
    add_bullet("Scenario 3: Circular Gridlock Resolution (A closed 3-bank dependency cycle settled atomically with zero net cash via BCGR).")

    # SCENARIO 1
    add_h2("9.1 Scenario 1: Normal Payments Execution")
    add_p(
        "Stage 1: Preflight Connection & Batch Preparation in Streamlit Dashboard. The operator dashboard confirms active connectivity to AWS ap-south-1 and reads initial balances from DynamoDB AccountsTable: Bank A holds INR 973.00, Bank B holds INR 1,009.00, and Bank C holds INR 1,018.00, totaling exactly INR 3,000.00."
    )
    add_figure("Figure_2.png", "Figure 2. Dashboard preflight confirming AWS connection and live DynamoDB balances in ap-south-1.", width_inches=5.9)

    add_p(
        "The operator selects the 'Normal payments' test case consisting of three offsetting obligations: Bank A pays Bank B INR 10.00, Bank B pays Bank C INR 7.00, and Bank C pays Bank A INR 5.00. The batch is submitted to AWS."
    )
    add_figure("Figure_3.png", "Figure 3. Normal payments test batch prepared and submitted from the dashboard.", width_inches=5.9)

    add_p(
        "Stage 2: Amazon API Gateway Ingestion. API Gateway exposes RESTful routes POST /payments and GET /payments/{payment_id}. Submitting the batch invokes IngestFunction with client idempotency tokens."
    )
    add_figure("Figure_4.png", "Figure 4. Amazon API Gateway HTTP API console routing payments to Lambda.", width_inches=5.9)

    add_p(
        "Each payment is validated, accepted, and assigned status PENDING with a unique run ID. No balances have moved at this stage."
    )
    add_figure("Figure_5.png", "Figure 5. API Gateway response showing payments accepted with status PENDING.", width_inches=5.9)

    add_p(
        "Stage 3: AWS Lambda Functions & Least-Privilege IAM Roles. The AWS Lambda console displays all deployed serverless functions (ingest, get_payment, poster, collect, net, finalize, reconcile) executing on Python 3.12."
    )
    add_figure("Figure_6.png", "Figure 6. Deployed serverless microservice Lambda functions in AWS ap-south-1.", width_inches=5.9)

    add_p(
        "Each Lambda operates under a dedicated least-privilege IAM execution role restricting DynamoDB and S3 access strictly to required table ARNs."
    )
    add_figure("Figure_7.png", "Figure 7. IAM least-privilege execution role policies for IngestFunction.", width_inches=5.9)

    add_p(
        "Stage 4: DynamoDB Persistent Storage. The DynamoDB console confirms the four provisioned tables (PaymentsTable, AccountsTable, LedgerTable, SettlementsTable)."
    )
    add_figure("Figure_8.png", "Figure 8. Persistent DynamoDB tables provisioned by AWS SAM CloudFormation.", width_inches=5.9)

    add_p(
        "Querying PaymentsTable reveals the newly ingested batch records stored with status PENDING before settlement initiation."
    )
    add_figure("Figure_9.png", "Figure 9. PaymentsTable query confirming demo batch stored with status PENDING.", width_inches=5.9)

    add_p(
        "Stage 5: Amazon SQS Queue & Dead-Letter Queue (DLQ). The PaymentsQueue handles real-time Mode 0 transfers, backed by PaymentsDLQ with maxReceiveCount = 3."
    )
    add_figure("Figure_10.png", "Figure 10. Amazon SQS PaymentsQueue and Dead-Letter Queue (DLQ) in AWS console.", width_inches=5.9)

    add_p(
        "Stage 6: AWS Step Functions Settlement Orchestration. The operator initiates cloud settlement by triggering LiquiditySettlementStateMachine."
    )
    add_figure("Figure_11.png", "Figure 11. Triggering batch settlement state machine from operator dashboard.", width_inches=5.9)

    add_p(
        "The Step Functions console displays the complete execution history, showing the active dashboard-initiated execution run."
    )
    add_figure("Figure_12.png", "Figure 12. LiquiditySettlementStateMachine execution history in AWS Step Functions.", width_inches=5.9)

    add_p(
        "The visual execution graph tracks the workflow progression through CollectPending, AnyPending?, and SettlePending Lambda tasks."
    )
    add_figure("Figure_13.png", "Figure 13. Step Functions visual state transition graph and event log of successful run.", width_inches=5.9)

    add_p(
        "The workflow concludes with status SUCCEEDED. The dashboard reports 3/3 payments settled, 0 deferred, 3/3 ledger checks verified, and balance conservation PASS."
    )
    add_figure("Figure_14.png", "Figure 14. Step Functions execution SUCCEEDED with 3/3 settled and balance conservation PASS.", width_inches=5.9)

    add_p(
        "Stage 7: S3 Storage and DynamoDB Settlement Commitment. S3 DataBucket stores the window snapshot and frozen SHA-256 approved plan."
    )
    add_figure("Figure_15.png", "Figure 15. Amazon S3 bucket storing settlement window snapshots and frozen plans.", width_inches=5.9)

    add_p(
        "Querying PaymentsTable confirms that all three payments have transitioned from PENDING to SETTLED with settled_at timestamps and window_id associations."
    )
    add_figure("Figure_16.png", "Figure 16. PaymentsTable records updated to status SETTLED following state machine execution.", width_inches=5.9)

    add_p(
        "Stage 8: Dashboard Verification and Double-Entry Ledger Validation. The dashboard cross-verifies cloud records: Bank A = INR 968.00 (-5), Bank B = INR 1,012.00 (+3), Bank C = INR 1,020.00 (+2). The sum remains exactly INR 3,000.00."
    )
    add_figure("Figure_17.png", "Figure 17. Final dashboard verification table confirming double-entry ledger entries and balance conservation.", width_inches=5.9)

    # SCENARIO 2
    add_h2("9.2 Scenario 2: Insufficient Liquidity and Overdraft Prevention")
    add_p(
        "Scenario 2 evaluates the engine's fault tolerance under severe liquidity deficit. Bank A (current balance INR 968.00) attempts to submit a transfer of INR 1,068.00 to Bank B. The payment exceeds Bank A's balance by INR 100.00 with no incoming transfers to offset it. ClearPay must safely defer the payment rather than allowing an unauthorized overdraft."
    )
    add_figure("Figure_18.png", "Figure 18. Insufficient liquidity test scenario: INR 1,068.00 payment from Bank A (balance INR 968.00).", width_inches=5.9)

    add_p(
        "The payment is submitted to API Gateway and accepted into PaymentsTable with status PENDING."
    )
    add_figure("Figure_19.png", "Figure 19. Payment submitted and confirmed with status PENDING.", width_inches=5.9)

    add_p(
        "DynamoDB PaymentsTable confirms the pending payment item prior to settlement execution."
    )
    add_figure("Figure_20.png", "Figure 20. DynamoDB PaymentsTable showing the un-settled INR 1,068.00 payment record.", width_inches=5.9)

    add_p(
        "Filtering by run ID verifies that amount_paise is stored as exactly 106,800 paise."
    )
    add_figure("Figure_21.png", "Figure 21. Payment item filtered in DynamoDB showing amount_paise = 106,800 and status PENDING.", width_inches=5.9)

    add_p(
        "Triggering settlement causes the engine to evaluate Bank A's shortfall. SettlePending defers the payment. The dashboard displays 0/1 settled and 1 deferred."
    )
    add_figure("Figure_22.png", "Figure 22. Step Functions execution completing with 0/1 settled and 1 payment deferred.", width_inches=5.9)

    add_p(
        "Inspection of the approved_plan.json object in S3 confirms that selected_ids is empty, deferred_ids contains the payment, and settled_pct is 0.0%."
    )
    add_figure("Figure_23.png", "Figure 23. S3 approved_plan.json demonstrating empty selected_ids and deferred payment ID.", width_inches=5.9)

    add_p(
        "The dashboard performs final audit checks: cloud decision is DEFER, DynamoDB status remains PENDING, exactly 0 ledger entries were written, and all three bank balances remain completely untouched (Bank A = INR 968.00, Bank B = INR 1,012.00, Bank C = INR 1,020.00). Overdraft is 100% prevented."
    )
    add_figure("Figure_24.png", "Figure 24. Verification panel confirming DEFER decision, zero ledger writes, and unchanged balances.", width_inches=5.9)

    # SCENARIO 3
    add_h2("9.3 Scenario 3: Circular Gridlock Resolution via BCGR")
    add_p(
        "Scenario 3 tests ClearPay's novel Bounded-Cycle Gridlock Repair (BCGR) algorithm. Three payments of INR 1,120.00 form a closed directed dependency cycle: Bank A owes Bank B INR 1,120.00, Bank B owes Bank C INR 1,120.00, and Bank C owes Bank A INR 1,120.00. Because each bank's balance (INR 968.00, INR 1,012.00, INR 1,020.00) is lower than INR 1,120.00, traditional single-pass heuristics reject all three payments. However, the net liquidity change for every bank is exactly zero."
    )
    add_figure("Figure_25.png", "Figure 25. Circular gridlock scenario: Three INR 1,120.00 payments forming a closed credit loop.", width_inches=5.9)

    add_p(
        "The three cyclic payments are submitted and recorded in PaymentsTable with status PENDING."
    )
    add_figure("Figure_26.png", "Figure 26. PaymentsTable displaying first cycle payment DEMO-5cb...-01 as PENDING.", width_inches=5.9)

    add_p(
        "DynamoDB confirms the second cycle payment DEMO-5cb...-02 is also stored as PENDING."
    )
    add_figure("Figure_27.png", "Figure 27. PaymentsTable displaying second cycle payment DEMO-5cb...-02 as PENDING.", width_inches=5.9)

    add_p(
        "When Step Functions runs, SettlePending first identifies that standard greedy selection cannot admit the payments. The BCGR module extracts the closed cycle from the deferred pool, verifies that net debit is zero across all nodes, and approves all three payments simultaneously. The execution finishes with SUCCEEDED."
    )
    add_figure("Figure_28.png", "Figure 28. Step Functions execution SUCCEEDED via BCGR cycle extraction and repair.", width_inches=5.9)

    add_p(
        "In DynamoDB PaymentsTable, all three circular payments transition to SETTLED without requiring any external liquidity injection."
    )
    add_figure("Figure_29.png", "Figure 29. PaymentsTable showing all three circular payments updated to SETTLED.", width_inches=5.9)

    add_p(
        "The window_id column confirms all three payments are linked to the same settlement window and frozen S3 plan."
    )
    add_figure("Figure_30.png", "Figure 30. DynamoDB window_id attribute linking settled cycle payments to approved S3 plan.", width_inches=5.9)

    add_p(
        "Final dashboard audit confirms: 3/3 payments settled, 0 deferred, 3/3 ledger checks verified (2 double-entry rows per payment), and balances remain identical at INR 968.00, INR 1,012.00, and INR 1,020.00. Total liquidity is perfectly conserved at INR 3,000.00."
    )
    add_figure("Figure_31.png", "Figure 31. Verification panel confirming successful 3/3 cycle clearing with zero net balance change.", width_inches=5.9)

    # =========================================================================
    # SECTION 10: RESULTS
    # =========================================================================
    add_h1("10. Results:")
    add_p(
        "ClearPay was subjected to comprehensive empirical benchmarking against real-world transaction graphs from the Stanford SNAP repository, followed by operational performance verification of the live AWS serverless stack."
    )

    add_h2("10.1 Benchmark on Real-World Financial Data (Stanford SNAP Bitcoin OTC)")
    add_p(
        "To evaluate settlement efficiency under liquidity stress, 300 sequential payment obligations from the Stanford SNAP Bitcoin OTC network were evaluated under extreme liquidity constraints (alpha = 0.10, indicating bank liquidity deposits equaled only 10% of gross obligations). Five distinct algorithms were compared:"
    )
    add_bullet("All-or-Nothing (Baseline): Legacy settlement rule where entire batch must settle or abort.")
    add_bullet("Greedy Cumulative (Baseline): Admits payments sequentially in queue order as long as balance constraints hold.")
    add_bullet("Removal Heuristic (RH - Baseline): Iteratively removes smallest offending payment from shortfall banks, then restores feasible obligations.")
    add_bullet("Bounded-Cycle Gridlock Repair (BCGR - Novel): Augments RH by detecting and resolving 2-bank and 3-bank cycles from deferred queues.")
    add_bullet("Topology Hub-Spoke Clearing (HSC - Novel): K-core elbow decomposition prioritizing high-degree core hubs.")

    # Insert Figure 32
    add_figure("Figure_32.png", "Figure 32. Payments cleared, settled value percentage, and execution runtime (ms) on Bitcoin OTC benchmark.", width_inches=6.1)

    # Table 2: Benchmark Results
    bench_data = [
        ("Algorithm", "Payments Cleared (of 300)", "Settled Value (%)", "Runtime (ms)", "Algorithmic Role"),
        ("All-or-Nothing", "0", "0.0%", "0.19 ms", "Legacy Baseline"),
        ("Greedy Cumulative", "82", "16.8%", "5.98 ms", "Standard Baseline"),
        ("Removal Heuristic (RH)", "233", "60.2%", "29.74 ms", "Heuristic Baseline"),
        ("BCGR (Proposed)", "236", "62.3%", "27.52 ms", "Novel Contribution"),
        ("Hub-Spoke Clearing (HSC)", "52", "10.0%", "4.12 ms", "Novel Fast-Path")
    ]

    t2 = doc.add_table(rows=len(bench_data), cols=5)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)

    for r_idx, row in enumerate(bench_data):
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx, c_idx)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            if r_idx == 0:
                set_cell_background(cell, "2B2B2B")
                run.font.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                bg = "F9F9F9" if r_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(0, 0, 0)

    col_widths2 = [Inches(1.8), Inches(1.3), Inches(1.2), Inches(1.1), Inches(1.1)]
    for row in t2.rows:
        for i, w in enumerate(col_widths2):
            row.cells[i].width = w

    p_cap_t2 = doc.add_paragraph()
    p_cap_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_t2.paragraph_format.space_before = Pt(4)
    p_cap_t2.paragraph_format.space_after = Pt(12)
    r_ct2_label = p_cap_t2.add_run("Table 2. ")
    r_ct2_label.font.name = 'Times New Roman'
    r_ct2_label.font.size = Pt(10.5)
    r_ct2_label.font.bold = True
    r_ct2_label.font.color.rgb = RGBColor(30, 30, 30)
    r_ct2_desc = p_cap_t2.add_run("Algorithmic benchmark results on Stanford SNAP Bitcoin OTC dataset (alpha = 0.10).")
    r_ct2_desc.font.name = 'Times New Roman'
    r_ct2_desc.font.size = Pt(10.5)
    r_ct2_desc.font.italic = True
    r_ct2_desc.font.color.rgb = RGBColor(40, 40, 40)

    add_p(
        "Key benchmark findings: (1) All-or-Nothing catastrophic failure: Because at least one bank experienced a deficit, All-or-Nothing aborted the entire batch, clearing 0 payments (0.0% value). (2) BCGR superiority: BCGR cleared 236 payments (62.3% value) in 27.52 ms, rescuing 3 additional payments (+2.1 percentage points) over RH while executing faster due to early cycle extraction. (3) HSC ultra-low latency: HSC executed in only 4.12 ms, validating its efficacy as a rapid pre-clearing stage."
    )

    # Table 3: Live AWS Scenarios
    add_h2("10.2 Live AWS Serverless Deployment Validation")
    add_p("Table 3 summarizes the empirical verification outcomes across the three live production scenarios executed on the deployed AWS stack:")

    aws_data = [
        ("Scenario", "Input Obligations", "Cloud Decision", "DynamoDB Status", "Ledger & Conservation Audit"),
        ("Normal Payments", "3 payments: 10.00, 7.00, 5.00 (A->B, B->C, C->A)", "All 3 settled", "3 SETTLED, 2 ledger entries each", "3/3 ledger verified, Balances: 968, 1012, 1020, Total: 3000 (PASS)"),
        ("Insufficient Liquidity", "1 payment: 1068.00 from Bank A (balance 968.00)", "Deferred", "PENDING, 0 ledger entries", "Balances unchanged: 968, 1012, 1020, Overdraft prevented (PASS)"),
        ("Circular Gridlock", "3 payments: 1120.00 cycle (A->B, B->C, C->A)", "All 3 settled via BCGR", "3 SETTLED, 2 ledger entries each", "3/3 ledger verified, Balances unchanged: 968, 1012, 1020 (PASS)")
    ]

    t3 = doc.add_table(rows=len(aws_data), cols=5)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3)

    for r_idx, row in enumerate(aws_data):
        for c_idx, val in enumerate(row):
            cell = t3.cell(r_idx, c_idx)
            set_cell_margins(cell, top=100, bottom=100, left=110, right=110)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [2] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = 'Times New Roman'
            if r_idx == 0:
                set_cell_background(cell, "2B2B2B")
                run.font.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                bg = "F9F9F9" if r_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0, 0, 0)

    col_widths3 = [Inches(1.2), Inches(1.5), Inches(1.1), Inches(1.2), Inches(1.5)]
    for row in t3.rows:
        for i, w in enumerate(col_widths3):
            row.cells[i].width = w

    p_cap_t3 = doc.add_paragraph()
    p_cap_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_t3.paragraph_format.space_before = Pt(4)
    p_cap_t3.paragraph_format.space_after = Pt(12)
    r_ct3_label = p_cap_t3.add_run("Table 3. ")
    r_ct3_label.font.name = 'Times New Roman'
    r_ct3_label.font.size = Pt(10.5)
    r_ct3_label.font.bold = True
    r_ct3_label.font.color.rgb = RGBColor(30, 30, 30)
    r_ct3_desc = p_cap_t3.add_run("Live AWS production scenario validation results in ap-south-1 (Mumbai).")
    r_ct3_desc.font.name = 'Times New Roman'
    r_ct3_desc.font.size = Pt(10.5)
    r_ct3_desc.font.italic = True
    r_ct3_desc.font.color.rgb = RGBColor(40, 40, 40)

    # Cloud Cost Analysis
    add_h2("10.3 Cloud Cost and Free-Tier Analysis")
    add_p(
        "ClearPay was specifically engineered to operate entirely within the AWS Free Tier. Across all benchmark runs and live test scenarios, AWS consumption was logged as: (1) AWS Lambda: 256 MB arm64 memory with average execution duration under 35 ms (well within the 1,000,000 free requests/month and 3.2M seconds of compute), (2) DynamoDB: On-demand pay-per-request mode with single-digit read/write units consumed (within the 25 GB free storage and 25 WCU/RCU allowance), (3) Amazon SQS: Under 500 messages (within 1,000,000 free requests/month), (4) Amazon S3: Under 5 MB stored (within 5 GB standard free tier), and (5) AWS Step Functions: Under 200 state transitions (within 4,000 free state transitions/month). The total billed AWS expenditure for development, testing, and deployment was exactly $0.00."
    )

    # =========================================================================
    # SECTION 11: CONCLUSION
    # =========================================================================
    add_h1("11. Conclusion:")
    add_p(
        "This project successfully designed, implemented, and verified ClearPay, a production-grade, liquidity-aware, fault-tolerant payment clearing and settlement engine deployed on AWS serverless architecture. By replacing brittle all-or-nothing batch settlement with partial removal heuristics and novel Bounded-Cycle Gridlock Repair (BCGR), ClearPay overcomes the systemic gridlock vulnerabilities inherent in conventional RTGS and clearinghouse infrastructures. On real-world financial transaction networks from the Stanford Network Analysis Project (SNAP), ClearPay demonstrated the ability to clear over 62% of transaction value under extreme liquidity stress where legacy baselines completely failed."
    )
    add_p(
        "The serverless architecture deployed in AWS ap-south-1 proved that cloud-native distributed microservices can execute high-volume financial settlement with rigorous ACID guarantees. The combination of SHA-256 frozen plan hashing, deterministic composite ledger primary keys, and idempotent payment tokens completely eliminates double-debit hazards during cloud retries. Furthermore, automated S3-triggered event-driven reconciliation successfully detected 100% of injected discrepancies without human intervention."
    )
    add_p(
        "Future research extensions will incorporate machine learning-driven predictive models to forecast intraday bank liquidity positions before settlement windows open, multi-currency cross-border settlement with dynamic foreign exchange rates, and active-active multi-region AWS replication across Mumbai (ap-south-1) and Singapore (ap-southeast-1) for high-availability disaster recovery."
    )

    # =========================================================================
    # SECTION 12: REFERENCES
    # =========================================================================
    add_h1("12. References(with DOI or weblink):Min 30 references with links")
    add_p("The following 30 references document the theoretical foundations, algorithms, cloud systems, and real-world datasets utilized in ClearPay:")

    references = [
        ("[1]", "Amazon Web Services. AWS Lambda Developer Guide. Available: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html"),
        ("[2]", "Amazon Web Services. AWS Step Functions Developer Guide. Available: https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html"),
        ("[3]", "Amazon Web Services. Amazon DynamoDB Developer Guide. Available: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html"),
        ("[4]", "Amazon Web Services. Working with transactions in Amazon DynamoDB. Available: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html"),
        ("[5]", "Amazon Web Services. Amazon SQS Developer Guide. Available: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html"),
        ("[6]", "Amazon Web Services. Using dead-letter queues in Amazon SQS. Available: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html"),
        ("[7]", "Amazon Web Services. Amazon S3 User Guide. Available: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html"),
        ("[8]", "Amazon Web Services. Working with HTTP APIs in Amazon API Gateway. Available: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html"),
        ("[9]", "Amazon Web Services. AWS Serverless Application Model (SAM) Developer Guide. Available: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html"),
        ("[10]", "Amazon Web Services. AWS Identity and Access Management User Guide. Available: https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html"),
        ("[11]", "Streamlit Inc. Streamlit Open-Source Python Library Documentation. Available: https://docs.streamlit.io"),
        ("[12]", "Amazon Web Services. Boto3 Documentation (AWS SDK for Python v3). Available: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html"),
        ("[13]", "Leskovec, J. and Krevl, A. SNAP Datasets: Stanford Large Network Dataset Collection. Available: https://snap.stanford.edu/data"),
        ("[14]", "Stanford Network Analysis Project (SNAP). Bitcoin OTC trust weighted signed network. Available: https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html"),
        ("[15]", "Stanford Network Analysis Project (SNAP). Bitcoin Alpha trust weighted signed network. Available: https://snap.stanford.edu/data/soc-sign-bitcoin-alpha.html"),
        ("[16]", "Kumar, S., Spezzano, F., Subrahmanian, V.S. and Faloutsos, C. (2016). Edge weight prediction in weighted signed networks. IEEE International Conference on Data Mining (ICDM), pp. 221-230. DOI: https://doi.org/10.1109/ICDM.2016.0033"),
        ("[17]", "Kumar, S., Hooi, B., Makhija, D., Kumar, M., Faloutsos, C. and Subrahmanian, V.S. (2018). REV2: Fraudulent user prediction in rating platforms. ACM WSDM, pp. 333-341. DOI: https://doi.org/10.1145/3159652.3159729"),
        ("[18]", "Güntzer, M.M., Jungnickel, D. and Leclerc, M. (1998). Efficient algorithms for the clearing of interbank payments. European Journal of Operational Research, 106(1), pp. 212-219. DOI: https://doi.org/10.1016/S0377-2217(97)00304-6"),
        ("[19]", "Martin, A. and McAndrews, J. (2008). Liquidity-saving mechanisms. Journal of Monetary Economics, 55(3), pp. 554-567. DOI: https://doi.org/10.1016/j.jmoneco.2008.01.003"),
        ("[20]", "Galbiati, M. and Soramäki, K. (2011). An agent-based model of payment systems. Journal of Economic Dynamics and Control, 35(6), pp. 859-875. DOI: https://doi.org/10.1016/j.jedc.2010.11.001"),
        ("[21]", "Bech, M.L. and Garratt, R. (2003). The intraday liquidity management game. Journal of Economic Theory, 109(2), pp. 198-219. DOI: https://doi.org/10.1016/S0022-0531(03)00007-2"),
        ("[22]", "Seidman, S.B. (1983). Network structure and minimum degree. Social Networks, 5(3), pp. 269-287. DOI: https://doi.org/10.1016/0378-8733(83)90028-X"),
        ("[23]", "Batagelj, V. and Zaversnik, M. (2003). An O(m) algorithm for cores decomposition of networks. arXiv preprint, arXiv:cs/0310049. Available: https://arxiv.org/abs/cs/0310049"),
        ("[24]", "Johnson, D.B. (1975). Finding all the elementary circuits of a directed graph. SIAM Journal on Computing, 4(1), pp. 77-84. DOI: https://doi.org/10.1137/0204007"),
        ("[25]", "Garcia-Molina, H. and Salem, K. (1987). Sagas. ACM SIGMOD Record, 16(3), pp. 249-259. DOI: https://doi.org/10.1145/38713.38742"),
        ("[26]", "Jonas, E., Schleier-Smith, J., Sreekanti, V., et al. (2019). Cloud Programming Simplified: A Berkeley View on Serverless Computing. arXiv preprint, arXiv:1902.03383. Available: https://arxiv.org/abs/1902.03383"),
        ("[27]", "Mell, P. and Grance, T. (2011). The NIST Definition of Cloud Computing. NIST Special Publication 800-145, National Institute of Standards and Technology. DOI: https://doi.org/10.6028/NIST.SP.800-145"),
        ("[28]", "National Institute of Standards and Technology (2015). Secure Hash Standard (SHS). FIPS PUB 180-4, NIST, U.S. Department of Commerce. DOI: https://doi.org/10.6028/NIST.FIPS.180-4"),
        ("[29]", "Bank for International Settlements and CPMI-IOSCO (2012). Principles for Financial Market Infrastructures (PFMI). CP101, Bank for International Settlements. Available: https://www.bis.org/cpmi/publ/d101a.pdf"),
        ("[30]", "Stripe Inc. Idempotent Requests in Financial API Architecture (API Reference & Engineering Standards). Available: https://stripe.com/docs/api/idempotent_requests")
    ]

    for num, ref_text in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_n = p_ref.add_run(num + " ")
        r_n.font.name = 'Times New Roman'
        r_n.font.size = Pt(11)
        r_n.font.bold = True
        r_n.font.color.rgb = RGBColor(0, 0, 0)
        r_t = p_ref.add_run(ref_text)
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_t.font.color.rgb = RGBColor(30, 30, 30)

    # =========================================================================
    # SECTION 13: APPENDIX
    # =========================================================================
    add_h1("13. Appendix: Research Paper (word format) link: (if any) - an added advantage")
    add_p(
        "Link to ClearPay Full Research Paper & Documentation: https://github.com/Mrinalini10/clearpay_novel_final/blob/main/docs/RESEARCH_PAPER.md",
        bold_prefix="13.1 Research Paper (Markdown & Source Format): "
    )
    add_p(
        "Direct link to supplementary Word format (.docx) research document: https://github.com/Mrinalini10/clearpay_novel_final/blob/main/docs/CA-HSC_New_Work_Supplement.docx (also archived locally in project documentation folder).",
        bold_prefix="13.2 Supplementary Research Paper (Word Format): "
    )
    add_p(
        "The project repository includes a 170-test automated test suite (including 66 dedicated unit and property tests for the core liquidity and novel gridlock algorithms across 'tests/test_liquidity.py', 'tests/test_novel_engine.py', 'tests/test_account_liquidity.py', etc.) covering: (1) Idempotent payment ingestion and schema validation, (2) Atomic DynamoDB debit/credit balance conservation, (3) Exact match between removal heuristic and scipy MILP ground truth on small topologies, (4) BCGR 2-bank bilateral and 3-bank triangular gridlock recovery, (5) S3 frozen plan SHA-256 hash validation, (6) Automated reconciliation detection of injected anomalies, and (7) Step Functions retry state transition safety. All 170 tests pass with 0 failures.",
        bold_prefix="13.3 Automated Verification Suite Summary: "
    )

    # Root repo paths
    repo_root = os.path.abspath(os.path.join(curr_dir, "..")) if os.path.basename(curr_dir) == "docs" else curr_dir
    out_docx_final = os.path.join(repo_root, "docs", "ClearPay_Project_Report_DA3_FINAL.docx")
    out_docx_repo_final = os.path.join(repo_root, "ClearPay_Project_Report_DA3_FINAL.docx")
    doc.save(out_docx_final)
    doc.save(out_docx_repo_final)

    # Also attempt to update standard names if not locked by Word
    for p in [os.path.join(repo_root, "ClearPay_Project_Report_DA3.docx"), os.path.join(repo_root, "docs", "ClearPay_Project_Report_DA3.docx")]:
        try:
            doc.save(p)
        except Exception:
            pass

    out_docx_repo = out_docx_final
    print(f"Report DOCX saved to: {out_docx_final}")

    # Export to PDF via Microsoft Word COM
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        out_pdf_repo = os.path.join(repo_root, "ClearPay_Project_Report_DA3_FINAL.pdf")
        out_pdf_docs = os.path.join(repo_root, "docs", "ClearPay_Project_Report_DA3_FINAL.pdf")
        downloads_dir = os.path.expanduser(r"~\Downloads")
        out_pdf_down = os.path.join(downloads_dir, "ClearPay_Project_Report_DA3_FINAL.pdf")
        out_docx_down = os.path.join(downloads_dir, "ClearPay_Project_Report_DA3_FINAL.docx")

        w_doc = word.Documents.Open(out_docx_final)
        w_doc.ExportAsFixedFormat(out_pdf_docs, 17) # 17 = wdExportFormatPDF
        w_doc.Close(False)
        word.Quit()

        shutil.copyfile(out_pdf_docs, out_pdf_repo)
        shutil.copyfile(out_pdf_docs, out_pdf_down)
        shutil.copyfile(out_docx_final, out_docx_down)
        print("Report PDF successfully generated and synchronized across all locations!")
    except Exception as e:
        print(f"Word PDF conversion notice: {e}")

    return out_docx_final

if __name__ == '__main__':
    create_report()
