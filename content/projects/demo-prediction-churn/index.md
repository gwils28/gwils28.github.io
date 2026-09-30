---
title: "[Démo] Prédiction de churn"
date: 2026-09-27
draft: false
description: "Projet de démonstration : prédire les départs clients un mois à l'avance, de l'EDA à l'API de scoring. Il sera retiré."
summary: "Projet de démonstration : prédire les départs clients un mois à l'avance, de l'EDA à l'API de scoring."
tags: ["démo", "python", "scikit-learn", "fastapi", "classification"]
featureImage: "cover.png"
showTableOfContents: true
---

{{< alert icon="triangle-exclamation" cardColor="#f59e0b" iconColor="#1f2937" textColor="#1f2937" >}}
**Projet de démonstration.** Les données et les chiffres sont fictifs : cette
fiche sert de modèle de mise en page pour les vrais projets, et sera retirée dès
la publication du premier.
{{< /alert >}}

{{< lead >}}
Repérer, un mois avant leur départ, les abonnés sur le point de résilier — assez
précisément pour que l'offre de rétention ne coûte pas plus cher que le churn.
{{< /lead >}}

{{< fiche-projet
    statut="Terminé"
    periode="Mars – mai 2026"
    role="Solo, de l'EDA au déploiement"
    stack="Python 3.12, polars, scikit-learn, XGBoost, SHAP, FastAPI, Docker"
    code="https://github.com/gwils28/REPO"
    demo="https://example.org" >}}

{{< stats >}}
{{< stat value="0,89" label="AUC" >}}contre 0,84 pour la baseline{{< /stat >}}
{{< stat value="58 %" label="des départs captés" >}}en ne ciblant que 20 % des clients{{< /stat >}}
{{< stat value="40 ms" label="par prédiction" >}}servie par l'API, p95{{< /stat >}}
{{< /stats >}}

## Le problème

Un opérateur perd **12 % de ses abonnés par an**. Une offre de rétention coûte
environ 30 €, un client perdu près de 400 € de marge : l'offre est rentable,
à condition de ne pas l'envoyer à toute la base.

La vraie question n'était donc pas « qui va partir ? » mais **« qui cibler, et
jusqu'où descendre dans la liste ? »** — un problème de classement et de coût,
plus que de précision brute.

## L'approche

{{< steps >}}
{{< step number="1" title="Explorer" >}}
7 000 clients, 21 variables. Deux signaux dominent dès l'EDA : le type de
contrat et l'ancienneté. Les clients au mois partent **trois fois plus**.
{{< /step >}}
{{< step number="2" title="Poser une baseline" >}}
Régression logistique : un plancher de performance, et des coefficients lisibles
pour valider l'intuition métier avant d'aller plus loin.
{{< /step >}}
{{< step number="3" title="Monter en puissance" >}}
Gradient boosting (XGBoost), validation croisée **temporelle** — on entraîne sur
le passé, on teste sur le futur, comme en production.
{{< /step >}}
{{< step number="4" title="Choisir le seuil" >}}
Seuil calé sur le **coût métier** plutôt que sur le F1 : un départ manqué coûte
treize fois plus qu'une offre envoyée pour rien.
{{< /step >}}
{{< step number="5" title="Servir" >}}
Modèle exposé derrière une API FastAPI, conteneurisée, avec les trois
principales raisons du score (SHAP) renvoyées pour chaque client.
{{< /step >}}
{{< /steps >}}

## Le résultat

La courbe de gain répond directement à la question du ciblage : en contactant
les 20 % de clients les mieux classés, on touche 58 % des futurs départs, contre
20 % au hasard.

{{< chart >}}
type: 'line',
data: {
  labels: ['0 %', '10 %', '20 %', '30 %', '40 %', '50 %', '60 %', '70 %', '80 %', '90 %', '100 %'],
  datasets: [
    { label: 'Gradient boosting', data: [0, 36, 58, 72, 82, 89, 93, 96, 98, 99, 100],
      borderColor: css(modeSombre ? '--color-primary-400' : '--color-primary-700'), backgroundColor: css(modeSombre ? '--color-primary-400' : '--color-primary-700'), borderWidth: 3, tension: 0.3 },
    { label: 'Régression logistique', data: [0, 28, 47, 61, 72, 81, 87, 92, 96, 99, 100],
      borderColor: css(modeSombre ? '--color-primary-700' : '--color-primary-300'), backgroundColor: css(modeSombre ? '--color-primary-700' : '--color-primary-300'), borderWidth: 2, tension: 0.3 },
    { label: 'Hasard', data: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      borderColor: css('--color-neutral-500'), backgroundColor: css('--color-neutral-500'), borderDash: [6, 6], borderWidth: 1.5, pointRadius: 0 }
  ]
},
options: {
  plugins: { title: { display: true, text: 'Part des départs captés selon la part de clients ciblés' } },
  scales: {
    x: { title: { display: true, text: 'Clients ciblés (par score décroissant)' } },
    y: { title: { display: true, text: 'Départs captés (%)' }, min: 0, max: 100 }
  }
}
{{< /chart >}}

| Modèle                | AUC  | Rappel @ précision 50 % | Gain net estimé / an |
| --------------------- | ---- | ----------------------- | -------------------- |
| Régression logistique | 0,84 | 0,61                    | 142 k€               |
| Gradient boosting     | 0,89 | 0,73                    | 187 k€               |

{{< alert icon="circle-info" >}}
**Limite connue** : le modèle se dégrade sur les contrats souscrits après la
refonte tarifaire, sous-représentés dans l'historique. Un réentraînement
trimestriel et un suivi de dérive sont prévus.
{{< /alert >}}

## Ce que j'en retiens

- **Le seuil compte autant que le modèle.** Passer du F1 au coût métier a
  rapporté plus que le passage de la logistique au boosting.
- **La validation temporelle est non négociable.** En validation croisée
  aléatoire, l'AUC montait à 0,93 — un chiffre flatteur et faux.
- **Expliquer chaque score** (SHAP) a fait adopter l'outil par l'équipe
  commerciale bien plus vite qu'une métrique globale.
