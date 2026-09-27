---
title: "Exemple : prédiction de churn"
date: 2026-09-27
draft: true
description: "Modèle de prédiction d'attrition client, de l'EDA à l'API de scoring."
summary: "Modèle de prédiction d'attrition client, de l'EDA à l'API de scoring."
tags: ["python", "scikit-learn", "fastapi", "classification"]
showTableOfContents: true
---

{{< alert icon="pencil" >}}
Fiche de démonstration (`draft: true`, donc non publiée). Duplique-la pour un
vrai projet, ou supprime le dossier.
{{< /alert >}}

{{< button href="https://github.com/wilson-goma/REPO" target="_blank" >}}Code source{{< /button >}}

## Le problème

Un opérateur perd 12 % de ses abonnés par an. Les identifier un mois avant leur
départ permettrait de déclencher une offre de rétention ciblée — encore faut-il
que le modèle soit assez précis pour ne pas arroser toute la base.

## L'approche

- **Données** : 7 000 clients, 21 variables (contrat, consommation, facturation).
- **Baseline** : régression logistique, pour avoir un plancher interprétable.
- **Modèle retenu** : gradient boosting, seuil de décision calé sur le coût métier
  plutôt que sur le F1 — un faux négatif coûte bien plus cher qu'un faux positif.

## Le résultat

| Modèle               | AUC  | Rappel @ précision 50 % |
| -------------------- | ---- | ----------------------- |
| Régression logistique | 0.84 | 0.61                    |
| Gradient boosting     | 0.89 | 0.73                    |

**Limite connue** : le modèle se dégrade sur les contrats souscrits après la
refonte tarifaire, sous-représentés dans l'historique d'entraînement.

## La stack

- **Langage** : Python 3.12
- **Librairies** : polars, scikit-learn, XGBoost, SHAP
- **Service** : FastAPI + Docker
