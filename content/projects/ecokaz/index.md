---
title: "Ecokaz : l'énergie et le carbone d'un foyer, mesurés plutôt qu'estimés"
date: 2026-10-10
draft: true
nature: "produit"
description: "Une application web pour suivre l'électricité, le gaz, l'eau et le carburant d'un foyer, en unités, en euros et en kgCO₂e, avec un coach IA qui explique sans jamais calculer. En cours de développement : les fondations sont posées."
summary: "Copilote énergie et carbone du foyer : consommations réelles d'électricité, de gaz, d'eau et de carburant, en unités, en euros et en kgCO₂e, avec un coach IA qui explique. Les fondations sont livrées ; le domaine et l'import Linky suivent."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "llm", "claude code"]
featureImage: "carte.png"
showTableOfContents: true
---

{{< lead >}}
Savoir ce que le foyer consomme vraiment, en kWh, en euros et en CO₂, semaine après semaine,
et être prévenu quand quelque chose dérape. Avec des chiffres qu'on peut toujours vérifier.
{{< /lead >}}

{{< fiche-projet
    statut="En développement · lot 0 sur 9 livré"
    periode="Depuis octobre 2026"
    role="Solo : cadrage, architecture, développement"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 17, React 19, TypeScript, Vite, Tailwind, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/Ecokaz" >}}

{{< stats >}}
{{< stat value="9" label="lots planifiés" >}}chacun clos par une preuve, pas par une impression{{< /stat >}}
{{< stat value="17 500" label="mesures par an" >}}la courbe de charge Linky au pas de 30 minutes{{< /stat >}}
{{< stat value="0" label="chiffre calculé par le LLM" >}}le coach appelle des fonctions testées, puis commente{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Projet en cours.** Cette fiche décrit l'état du dépôt au 10 octobre 2026 : le plan est validé
et les fondations sont posées. Elle sera mise à jour à chaque lot livré.
{{< /alert >}}

## Le problème

Les ordres de grandeur du bilan carbone d'un foyer sont connus : chauffage, voiture,
alimentation. Mais les calculateurs en ligne travaillent sur des déclarations (« combien de
kilomètres par an, à peu près ? ») et donnent un chiffre unique, une fois. Rien ne dit ensuite
si un changement d'habitude a vraiment fait baisser la consommation, ni pourquoi la facture
du mois a grimpé.

Les données existent pourtant : le compteur Linky mesure l'électricité toutes les demi-heures,
et les compteurs de gaz et d'eau se relèvent en dix secondes. Je voulais un outil qui parte de
ces **mesures réelles** :

- **en trois unités à la fois** : la quantité consommée, son coût, et son empreinte en kgCO₂e ;
- **comparées** au bilan déclaré de départ, pour voir l'écart entre ce qu'on croit et ce qu'on
  mesure ;
- **surveillées** : une alerte quand une consommation s'écarte de son niveau habituel, avec
  l'explication de la méthode ;
- **commentées** par un coach qui répond aux questions en langage naturel, sans jamais inventer
  un chiffre.

Le critère de réussite de la première version est volontairement concret : l'ouvrir chaque
semaine pendant deux mois, et avoir pris au moins une décision grâce à lui.

## Quatre principes non négociables

### Le LLM ne calcule jamais

Un modèle de langage qui annonce « vous avez consommé 412 kWh ce mois-ci » peut se tromper, et
personne ne s'en apercevra. Dans Ecokaz, **tout chiffre sort d'une fonction Python testée** :
conversions, coûts, émissions, anomalies, objectifs. Le coach (règles déterministes, puis
Mistral) appelle ces fonctions comme des outils et se contente d'expliquer leur résultat. Un jeu
d'évaluation sera écrit **avant** les prompts, pour vérifier qu'aucun chiffre n'est halluciné.

### Des facteurs d'émission sourcés et versionnés

Aucun facteur d'émission, prix ou coefficient de conversion n'est écrit en dur dans le code. Ils
vivent dans une seule table, chaque valeur avec sa source (Base Empreinte de l'ADEME) et sa
période de validité. Chaque kgCO₂e affiché peut ainsi être retracé jusqu'à sa source, et un
facteur mis à jour ne réécrit pas le passé.

### Une source de données, un adaptateur

L'API Conso (qui relaie les données Enedis), l'export CSV de l'espace client, les relevés
manuels de gaz, d'eau et de kilométrage : chaque source implémente la même interface et produit
des **relevés normalisés**. Ajouter une source ne touche ni le stockage ni le tableau de bord.

### Une référence simple avant un modèle

Les anomalies seront d'abord détectées par une méthode statistique simple et explicable : un
niveau de référence robuste par jour de la semaine. Un modèle de machine learning ne la
remplacera que s'il fait mieux, sur un protocole écrit à l'avance. C'est la même discipline que
dans mon travail sur les séries temporelles : on bat d'abord le modèle naïf.

## La feuille de route

Le développement est découpé en neuf lots. Aucun n'est déclaré fini sans une preuve écrite
d'avance.

| Lot | Contenu | Preuve attendue |
|---|---|---|
| 0 ✅ | Fondations : dépôt, outillage, Docker Compose, CI, configuration de Claude Code | `docker compose up` et CI au vert |
| 1 | Domaine : conversions, euros, CO₂e, relevés → consommations | tests de propriété au vert (positivité, additivité, index décroissant rejeté) |
| 2 | Électricité : import CSV Enedis, connecteur API Conso, synchronisation quotidienne | ma vraie courbe de charge importée, contrôles qualité passés (trous, doublons, unités) |
| 3 | Authentification, interface, tableau de bord électricité | captures d'écran en bureau et en mobile, thème clair et sombre |
| 4 | Déploiement sur un serveur en Europe | URL en HTTPS, restauration de sauvegarde testée |
| 5 | Gaz, eau, voiture, tarifs, tableau de bord multi-catégories | totaux cohérents avec mes factures, écart expliqué |
| 6 | Bilan carbone déclaré, comparé au mesuré | résultat confronté à Nos Gestes Climat sur mon profil |
| 7 | Objectifs et détection des pics | tests sur séries synthétiques : pic injecté détecté, série plate sans fausse alerte |
| 8 | Coach : règles, puis Mistral en appel d'outils | jeu d'évaluation versionné, aucun chiffre halluciné |

Le déploiement arrive volontairement tôt (lot 4) : un outil qu'on n'utilise pas au quotidien ne
peut pas remplir son critère de réussite.

## Comment c'est construit

### Un monolithe modulaire

Une API FastAPI découpée en modules : `domain` pour les calculs purs, `sources` pour les
adaptateurs, `coach` pour les règles et le client Mistral, `api` pour les routes, `jobs` pour la
synchronisation quotidienne. Les règles métier vivent dans un paquet sans aucune entrée-sortie,
testé avec des tests de propriété (Hypothesis). En face, une interface React reprend la charte
graphique de ce blog, servie derrière Caddy.

Quelques choix délibérément sobres :

- **PostgreSQL sans extension de séries temporelles.** Au pas de 30 minutes, l'électricité
  représente environ 17 500 points par an : une base classique suffit largement.
- **Pas de file de tâches.** La synchronisation quotidienne tourne avec un planificateur
  intégré, sans Celery ni Redis.
- **Des décimaux exacts.** Quantités et montants sont des `Decimal` / `NUMERIC`, jamais des
  flottants ; les relevés sont des intervalles semi-ouverts en UTC, et un index de compteur qui
  diminue est rejeté, pas corrigé en silence.
- **Pas de découpage inventé.** Deux relevés de gaz espacés de trois semaines donnent une
  consommation sur trois semaines, sans la répartir jour par jour.

### Un socle hérité de Kwak Finance

Les fondations reprennent celles de [Kwak Finance](/projects/kwak-finance/), mon autre produit :
mêmes conventions, mêmes hooks, même configuration de Claude Code. Repartir d'un socle éprouvé a
fait gagner du temps, mais la relecture a révélé des défauts hérités : les migrations ne voyaient
aucun modèle, le conteneur de l'API ne les appliquait jamais, et l'interface recevait les
identifiants de la base. Tous sont corrigés, et consignés dans le journal des écarts au plan.

### Développé avec un agent, sous contrôle

Comme Kwak Finance, le projet applique la méthode décrite dans
[mon article sur Claude Code](/posts/claude-code-data-science/) : ce qui doit toujours être vrai
devient un hook, pas une consigne.

- **Je suis le seul auteur des commits.** L'agent prépare le changement et propose un message au
  format Conventional Commits ; un hook Git et la CI refusent tout autre format et tout
  co-auteur.
- **Les données du foyer sont hors d'atteinte.** Un hook rend le dossier `data/` en lecture seule
  et les secrets illisibles ; les jeux de test sont synthétiques.
- **« Fini » veut dire « vérifié ».** L'agent ne peut pas conclure tant que lint, typage et tests
  échouent.
- **Une relecture à froid.** Un sous-agent en lecture seule relit chaque diff et ne signale que
  les erreurs de justesse.

## La suite

Le lot 1 pose le cœur du domaine, en écrivant les tests avant le code. Le lot 2 branchera ma
vraie courbe de charge Linky, et c'est là que le projet deviendra intéressant : des séries
temporelles réelles, avec leurs trous, leurs doublons et leurs changements d'heure. Cette fiche
sera mise à jour à chaque lot livré.

## Essayer

```bash
git clone https://github.com/gwils28/Ecokaz
cd Ecokaz
cp .env.example .env   # puis changer les valeurs
make setup             # dépendances et hook Git
make check             # tout ce que lance la CI
make up                # la pile complète sur https://localhost:8453
```
