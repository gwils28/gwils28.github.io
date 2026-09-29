---
title: "[Démo] Article de test du thème"
date: 2026-09-27
draft: false
description: "Article de démonstration et de test : il montre ce que le thème sait afficher. Il sera retiré."
summary: "Article de démonstration et de test : code, maths, encadrés. Il sera retiré."
categories: ["Veille"]
tags: ["démo", "hugo"]
showTableOfContents: true
---

{{< alert icon="triangle-exclamation" cardColor="#f59e0b" iconColor="#1f2937" textColor="#1f2937" >}}
**Article de démonstration et de test.** Il sert uniquement à vérifier le rendu
du thème (code, maths, encadrés) et sera retiré dès la publication des premiers
vrais articles.
{{< /alert >}}

Cet article montre ce que le thème sait afficher, et pose au passage ce que je
compte publier ici.

## Ce que je publie

Trois types de contenus, pas plus :

1. **Notes de veille** — ce que j'ai lu et ce que j'en retiens, en quelques paragraphes.
2. **Retours d'expérience** — un problème rencontré, la solution trouvée, le temps perdu.
3. **Projets** — dans [la section dédiée]({{< ref "/projects" >}}), avec le code.

## Le code s'affiche bien

Un exemple avec la coloration syntaxique et le bouton « copier » :

```python
import polars as pl

def charger_ventes(chemin: str) -> pl.DataFrame:
    """Charge et nettoie le jeu de ventes brut."""
    return (
        pl.scan_parquet(chemin)
        .filter(pl.col("montant") > 0)
        .with_columns(
            pl.col("date").str.to_date("%Y-%m-%d"),
            marge=pl.col("montant") - pl.col("cout"),
        )
        .collect()
    )
```

## Les maths aussi

{{< katex >}}

Blowfish rend le LaTeX — il suffit d'appeler `{{</* katex */>}}` une fois dans la
page pour charger la librairie. La perte d'entropie croisée binaire s'écrit :

$$
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} \Big[ y_i \log(\hat{y}_i) + (1 - y_i)\log(1 - \hat{y}_i) \Big]
$$

## Les encadrés

{{< alert icon="circle-info" cardColor="#3b82f6" iconColor="#fff" textColor="#fff" >}}
Les shortcodes de Blowfish (`alert`, `button`, `badge`, `chart`, `timeline`…)
sont documentés sur [blowfish.page](https://blowfish.page/docs/shortcodes/).
{{< /alert >}}

## La suite

Les vrais articles arrivent bientôt.
