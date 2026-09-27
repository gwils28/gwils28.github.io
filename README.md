# Mes notes & veille

Blog technique et portfolio de **Wilson Goma**, Data Scientist. Notes de veille,
retours d'expérience et projets personnels — en français, avec traductions
anglaises.

**→ [gwils28.github.io](https://gwils28.github.io/)**

Site statique construit avec [Hugo](https://gohugo.io/) et le thème
[Blowfish](https://blowfish.page/), publié automatiquement sur GitHub Pages à
chaque push.

---

## Démarrer en local

**Prérequis :** Hugo ≥ 0.165 et Git. Blowfish livre son CSS déjà compilé — la
version *extended* n'est donc pas indispensable, mais c'est elle qu'utilise la
CI, et l'installer en local garantit un build identique.

```bash
# Le thème est un sous-module : sans --recursive, rien ne se construit.
git clone --recursive git@github.com:gwils28/gwils28.github.io.git
cd gwils28.github.io

hugo server -D          # http://localhost:1313/ — brouillons inclus
```

Si le dépôt a été cloné sans `--recursive` :

```bash
git submodule update --init --recursive
```

| Commande | Effet |
| --- | --- |
| `hugo server -D` | Serveur local, rechargement à chaud, brouillons visibles |
| `hugo server` | Idem sans les brouillons — l'aperçu fidèle du site publié |
| `hugo --gc` | Build de production dans `public/` |

Il n'y a ni tests ni linter : **le build fait office de vérification**.

---

## Écrire

```bash
hugo new posts/mon-sujet/index.md       # un article
hugo new projects/mon-projet/index.md   # une fiche projet
```

Les gabarits (`archetypes/`) pré-remplissent le front matter et la structure
attendue. Chaque entrée est un **page bundle** — un dossier contenant son
`index.md` — pour que les images vivent à côté du texte :

```
content/posts/mon-sujet/
├── index.md
└── cover.jpg          → featureImage: "cover.jpg"
```

Un article reste invisible en ligne tant que `draft: true` figure dans son front
matter. Le retirer et pousser suffit à le publier.

### Traduire une page

Le suffixe de langue dans le nom de fichier fait tout le travail :

```
index.md        → français, servi à la racine       /posts/mon-sujet/
index.en.md     → anglais,  servi sous /en/      /en/posts/mon-sujet/
```

Aucune traduction n'est obligatoire : une page sans version anglaise
n'apparaît simplement pas dans le site anglais.

---

## Publier

Un push sur `master` déclenche [le workflow](.github/workflows/deploy.yml), qui
construit le site et le déploie sur GitHub Pages (~1 min).

```bash
git add -A && git commit -m "Nouvel article : mon sujet" && git push
```

> **`public/` est volontairement absent du dépôt.** C'est un artefact de build
> produit par la CI. Le versionner rendrait chaque commit d'article illisible
> sous des centaines de fichiers générés.

Deux points dont dépend le workflow, à ne pas casser :

- `submodules: recursive` à l'étape de checkout — sans ça, pas de thème ;
- la source Pages réglée sur **GitHub Actions** dans les réglages du dépôt, et
  non sur « Deploy from a branch ».

---

## Structure

```
config/_default/     Configuration éclatée, comme l'exige Blowfish
├── hugo.toml          baseURL, taxonomies, pagination
├── params.toml        Comportement du thème
├── markup.toml        Rendu Markdown — copie du thème, requise telle quelle
├── languages.*.toml   Titre, description et profil auteur, par langue
└── menus.*.toml       Menus d'en-tête et de pied, par langue

content/
├── posts/           Articles et notes de veille
└── projects/        Portfolio, affiché en cartes

assets/
├── css/custom.css       Surcharges — chargé en dernier, donc prioritaire
├── css/schemes/         Palette sur mesure (voir plus bas)
└── img/profile.jpg      Photo de profil

layouts/partials/
└── extend-head.html  Point d'extension du thème : chargement des polices

archetypes/          Gabarits utilisés par `hugo new`
themes/blowfish/     Sous-module Git — ne jamais éditer directement
```

L'identité de l'auteur (nom, bio, liens sociaux) vit dans les fichiers
`languages.*.toml`, **pas** dans `params.toml` : la modifier suppose donc
d'éditer les deux langues.

---

## Design

Palette sur mesure définie dans `assets/css/schemes/mousse.css`, bâtie autour
d'un vert forêt — `#2E6218`, soit `hsl(102°, 61%, 24%)`.

Cette couleur est trop sombre pour servir d'accent sur fond sombre (2,4:1, sous
le seuil lisible). Elle est donc **étagée** plutôt que remplacée :

| Nuance | Rôle | Contraste |
| --- | --- | --- |
| `primary-400` `#73C251` | Liens en mode sombre | 8,6:1 — AAA |
| `primary-700` `#2E6218` | Liens en mode clair | 7,3:1 — AAA |
| `neutral-800` `#181D16` | Fond en mode sombre | — |
| `secondary-400` `#F3B73F` | Catégories, chiffres clés | — |

Les gris portent une pointe de la même teinte (100°) : un gris neutre à côté
d'un vert paraît sale.

**Typographie** — [Archivo](https://fonts.google.com/specimen/Archivo) 800/900
pour les titres, [IBM Plex Sans](https://fonts.google.com/specimen/IBM+Plex+Sans)
et [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono) pour le corps
et le code. Chargées via `layouts/partials/extend-head.html`.

### Personnaliser

Le thème est un sous-module : **toute modification à l'intérieur de
`themes/blowfish/` sera perdue** à la prochaine mise à jour. Les points
d'accroche prévus :

- `assets/css/custom.css` — ajouté en dernier au bundle CSS, donc prioritaire ;
- `layouts/` — un fichier placé au même chemin relatif que dans le thème le
  remplace ;
- `assets/css/schemes/<nom>.css` + `colorScheme = "<nom>"` — nouvelle palette.

Attention aux maths : KaTeX n'est chargé que sur les pages appelant au moins une
fois `{{< katex >}}`. Sans ce shortcode, un `$$...$$` s'affiche en texte brut.

---

## Crédits

Thème [Blowfish](https://github.com/nunocoracao/blowfish) de Nuno Coração,
sous licence MIT.

Le code de configuration de ce dépôt est librement réutilisable. Les **articles
et leurs illustrations** restent la propriété de leur auteur.
