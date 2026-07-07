// Markdown/Pandoc PDF template.
// Direction: executive technical memo — deterministic, neutral, printable.
//
// Pandoc note:
// Configure syntax highlighting from Pandoc, not inside Typst:
// pandoc input.md -o output.pdf --pdf-engine=typst --syntax-highlighting=github

// --- Design tokens ---------------------------------------------------------
#let color-text = rgb("#111827")
#let color-heading = rgb("#0F172A")
#let color-subtle = rgb("#334155")
#let color-muted = rgb("#64748B")
#let color-line = rgb("#E2E8F0")
#let color-line-strong = rgb("#CBD5E1")
#let color-soft = rgb("#F8FAFC")
#let color-soft-strong = rgb("#F1F5F9")
#let color-table-alt = rgb("#FBFDFF")
#let color-table-total = rgb("#EEF6FF")
#let color-code-fill = rgb("#F8FAFC")
#let color-code-text = rgb("#334155")
#let accent-neutral = rgb("#475569")
#let accent-warning = rgb("#B45309")
#let accent-warning-soft = rgb("#FFF7ED")
#let accent-danger = rgb("#B91C1C")
#let accent-danger-soft = rgb("#FEF2F2")
#let accent-success = rgb("#047857")
#let accent-success-soft = rgb("#ECFDF5")

#let _accent(brand) = accent-neutral
#let _accent-dark(brand) = color-heading
#let _accent-soft(brand) = color-soft
#let _accent-soft-strong(brand) = color-soft-strong
#let _accent-line(brand) = color-line
#let _accent-muted(brand) = color-muted
#let _label(fr, en, lang) = if lang == "en" { en } else { fr }
#let _density(template-kind) = if template-kind == "pro" { "comfortable" } else { "compact" }
#let _body-size(template-kind) = if template-kind == "pro" { 11pt } else { 10.5pt }
#let _body-leading(template-kind) = if template-kind == "pro" { 0.92em } else { 0.84em }
#let _para-spacing(template-kind) = if template-kind == "pro" { 0.82em } else { 0.60em }
#let _list-spacing(template-kind) = if template-kind == "pro" { 0.60em } else { 0.42em }
#let _code-size(template-kind) = if template-kind == "pro" { 8.8pt } else { 8.45pt }
#let _table-size(template-kind) = if template-kind == "pro" { 8.75pt } else { 8.55pt }

#let _has-cover-meta(date, author, author-email, version, exported-at) = {
  date != "" or author != "" or author-email != "" or version != "" or exported-at != ""
}

#let _has-contact(name, company, email) = {
  name != "" or company != "" or email != ""
}

#let _meta-row(label, value, brand: "neutral", label_width: 38mm) = if value != "" [
  #grid(columns: (label_width, 1fr), gutter: 6mm,
    text(size: 8.2pt, fill: _accent-muted(brand), weight: "semibold", tracking: 0.2pt)[#label],
    text(size: 9pt, fill: color-text)[#value],
  )
  #v(3.2mm)
]

// --- Reusable blocks -------------------------------------------------------
#let callout(title, body, tone: "neutral", brand: "neutral") = {
  let accent = if tone == "warning" {
    accent-warning
  } else if tone == "danger" {
    accent-danger
  } else if tone == "success" {
    accent-success
  } else {
    _accent(brand)
  }

  let fill = if tone == "warning" {
    accent-warning-soft
  } else if tone == "danger" {
    accent-danger-soft
  } else if tone == "success" {
    accent-success-soft
  } else {
    _accent-soft(brand)
  }

  block(
    fill: fill,
    stroke: (left: 2.4pt + accent, rest: 0.45pt + color-line),
    radius: 4pt,
    inset: (x: 10pt, y: 7pt),
    width: 100%,
    above: 1.00em,
    below: 1.05em,
  )[
    #if title != "" [
      #text(size: 9pt, weight: "bold", fill: accent)[#title]
      #v(4pt)
    ]
    #body
  ]
}

#let scope_box(title, body, brand: "neutral") = block(
  fill: _accent-soft(brand),
  stroke: 0.45pt + _accent-line(brand),
  radius: 4pt,
  inset: (x: 10pt, y: 7pt),
  width: 100%,
  above: 0.90em,
  below: 1.00em,
)[
  #set par(justify: false, leading: 0.84em, spacing: 0.46em)
  #if title != "" [
    #text(size: 9pt, weight: "bold", fill: _accent-dark(brand))[#title]
    #v(4pt)
  ]
  #text(fill: color-heading)[#body]
]

