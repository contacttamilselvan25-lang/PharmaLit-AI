import io
from pathlib import Path
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelExporter:
    PRIMARY_COLOR = "1B365D"
    ACCENT_COLOR = "008080"
    HEADER_TEXT_COLOR = "FFFFFF"
    ZEBRA_FILL_COLOR = "F4F7FB"
    BORDER_COLOR = "D0D7DE"

    @classmethod
    def create_workbook(
        cls,
        project_dict: Dict[str, Any],
        papers: List[Any],
        gap_data: Optional[Dict[str, Any]] = None
    ) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        header_font = Font(name="Segoe UI", size=11, bold=True, color=cls.HEADER_TEXT_COLOR)
        header_fill = PatternFill(start_color=cls.PRIMARY_COLOR, end_color=cls.PRIMARY_COLOR, fill_type="solid")
        accent_fill = PatternFill(start_color=cls.ACCENT_COLOR, end_color=cls.ACCENT_COLOR, fill_type="solid")
        zebra_fill = PatternFill(start_color=cls.ZEBRA_FILL_COLOR, end_color=cls.ZEBRA_FILL_COLOR, fill_type="solid")
        
        regular_font = Font(name="Segoe UI", size=10)
        bold_font = Font(name="Segoe UI", size=10, bold=True)
        title_font = Font(name="Segoe UI", size=16, bold=True, color=cls.PRIMARY_COLOR)
        subtitle_font = Font(name="Segoe UI", size=11, italic=True, color="555555")

        thin_side = Side(border_style="thin", color=cls.BORDER_COLOR)
        cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        align_center = Alignment(horizontal="center", vertical="center")
        align_header = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws_sum = wb.create_sheet(title="Project Summary")
        ws_sum.views.sheetView[0].showGridLines = True

        ws_sum["A2"] = "PharmaLit AI — Literature Review & Research Intelligence"
        ws_sum["A2"].font = title_font
        ws_sum["A3"] = "Executive Project Summary and Metadata Audit"
        ws_sum["A3"].font = subtitle_font

        metadata_rows = [
            ("Project Name", project_dict.get("name", "N/A")),
            ("Therapeutic Area", project_dict.get("therapeutic_area", "N/A")),
            ("Target Drug / API", project_dict.get("target_drug", "N/A")),
            ("Description", project_dict.get("description", "N/A")),
            ("Total Papers in Project", len(papers)),
            ("Active (Included) Papers", len([p for p in papers if not p.is_excluded])),
            ("Excluded / Duplicates", len([p for p in papers if p.is_excluded])),
            ("Papers with DOI", len([p for p in papers if p.doi])),
            ("Papers with Abstract", len([p for p in papers if p.abstract])),
            ("Full-Text Attached", len([p for p in papers if p.has_full_text])),
            ("Analyzed Papers", len([p for p in papers if p.analysis and p.analysis.status == "completed"])),
            ("Generated Timestamp", project_dict.get("updated_at", "N/A"))
        ]

        ws_sum["A5"] = "Metric / Parameter"
        ws_sum["B5"] = "Value / Details"
        ws_sum["A5"].font = header_font
        ws_sum["A5"].fill = header_fill
        ws_sum["A5"].alignment = align_center
        ws_sum["B5"].font = header_font
        ws_sum["B5"].fill = header_fill
        ws_sum["B5"].alignment = align_center

        row_idx = 6
        for param, val in metadata_rows:
            ws_sum.cell(row=row_idx, column=1, value=param).font = bold_font
            ws_sum.cell(row=row_idx, column=2, value=str(val)).font = regular_font
            ws_sum.cell(row=row_idx, column=1).border = cell_border
            ws_sum.cell(row=row_idx, column=2).border = cell_border
            if row_idx % 2 == 1:
                ws_sum.cell(row=row_idx, column=1).fill = zebra_fill
                ws_sum.cell(row=row_idx, column=2).fill = zebra_fill
            row_idx += 1

        ws_sum.column_dimensions["A"].width = 30
        ws_sum.column_dimensions["B"].width = 65

        ws_papers = wb.create_sheet(title="Collected Papers")
        ws_papers.views.sheetView[0].showGridLines = True
        ws_papers.freeze_panes = "A2"

        paper_headers = [
            "ID", "Title", "Authors", "Year", "Journal", "DOI", "PMID",
            "PMCID", "Database Source", "Open Access", "Status", "Abstract Preview"
        ]
        for col_idx, h in enumerate(paper_headers, 1):
            cell = ws_papers.cell(row=1, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_header
            cell.border = cell_border

        for r_idx, p in enumerate(papers, 2):
            status = "Excluded" if p.is_excluded else "Included"
            oa_str = "Yes" if p.is_open_access else "No"
            abs_preview = (p.abstract[:200] + "...") if p.abstract else "No abstract available"

            vals = [
                p.id, p.title, p.authors, p.year, p.journal, p.doi,
                p.pmid, p.pmcid, p.database_source, oa_str, status, abs_preview
            ]
            fill = zebra_fill if r_idx % 2 == 1 else None

            for col_idx, v in enumerate(vals, 1):
                c = ws_papers.cell(row=r_idx, column=col_idx, value=v)
                c.font = regular_font
                c.border = cell_border
                c.alignment = align_left if col_idx in [2, 3, 5, 12] else align_center
                if fill:
                    c.fill = fill

        col_widths = {1: 8, 2: 45, 3: 28, 4: 10, 5: 25, 6: 22, 7: 12, 8: 14, 9: 16, 10: 12, 11: 12, 12: 50}
        for col_i, w in col_widths.items():
            ws_papers.column_dimensions[get_column_letter(col_i)].width = w

        ws_an = wb.create_sheet(title="Detailed AI Analysis")
        ws_an.views.sheetView[0].showGridLines = True
        ws_an.freeze_panes = "A2"

        analysis_headers = [
            "Paper ID", "Title", "Year", "Evidence Confidence", "Research Objective",
            "Study Design", "Experimental Model", "Formulation Methods", "Analytical Instruments",
            "Quantitative Results", "Author Limitations", "AI-Inferred Limitations",
            "Unanswered Gaps", "Future Directions", "Scientific Importance"
        ]
        for col_idx, h in enumerate(analysis_headers, 1):
            cell = ws_an.cell(row=1, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = accent_fill
            cell.alignment = align_header
            cell.border = cell_border

        a_row = 2
        for p in papers:
            if not p.analysis:
                continue
            an = p.analysis
            meth = an.methodology
            res = an.results
            lims = an.limitations
            gaps = an.gaps
            futs = an.future_directions

            inst_str = ", ".join(meth.get("analytical_instruments", []))
            quant_str = " | ".join(res.get("quantitative_metrics", []))
            auth_lim = " | ".join(lims.get("author_reported_limitations", []))
            inf_lim = " | ".join(lims.get("ai_inferred_limitations", []))
            unans_str = " | ".join(gaps.get("unanswered_questions", []))
            fut_str = " | ".join(futs if isinstance(futs, list) else [])

            an_vals = [
                p.id, p.title, p.year, an.evidence_confidence, an.research_objective,
                meth.get("study_design", ""), meth.get("experimental_model", ""),
                meth.get("formulation_methods", ""), inst_str, quant_str,
                auth_lim, inf_lim, unans_str, fut_str, an.scientific_importance
            ]

            fill = zebra_fill if a_row % 2 == 1 else None
            for col_idx, v in enumerate(an_vals, 1):
                c = ws_an.cell(row=a_row, column=col_idx, value=v)
                c.font = regular_font
                c.border = cell_border
                c.alignment = align_left
                if fill:
                    c.fill = fill
            a_row += 1

        an_col_widths = {1: 10, 2: 35, 3: 8, 4: 25, 5: 35, 6: 25, 7: 25, 8: 25, 9: 25, 10: 35, 11: 30, 12: 30, 13: 30, 14: 30, 15: 35}
        for col_i, w in an_col_widths.items():
            ws_an.column_dimensions[get_column_letter(col_i)].width = w

        ws_gap = wb.create_sheet(title="Research Gap Matrix")
        ws_gap.views.sheetView[0].showGridLines = True
        ws_gap.freeze_panes = "A2"

        gap_headers = [
            "Research Theme", "Existing Evidence", "Supporting Papers Count",
            "Identified Limitation", "Unanswered Question",
            "Proposed Research Opportunity", "Supporting DOIs", "Confidence Level"
        ]
        for col_idx, h in enumerate(gap_headers, 1):
            cell = ws_gap.cell(row=1, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_header
            cell.border = cell_border

        matrix_items = gap_data.get("gap_matrix", []) if gap_data else []
        g_row = 2
        for item in matrix_items:
            dois = ", ".join(item.get("supporting_dois", []))
            g_vals = [
                item.get("theme", ""),
                item.get("existing_evidence", ""),
                item.get("supporting_papers_count", 0),
                item.get("identified_limitation", ""),
                item.get("unanswered_question", ""),
                item.get("proposed_opportunity", ""),
                dois,
                item.get("confidence_level", "")
            ]
            fill = zebra_fill if g_row % 2 == 1 else None
            for col_idx, v in enumerate(g_vals, 1):
                c = ws_gap.cell(row=g_row, column=col_idx, value=v)
                c.font = regular_font
                c.border = cell_border
                c.alignment = align_left if col_idx != 3 else align_center
                if fill:
                    c.fill = fill
            g_row += 1

        gap_widths = {1: 25, 2: 35, 3: 15, 4: 35, 5: 35, 6: 40, 7: 25, 8: 15}
        for col_i, w in gap_widths.items():
            ws_gap.column_dimensions[get_column_letter(col_i)].width = w

        ws_snip = wb.create_sheet(title="Evidence Snippets")
        ws_snip.views.sheetView[0].showGridLines = True
        ws_snip.freeze_panes = "A2"

        snip_headers = ["Paper ID", "Paper Title", "DOI", "Confidence Level", "Exact Verbatim Evidence Quote"]
        for col_idx, h in enumerate(snip_headers, 1):
            cell = ws_snip.cell(row=1, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = accent_fill
            cell.alignment = align_header
            cell.border = cell_border

        s_row = 2
        for p in papers:
            if not p.analysis:
                continue
            snips = p.analysis.evidence_snippets
            for quote in snips:
                fill = zebra_fill if s_row % 2 == 1 else None
                s_vals = [p.id, p.title, p.doi, p.analysis.evidence_confidence, quote]
                for col_idx, v in enumerate(s_vals, 1):
                    c = ws_snip.cell(row=s_row, column=col_idx, value=v)
                    c.font = regular_font
                    c.border = cell_border
                    c.alignment = align_left
                    if fill:
                        c.fill = fill
                s_row += 1

        snip_widths = {1: 10, 2: 35, 3: 20, 4: 25, 5: 75}
        for col_i, w in snip_widths.items():
            ws_snip.column_dimensions[get_column_letter(col_i)].width = w

        return wb

    @classmethod
    def export_to_file(
        cls,
        file_path: Path,
        project_dict: Dict[str, Any],
        papers: List[Any],
        gap_data: Optional[Dict[str, Any]] = None
    ) -> Path:
        wb = cls.create_workbook(project_dict, papers, gap_data)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(file_path)
        return file_path

    @classmethod
    def export_to_bytes(
        cls,
        project_dict: Dict[str, Any],
        papers: List[Any],
        gap_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        wb = cls.create_workbook(project_dict, papers, gap_data)
        out = io.BytesIO()
        wb.save(out)
        return out.getvalue()
