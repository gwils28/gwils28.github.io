---
title: "Kwak Finance : le budget et le patrimoine d'un foyer, auto-hébergés"
date: 2026-10-08
draft: false
nature: "produit"
description: "Une application web auto-hébergée pour suivre le budget et le patrimoine d'un foyer, sans que les données quittent la maison. En cours de développement : le budget complet et le suivi du patrimoine sont livrés, la data science arrive."
summary: "Application web auto-hébergée de budget et de patrimoine familial. Import et rapprochement bancaires, plans budgétaires avec bilan et flux d'argent, opérations récurrentes, rapports, matrice de patrimoine mensuelle ; prévision et IA locale suivent."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "claude code"]
featureImage: "carte.png"
showTableOfContents: true
---

{{< lead >}}
Savoir où part l'argent du foyer, mois après mois, et ce que vaut son patrimoine, sans confier
ses relevés bancaires à un service en ligne. Tout tourne sur une machine de la maison.
{{< /lead >}}

{{< fiche-projet
    statut="En développement · phases 1 à 3 livrées, phase 4 à venir"
    periode="Depuis octobre 2026"
    role="Solo : spécifications, architecture, développement, exploitation"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL 17, React 19, TypeScript, Tailwind, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/kwak-finance" >}}

{{< stats >}}
{{< stat value="99" label="pull requests fusionnées" >}}chacune bloquée tant que la CI n'est pas verte{{< /stat >}}
{{< stat value="910" label="tests automatisés" >}}dont 48 tests de propriété sur les invariants financiers{{< /stat >}}
{{< stat value="8" label="décisions d'architecture" >}}écrites, avec les alternatives rejetées{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Projet en cours.** Cette fiche décrit l'état du dépôt au 15 octobre 2026. Les chiffres
ci-dessus sont comptés dans le code, et seront mis à jour à chaque phase livrée.
{{< /alert >}}

{{< alert icon="image" >}}
**Toutes les captures montrent des données fictives.** Elles viennent d'une instance de
démonstration, alimentée par un foyer inventé (Camille et Sam, quatre comptes, deux ans
d'opérations générées, une dizaine de placements). Aucun montant, libellé ni solde ne provient
de comptes réels.
{{< /alert >}}

## Le problème

Les applications de budget grand public demandent presque toutes la même chose : un accès à vos
comptes bancaires, et l'hébergement de votre historique financier sur leurs serveurs. Les
tableurs, eux, ne demandent rien, mais s'abandonnent au bout de trois mois : ressaisir, recopier
et catégoriser à la main coûte trop cher.

Je voulais un outil entre les deux :

- **privé par construction** : les données restent sur une machine du foyer, sans télémétrie ni
  service tiers ;
- **alimenté sans effort** : on importe l'export CSV de la banque, et les dépenses se rangent
  seules dans leurs catégories ;
- **juste au centime** : chaque total doit pouvoir se recalculer à partir des opérations ;
- **prêt pour la data science** : prévision de trésorerie, simulation de patrimoine et
  assistant en langage naturel doivent pouvoir s'ajouter sans refaire le socle.

C'est aussi mon premier produit : un projet qui doit tenir dans la durée, pas une expérience
jetable. Il me sert donc de terrain d'application pour
[ma méthode de travail avec Claude Code](/posts/claude-code-data-science/).

## Où en est le projet

{{< timeline >}}

{{< timelineItem icon="check" header="Phase 0 · Fondations" badge="Livrée" subheader="Socle technique" >}}
Spécifications, architecture et décisions écrites avant la première ligne de code. Dépôt,
outillage, intégration continue, pile Docker Compose, configuration de Claude Code et charte
graphique reprise de ce blog.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 1 · Budget" badge="Livrée" subheader="Le cœur du produit" >}}
Authentification à double facteur, foyer et invitations, comptes, import bancaire, saisie
manuelle, catégorisation par règles, virements internes, matrice budgétaire, indicateurs de
dépenses et sauvegardes automatiques. Interface en français et en anglais.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 2 · Budget complet" badge="Livrée" subheader="Ce qui rend l'outil quotidien" >}}
Plans budgétaires par période avec leur bilan (projection, dérives, flux d'argent, comparaison),
compte commun et vues par périmètre, mois budgétaire, catégories d'épargne, opérations
récurrentes et solde projeté, rapprochement des saisies avec le relevé, ventilation et notes,
rapports par période, journal d'activité. Le partage des dépenses communes a été abandonné en
route.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 3 · Patrimoine" badge="Livrée" subheader="Actifs et passifs, mois par mois" >}}
Une matrice de patrimoine mensuelle : catégories et lignes saisies à la main, dettes, valeur
nette, et quatre graphiques (historique, répartition en sunburst et en mosaïque, contributions à
la variation). Recadrée en cours de route, voir plus bas.
{{< /timelineItem >}}

{{< timelineItem icon="lightbulb" header="Phase 4 · Analyse et data science" badge="À venir" subheader="Là où mon métier entre en jeu" >}}
Prévision de trésorerie, évaluée par backtest à origine glissante contre un modèle naïf, et
simulation de patrimoine par Monte-Carlo (scénarios d'allocation, projection de retraite).
{{< /timelineItem >}}

{{< timelineItem icon="wand-magic-sparkles" header="Phase 5 · IA générative locale" badge="À venir" subheader="Sans que rien ne sorte de la machine" >}}
Un assistant qui répond en langage naturel sur ses propres données, à partir d'un modèle de
langage local (Ollama), limité à une vue analytique en lecture seule.
{{< /timelineItem >}}

{{< /timeline >}}

## Ce qui fonctionne aujourd'hui

### Un foyer, des comptes, trois points de vue

Le propriétaire crée le foyer et invite les autres membres par un lien à usage unique ; il n'y a
pas d'inscription publique. Connexion par mot de passe (argon2id) et code TOTP obligatoire.

Chaque compte a une visibilité :

- **privé** : son titulaire seul le voit ;
- **partagé** : tout le foyer le voit, mais il reste à son titulaire ;
- **commun** : le compte joint qui paie le loyer et les courses, qui n'est à personne.

Toutes les vues agrégées se lisent ensuite à l'échelle du **foyer**, des **comptes communs** ou de
**mes comptes**. Dans une vue restreinte, la participation de chacun au compte commun apparaît
comme de l'argent « reçu d'autres comptes » ; à l'échelle du foyer, ces virements s'annulent.

### La vue d'ensemble

La page d'accueil résume le mois et l'application entière : valeur nette du foyer, dépenses,
revenus, solde et taux d'épargne, comparés au mois précédent et à la moyenne sur douze mois.

![La vue d'ensemble d'octobre](vue-ensemble.webp "Octobre à l'échelle du foyer : patrimoine net et sa variation, puis les indicateurs du mois. Données fictives.")

En dessous, **les objectifs du mois** : une barre par catégorie budgétée, triée par part
consommée. Le trait vertical marque la part du mois écoulée, si bien qu'une dépense en avance
sur le calendrier se voit avant de dépasser.

![Les objectifs du mois en cours](mois-en-cours.webp "Au 15 octobre : les restaurants ont déjà doublé leur objectif ; le loyer, payé en une fois, n'est pas jugé sur le rythme du mois. Données fictives.")

- « Attention » à partir d'un seuil réglable (80 % par défaut) ;
- les catégories **ponctuelles** (loyer, abonnements), payées en début de mois, échappent au
  rythme : on ne les signale jamais pour avoir été payées.

Enfin, ce qui reste **attendu d'ici la fin du mois**, avec le solde projeté. Rien n'est saisi
tout seul : « La saisir » ouvre une saisie pré-remplie.

![Ce qui reste attendu ce mois-ci](echeances.webp "Une assurance en retard, deux salaires à venir, et le solde projeté en fin de mois. Données fictives.")

### Importer et rapprocher

Les banques n'exportent un relevé qu'une fois par mois : la plupart des opérations sont donc
saisies à la main pendant le mois, et le relevé arrive après. L'import affiche un **aperçu**
avant d'écrire quoi que ce soit, et reconnaît ce qui a déjà été saisi.

![Aperçu d'un relevé déjà saisi à la main](rapprochement.webp "Le relevé d'octobre, après deux semaines de saisies : seize lignes reconnues « déjà saisies », une seule nouvelle. Données fictives.")

- une ligne du relevé **correspond** à une saisie du même compte, au même montant exact, à
  cinq jours près ; « Pas la même » défait un rapprochement erroné ;
- la saisie garde sa catégorie et prend la date de la banque ;
- chaque opération a une empreinte : **réimporter le même fichier ne change rien** ;
- le solde calculé est comparé à celui de la banque, et tout import peut être annulé.

Deux banques sont prises en charge, avec trois mises en page.

### Catégoriser une fois, plus jamais

Une arborescence de catégories à deux niveaux, et des **règles** ordonnées (« le libellé
contient… », montant, compte) appliquées à chaque import et à chaque saisie. Ce qu'elles n'ont
pas reconnu reste signalé « à catégoriser ».

![La liste des opérations d'octobre](operations.webp "Les opérations de tout le foyer : la catégorie se choisit sur la ligne ; celle qu'aucune règle n'a reconnue est signalée. Données fictives.")

![Les règles de catégorisation](regles.webp "Les règles, appliquées dans l'ordre : la première qui correspond fixe la catégorie. Données fictives.")

Les virements entre ses propres comptes sont détectés puis reliés, ou saisis directement comme
virement : ils sortent des dépenses et des revenus.

![Virements internes reliés entre les comptes du foyer](virements.webp "Virements reliés : épargne vers le livret, participations au compte commun. Ni dépense ni revenu. Données fictives.")

Une opération peut aussi être **ventilée** sur plusieurs catégories (la dernière part prend le
reste, si bien que la somme tombe toujours juste) et porter une **note**, que la recherche
retrouve.

![Une opération ventilée, avec sa note](ventilation.webp "Un passage au supermarché ventilé entre les courses et la maison. Données fictives.")

### Le mois budgétaire

Un salaire versé le 28 paie les dépenses du mois suivant. Chaque opération garde sa vraie date,
mais compte aussi dans un **mois budgétaire** : décalé au mois suivant par sa catégorie à partir
d'un jour donné, ou fixé à la main.

![Des salaires comptés le mois suivant](mois-budgetaire.webp "Les salaires de fin septembre comptent pour octobre : la date réelle reste, le mois budgétaire s'affiche dessous. Données fictives.")

Tous les chiffres par mois suivent le mois budgétaire ; les soldes gardent la date réelle. Une
troisième nature de catégorie, l'**épargne** (un PEA, une assurance-vie que l'application ne
suit pas), n'est jamais une dépense, et peut recevoir un objectif minimum.

### Les opérations récurrentes

Salaire, loyer, abonnements, électricité : une **récurrence** décrit une opération attendue, à
montant fixe ou estimé sur ses trois dernières occurrences (« ≈ »). L'application en suggère à
partir de l'historique, à suivre ou à ignorer.

![La page des récurrences](recurrences.webp "En haut, les séries repérées dans l'historique ; en dessous, les récurrences suivies, avec leur prochaine échéance et celle qui est en retard. Données fictives.")

Chaque opération qui arrive honore au plus une occurrence ; une occurrence non honorée passe
« en retard ». Un virement mensuel vers le compte commun est une récurrence comme une autre.

### Des plans budgétaires par période

Un objectif mensuel par catégorie ne survit pas à la vie réelle. Les objectifs vivent donc dans
des **plans** d'un trimestre, d'un semestre ou d'une année :

- un mois moins cher compense un mois plus cher dans l'enveloppe du plan ;
- un nouveau plan reprend les objectifs du précédent ;
- il reste modifiable pendant son premier mois ; ensuite, on le **clôture par anticipation**,
  avec un motif, et un plan de remplacement couvre le reste de la période ;
- chaque objectif dit qui paie : le compte commun ou les comptes personnels.

La matrice budgétaire reste la vue centrale : une ligne par catégorie, une colonne par mois,
chaque case colorée selon l'écart à l'objectif du plan qui couvre ce mois.

![Le plan du trimestre et la matrice budgétaire](matrice.webp "Le plan du trimestre (revenu attendu, objectifs et qui les paie), puis la matrice. Vert : sous l'objectif ; gris : à ±5 % ; terre brûlée : au-dessus. Données fictives.")

### Le bilan du plan

C'est la partie qui ressemble le plus à mon métier. Pendant un plan, le bilan dit où l'on en est
et surtout où l'on va finir : une **projection** en fin de plan, et la liste des catégories qui
**dérapent**.

![Synthèse du plan en cours et catégorie qui dérape](bilan-synthese.webp "Le trimestre en cours au 15 octobre : les restaurants sont projetés à 200 € au-dessus de leur enveloppe. Données fictives.")

La projection n'est pas une règle de trois :

- les mois terminés comptent tels quels ;
- le mois en cours et les suivants comptent au moins pour leur objectif, ou pour la moyenne des
  mois terminés si elle est plus élevée ;
- un loyer prélevé le 1er n'est donc pas une dérive, alors qu'une dépense au-dessus de
  l'objectif se voit tout de suite.

Une fois le plan terminé, le même écran donne le résultat final, l'épargne réalisée et l'épargne
prévue.

![Le bilan d'un plan terminé](bilan-final.webp "Le trimestre d'été, terminé : 5 % sous l'enveloppe, 38 % d'épargne. Données fictives.")

Deux graphiques suivent : l'écart par catégorie, dans les couleurs de la matrice, et les dépenses
cumulées jour après jour face à la ligne d'enveloppe.

![Écart par catégorie et dépenses cumulées](bilan-graphiques.webp "Trimestre d'été : écart final par catégorie, et cumul des dépenses face à la ligne d'enveloppe. Données fictives.")

Le diagramme de flux montre d'où vient l'argent du plan et où il va. Les deux côtés ont toujours
le même total.

![Les flux d'argent du plan](bilan-flux.webp "Les flux du trimestre d'été : les salaires à gauche ; dépenses, épargne et reste non alloué à droite. Les catégories au-dessus de leur objectif sont plus foncées. Données fictives.")

Enfin, deux plans côte à côte, en moyennes mensuelles pour que des plans de durées différentes
restent comparables.

![Comparaison entre deux plans](bilan-comparaison.webp "Le trimestre de printemps face au trimestre d'été : objectifs, dépense mensuelle moyenne et évolution. Données fictives.")

### Des rapports sur n'importe quelle période

Un mois, un trimestre, une année ou toute période jusqu'à dix ans, comparée à la **précédente de
même longueur**. Une période en cours s'arrête au mois courant : « cette année » se compare aux
mêmes mois de l'an dernier, pas à une année entière.

![Les totaux d'un rapport](rapport.webp "Cette année jusqu'à octobre, face aux mêmes mois de l'an dernier. Données fictives.")

![Le rapport par catégorie](rapport-categories.webp "Le détail par catégorie : total, moyenne mensuelle, part et évolution. Données fictives.")

Le rapport donne aussi un graphique mensuel et les flux d'argent de la période. Le propriétaire
peut fixer un **début des analyses** : l'historique plus ancien, souvent incomplet, ne fausse
plus les moyennes.

### Le patrimoine, mois par mois

Le patrimoine se suit comme dans un tableur : une ligne par placement, rangée dans une catégorie,
une colonne par mois, et une valeur saisie à la main une fois par mois.

![La matrice de patrimoine](patrimoine-matrice.webp "Le suivi mensuel : valeur nette, actif brut et dettes, puis les lignes par catégorie et la part de chacune. Données fictives.")

- un mois sans saisie reprend la valeur précédente, affichée comme reportée ;
- « Mettre à jour ce mois-ci » liste toutes les lignes avec leur dernière valeur, pour tout
  saisir d'un coup ;
- chaque ligne a un titulaire et une visibilité, comme un compte.

Une page *Analyse* donne quatre graphiques, chaque catégorie dans sa couleur. Comme dix teintes
ne peuvent pas toutes rester distinctes pour tous les daltonismes, chaque graphique garde aussi
ses libellés et son tableau de données.

![La valeur nette dans le temps](patrimoine-temps.webp "Les catégories empilées mois par mois, les dettes sous zéro, et la valeur nette en ligne. Données fictives.")

![La répartition en sunburst et en mosaïque](patrimoine-repartition.webp "La répartition d'octobre : catégories puis lignes dans le sunburst, une tuile par catégorie dans la mosaïque. Données fictives.")

![Ce qui a fait bouger le patrimoine](patrimoine-variation.webp "De novembre 2025 à octobre 2026, la contribution de chaque catégorie à la valeur nette ; le prêt remboursé la fait monter. Données fictives.")

L'application est rangée en deux espaces, **Dépenses** et **Patrimoine**, chacun avec ses
onglets ; la vue d'ensemble, en tête, résume les deux.

### Des sauvegardes vérifiées, des actions tracées

Une sauvegarde complète chaque nuit, contrôlée avant d'être conservée, avec une rotation
(7 jours, 4 semaines, 12 mois) et une procédure de restauration écrite.

Un **journal d'activité** garde les actions sensibles, écrites dans la même transaction que
l'action elle-même. Le propriétaire voit tout le foyer, un membre ses propres entrées.

![Le journal d'activité](journal.webp "Connexions (dont un mot de passe erroné), invitation envoyée puis annulée, suppression, imports. Données fictives.")

## Comment c'est construit

### Une architecture simple, pensée pour la suite

Tout démarre d'un seul `docker compose up` : un proxy Caddy en TLS sur le réseau local, une API
FastAPI, une base PostgreSQL et un service de sauvegarde. L'interface React est servie depuis la
même origine que l'API, ce qui permet des sessions par cookie sans configuration CORS.

Côté Python, le code est découpé en paquets avec une règle stricte : `kwak_core` contient
**toutes les règles métier** (montants, soldes, empreintes de déduplication, règles de
catégorisation, plans, projection, flux, indicateurs, récurrences, patrimoine) et ne dépend de rien. Il se teste sans base
de données. L'API et la future couche analytique en dépendent, jamais l'inverse : un même chiffre
n'a qu'une seule définition.

Le contrat entre l'API et l'interface est le schéma OpenAPI : le client TypeScript en est
**généré**, jamais écrit à la main. La CI échoue si quelqu'un oublie de le régénérer.

### L'argent ne supporte pas l'à-peu-près

Les montants sont des décimaux exacts (`Decimal` en Python, `NUMERIC` en base), jamais des
flottants. Et les règles qui doivent toujours être vraies sont écrites dans les spécifications
puis vérifiées par des **tests de propriété** (Hypothesis) : au lieu de quelques exemples choisis à
la main, le test génère des centaines de cas et cherche celui qui casse la règle.

| Invariant | Ce que le test vérifie |
|---|---|
| Solde | Le solde d'un compte vaut son solde d'ouverture plus ses opérations, quel que soit leur ordre |
| Import idempotent | Importer deux fois le même fichier ne change rien |
| Virements | Un virement relié s'annule entre les deux comptes et n'est jamais réutilisé |
| Matrice | La ligne total égale la somme des catégories plus le « à catégoriser » |
| Plans | Deux plans ne se chevauchent jamais, et une enveloppe vaut l'objectif mensuel fois le nombre de mois |
| Flux | Les deux côtés du diagramme de flux ont le même total |
| Ventilation | Les parts d'une opération ventilée font exactement son montant, chacune de son signe |
| Mois budgétaire | Revenus, dépenses et épargne sont les mêmes, sommés sur tous les mois, par mois budgétaire que par date réelle |
| Rapprochement | Un relevé déjà saisi à la main n'ajoute que les lignes sans saisie, et le solde est celui du relevé seul |
| Cohérence | Un rapport, la matrice, le bilan d'un plan et le mois en cours donnent toujours les mêmes chiffres |
| Patrimoine | La valeur nette d'un mois vaut ses actifs moins ses dettes, et le foyer est la somme exacte de ses périmètres |
| Format bancaire | Tout ce que la banque écrit est relu exactement |
| Visibilité | Un autre membre ne voit que les comptes partagés et communs |

Les tests d'API tournent contre un **vrai PostgreSQL** lancé dans un conteneur, jamais contre une
base simulée.

### Des décisions écrites

Chaque choix structurant fait l'objet d'une note de décision (ADR), datée, avec ses alternatives
rejetées. Une décision qui change donne une nouvelle note ; l'ancienne n'est jamais réécrite.

| Décision | Plutôt que |
|---|---|
| Auto-hébergement en Docker Compose | Un hébergement cloud : coût inutile et données financières exposées |
| FastAPI, SQLAlchemy 2, Alembic | Django : plus lourd, et l'interface d'administration ne sert pas |
| PostgreSQL, puis DuckDB pour l'analyse | SQLite seul : écritures concurrentes, pas d'extension vectorielle |
| Euro uniquement | Une comptabilité multidevise complète, trop coûteuse pour un seul besoin réel |
| Sessions serveur et TOTP obligatoire | Des jetons JWT, difficiles à révoquer |
| Modèle de langage local (Ollama) | Une API dans le cloud : les données ne doivent jamais quitter la machine |

Les écarts au plan initial sont, eux aussi, journalisés dans le `README`, au jour près.

### Développé avec un agent, sous contrôle

Le projet applique la méthode décrite dans
[mon article sur Claude Code](/posts/claude-code-data-science/), avec une règle de départ :
**ce qui doit toujours être vrai devient un hook**, pas une consigne.

- **Je suis le seul auteur des commits.** L'agent prépare le changement et propose le message ; un
  hook Git et la CI refusent tout message qui n'est pas au format Conventional Commits ou qui
  ajoute un co-auteur.
- **Les données réelles sont hors d'atteinte.** Un hook bloque toute écriture dans `data/` et la
  lecture des secrets ; les fichiers de test sont synthétiques, et reproduisent seulement la mise
  en page de la banque.
- **« Fini » veut dire « vérifié ».** Quand l'agent a modifié du code, un hook relance lint, types
  et tests, et l'empêche de conclure tant qu'ils échouent.
- **Une relecture à froid.** Un sous-agent en lecture seule relit chaque diff avant la pull
  request : justesse, invariants, tests, un seul sujet par changement. Un second le relit sous
  l'angle de la sécurité : comptes privés des autres membres, actions réservées au propriétaire,
  sessions.
- **Les migrations fusionnées sont figées.** Un hook refuse toute modification d'une migration de
  base déjà sur `main` : il faut en ajouter une nouvelle.
- **Le guide suit l'interface.** Une branche qui change une page sans toucher au guide intégré est
  arrêtée une fois, avec un rappel.
- **Vérifier dans le navigateur, sans toucher aux vraies données.** Une compétence lance une
  instance jetable (base dans un conteneur, données synthétiques), et un sous-agent la parcourt
  avec l'extension Chrome : deux langues, thème clair et sombre, largeur de téléphone, erreurs de
  console. Les captures restent hors du contexte principal.
- **Une PR par sujet.** Chaque changement passe par une branche courte et une pull request, qui
  n'est fusionnée qu'une fois tous les contrôles au vert (lint, typage strict, tests, construction
  des images Docker).
- **La spécification d'abord.** Chaque fonctionnalité commence par une PR de documentation
  seule, qui fixe les règles avant le code : la spécification en est à sa 23e version. Une
  compétence décrit le parcours complet d'une fonctionnalité, de la règle métier testée en premier
  jusqu'au guide bilingue.

## Ce qui a coincé

- **Le format bancaire réel.** Les spécifications prévoyaient des profils d'import configurables
  par l'utilisateur. Les banques exportent en fait des mises en page bien différentes, parfois
  deux pour la même banque selon le type de compte. J'ai préféré coder un format par mise en page,
  chacun testé sur un fichier synthétique qui en copie la structure exacte. Un profil générique
  viendra pour les autres banques.
- **Une projection trop naïve.** La première projection des plans était linéaire : dépensé
  divisé par la part du temps écoulée. Le 3 du mois, un loyer déjà prélevé apparaissait donc comme
  une dérive énorme. Elle part désormais de la dépense attendue de chaque mois restant.
- **Le compte commun.** Tant que tout était « privé » ou « partagé », un virement vers le compte
  joint n'avait pas de sens dans une vue personnelle. Il a fallu une troisième visibilité, puis
  juger chaque périmètre sur ses propres virements et sur ses propres objectifs.
- **L'outillage qui bouge.** Le générateur du client TypeScript a besoin de l'API du compilateur
  JavaScript, que TypeScript 7 n'expose plus : il tourne à part, avec TypeScript 6.
- **Le patrimoine imaginé contre le patrimoine réel.** La phase 3 prévoyait des positions en
  titres valorisées par des cours de marché quotidiens, des tableaux d'amortissement et des biens
  amortis. Au moment de la spécifier en détail, il est apparu que je valorise chaque placement une
  fois par mois, à la main, dans un tableur, et que c'est ce suivi que je veux retrouver. La phase
  est devenue une matrice mensuelle, et les cours de marché ont été abandonnés : moins ambitieux,
  mais livré en une journée, et utilisé.
- **Une fonctionnalité qui n'a plus servi.** Le partage des dépenses communes (« qui doit quoi à
  qui ») était prévu dès le départ. Le compte commun et les virements récurrents de chacun vers
  lui couvrent déjà ce besoin : la fonctionnalité a été retirée de la spécification avant d'être
  codée, comme l'export CSV, que les sauvegardes rendent inutile.
- **Le salaire du 28.** Compter les opérations par date réelle mettait chaque salaire dans le
  mauvais mois, et faisait paraître un mois sur deux déficitaire. D'où le mois budgétaire, et un
  invariant qui garantit qu'il ne fait que déplacer l'argent d'un mois à l'autre.
- **Ce qui ne survit pas au disque.** Une sauvegarde sur le même disque ne protège pas d'une panne
  du disque. La copie hors machine reste manuelle, et c'est une question ouverte.

## La suite

Le budget et le patrimoine sont en place : reste la phase qui m'intéresse le plus. La phase 4
traitera la prévision de trésorerie comme un vrai problème de séries temporelles, avec un
protocole écrit d'avance, un backtest sans fuite du futur et un modèle naïf à battre avant tout le
reste. Elle a déjà deux clients tout trouvés : la projection du bilan de plan et le solde projeté
en fin de mois, aujourd'hui calculés par des règles simples. La matrice de patrimoine, elle,
servira de point de départ à la simulation par Monte-Carlo. Cette fiche sera mise à jour à chaque
phase livrée.

## Essayer

```bash
git clone https://github.com/gwils28/kwak-finance
cd kwak-finance
make setup        # dépendances et hooks Git
make check        # tout ce que lance la CI
make up           # la pile complète sur https://localhost:8443
```

Les étapes de création du compte propriétaire et de la clé de chiffrement sont dans le `README`,
et l'application elle-même propose, en bas de chaque page, un guide pour la lancer, l'arrêter et
la mettre à jour.