#let _contact_block(
  name: "",
  role: "",
  company: "",
  address: "",
  phone: "",
  fax: "",
  email: "",
  url: "",
  brand: "neutral",
  lang: "fr",
) = if _has-contact(name, company, email) [
  #v(1.4em)
  #block(
    fill: color-soft,
    stroke: 0.45pt + color-line,
    radius: 4pt,
    inset: (x: 9pt, y: 7pt),
    width: 100%,
  )[
    #set par(justify: false, leading: 0.72em, spacing: 0.32em)
    #grid(columns: (1fr, 1.2fr), gutter: 8mm,
      [
        #text(size: 8.2pt, fill: _accent-muted(brand), weight: "semibold", tracking: 0.2pt)[#_label("Contact", "Contact", lang)]
        #v(3pt)
        #text(size: 9pt, fill: color-heading, weight: "semibold")[#name#if role != "" [ — #role]]
        #if company != "" [
          #linebreak()
          #text(size: 8.8pt, fill: color-subtle)[#company]
        ]
      ],
      [
        #text(size: 8.35pt, fill: color-subtle)[
          #if address != "" [#address#linebreak()]
          #if phone != "" [#_label("Téléphone", "Phone", lang) : #phone#linebreak()]
          #if fax != "" [#_label("Télécopie", "Fax", lang) : #fax#linebreak()]
          #if email != "" [#_label("Courriel", "Email", lang) : #email#linebreak()]
          #if url != "" [Url : #url]
        ]
      ],
    )
  ]
]

