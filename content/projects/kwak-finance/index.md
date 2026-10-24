---
title: "Kwak Finance : le budget et le patrimoine d'un foyer, auto-hébergés"
date: 2026-10-08
draft: false
nature: "produit"
description: "Une application web auto-hébergée pour suivre le budget, le patrimoine et les objectifs financiers d'un foyer, sans que les données quittent la maison. En cours de développement : budget, patrimoine et objectifs sont livrés, la data science a commencé."
summary: "Application web auto-hébergée de budget et de patrimoine familial. Saisie au clavier, dépenses fixes, objectifs budgétaires, rapports, matrice de patrimoine mensuelle, objectifs financiers en pyramide avec leur analyse ; une projection du patrimoine par Monte-Carlo est en route."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "claude code"]
featureImage: "carte.png"
showTableOfContents: true
---

{{< lead >}}
Savoir où part l'argent du foyer, mois après mois, ce que vaut son patrimoine et quand ses projets
seront financés, sans confier ses comptes à un service en ligne. Tout tourne sur une machine de la
maison.
{{< /lead >}}

{{< fiche-projet
    statut="En développement · phases 1 à 4 livrées, phase 5 en cours"
    periode="Depuis octobre 2026"
    role="Solo : spécifications, architecture, développement, exploitation"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL 17, NumPy, React 19, TypeScript, Tailwind, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/kwak-finance" >}}

{{< stats >}}
{{< stat value="137" label="pull requests fusionnées" >}}chacune bloquée tant que la CI n'est pas verte{{< /stat >}}
{{< stat value="736" label="tests automatisés" >}}dont 49 tests de propriété sur les invariants financiers{{< /stat >}}
{{< stat value="8" label="décisions d'architecture" >}}écrites, avec les alternatives rejetées{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Projet en cours.** Cette fiche décrit l'état du dépôt au 24 octobre 2026. Les chiffres
ci-dessus sont comptés dans le code, et seront mis à jour à chaque phase livrée. Il y a moins de
tests qu'au 15 octobre : la refonte des dépenses a supprimé l'import bancaire et tout ce qui en
dépendait, tests compris.
{{< /alert >}}

{{< alert icon="image" >}}
**Toutes les captures montrent des données fictives.** Elles viennent d'une instance de
démonstration, alimentée par un foyer inventé (Camille et Sam, dix mois de dépenses, deux ans de
patrimoine, neuf objectifs). Aucun montant, libellé ni solde ne provient de comptes réels.
{{< /alert >}}

## Le problème

Les applications de budget grand public demandent presque toutes la même chose : un accès à vos
comptes bancaires, et l'hébergement de votre historique financier sur leurs serveurs. Les
tableurs, eux, ne demandent rien, mais s'abandonnent au bout de trois mois : la saisie y est lente
et les totaux se cassent au premier copier-coller.

Je voulais un outil entre les deux :

- **privé par construction** : les données restent sur une machine du foyer, sans télémétrie ni
  service tiers ;
- **rapide à tenir** : une séance de saisie par semaine, au clavier, sans rien à trier ensuite ;
- **juste au centime** : chaque total doit pouvoir se recalculer à partir des lignes saisies ;
- **tourné vers l'avenir** : dire si les projets du foyer seront financés à temps, et où le
  patrimoine peut aller ;
- **prêt pour la data science** : simulation, prévision et assistant en langage naturel doivent
  pouvoir s'ajouter sans refaire le socle.

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

{{< timelineItem icon="check" header="Phases 1 et 2 · Budget" badge="Livrées, puis refaites" subheader="Le cœur du produit" >}}
Authentification à double facteur, foyer et invitations, comptes, import et rapprochement
bancaires, règles de catégorisation, virements, plans budgétaires par période avec leur bilan,
opérations récurrentes, rapports et journal d'activité. Toute la partie comptes et import a
ensuite été remplacée par la refonte v1.0.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 3 · Patrimoine" badge="Livrée" subheader="Actifs et passifs, mois par mois" >}}
Une matrice de patrimoine mensuelle : catégories et lignes saisies à la main, dettes, valeur
nette, et quatre graphiques (historique, répartition en sunburst et en mosaïque, contributions à
la variation).
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 4 · Objectifs financiers" badge="Livrée" subheader="Une somme à réunir pour une date" >}}
Les objectifs rangés en pyramide (l'épargne de précaution en fondation, puis le long, le moyen et
le court terme, sous une coiffe dorée pour les envies), financés par des enveloppes prises sur les
lignes de patrimoine, avec leur suivi mensuel et un plan d'effort pour le mois.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Refonte v1.0 · Des dépenses plus simples" badge="Livrée" subheader="Ce que je fais vraiment, pas ce que j'avais imaginé" >}}
Plus de comptes, d'import ni de virements : chaque dépense est une ligne saisie à la main, dans
une grille pensée pour le clavier. Un seul niveau de catégories, des dépenses fixes à confirmer,
des objectifs mensuels avec leur matrice et une vue annuelle. Les données des dépenses repartent
de zéro.
{{< /timelineItem >}}

{{< timelineItem icon="lightbulb" header="Phase 5 · Analyse et data science" badge="En cours" subheader="Là où mon métier entre en jeu" >}}
Livrés : l'analyse des objectifs (six vues et des points à regarder calculés par des règles) et
le moteur de projection du patrimoine par Monte-Carlo. À venir : la page de projection, la
chance d'atteindre chaque objectif, la retraite, puis la prévision de trésorerie quand les
dépenses auront assez d'historique.
{{< /timelineItem >}}

{{< timelineItem icon="wand-magic-sparkles" header="Phase 6 · IA générative locale" badge="À venir" subheader="Sans que rien ne sorte de la machine" >}}
Un assistant qui répond en langage naturel sur ses propres données, à partir d'un modèle de
langage local (Ollama), limité à une vue analytique en lecture seule.
{{< /timelineItem >}}

{{< /timeline >}}

### Pourquoi l'import bancaire a disparu

L'import était le point de départ du projet : déposer l'export CSV de la banque, laisser les
règles ranger les dépenses. À l'usage, je saisissais déjà mes dépenses à la main chaque semaine,
et le relevé arrivait ensuite comme une corvée : des lignes à trier de nouveau, des doublons de ce
qui était déjà saisi, un rapprochement à vérifier. La v1.0 a donc retiré les comptes, l'import,
les virements, les règles, les récurrences, le mois budgétaire et les plans, avec leurs données,
pour garder ce qui sert : une saisie rapide et un budget lisible. L'écart est consigné dans le
`README` du dépôt, comme chaque écart au plan initial.

## Ce qui fonctionne aujourd'hui

### Un foyer, trois points de vue

Le propriétaire crée le foyer et invite les autres membres par un lien à usage unique ; il n'y a
pas d'inscription publique. Connexion par mot de passe (argon2id) et code TOTP obligatoire.

Les dépenses appartiennent au foyer : chaque membre voit et modifie chaque ligne. Le patrimoine
et les objectifs, eux, ont une visibilité, ligne par ligne :

- **privé** : son titulaire seul le voit ;
- **partagé** : tout le foyer le voit, mais il reste à son titulaire ;
- **commun** : le bien du foyer, qui n'est à personne.

Le patrimoine et les objectifs se lisent ensuite à l'échelle du **foyer**, du **commun** ou de
**mes lignes**. L'application est rangée en trois espaces, **Dépenses**, **Patrimoine** et
**Objectifs** ; la vue d'ensemble, en tête, résume les trois.

![La vue d'ensemble d'octobre](vue-ensemble.webp "Octobre à l'échelle du foyer : le patrimoine net et sa variation, la progression de chaque étage de la pyramide, puis les chiffres du mois. Données fictives.")

### Saisir vite, au clavier

La page principale des dépenses est une **grille** : un mois, ses lignes, chaque case modifiable
sur place. Une ligne vide attend toujours en bas ; Tab passe à la case suivante, Entrée enregistre
et ouvre une nouvelle ligne à la même date. Tout se fait sans la souris.

Au-dessus, une **ligne rapide** accepte une dépense tapée dans n'importe quel ordre :
`boulangerie 12,50 hier`, `45 sncf 13/10` ou `carrefour 87.40 #foyer`.

- la date se reconnaît (« hier », un jour de la semaine, `jj/mm`) ;
- le montant est le dernier nombre, les autres restent dans le libellé ;
- `#mot` force la catégorie qui commence par ce mot ;
- le reste est le libellé, et sa catégorie vient de la **mémoire des libellés** : choisir un
  libellé déjà utilisé reprend la catégorie de sa dernière ligne.

![La grille des dépenses et la ligne rapide](grille.webp "La ligne rapide a compris « cinéma 24,50 vendredi #loisirs » avant même la validation ; en dessous, les dépenses fixes à confirmer, grisées, puis les lignes du mois. Données fictives.")

Un en-tête rappelle la dernière ligne saisie et quand, et un point la marque dans la grille, pour
reprendre là où l'on s'est arrêté.

![La fin de la grille](derniere-saisie.webp "Le point vert marque la dernière ligne saisie ; la ligne vide attend la suivante, à la même date. Données fictives.")

Une ligne peut aussi être **ventilée** sur plusieurs catégories : la dernière part prend le reste,
si bien que la somme tombe toujours juste.

![Une ligne ventilée](ventilation.webp "Un passage à l'hypermarché : 88,51 € de courses, le reste (36 €) pour le foyer. Données fictives.")

### Des catégories à trois natures

Un seul niveau de catégories, chacune d'une nature :

- **dépense** : le loyer, les courses, les loisirs ;
- **épargne** : l'argent mis de côté, qui n'est jamais une dépense mais réduit le reste du mois ;
- **revenu** : salaires, aides, remboursements.

Le revenu d'un mois est la somme de ses lignes de revenu, et le reste vaut revenus moins dépenses
moins épargne. Les catégories **ponctuelles** (loyer, abonnements), payées en une fois, ne sont
jamais jugées sur le rythme du mois.

### Les dépenses fixes

Loyer, assistante maternelle, abonnements, assurances : une **dépense fixe** décrit une ligne qui
revient chaque mois, trimestre ou année. Chaque échéance due apparaît grisée en haut de la grille
du mois. Entrée la confirme et crée la ligne, modifiable avant ; on peut aussi la sauter pour le
mois. Rien n'est jamais créé tout seul.

![La liste des dépenses fixes](depenses-fixes.webp "Loyer, assistante maternelle, abonnements : chaque dépense fixe avec sa fréquence, son jour et sa catégorie. Données fictives.")

La vue d'ensemble liste ce qui reste à confirmer et le **reste projeté** en fin de mois.

![Les dépenses fixes encore à confirmer](a-confirmer.webp "Trois échéances d'octobre encore à confirmer, et le reste projeté une fois qu'elles seront payées. Données fictives.")

### Des objectifs mensuels

Chaque catégorie de dépense peut recevoir un **objectif mensuel**, fixé à partir d'un mois et
gardé jusqu'à ce qu'on le change ; les mois passés gardent les leurs. Une catégorie d'épargne
reçoit un minimum à atteindre.

- **le mois en cours**, sur la vue d'ensemble : une barre par catégorie, triée par part
  consommée, avec un trait qui marque la part du mois écoulée, si bien qu'une dépense en avance
  sur le calendrier se voit avant de dépasser ;
- **la matrice** : une ligne par catégorie, une colonne par mois, chaque case colorée selon
  l'écart à l'objectif (vert en dessous, gris à ±5 %, terre brûlée au-dessus) ;
- **l'année** : les objectifs cumulés à date et sur l'année entière, l'écart, et combien de mois
  ont été au-dessus, dans ou sous l'objectif.

![Les cibles du mois en cours](mois-en-cours.webp "Au 24 octobre : le transport et le shopping ont dépassé leur cible ; le trait vertical marque la part du mois écoulée, et le loyer, payé en une fois, n'est pas jugé sur le rythme. Données fictives.")

![La matrice budgétaire](budget-matrice.webp "Six mois de budget : les revenus reçus en haut, puis chaque catégorie face à sa cible. Vert : sous la cible ; gris : à ±5 % ; orange : au-dessus. Données fictives.")

![La vue annuelle](budget-annee.webp "L'année 2026 à date : cible cumulée, dépensé, écart, et combien de mois au-dessus, dans et sous la cible. Données fictives.")

### Des rapports sur n'importe quelle période

Un mois, un trimestre, une année ou toute période jusqu'à dix ans, comparée à la **précédente de
même longueur**. Une période en cours s'arrête au mois courant : « cette année » se compare aux
mêmes mois de l'an dernier, pas à une année entière.

![Les totaux et le détail d'un rapport](rapport.webp "Septembre face à août : les totaux, puis chaque catégorie avec sa moyenne, sa part et son évolution. Données fictives.")

Le rapport donne aussi un graphique mensuel empilé par catégorie, les dépenses cumulées jour après
jour, et les **flux d'argent** de la période : les revenus à gauche ; dépenses, épargne et reste non
alloué à droite, les deux côtés toujours au même total.

![Les dépenses mois par mois](rapport-mois.webp "2026 mois par mois : les six plus grosses catégories en couleur, les autres en gris, face à la courbe des revenus. Données fictives.")

![Les flux d'argent de l'année](rapport-flux.webp "Les flux de 2026 : salaires et aides à gauche ; chaque catégorie, l'épargne et le reste non alloué à droite. Données fictives.")

### Le patrimoine, mois par mois

Le patrimoine se suit comme dans un tableur : une ligne par placement, rangée dans une catégorie,
une colonne par mois, et une valeur saisie à la main une fois par mois.

![La matrice de patrimoine](patrimoine-matrice.webp "Le suivi mensuel : valeur nette, actif brut et dettes, puis les lignes par catégorie et la part de chacune. Données fictives.")

- un mois sans saisie reprend la valeur précédente, affichée comme reportée ;
- « Mettre à jour ce mois-ci » liste toutes les lignes avec leur dernière valeur, pour tout
  saisir d'un coup ;
- chaque ligne a un titulaire et une visibilité ;
- un livret réglementé (livret A, LDDS, LEP, PEL, livret jeune) connaît son plafond.

Une page *Analyse* donne quatre graphiques, chaque catégorie dans sa couleur. Comme dix teintes
ne peuvent pas toutes rester distinctes pour tous les daltonismes, chaque graphique garde aussi
ses libellés et son tableau de données.

![La valeur nette dans le temps](patrimoine-temps.webp "Les catégories empilées mois par mois, les dettes sous zéro, et la valeur nette en ligne. Données fictives.")

![La répartition en sunburst et en mosaïque](patrimoine-repartition.webp "La répartition d'octobre : catégories puis lignes dans le sunburst, une tuile par catégorie dans la mosaïque. Données fictives.")

![Ce qui a fait bouger le patrimoine](patrimoine-variation.webp "De novembre 2025 à octobre 2026, la contribution de chaque catégorie à la valeur nette ; le prêt remboursé la fait monter. Données fictives.")

### Les objectifs, en pyramide

Un **objectif** est une somme à réunir pour une date : une épargne de précaution, un voyage, un
apport immobilier. Ils sont rangés en pyramide, dessinée en pierre :

- en **fondation**, une colonne romaine : l'épargne de précaution, à remplir en premier.
  L'application propose son montant, six mois de dépenses fixes par défaut ;
- trois **étages**, donnés par l'échéance et jamais choisis : le long terme (au-delà de cinq ans)
  à la base, le moyen terme au milieu, le court terme (douze mois au plus) au sommet. Un objectif
  monte d'étage tout seul à mesure que son échéance approche ;
- une **coiffe dorée** pour les envies (des gants de boxe, une platine, une belle bouteille de
  rhum), sans échéance, **verrouillée** tant que l'essentiel n'est pas en ordre : précaution
  remplie et au moins trois quarts des objectifs en avance.

![La pyramide des objectifs et le plan d'effort](pyramide.webp "La pyramide du foyer : la colonne de la précaution à 96 %, les trois étages, la coiffe verrouillée ; à droite, le plan d'effort du mois, la précaution servie d'abord. Données fictives.")

Un objectif ne demande aucune saisie de plus : il est financé par des **enveloppes**, la part
d'une ligne de patrimoine mise de côté pour lui. Quand la ligne monte, chaque objectif reçoit sa
part de la hausse ; quand elle baisse, la baisse sort d'abord de la partie libre, et les objectifs
ne perdent qu'une fois la ligne descendue sous ce qu'ils détiennent, les envies en premier et la
précaution en dernier.

{{< mermaid >}}
flowchart LR
    L["Ligne de patrimoine<br/>Assurance-vie fonds euros"] -->|50 % des hausses| A["Enveloppe<br/>Vacances au Portugal"]
    L -->|30 % des hausses| B["Enveloppe<br/>Nouvelle voiture"]
    L -->|20 % des hausses| C["Enveloppe<br/>Apport immobilier"]
    L -.->|baisses d'abord| F["Partie libre"]
{{< /mermaid >}}

Chaque objectif a son statut (atteint, en avance, dans les temps, en retard), comparé à une
trajectoire droite du départ à la cible, et ses estimations : l'effort mensuel nécessaire,
l'effort réel des six derniers mois, la date estimée à ce rythme. Le **plan d'effort** du mois
répartit la capacité d'épargne du foyer : la précaution d'abord, dans la limite d'une part
réglable, puis les autres objectifs selon leur effort nécessaire, puis les envies déverrouillées.
C'est une recommandation : rien n'est déplacé.

![Les cartes de l'étage court terme](objectifs-cartes.webp "Le court terme : deux objectifs en avance, chacun avec sa jauge, son repère de rythme et ses estimations. Données fictives.")

![La coiffe et ses envies](coiffe.webp "La coiffe : deux envies verrouillées tant que l'essentiel n'est pas en ordre. Données fictives.")

Chaque objectif a aussi sa page : ses estimations, sa trajectoire, ses enveloppes ligne par ligne
et son suivi mois par mois.

![La page d'un objectif](objectif-page.webp "Vacances au Portugal : en avance de trois mois ; la trajectoire montre les valeurs, la ligne attendue et la projection au rythme actuel. Données fictives.")

![Les enveloppes d'un objectif et son suivi mensuel](objectif-enveloppes.webp "Son enveloppe sur l'assurance-vie, puis chaque mois : atteint, gagné, attendu et écart. Données fictives.")

### L'analyse des objectifs

Un onglet *Analyse* regarde les objectifs **ensemble**, à un mois de référence : le dernier mois
où toutes les lignes qui les financent ont une valeur saisie, pour qu'un mois pas encore saisi ne
passe jamais pour un mois sans gain.

- **l'effort nécessaire face à la capacité** sur les deux ans à venir, les mois sur-engagés
  grisés ;
- **une frise** : chaque objectif de son départ à son échéance, avec sa date estimée au rythme
  réel et au rythme du plan ;
- **horizon et risque** : chaque objectif placé selon les mois qui restent et la volatilité de ses
  enveloppes, avec des zones à surveiller (court et volatil, long et rongé par l'inflation) et la
  perte dans un cas sur dix ;
- **où est l'argent** : un diagramme de flux des catégories aux lignes, puis aux enveloppes et à la
  partie libre ;
- **le statut mois par mois** de chaque objectif.

![L'effort requis face à la capacité](analyse-effort.webp "Les efforts requis empilés par objectif face à la capacité : novembre 2026 dépasse, le temps que la précaution de Sam se remplisse. Données fictives.")

![La frise des objectifs](analyse-frise.webp "Chaque objectif de son départ à son échéance : la date estimée au rythme réel (●) et au rythme du plan (◇). Données fictives.")

![Horizon et risque](analyse-risque.webp "Le vélo électrique, à six mois de son échéance, est financé par des lignes volatiles : il tombe dans la zone à surveiller. Données fictives.")

![Où est l'argent des objectifs](analyse-flux.webp "Des catégories aux lignes, puis aux enveloppes des objectifs et à la partie libre de chaque ligne. Données fictives.")

![Le statut des objectifs mois par mois](analyse-statut.webp "Le statut de chaque objectif, mois après mois. Données fictives.")

Au-dessus, des **points à regarder**, calculés par une quinzaine de règles fixes : un objectif en
retard depuis trois mois, une précaution trop mince ou placée sur des lignes volatiles, un livret
proche de son plafond, de l'argent qui dort sur un compte courant, des objectifs qui demandent
plus que la capacité (avec le report d'échéance qui suffirait). Chaque point donne les faits, les
chiffres, pourquoi c'est important et des options ; jamais une consigne d'achat ou de vente, ni un
produit nommé. Trois au plus s'affichent, et chaque membre peut en reporter ou en écarter un.

![Les points à regarder](analyse-points.webp "Trois points à regarder : une précaution qui couvre moins de trois mois de charges fixes, deux objectifs proches financés par des lignes volatiles. Données fictives.")

### Des sauvegardes vérifiées, des actions tracées

Une sauvegarde complète chaque nuit, contrôlée avant d'être conservée, avec une rotation
(7 jours, 4 semaines, 12 mois) et une procédure de restauration écrite.

Un **journal d'activité** garde les actions sensibles, écrites dans la même transaction que
l'action elle-même : connexions, invitations, suppressions. Le propriétaire voit tout le foyer, un
membre ses propres entrées.

![Le journal d'activité](journal.webp "Connexions (dont un code erroné), invitation envoyée puis annulée, réglages, suppression d'une ligne. Données fictives.")

## Comment c'est construit

### Une architecture simple, pensée pour la suite

Tout démarre d'un seul `docker compose up` : un proxy Caddy en TLS sur le réseau local, une API
FastAPI, une base PostgreSQL et un service de sauvegarde. L'interface React est servie depuis la
même origine que l'API, ce qui permet des sessions par cookie sans configuration CORS.

{{< mermaid >}}
flowchart LR
    N["Navigateur<br/>réseau local"] -->|HTTPS| C["Caddy<br/>TLS + interface React"]
    C -->|/api| A["API FastAPI<br/>kwak_api"]
    A --> K["kwak_core<br/>toutes les règles métier"]
    A -.->|page à venir| M["kwak_analytics<br/>Monte-Carlo, NumPy"]
    M --> K
    A --> P[("PostgreSQL")]
    S["Sauvegarde nocturne<br/>pg_dump vérifié"] --> P
{{< /mermaid >}}

Côté Python, le code est découpé en paquets avec une règle stricte : `kwak_core` contient
**toutes les règles métier** (montants, ligne rapide, ventilation, objectifs mensuels, dépenses
fixes, rapports, patrimoine, enveloppes et plan d'effort, règles de l'analyse) et ne dépend de
rien. Il se teste sans base de données. L'API et la couche analytique `kwak_analytics` en
dépendent, jamais l'inverse : un même chiffre n'a qu'une seule définition.

Le contrat entre l'API et l'interface est le schéma OpenAPI : le client TypeScript en est
**généré**, jamais écrit à la main. La CI échoue si quelqu'un oublie de le régénérer.

### L'argent ne supporte pas l'à-peu-près

Les montants sont des décimaux exacts (`Decimal` en Python, `NUMERIC` en base), jamais des
flottants. Et les règles qui doivent toujours être vraies sont écrites dans les spécifications
puis vérifiées par des **tests de propriété** (Hypothesis) : au lieu de quelques exemples choisis à
la main, le test génère des centaines de cas et cherche celui qui casse la règle.

| Invariant | Ce que le test vérifie |
|---|---|
| Ligne rapide | Chaque mot tapé finit dans exactement un champ : date, montant, catégorie ou libellé |
| Ventilation | Les parts d'une ligne ventilée font exactement son montant, chacune positive |
| Épargne | L'épargne n'est jamais une dépense, et le reste du mois est la somme de ses lignes |
| Objectifs mensuels | Un seul objectif en vigueur par catégorie et par mois, et l'objectif annuel est la somme des mois |
| Dépenses fixes | Une ligne honore au plus une échéance, et le reste projeté déduit exactement celles qui restent |
| Cohérence | Un rapport, la matrice, l'année et le mois en cours donnent toujours les mêmes chiffres |
| Flux | Les deux côtés du diagramme de flux ont le même total |
| Patrimoine | La valeur nette d'un mois vaut ses actifs moins ses dettes, et le foyer est la somme exacte de ses périmètres |
| Enveloppes | Les enveloppes d'une ligne ne sont jamais négatives et ne dépassent jamais sa valeur, ni un objectif sa cible |
| Plan d'effort | Le plan ne distribue jamais plus que la capacité, et la précaution est servie la première |
| Coiffe | Une envie verrouillée ne reçoit rien, ni des hausses ni du plan |
| Analyse | Les poids d'un objectif sur ses lignes font 1, et le report proposé suffit, un mois de moins non |
| Projection | Sans volatilité, tous les chemins coïncident avec le calcul exact ; l'argent est conservé à chaque mois |

Les tests d'API tournent contre un **vrai PostgreSQL** lancé dans un conteneur, jamais contre une
base simulée.

### Une projection par Monte-Carlo

La première brique de la phase 5 est le moteur qui dira où le patrimoine peut être dans 1 à
40 ans. Le point de départ est le mois courant de la matrice ; chaque catégorie a un rendement
attendu et une volatilité, réglables, et l'épargne mensuelle du foyer s'ajoute chaque mois,
répartie entre les catégories.

- **5 000 chemins**, mois par mois : chaque catégorie croît d'un rendement log-normal tiré de son
  propre flux aléatoire, calibré pour que douze mois composent exactement la moyenne et la
  volatilité annuelles choisies ;
- **une graine fixe** : les mêmes hypothèses donnent toujours le même résultat, et deux scénarios
  partagent les mêmes tirages, si bien que leur écart ne vient que des hypothèses ;
- **les dettes** se remboursent selon leur mensualité et leur taux, et ce qu'elles libèrent
  rejoint l'épargne ;
- **une épargne négative** puise dans les comptes courants puis les livrets, jamais dans le
  logement ni les placements bloqués ; le manque devient une dette empruntée à 8 %.

C'est le seul endroit où l'argent passe en flottant, pour la vitesse : les entrées sont des
`Decimal`, les résultats y reviennent au centime. Les invariants de la projection (conservation de
l'argent, percentiles ordonnés, chemins identiques sans volatilité, moyenne simulée égale au
rendement choisi) sont testés comme le reste, et une version du moteur est figée par un test de
référence.

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

## La suite

Le moteur de projection est prêt : reste à lui donner sa page, un éventail des issues possibles
(médiane, bandes 25–75 % et 10–90 %), la chance d'atteindre un montant à une date, la médiane par
catégorie et deux scénarios à comparer, avec ses limites écrites en clair. Le même moteur donnera
ensuite à chaque objectif sa **chance d'être atteint** à temps, puis une projection de retraite.

La prévision de trésorerie attend, elle, que les dépenses repartent avec assez d'historique depuis
la v1.0. Elle sera traitée comme un vrai problème de séries temporelles : protocole écrit
d'avance, backtest sans fuite du futur, et un modèle naïf à battre avant tout le reste. Cette
fiche sera mise à jour à chaque étape livrée.

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
