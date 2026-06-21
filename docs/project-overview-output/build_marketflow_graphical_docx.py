from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


OUT = Path("docs/project-overview-output/marketflow-project-overview-graphical.docx")


def x(text: str) -> str:
    return escape(text)


def r(text: str, *, bold=False, italic=False, size=22, color="1B1B18") -> str:
    props = [f'<w:sz w:val="{size}"/>', f'<w:color w:val="{color}"/>']
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    return f"<w:r><w:rPr>{''.join(props)}</w:rPr><w:t>{x(text)}</w:t></w:r>"


def p(
    text: str = "",
    *,
    style: str | None = None,
    bold=False,
    italic=False,
    size=22,
    color="1B1B18",
    align: str | None = None,
    before=0,
    after=120,
    page_break=False,
) -> str:
    ppr = [f'<w:spacing w:before="{before}" w:after="{after}"/>']
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    runs = '<w:r><w:br w:type="page"/></w:r>' if page_break else ""
    if text:
        runs += r(text, bold=bold, italic=italic, size=size, color=color)
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{runs}</w:p>"


def cell(content: str, width: int, *, fill="FFFFFF", valign="center", border="D7DBE2") -> str:
    return (
        f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
        f'<w:vAlign w:val="{valign}"/><w:shd w:fill="{fill}"/>'
        '<w:tcMar><w:top w:w="160" w:type="dxa"/><w:left w:w="180" w:type="dxa"/>'
        '<w:bottom w:w="160" w:type="dxa"/><w:right w:w="180" w:type="dxa"/></w:tcMar>'
        f'<w:tcBorders><w:top w:val="single" w:sz="4" w:color="{border}"/>'
        f'<w:left w:val="single" w:sz="4" w:color="{border}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:color="{border}"/>'
        f'<w:right w:val="single" w:sz="4" w:color="{border}"/></w:tcBorders>'
        f"</w:tcPr>{content}</w:tc>"
    )


def table(rows: list[list[str]], widths: list[int], *, indent=0, borders=True) -> str:
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    border_xml = ""
    if not borders:
        border_xml = (
            '<w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/>'
            '<w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>'
        )
    out = [
        '<w:tbl><w:tblPr><w:tblW w:w="14400" w:type="dxa"/>'
        f'<w:tblInd w:w="{indent}" w:type="dxa"/><w:tblLayout w:type="fixed"/>{border_xml}</w:tblPr>',
        f"<w:tblGrid>{grid}</w:tblGrid>",
    ]
    for row in rows:
        out.append("<w:tr>")
        for c in row:
            out.append(c)
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def metric(title: str, value: str, note: str, fill="FFF7ED", accent="D95F18") -> str:
    return cell(
        p(title.upper(), bold=True, size=16, color=accent, after=40)
        + p(value, bold=True, size=34, color="171A15", after=40)
        + p(note, size=16, color="555555", after=0),
        3400,
        fill=fill,
        border="E6D7C8",
    )


def slide_title(kicker: str, title: str, subtitle: str = "", *, dark=False) -> str:
    color = "F9F2E5" if dark else "171A15"
    muted = "D5CDBD" if dark else "555555"
    accent = "F28C38" if dark else "D95F18"
    return (
        p(kicker.upper(), bold=True, size=16, color=accent, after=90)
        + p(title, bold=True, size=42, color=color, after=120)
        + (p(subtitle, size=20, color=muted, after=180) if subtitle else "")
    )


def page_bg(content: str, fill: str, *, dark=False) -> str:
    # A one-cell full-page table gives Word-native slide-like color blocking.
    return table([[cell(content, 14400, fill=fill, border=fill, valign="top")]], [14400], borders=False)


