from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


OUT = Path("docs/project-overview-output/marketflow-project-overview.docx")

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def t(text: str) -> str:
    return escape(text)


def p(
    text: str = "",
    style: str | None = None,
    *,
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
    size: int | None = None,
    num_id: int | None = None,
    page_break: bool = False,
) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if num_id is not None:
        ppr.append(
            f"<w:numPr><w:ilvl w:val=\"0\"/><w:numId w:val=\"{num_id}\"/></w:numPr>"
        )
    rpr = []
    if bold:
        rpr.append("<w:b/>")
    if italic:
        rpr.append("<w:i/>")
    if color:
        rpr.append(f'<w:color w:val="{color}"/>')
    if size:
        rpr.append(f'<w:sz w:val="{size * 2}"/>')
    run = ""
    if page_break:
        run += "<w:r><w:br w:type=\"page\"/></w:r>"
    if text:
        run += f"<w:r>{'<w:rPr>' + ''.join(rpr) + '</w:rPr>' if rpr else ''}<w:t>{t(text)}</w:t></w:r>"
    return f"<w:p>{'<w:pPr>' + ''.join(ppr) + '</w:pPr>' if ppr else ''}{run}</w:p>"


def table(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out = [
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="9360" w:type="dxa"/>'
        '<w:tblInd w:w="120" w:type="dxa"/>'
        '<w:tblLayout w:type="fixed"/>'
        '<w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="140" w:type="dxa"/>'
        '<w:bottom w:w="100" w:type="dxa"/><w:right w:w="140" w:type="dxa"/></w:tblCellMar>'
        '</w:tblPr>',
        f"<w:tblGrid>{grid}</w:tblGrid>",
    ]
    out.append("<w:tr><w:trPr><w:tblHeader/></w:trPr>")
    for h, w in zip(headers, widths):
        out.append(
            f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:shd w:fill="F2F4F7"/></w:tcPr>'
            f'{p(h, bold=True, color="0B2545")}</w:tc>'
        )
    out.append("</w:tr>")
    for row in rows:
        out.append("<w:tr>")
        for cell, w in zip(row, widths):
            out.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/></w:tcPr>{p(cell)}</w:tc>'
            )
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def document_xml() -> str:
    parts: list[str] = []
    parts.append(p("MarketFlow Project Overview", "Title"))
    parts.append(p("Full project brief generated from the current repository state", "Subtitle"))
    parts.append(p("Prepared: June 21, 2026 | Repository: cashflow_analyzer", "Meta"))
    parts.append(p("Project summary", "Heading1"))
    parts.append(
        p(
            "MarketFlow is a cash-flow tracker for Nigerian market traders. The current repository contains a Django backend API and a React/Vite frontend. The product helps traders record daily sales, track expenses, monitor inventory, understand profit and capital position, and prepare for future reporting, tax, and forecasting workflows."
        )
    )
    parts.append(
        table(
            ["Area", "Current state"],
            [
                ["Frontend", "React 19, TypeScript, Vite, Tailwind, React Router, shadcn-style UI primitives, lucide icons."],
                ["Backend", "Django 6 modular prototype using SQLite locally, Django REST Framework, Simple JWT, and session compatibility."],
                ["Product scope", "Authentication, dashboard, sales, expenses, inventory, reports, profile, and project documentation."],
                ["Documentation", "Knowledge base, backend reconstruction blueprint, and authentication implementation plan."],
            ],
            [2200, 7160],
        )
    )

    parts.append(p("", page_break=True))
    parts.append(p("What has been built so far", "Heading1"))
    parts.append(p("The prototype already covers the main operating loop for a trader:", "BodyText"))
    for item in [
        "Register or sign in with email and password.",
        "View a dashboard with sales today, expenses today, net profit, transaction count, capital status, inventory value, recent activity, low stock, top selling item, and weekly performance.",
        "Create and delete sales records with item name, amount, quantity, and optional note.",
        "Create and delete expense records with category, amount, and optional note.",
        "Create and delete inventory items with quantity, unit, reorder level, unit cost, stock value, and low-stock state.",
        "Review simple reports for net profit, current capital, tax set-aside, and weekly movement.",
        "View profile information and sign out.",
    ]:
        parts.append(p(item, num_id=1))
    parts.append(
        table(
            ["Screen", "Route", "Purpose"],
            [
                ["Landing page", "/", "Positions MarketFlow for Nigerian traders and sends users to authentication."],
                ["Auth", "/auth", "Login and registration with token storage in the frontend API client."],
                ["Dashboard", "/dashboard", "Daily financial snapshot and activity overview."],
                ["Sales", "/sales", "Daily revenue capture."],
                ["Expenses", "/expenses", "Cost capture for profit tracking."],
                ["Inventory", "/inventory", "Stock visibility and low-stock alerts."],
                ["Reports", "/reports", "Simple profit, capital, tax set-aside, and movement reporting."],
                ["Profile", "/profile", "Account and business details."],
            ],
            [2100, 1600, 5660],
        )
    )

    parts.append(p("", page_break=True))
    parts.append(p("Backend implementation overview", "Heading1"))
    parts.append(
        p(
            "The current backend is a working prototype API. Financial records are scoped directly to users, while the project documentation identifies business ownership as the target boundary for the next reconstruction phase."
        )
    )
    parts.append(
        table(
            ["Model", "Current responsibility"],
            [
                ["BusinessProfile", "Stores business name, stall name, initial capital, and profile timestamps."],
                ["Sale", "Stores user-owned sale item, amount, quantity, note, and sold timestamp."],
                ["Expense", "Stores user-owned category, amount, note, and spent timestamp."],
                ["InventoryItem", "Stores user-owned stock item, quantity, unit, reorder level, unit cost, and stock value basis."],
                ["OAuthIdentity", "Provides a provider-neutral identity scaffold for future OAuth providers."],
            ],
            [2300, 7060],
        )
    )
    parts.append(p("Current API surface", "Heading2"))
    for endpoint in [
        "/api/auth/register/",
        "/api/auth/login/",
        "/api/auth/logout/",
        "/api/auth/me/",
        "/api/dashboard/",
        "/api/sales/",
        "/api/expenses/",
        "/api/inventory/",
    ]:
        parts.append(p(endpoint, num_id=1))

    parts.append(p("", page_break=True))
    parts.append(p("Important product principles", "Heading1"))
    parts.append(
        p(
            "The project knowledge base makes a clear distinction between user-friendly trader language and correct accounting behavior. The backend should preserve accounting distinctions even when the interface stays simple."
        )
    )
    for item in [
        "Business should become the ownership boundary; records should not remain directly scoped only to users.",
        "Cash flow is not profit. Inventory purchases reduce cash immediately but should normally affect profit through cost of goods sold when sold.",
        "Profit, burn rate, break-even, tax estimates, trends, and forecasts should be derived by calculation services.",
        "Important financial source records need auditability through statuses, reversals, or soft deletion.",
        "Tax rules need versioning, effective dates, assumptions, and clear separation from filed tax obligations.",
    ]:
        parts.append(p(item, num_id=1))
    parts.append(p("Initial calculation definitions", "Heading2"))
    parts.append(
        table(
            ["Metric", "Baseline definition"],
            [
                ["Revenue", "Sum of completed sale totals."],
                ["Gross profit", "Revenue less cost of goods sold."],
                ["Net profit", "Gross profit less operating expenses."],
                ["Cash position", "Opening cash plus cash inflow less cash outflow."],
                ["Runway", "Available operating cash divided by average daily burn."],
                ["Break-even", "Fixed costs divided by contribution margin."],
            ],
            [2300, 7060],
        )
    )

    parts.append(p("", page_break=True))
    parts.append(p("Target architecture direction", "Heading1"))
    parts.append(
        p(
            "The backend reconstruction blueprint proposes a modular Django monolith. The goal is to keep deployment simple while separating identity, business ownership, transaction capture, inventory, ledger, analytics, planning, tax, and forecasting responsibilities."
        )
    )
    parts.append(
        table(
            ["Domain", "Target responsibility"],
            [
                ["users", "Identity, authentication, user preferences, and linked OAuth identities."],
                ["businesses", "Businesses, stalls, memberships, roles, and permissions."],
                ["sales", "Sales, sale lines, payment status, sale payments, and revenue source records."],
                ["expenses", "Expense categories, classifications, payments, and cost source records."],
                ["inventory", "Products, stock movements, purchases, purchasing lines, and valuation basis."],
                ["ledger", "Normalized cash and capital entries that prevent profit/cash/capital confusion."],
                ["analytics", "Dashboard, trend, profit, and period comparison query services."],
                ["planning", "Burn rate, runway, and break-even scenarios."],
                ["taxes", "Versioned VAT/FIRS estimates, assumptions, and tax rules."],
                ["forecasting", "Forecast runs, assumptions, projected periods, and evaluation."],
            ],
            [2100, 7260],
        )
    )

    parts.append(p("", page_break=True))
    parts.append(p("Recommended next implementation slice", "Heading1"))
    parts.append(
        p(
            "The next work should avoid an all-at-once rewrite. The documented direction starts with characterization and business ownership so later financial features can be built on the correct boundary."
        )
    )
    for step in [
        "Add characterization tests for every existing API endpoint.",
        "Create businesses.Business and businesses.BusinessMembership.",
        "Complete the users app and move auth endpoints into it cleanly.",
        "Add a data migration from BusinessProfile to Business.",
        "Add nullable business ownership to existing finance records, backfill it, then make it required.",
        "Keep existing endpoint payloads unchanged until the frontend migration is planned.",
    ]:
        parts.append(p(step, num_id=2))
    parts.append(p("Key risks to manage", "Heading2"))
    for item in [
        "Current capital is calculated as initial capital plus net profit, which is useful for prototype display but not a durable accounting model.",
        "Current deletes permanently remove source records; the target design needs auditability.",
        "Current sales do not contain sale lines, unit cost, payment status, or inventory movement links.",
        "Expense categories are free text and cannot yet support reliable burn-rate, break-even, or tax classification.",
    ]:
        parts.append(p(item, num_id=1))

    parts.append(p("", page_break=True))
    parts.append(p("Source files reviewed", "Heading1"))
    parts.append(p("This overview was generated from repository files, not from assumptions.", "BodyText"))
    for item in [
        "README.md",
        "docs/PROJECT_KNOWLEDGE_BASE.md",
        "docs/BACKEND_RECONSTRUCTION_BLUEPRINT.md",
        "docs/AUTHENTICATION_IMPLEMENTATION_PLAN.md",
        "backend/finance/models.py and backend/finance/views.py",
        "backend/users/models.py, serializers.py, services.py, and views.py",
        "cashflow_frontend/src/App.tsx, src/lib/api.ts, and implemented page components",
    ]:
        parts.append(p(item, num_id=1))
    parts.append(p("Document note", "Heading2"))
    parts.append(
        p(
            "A separate slide-style PDF already exists at docs/project-overview-output/marketflow-project-overview.pdf. This DOCX version is optimized for Word review, editing, and handoff."
        )
    )

    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="rId6"/>'
        '<w:footerReference w:type="default" r:id="rId7"/>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{''.join(parts)}{sect}</w:body></w:document>"
    )


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
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
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
<Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:color w:val="1B1B18"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:color w:val="1B1B18"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:before="0" w:after="120"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri Light" w:hAnsi="Calibri Light"/><w:b/><w:sz w:val="56"/><w:color w:val="0B2545"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="28"/><w:color w:val="555555"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Meta"><w:name w:val="Meta"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="300"/></w:pPr><w:rPr><w:b/><w:sz w:val="20"/><w:color w:val="7A5A00"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="320" w:after="160"/></w:pPr><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="2E74B5"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="2E74B5"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="22"/><w:color w:val="1B1B18"/></w:rPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="D7DBE2"/><w:left w:val="single" w:sz="4" w:space="0" w:color="D7DBE2"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D7DBE2"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D7DBE2"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="D7DBE2"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="D7DBE2"/></w:tblBorders></w:tblPr></w:style>
</w:styles>"""

NUMBERING = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="720"/></w:tabs><w:ind w:left="720" w:hanging="360"/><w:spacing w:after="120" w:line="280" w:lineRule="auto"/></w:pPr></w:lvl></w:abstractNum>
<w:abstractNum w:abstractNumId="2"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="720"/></w:tabs><w:ind w:left="720" w:hanging="360"/><w:spacing w:after="120" w:line="280" w:lineRule="auto"/></w:pPr></w:lvl></w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>
<w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num>
</w:numbering>"""

SETTINGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/></w:settings>"""

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="right"/><w:spacing w:after="80"/></w:pPr><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="777777"/></w:rPr><w:t>MarketFlow Project Overview</w:t></w:r></w:p></w:hdr>"""

FOOTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="right"/></w:pPr><w:r><w:rPr><w:sz w:val="18"/><w:color w:val="777777"/></w:rPr><w:t>cashflow_analyzer</w:t></w:r></w:p></w:ftr>"""


def core_props() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>MarketFlow Project Overview</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>"""


APP_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Codex</Application></Properties>"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document_xml())
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/numbering.xml", NUMBERING)
        z.writestr("word/settings.xml", SETTINGS)
        z.writestr("word/header1.xml", HEADER)
        z.writestr("word/footer1.xml", FOOTER)
        z.writestr("docProps/core.xml", core_props())
        z.writestr("docProps/app.xml", APP_PROPS)
    print(OUT.resolve())


if __name__ == "__main__":
    main()