// --- Cover -----------------------------------------------------------------
#let _cover(
  title: "",
  subtitle: "",
  author: "",
  date: "",
  status: "",
  version: "",
  exported_at: "",
  author_email: "",
  brand: "neutral",
  brand_label: "DOCUMENT",
  template_kind: "internal",
  lang: "fr",
  logo_path: "",
  show_contact: false,
  contact_name: "",
  contact_role: "",
  contact_company: "",
  contact_address: "",
  contact_phone: "",
  contact_fax: "",
  contact_email: "",
  contact_url: "",
) = {
  let accent = _accent(brand)

  set page(paper: "a4", margin: (x: 25mm, y: 25mm), header: none, footer: none)
  set text(font: ("Inter", "IBM Plex Sans", "Noto Sans", "Arial"), fill: color-text, lang: lang)

  v(16mm)
  grid(columns: (1fr, auto), align: (left + top, right + top),
    rect(width: 78mm, height: 2pt, fill: accent),
    move(dy: -4.7mm)[
      #grid(columns: (auto, auto), gutter: 7pt, align: (right + top, horizon),
        if logo_path != "" {
          image(logo_path, width: 15mm)
        } else {
          none
        },
        text(size: 9pt, fill: _accent-muted(brand), weight: "semibold", tracking: 0.6pt)[#brand_label],
      )
    ],
  )

  v(26mm)
  text(size: if template_kind == "pro" { 29pt } else { 25pt }, weight: "bold", fill: color-heading, tracking: -0.35pt)[#title]

  if subtitle != "" [
    #v(6mm)
    #text(size: 14pt, fill: color-muted)[#subtitle]
  ]

  v(1fr)

  if status != "" and not show_contact [
    #rect(fill: _accent-soft-strong(brand), stroke: 0.55pt + _accent-line(brand), radius: 999pt, inset: (x: 9pt, y: 4pt))[
      #text(size: 8.2pt, fill: _accent-dark(brand), weight: "semibold", tracking: 0.2pt)[#status]
    ]
    #v(6mm)
  ]

  if show_contact [
    #rect(width: 100%, fill: white, stroke: 0.65pt + _accent-line(brand), radius: 4pt, inset: (x: 7mm, y: 5.5mm))[
      #set par(justify: false, leading: 0.72em, spacing: 0.26em)
      #grid(columns: (1fr, auto), align: (left, right),
        [
          #text(size: 8pt, fill: _accent-muted(brand), weight: "semibold", tracking: 0.5pt)[#_label("DOCUMENT", "DOCUMENT", lang)]
        ],
        [
          #if status != "" [
            #rect(fill: _accent-soft(brand), stroke: 0.45pt + _accent-line(brand), radius: 999pt, inset: (x: 7pt, y: 3pt))[
              #text(size: 7.8pt, fill: _accent-dark(brand), weight: "semibold")[#status]
            ]
          ]
        ],
      )
      #v(5pt)
      #line(length: 100%, stroke: 0.45pt + color-line)
      #v(6pt)
      #grid(columns: (0.92fr, 1.08fr), gutter: 7mm,
        [
          #_meta-row(_label("Date", "Date", lang), date, brand: brand, label_width: 18mm)
          #_meta-row(_label("Version", "Version", lang), version, brand: brand, label_width: 18mm)
          #_meta-row(_label("Export", "Export", lang), exported_at, brand: brand, label_width: 18mm)
        ],
        [
          #text(size: 9.2pt, fill: color-heading, weight: "semibold")[#contact_name#if contact_role != "" [ — #contact_role]]
          #if contact_company != "" [
            #linebreak()
            #text(size: 8.8pt, fill: color-subtle)[#contact_company]
          ]
          #v(7pt)
          #grid(columns: (18mm, 1fr), gutter: 4.5mm, row-gutter: 4.2pt,
            if contact_email != "" {
              text(size: 7.4pt, fill: _accent-muted(brand), weight: "semibold")[Email]
            } else { none },
            if contact_email != "" {
              text(size: 8.15pt, fill: _accent-muted(brand), weight: "medium")[#contact_email]
            } else { none },
            if contact_phone != "" {
              text(size: 7.4pt, fill: _accent-muted(brand), weight: "semibold")[Tel.]
            } else { none },
            if contact_phone != "" {
              text(size: 8.15pt, fill: color-subtle)[#contact_phone]
            } else { none },
            if contact_fax != "" {
              text(size: 7.4pt, fill: _accent-muted(brand), weight: "semibold")[Fax]
            } else { none },
            if contact_fax != "" {
              text(size: 8.15pt, fill: color-subtle)[#contact_fax]
            } else { none },
            if contact_url != "" {
              text(size: 7.4pt, fill: _accent-muted(brand), weight: "semibold")[Web]
            } else { none },
            if contact_url != "" {
              text(size: 8.15pt, fill: color-subtle)[#contact_url]
            } else { none },
            if contact_address != "" {
              text(size: 7.4pt, fill: _accent-muted(brand), weight: "semibold")[Adresse]
            } else { none },
            if contact_address != "" {
              text(size: 7.8pt, fill: color-muted)[#contact_address]
            } else { none },
          )
        ],
      )
    ]
  ] else if _has-cover-meta(date, author, author_email, version, exported_at) [
    #rect(width: 100%, fill: _accent-soft(brand), stroke: 0.7pt + _accent-line(brand), radius: 4pt, inset: 8mm)[
      #_meta-row(_label("Date", "Date", lang), date, brand: brand)
      #_meta-row(_label("Auteur", "Author", lang), author, brand: brand)
      #_meta-row(_label("Version", "Version", lang), version, brand: brand)
      #_meta-row(_label("Export", "Export", lang), exported_at, brand: brand)
    ]
  ]
}

