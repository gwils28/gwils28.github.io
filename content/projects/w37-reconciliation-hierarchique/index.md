---
title: "Réconciliation hiérarchique : MinT de zéro et éCO2mix"
date: 2026-10-02
draft: false
nature: "labo"
description: "Une semaine pour maîtriser la réconciliation hiérarchique : MinT réécrit en NumPy, ses limites mesurées, et un mini-projet sur les données RTE où le bottom-up gagne."
summary: "MinT réécrit de zéro, ses hypothèses testées une à une, et un mini-projet éCO2mix (12 régions → France) où le bottom-up bat la méthode de référence."
tags: ["forecasting", "réconciliation hiérarchique", "MinT", "python", "séries temporelles", "éCO2mix"]
featureImage: "cover.png"
showTableOfContents: true
---

{{< lead >}}
Comprendre la réconciliation hiérarchique assez finement pour savoir quand elle aide, quand
elle nuit, et pourquoi. Pas l'appeler : la réécrire, puis la mettre à l'épreuve sur de vraies
données.
{{< /lead >}}

{{< fiche-projet
    stack="Python 3.12, NumPy, statsforecast, HierarchicalForecast, BayesReconPy, uv, pytest"
    code="https://github.com/gwils28/W37_hierarchical_reconciliation" >}}

{{< stats >}}
{{< stat value="1,07e-5" label="écart à la bibliothèque" >}}MinT(shrink) maison face à HierarchicalForecast{{< /stat >}}
{{< stat value="+2,3 %" label="MASE régional" >}}MinT shrink face au bottom-up, sur 119 origines éCO2mix{{< /stat >}}
{{< stat value="88" label="tests" >}}77 unitaires, 11 de bout en bout{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

Ce dépôt est le laboratoire de l'article
[La réconciliation hiérarchique en forecasting : promesses et limites]({{< relref "/posts/reconciliation-hierarchique" >}}).
L'article raconte ce que j'en ai tiré ; cette fiche montre comment le travail est organisé et
comment le reproduire.

## L'objectif

Des prévisions produites série par série ne somment pas : la somme des régions ne donne pas le
total national, et quelqu'un doit trancher. La réconciliation (MinT en tête) promet de supprimer
cet arbitrage. Je voulais savoir trois choses :

- écrire la projection `P = S(S'W⁻¹S)⁻¹S'W⁻¹` de ma main, et retrouver la bibliothèque au chiffre près ;
- identifier où MinT casse : biais, quantiles, mur numérique ;
- vérifier sur de vraies données si la réconciliation améliore la précision, ou seulement la cohérence.

## La démarche

Le travail suit six blocs, un dossier chacun. Le code vit dans un seul package
(`src/w37_reconciliation`), les notebooks pédagogiques l'appellent, et chaque bloc a son
`README` (résultats) et son `TUTORIEL` (pour relancer).

{{< steps >}}
{{< step number="1" title="Veille" >}}
Quatre articles de 2026 vérifiés, une synthèse en trois points et une note sur ce qui est
surcoté : la réconciliation vendue comme un gain de précision.
{{< /step >}}
{{< step number="2" title="MinT de zéro" >}}
Shrinkage de Schäfer–Strimmer, projection oblique, trois assertions. Écart à
HierarchicalForecast : 1,07e-5. Il ne vient pas de λ, comme le plan le supposait, mais de
l'estimateur de covariance (centrage et division par T−1).
{{< /step >}}
{{< step number="3" title="System design" >}}
Un job batch matérialisé avec un contrat YAML versionné, un hash de la hiérarchie et un
quality gate qui bloque la publication.
{{< /step >}}
{{< step number="4" title="Fondamentaux" >}}
MinT propage le biais d'une seule prévision à toutes les feuilles. Appliqué à des quantiles,
il donne un vecteur cohérent et faux : 0,764 de couverture au lieu de 0,900. Seul un
échantillonnage joint est calibré.
{{< /step >}}
{{< step number="5" title="Mini-projet éCO2mix" >}}
12 régions → France, données RTE 2013-2024, backtest à origines glissantes. Le détail est
plus bas.
{{< /step >}}
{{< step number="6" title="BayesReconPy" >}}
Sur des ventes intermittentes (M5), le MinT gaussien produit des ventes négatives ; le
conditionnement bayésien n'en produit aucune, et il est le plus précis.
{{< /step >}}
{{< /steps >}}

## Le mini-projet éCO2mix

**L'objectif métier** : livrer des prévisions de consommation électrique dont la somme des
12 régions reproduit exactement le total France.

**Le protocole**, fixé avant les résultats dans `configs/eco2mix.yaml` :
- pas horaire ;
- modèles de base SeasonalNaive(168) et MSTL ;
- fenêtre d'entraînement de 52 semaines, strictement antérieure à chaque origine ;
- horizon de 24 h ;
- cinq réconciliations, comparées par MASE niveau par niveau.

Le résultat se lit en deux temps. Sur les 4 origines du protocole principal, MinT shrink
semblait gagner (−2,2 % de MASE régional). Sur **119 origines** couvrant toute l'année 2024,
il fait moins bien que le bottom-up, sur les 13 séries.

![MASE par niveau et par méthode, 119 origines de 2024](figure_cle_robustesse.svg "MASE par niveau et par méthode (moyenne ± écart-type) sur 119 origines de 2024. Le bottom-up est le meilleur aux deux niveaux.")

**La cause est démontrée par une expérience contrôlée.** MinT estime sa matrice W sur les
résidus in-sample. Ceux de MSTL sont des restes de lissage, corrélés à 0,11 entre régions, alors
que les vraies erreurs le sont à 0,56. Estimée sur les erreurs des origines passées, W ramène
MinT au niveau du bottom-up (−0,1 %, non significatif).

## Ce qui a coincé

- **Les données avant les modèles.** La Nouvelle-Aquitaine s'arrête fin 2024. La source a aussi
  un défaut de changement d'heure chaque année : doublons en mars, heure manquante en octobre.
  Une ligne absente ne lève aucune erreur, elle fausse le total en silence.
- **4 origines ne classent rien.** Le classement s'inverse sur 119 origines : il faut des tests
  appariés avec correction de Holm avant de conclure.
- **Le λ naïf ne passe pas à l'échelle.** Le tenseur `T × m × m` pèse 31 Go à m = 5 000. Passer
  par la matrice de Gram `T × T` ramène ce coût à 0,6 Go, pour le même résultat.
- **Vérifier un paquet avant de le recommander.** BayesReconPy 0.5.0 ne s'installe plus tel quel
  (PuLP 4), et sa licence est contradictoire.

## Ce que j'en retiens

- Cohérent ne veut pas dire calibré, ni plus précis : MinT garantit la cohérence, le reste est
  un bonus.
- Sur une hiérarchie plate et très corrélée, le bottom-up est le choix le plus précis et le
  plus simple à défendre.
- Une hypothèse cachée (W in-sample) peut renverser un résultat : il faut la tester, pas la
  supposer.

## Reproduire

```bash
git clone https://github.com/gwils28/W37_hierarchical_reconciliation
cd W37_hierarchical_reconciliation
uv sync && uv run pytest
make eco2mix               # télécharge les données RTE, backtest, rapport
```

Données : **Open Data Réseaux Énergies (ODRÉ) — RTE**, Licence Ouverte v2.0.
