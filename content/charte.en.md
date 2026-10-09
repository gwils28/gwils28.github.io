---
title: "Style guide"
description: "The blog's colours, typography and components, read live from the stylesheet."
showDate: false
showAuthor: false
showReadingTime: false
showWordCount: false
showPagination: false
showTableOfContents: true
# Reference page, linked from the footer: kept out of lists, the RSS feed
# and the site search.
build:
  list: never
---

{{< lead >}}
Bold typography, restrained colour. The swatches below read the site's CSS variables directly:
changing the palette updates this page on its own.
{{< /lead >}}

## Colours

### Moss green · primary colour

Built around `#2E6218`, at a constant hue (102°). Too dark for dark mode (2.4:1), the source
colour gives way to `primary-400` there.

{{< nuancier gamme="primary" >}}

### Amber · secondary colour

Tags, badges, key figures; replaces the green on the Freelance block of the CV.

{{< nuancier gamme="secondary" >}}

### Tinted neutrals

Greys pulled towards green (hue 100°): a pure grey next to green looks dirty.

{{< nuancier gamme="neutral" >}}

### Off-palette

Brick red (`#E2A58C`, stamp `#8A3B22`), the opposite of green, reserved for the "terracotta"
sticky notes of the jazz notebook.

## Typography

<div class="not-prose charte-specimens">
  <div>
    <p class="charte-etiquette">Archivo 900 · page title</p>
    <p class="charte-titre">Hierarchical reconciliation</p>
  </div>
  <div>
    <p class="charte-etiquette">Archivo 800 · headings</p>
    <p class="charte-intertitre">What got stuck</p>
  </div>
  <div>
    <p class="charte-etiquette">IBM Plex Sans 400 · body text</p>
    <p class="charte-texte">Forecasts produced series by series don't add up: the regions don't sum to the national total.</p>
  </div>
  <div>
    <p class="charte-etiquette">IBM Plex Mono 400 · dates, tags, code</p>
    <p class="charte-mono">8 October 2026 · 1,701 words · 0123456789</p>
  </div>
  <div>
    <p class="charte-etiquette">Caveat 700 · jazz notebook only</p>
    <p class="charte-manuscrit">ii – V – I in F, to practise</p>
  </div>
</div>

## Components

### Link, badge, button

A [link in the text](/en/posts/), then a badge and a button:

{{< badge >}}New{{< /badge >}}

{{< button href="/en/projects/" >}}See the projects{{< /button >}}

### Callout

{{< alert icon="circle-info" >}}
**Work in progress.** An information callout, as at the top of the Kwak Finance page.
{{< /alert >}}

### Key figures

{{< stats >}}
{{< stat value="37" label="pull requests" >}}the figure in display type, the caption in mono{{< /stat >}}
{{< stat value="+2.3%" label="regional MASE" >}}second example{{< /stat >}}
{{< /stats >}}

### Project card

{{< fiche-projet
    statut="In development"
    periode="Since October 2026"
    role="Solo"
    stack="Python, FastAPI, PostgreSQL"
    code="https://github.com/gwils28" >}}

### Code and table

```python
def balance(opening: Decimal, transactions: list[Decimal]) -> Decimal:
    return opening + sum(transactions, Decimal(0))
```

| Example | Value | Gap |
|---|---:|---:|
| Baseline | 1,000.00 | — |
| Variant | 1,023.00 | +2.3% |
