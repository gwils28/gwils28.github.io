# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Wilson Goma's technical blog **and** portfolio — a Hugo static site using the **Blowfish** theme (v3.5), written in French with English translations. Deployed to GitHub Pages at `https://gwils28.github.io/` via GitHub Actions. It is a **user site**, so the repo must stay named `gwils28.github.io` and the site is served from the domain root (no path prefix).

## Commands

- `hugo server -D` — dev server with drafts (http://localhost:1313/mon-blog-tech/).
- `hugo --gc` — production build into `public/`.
- `hugo new posts/<slug>/index.md` — new article (uses `archetypes/posts.md`).
- `hugo new projects/<slug>/index.md` — new portfolio entry (uses `archetypes/projects.md`).
- `hugo new jazz/etudes/<slug>/index.md` — new jazz note in the Études tab (uses `archetypes/jazz.md`).
- `hugo new migration/<slug>/index.md` — new photo album (uses `archetypes/migration.md`).
- `python3 scripts/album-photos.py <photos-dir> <slug>` — preferred way to fill an album: auto-rotates, resizes to 2500 px, strips all EXIF (GPS), numbers files by capture date, creates the album if missing. Keeps the repo light — originals never go in.
- `git submodule update --init --recursive` — required after a fresh clone; the theme is a submodule and nothing builds without it.

No test suite or linter — the build itself is the check.

## Architecture

### Config is split, not a single `hugo.toml`

Blowfish requires the `config/_default/` layout. There is **no root `hugo.toml`** — adding one would shadow this directory.

- `hugo.toml` — baseURL, taxonomies, outputs, pagination.
- `params.toml` — all theme behavior (homepage layout, article options, header/footer).
- `markup.toml` — **copied verbatim from the theme; required for it to function.** Don't set a `[highlight] style` here: Blowfish colors code via its own CSS so it adapts to light/dark, and a style would break that.
- `languages.{fr,en}.toml` — per-language title, description, and the `[params.author]` block (name, bio, social links) that feeds the homepage profile.
- `menus.{fr,en}.toml` — header and footer menus, per language.

Author identity lives in the `languages.*.toml` files, **not** in `params.toml`. Editing the profile (photo, headline, social links) means editing both language files.

### Content

- `content/posts/` — articles and veille notes.
- `content/projects/` — portfolio entries, rendered as cards (`cardView: true` in `projects/_index.md`).
- `content/jazz/` — the jazz notebook. Deliberately **not** in `mainSections`, so it stays off the tech-focused homepage. One layout (`layouts/jazz/list.html`) renders three tabs as real pages, picked by the `onglet` front-matter param: `/jazz/` = **Albums** (cards from `data/jazz/albums.yaml`, rating 0–5 in stars), `/jazz/pantheon/` = **Panthéon** (big cards from `data/jazz/pantheon.yaml`), `/jazz/etudes/` = **Études** (the actual notes, page bundles). Album covers and Panthéon photos go in `assets/img/jazz/{albums,pantheon}/` — only resized WebP copies are published. The title and intro paragraph of every tab come from `content/jazz/_index.md`.
- `content/migration/` — travel photo albums, off the homepage like jazz. Each album is a page bundle: drop photos next to `index.md` (shown in filename order; optional captions via `resources` titles, optional `cover`, `place`, `coords` front matter). Custom layouts in `layouts/migration/` (polaroid cards, masonry, `<dialog>` lightbox). `publishResources: false` is cascaded so only resized WebP copies are published — never originals, so no EXIF/GPS leaks.
- `content/cv.md` — the CV page; its tables come from `data/cv.yaml` (bilingual fr/en fields) via the `{{< cv section="..." >}}` shortcode.
- Each entry is a **page bundle** (`<slug>/index.md`) so images sit next to the Markdown and `featureImage: "cover.jpg"` resolves as a relative path.
- **Bilingual by filename suffix**: `index.md` is French (the default language), `index.en.md` is English. `defaultContentLanguageInSubdir = false`, so French is served at `/` and English at `/en/`.

### Theme customisation

`themes/blowfish/` is a git submodule — never edit inside it; changes are lost on update. To override a template, copy it to the matching path under the root `layouts/` (custom templates: `layouts/_default/about.html` for the About page, and `layouts/migration/` for the albums). Also overridden: `partials/recent-articles/main.html` (homepage split into a posts block and a projects block), `partials/article-link/card*.html` (type label from `partials/type-contenu.html`), `partials/header/components/{desktop,mobile}-menu.html` (menu entries sharing a `params.groupe` get a separator + label from `nav.groupe.<name>`), and `assets/js/chart.js` (site font + dark-mode-aware chart defaults; exposes `modeSombre` to `{{< chart >}}` bodies). Custom UI strings live in the root `i18n/{fr,en}.yaml`, merged with the theme's. Blowfish's CSS is Tailwind-based; custom styles go in `assets/css/custom.css`, which the theme picks up automatically.

Profile photo goes in `assets/img/` (referenced as `image = "img/profile.jpg"` in the language files — `resources.Get` resolves against `assets/`). Favicons live in the root `static/` (they shadow the theme's): `favicon.svg` is the source logo, the PNG/ICO sizes are rendered from it. `layouts/partials/favicons.html` emits the `<link>` tags with a `?v=` cache-buster — bump it whenever the logo changes, or browsers keep showing the old one.

### Deployment

`.github/workflows/deploy.yml` builds and publishes on push to `master`/`main`. Two things it depends on:

- The "Récupérer le thème" step (`git submodule update --init --recursive --depth 1`) — the theme won't be there otherwise. It is fetched shallow on purpose: `fetch-depth: 0` on the checkout (needed for git-based `.Lastmod`) would otherwise pull the theme's full ~600 MB history.
- `--baseURL` from `actions/configure-pages`, which overrides the config value at build time.

**`public/` is gitignored** and must stay that way — it's a build artifact produced by CI, not source. (It was previously committed under the old Relearn theme; that history was cleaned up.)

### Shortcodes worth knowing

Blowfish ships `alert`, `button`, `badge`, `chart`, `timeline`, `gallery`, `katex` and others — documented at https://blowfish.page/docs/shortcodes/. **KaTeX only loads on pages that call `{{< katex >}}` at least once**; raw `$$...$$` renders as plain text without it.
