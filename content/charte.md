---
title: "Charte graphique"
description: "Couleurs, typographie et composants du blog, lus en direct dans la feuille de style."
showDate: false
showAuthor: false
showReadingTime: false
showWordCount: false
showPagination: false
showTableOfContents: true
# Page de référence, liée depuis le pied de page : absente des listes, du flux RSS
# et de la recherche du site.
build:
  list: never
---

{{< lead >}}
Typographie affirmée, couleur sobre. Les pastilles ci-dessous lisent directement les variables
CSS du site : changer la palette met cette page à jour toute seule.
{{< /lead >}}

## Couleurs

### Vert mousse · couleur principale

Bâtie autour de `#2E6218`, à teinte constante (102°). Trop sombre pour le mode sombre (2,4:1),
la couleur source y cède la place à `primary-400`.

{{< nuancier gamme="primary" >}}

### Ambre · couleur secondaire

Tags, badges, chiffres clés ; remplace le vert sur le bloc Freelance du CV.

{{< nuancier gamme="secondary" >}}

### Neutres teintés

Des gris tirés vers le vert (teinte 100°) : un gris pur à côté du vert paraît sale.

{{< nuancier gamme="neutral" >}}

### Hors palette

Le rouge brique (`#E2A58C`, tampon `#8A3B22`), opposé du vert, réservé aux post-it
« terre cuite » du carnet jazz.

## Typographie

<div class="not-prose charte-specimens">
  <div>
    <p class="charte-etiquette">Archivo 900 · titre de page</p>
    <p class="charte-titre">Réconciliation hiérarchique</p>
  </div>
  <div>
    <p class="charte-etiquette">Archivo 800 · intertitres</p>
    <p class="charte-intertitre">Ce qui a coincé</p>
  </div>
  <div>
    <p class="charte-etiquette">IBM Plex Sans 400 · texte courant</p>
    <p class="charte-texte">Les prévisions produites série par série ne se somment pas : la somme des régions ne donne pas le total national.</p>
  </div>
  <div>
    <p class="charte-etiquette">IBM Plex Mono 400 · dates, tags, code</p>
    <p class="charte-mono">8 octobre 2026 · 1 701 mots · 0123456789</p>
  </div>
  <div>
    <p class="charte-etiquette">Caveat 700 · carnet jazz uniquement</p>
    <p class="charte-manuscrit">ii – V – I en Fa, à travailler</p>
  </div>
</div>

## Composants

### Lien, badge, bouton

Un [lien dans le texte](/posts/), puis un badge et un bouton :

{{< badge >}}Nouveau{{< /badge >}}

{{< button href="/projects/" >}}Voir les projets{{< /button >}}

### Encadré

{{< alert icon="circle-info" >}}
**Projet en cours.** Un encadré d'information, comme en tête de la fiche Kwak Finance.
{{< /alert >}}

### Chiffres clés

{{< stats >}}
{{< stat value="37" label="pull requests" >}}le chiffre en display, la légende en mono{{< /stat >}}
{{< stat value="+2,3 %" label="MASE régional" >}}deuxième exemple{{< /stat >}}
{{< /stats >}}

### Fiche projet

{{< fiche-projet
    statut="En développement"
    periode="Depuis octobre 2026"
    role="Solo"
    stack="Python, FastAPI, PostgreSQL"
    code="https://github.com/gwils28" >}}

### Code et tableau

```python
def solde(ouverture: Decimal, operations: list[Decimal]) -> Decimal:
    return ouverture + sum(operations, Decimal(0))
```

| Exemple | Valeur | Écart |
|---|---:|---:|
| Référence | 1 000,00 | — |
| Variante | 1 023,00 | +2,3 % |