// --- Main template ---------------------------------------------------------
#let mdpdf_document(
  body,
  title: "",
  subtitle: "",
  author: "",
  date: "",
  status: "",
  version: "",
  exported_at: "",
  short_title: "",
  template_kind: "internal",
  brand: "neutral",
  brand_label: "DOCUMENT",
  lang: "fr",
  toc: false,
  justify_body: false,
  audience: "internal",
  logo_path: "",
  contact_name: "",
  contact_role: "",
  contact_company: "",
  contact_address: "",
  contact_phone: "",
  contact_fax: "",
  contact_email: "",
  contact_url: "",
) = {
  let accent = _accent(brand)
  let stitle = if short_title == "" { title } else { short_title }

  set document(title: title, author: author)
  set text(font: ("Inter", "IBM Plex Sans", "Noto Sans", "Arial"), size: _body-size(template_kind), fill: color-text, lang: lang)
  set par(justify: justify_body, leading: _body-leading(template_kind), spacing: _para-spacing(template_kind))
  set list(
    marker: ([#text(fill: color-muted)[–]], [#text(fill: color-muted)[•]], [#text(fill: color-muted)[◦]]),
    indent: 5.8mm,
    body-indent: 4.2mm,
    spacing: _list-spacing(template_kind),
  )
  set enum(numbering: "1.", indent: 5.8mm, body-indent: 4.2mm, spacing: _list-spacing(template_kind))
  set table(stroke: 0.35pt + color-line, inset: (x: 6.4pt, y: 4.8pt), align: left + horizon)
  set block(spacing: if template_kind == "pro" { 1.04em } else { 0.86em })

  // Inline semantics.
  show link: set text(fill: accent, weight: "medium")
  show strong: set text(weight: "bold", fill: color-heading)
  show emph: set text(style: "italic", fill: color-subtle)

  // Tables: compact and editorial.
  show table: set text(size: _table-size(template_kind))
  show figure.where(kind: table): set align(left)
  show table.header: set table.cell(fill: _accent-soft-strong(brand), inset: (x: 6.8pt, y: 5.2pt))
  show table.header: set text(weight: "bold", fill: _accent-dark(brand))

  // Headings: sticky to avoid orphaned section starts near page breaks.
  show heading.where(level: 1): it => block(sticky: true, above: 1.70em, below: 1.05em)[
    #text(size: 19pt, weight: "bold", fill: accent, tracking: -0.15pt)[#it.body]
    #v(3pt)
    #line(length: 100%, stroke: 0.7pt + _accent-line(brand))
  ]
  show heading.where(level: 2): it => block(sticky: true, above: 1.35em, below: 0.90em)[
    #text(size: 13.6pt, weight: "bold", fill: color-heading)[#it.body]
  ]
  show heading.where(level: 3): it => block(sticky: true, above: 1.08em, below: 0.55em)[
    #text(size: 11.35pt, weight: "semibold", fill: color-subtle)[#it.body]
  ]

  // Code/text blocks: technical but visually subordinate.
  show raw.where(block: true): it => block(
    fill: color-code-fill,
    stroke: 0.45pt + color-line,
    radius: 4pt,
    inset: (x: 8.5pt, y: 6pt),
    width: 100%,
    above: 0.90em,
    below: 1.00em,
  )[
    #text(font: ("IBM Plex Mono", "Noto Sans Mono", "DejaVu Sans Mono"), size: _code-size(template_kind), fill: color-code-text)[#it]
  ]

  // Quotes: neutral callout styling. For Obsidian [!NOTE]/[!WARNING],
  // prefer a Pandoc Lua filter that maps callout types to the callout() helper.
  show quote: it => callout("", [
    #set par(justify: false, leading: 0.84em, spacing: 0.50em)
    #text(fill: color-heading)[#it.body]
  ], brand: brand)

  _cover(
    title: title,
    subtitle: subtitle,
    author: author,
    date: date,
    status: status,
    version: version,
    exported_at: exported_at,
    author_email: contact_email,
    brand: brand,
    brand_label: brand_label,
    template_kind: template_kind,
    lang: lang,
    logo_path: logo_path,
    show_contact: audience == "external",
    contact_name: contact_name,
    contact_role: contact_role,
    contact_company: contact_company,
    contact_address: contact_address,
    contact_phone: contact_phone,
    contact_fax: contact_fax,
    contact_email: contact_email,
    contact_url: contact_url,
  )
  pagebreak()

  if toc [
    #set page(
      paper: "a4",
      margin: (x: if template_kind == "pro" { 25mm } else { 23mm }, y: 22mm),
      header: none,
      footer: none,
    )
    #block(above: 0.5em, below: 1em)[
      #text(size: 20pt, weight: "bold", fill: color-heading)[#if lang == "en" { "Table of contents" } else { "Sommaire" }]
    ]
    #outline(title: none, depth: 3)
    #pagebreak()
  ]

  set page(
    paper: "a4",
    margin: (x: if template_kind == "pro" { 25mm } else { 23mm }, y: 22mm),
    header: none,
    footer: context grid(
      columns: (1fr, auto),
      align: (left, right),
      text(size: 7.8pt, fill: color-muted)[#stitle],
      text(size: 7.8pt, fill: color-muted)[#counter(page).display()],
    ),
  )
  counter(page).update(1)
  body
}