def document_xml() -> str:
    pages: list[str] = []

    cover = (
        slide_title(
            "Project Overview",
            "MarketFlow",
            "A cash-flow tracker for Nigerian market traders, built with Django and React.",
            dark=True,
        )
        + table(
            [[
                metric("Frontend", "React 19", "Vite, TypeScript, Tailwind", fill="272C24", accent="F28C38"),
                metric("Backend", "Django 6", "DRF, Simple JWT, SQLite", fill="272C24", accent="F28C38"),
                metric("Scope", "7 routes", "Dashboard, records, reports", fill="272C24", accent="F28C38"),
                metric("Currency", "NGN", "Trader finance workflows", fill="272C24", accent="F28C38"),
            ]],
            [3400, 3400, 3400, 3400],
            borders=False,
        )
        + p("Generated from repository state on June 21, 2026", size=14, color="A8AD9A", align="right", after=0)
    )
    pages.append(page_bg(cover, "171A15", dark=True))

    thesis = (
        slide_title(
            "Product Thesis",
            "MarketFlow turns daily stall activity into cash-flow clarity.",
            "The product keeps the trader experience simple while the backend roadmap preserves correct accounting boundaries.",
        )
        + table(
            [[
                cell(p("1", bold=True, size=44, color="D95F18") + p("Record", bold=True, size=24) + p("Sales, expenses, inventory, business profile, and daily activity.", size=17), 4400, fill="FFFFFF"),
                cell(p("2", bold=True, size=44, color="2E8F5A") + p("Separate", bold=True, size=24) + p("Cash flow, profit, capital, stock value, and tax reserve concepts.", size=17), 4400, fill="FFFFFF"),
                cell(p("3", bold=True, size=44, color="0B2545") + p("Plan", bold=True, size=24) + p("Burn rate, break-even, tax estimates, trends, and forecasting.", size=17), 4400, fill="FFFFFF"),
            ]],
            [4400, 4400, 4400],
            borders=False,
        )
    )
    pages.append(p("", page_break=True) + page_bg(thesis, "FBF8F1"))

    ux = (
        slide_title(
            "Current User Experience",
            "The core trader workflow is already represented in the frontend.",
            "This Word-native mockup mirrors the implemented dashboard structure and route set.",
        )
        + table(
            [[
                cell(
                    p("MarketFlow", bold=True, size=22, color="F9F2E5")
                    + p("Dashboard", size=17, color="D5CDBD")
                    + p("Sales", size=17, color="D5CDBD")
                    + p("Expenses", size=17, color="D5CDBD")
                    + p("Inventory", size=17, color="D5CDBD")
                    + p("Reports", size=17, color="D5CDBD")
                    + p("Profile", size=17, color="D5CDBD"),
                    2600,
                    fill="20261D",
                    border="20261D",
                    valign="top",
                ),
                cell(
                    p("Good morning, Amina Okafor", bold=True, size=28, color="171A15")
                    + p("Here is what is happening with Amina Provisions today.", size=16, color="777168")
                    + table(
                        [[
                            metric("Sales Today", "NGN 174k", "Daily inflow", fill="FFF7ED"),
                            metric("Expenses", "NGN 15k", "Daily outflow", fill="FEF2F2", accent="C34230"),
                            metric("Net Profit", "NGN 159k", "Prototype profit", fill="F0FDF4", accent="23824D"),
                        ]],
                        [3100, 3100, 3100],
                        borders=False,
                    )
                    + table(
                        [[
                            cell(p("Recent Activity", bold=True, size=20) + p("Rice 50kg  +NGN 72,000", size=16, color="23824D") + p("Transport  -NGN 8,500", size=16, color="C34230") + p("Palm oil carton  +NGN 38,500", size=16, color="23824D"), 4550, fill="FFFFFF"),
                            cell(p("Low Stock Alert", bold=True, size=20, color="D95F18") + p("Palm oil carton: 3 cartons left", size=16) + p("Garri sack: 2 sacks left", size=16) + p("Inventory value appears in dashboard summary.", size=16, color="777168"), 4550, fill="FFF7ED"),
                        ]],
                        [4550, 4550],
                        borders=False,
                    ),
                    11000,
                    fill="F7F7F5",
                    border="E4DED2",
                    valign="top",
                ),
            ]],
            [2600, 11000],
            borders=False,
        )
    )
    pages.append(p("", page_break=True) + page_bg(ux, "EEF5EC"))

    screens = (
        slide_title(
            "Implemented Screens",
            "The product has a routed page for each main operating task.",
            "The current app is not just a landing page; it has working application surfaces.",
        )
        + table(
            [
                [
                    cell(p("Auth", bold=True, size=24) + p("/auth", bold=True, size=16, color="D95F18") + p("Register, login, token storage, refresh, logout, and profile request.", size=16), 4400, fill="FFFFFF"),
                    cell(p("Dashboard", bold=True, size=24) + p("/dashboard", bold=True, size=16, color="D95F18") + p("Daily summary, recent activity, stock alerts, top selling item, weekly chart.", size=16), 4400, fill="FFFFFF"),
                    cell(p("Sales", bold=True, size=24) + p("/sales", bold=True, size=16, color="D95F18") + p("Create and delete item-level sale records.", size=16), 4400, fill="FFFFFF"),
                ],
                [
                    cell(p("Expenses", bold=True, size=24) + p("/expenses", bold=True, size=16, color="D95F18") + p("Create and delete cost records for profit tracking.", size=16), 4400, fill="FFFFFF"),
                    cell(p("Inventory", bold=True, size=24) + p("/inventory", bold=True, size=16, color="D95F18") + p("Track quantity, unit cost, stock value, and reorder levels.", size=16), 4400, fill="FFFFFF"),
                    cell(p("Reports + Profile", bold=True, size=24) + p("/reports, /profile", bold=True, size=16, color="D95F18") + p("Simple profit/capital/tax reserve report plus account details.", size=16), 4400, fill="FFFFFF"),
                ],
            ],
            [4400, 4400, 4400],
            borders=False,
        )
    )
    pages.append(p("", page_break=True) + page_bg(screens, "FBF8F1"))

    backend = (
        slide_title(
            "Backend Reality",
            "The backend is a functional prototype with a documented path to stronger domain boundaries.",
        )
        + table(
            [[
                cell(p("Current models", bold=True, size=24, color="0B2545") + p("BusinessProfile", size=17) + p("Sale", size=17) + p("Expense", size=17) + p("InventoryItem", size=17) + p("OAuthIdentity", size=17), 4300, fill="FFFFFF"),
                cell(p("Current API", bold=True, size=24, color="0B2545") + p("/api/auth/*", size=17) + p("/api/dashboard/", size=17) + p("/api/sales/", size=17) + p("/api/expenses/", size=17) + p("/api/inventory/", size=17), 4300, fill="FFFFFF"),
                cell(p("Known limitation", bold=True, size=24, color="9B1C1C") + p("Financial records are currently scoped directly to users. The documented target is business-scoped ownership with memberships and permissions.", size=17), 4300, fill="FFF5F5"),
            ]],
            [4300, 4300, 4300],
            borders=False,
        )
        + p("Source: backend/finance, backend/users, README, and docs.", size=15, color="777168", align="right")
    )
    pages.append(p("", page_break=True) + page_bg(backend, "EEF5EC"))

    arch = (
        slide_title(
            "Architecture Direction",
            "The reconstruction plan moves MarketFlow from prototype CRUD to an accounting-aware modular monolith.",
        )
        + table(
            [[
                cell(p("Users", bold=True, size=20, color="F9F2E5") + p("Identity and auth", size=15, color="D5CDBD"), 1900, fill="20261D", border="20261D"),
                cell(p("Businesses", bold=True, size=20, color="F9F2E5") + p("Ownership boundary", size=15, color="D5CDBD"), 1900, fill="274032", border="274032"),
                cell(p("Sales", bold=True, size=20) + p("Sale lines and payments", size=15), 1900, fill="FFFFFF"),
                cell(p("Expenses", bold=True, size=20) + p("Classified costs", size=15), 1900, fill="FFFFFF"),
                cell(p("Inventory", bold=True, size=20) + p("Stock movements", size=15), 1900, fill="FFFFFF"),
                cell(p("Ledger", bold=True, size=20, color="F9F2E5") + p("Cash and capital", size=15, color="D5CDBD"), 1900, fill="0B2545", border="0B2545"),
                cell(p("Analytics", bold=True, size=20) + p("Profit and trends", size=15), 1900, fill="FFFFFF"),
            ]],
            [1900, 1900, 1900, 1900, 1900, 1900, 1900],
            borders=False,
        )
        + table(
            [[
                cell(p("Planning", bold=True, size=24) + p("Burn rate, runway, and break-even scenarios.", size=17), 4300, fill="FFFFFF"),
                cell(p("Taxes", bold=True, size=24) + p("Versioned VAT/FIRS estimates with assumptions.", size=17), 4300, fill="FFFFFF"),
                cell(p("Forecasting", bold=True, size=24) + p("Forecast runs, projected periods, and measured forecast error.", size=17), 4300, fill="FFFFFF"),
            ]],
            [4300, 4300, 4300],
            borders=False,
        )
    )
    pages.append(p("", page_break=True) + page_bg(arch, "FBF8F1"))

    next_steps = (
        slide_title(
            "Next Implementation Slice",
            "The next sprint should make ownership and tests safer before adding advanced finance features.",
            dark=True,
        )
        + table(
            [[
                cell(p("1", bold=True, size=36, color="F28C38") + p("Characterization tests", bold=True, size=21, color="F9F2E5") + p("Freeze existing API behavior before refactoring.", size=16, color="D5CDBD"), 4200, fill="272C24", border="3B4035"),
                cell(p("2", bold=True, size=36, color="F28C38") + p("Business ownership", bold=True, size=21, color="F9F2E5") + p("Create Business and BusinessMembership.", size=16, color="D5CDBD"), 4200, fill="272C24", border="3B4035"),
                cell(p("3", bold=True, size=36, color="F28C38") + p("Backfill safely", bold=True, size=21, color="F9F2E5") + p("Move existing records toward business scope.", size=16, color="D5CDBD"), 4200, fill="272C24", border="3B4035"),
            ]],
            [4200, 4200, 4200],
            borders=False,
        )
        + table(
            [[
                cell(p("Do not rewrite everything at once.", bold=True, size=26, color="F9F2E5") + p("Keep existing frontend payloads stable while backend boundaries are introduced behind compatibility endpoints.", size=18, color="D5CDBD"), 13200, fill="20261D", border="3B4035")
            ]],
            [13200],
            borders=False,
        )
    )
    pages.append(p("", page_break=True) + page_bg(next_steps, "171A15", dark=True))

    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="rId6"/>'
        '<w:footerReference w:type="default" r:id="rId7"/>'
        '<w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>'
        '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{''.join(pages)}{sect}</w:body></w:document>"
    )


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
<Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:color w:val="1B1B18"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:style>
</w:styles>"""

SETTINGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/></w:settings>"""

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="right"/></w:pPr><w:r><w:rPr><w:sz w:val="16"/><w:color w:val="888888"/></w:rPr><w:t>MarketFlow graphical overview</w:t></w:r></w:p></w:hdr>"""

FOOTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="right"/></w:pPr><w:r><w:rPr><w:sz w:val="16"/><w:color w:val="888888"/></w:rPr><w:t>cashflow_analyzer</w:t></w:r></w:p></w:ftr>"""

APP_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Codex</Application></Properties>"""


def core_props() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>MarketFlow Graphical Project Overview</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document_xml())
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/settings.xml", SETTINGS)
        z.writestr("word/header1.xml", HEADER)
        z.writestr("word/footer1.xml", FOOTER)
        z.writestr("docProps/core.xml", core_props())
        z.writestr("docProps/app.xml", APP_PROPS)
    print(OUT.resolve())


if __name__ == "__main__":
    main()
