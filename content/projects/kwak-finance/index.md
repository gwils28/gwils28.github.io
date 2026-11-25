---
title: "Kwak Finance : le budget et le patrimoine d'un foyer, auto-hébergés"
date: 2026-10-08
draft: false
nature: "produit"
description: "Une application web auto-hébergée pour suivre le budget, le patrimoine et les objectifs financiers d'un foyer, sans que les données quittent la maison. Toutes les phases prévues sont livrées : budget, patrimoine, objectifs, projection, retraite, prévision de trésorerie et document d'audit."
summary: "Application web auto-hébergée de budget et de patrimoine familial. Saisie au clavier, dépenses fixes, objectifs budgétaires, rapports, matrice de patrimoine mensuelle, objectifs financiers en pyramide, projection du patrimoine par Monte-Carlo, retraite, prévision de trésorerie choisie par back-test, et document d'audit pour un banquier, un conseiller ou un notaire."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "séries temporelles", "forecasting", "monte carlo", "LightGBM", "claude code"]
featureImage: "carte.png"
showTableOfContents: true
---

{{< lead >}}
Savoir où part l'argent du foyer, mois après mois, ce que vaut son patrimoine, quand ses projets
seront financés et de quoi il vivra à la retraite, sans confier ses comptes à un service en ligne.
Tout tourne sur une machine de la maison.
{{< /lead >}}

{{< fiche-projet
    statut="En développement · phases 0 à 6 livrées, place à l'usage réel"
    periode="Depuis octobre 2026"
    role="Solo : spécifications, architecture, développement, exploitation"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL 17, NumPy, statsforecast, mlforecast, LightGBM, React 19, TypeScript, Tailwind, Recharts, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/kwak-finance" >}}

{{< stats >}}
{{< stat value="212" label="pull requests fusionnées" >}}chacune bloquée tant que la CI n'est pas verte{{< /stat >}}
{{< stat value="1 213" label="tests automatisés" >}}dont 70 tests de propriété sur les invariants financiers{{< /stat >}}
{{< stat value="8" label="décisions d'architecture" >}}écrites, avec les alternatives rejetées{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Projet en cours.** Cette fiche décrit l'état du dépôt au 25 novembre 2026. Les chiffres
ci-dessus sont comptés dans le code. Depuis la version précédente de cette fiche (17 novembre),
17 pull requests ont livré la page du document d'audit, qui clôt la phase 6 et la feuille de route,
puis une passe d'ergonomie : une barre d'onglets par espace, une navigation propre au téléphone,
des pages vides qui guident, une aide sur chaque page et des libellés plus clairs.
{{< /alert >}}

{{< alert icon="image" >}}
**Toutes les captures montrent des données fictives.** Elles viennent du foyer de démonstration
intégré à l'application, la « Famille Martin » : Camille, Alex et leur fille Léa, trois ans
d'historique inventé. J'y ai ajouté deux objectifs professionnels, que la démo ne contient pas.
Seule la capture du journal d'activité vient d'une autre instance de démonstration. Aucun montant,
libellé ni solde ne provient de comptes réels.
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
- **tourné vers l'avenir** : dire si les projets du foyer seront financés à temps, où le
  patrimoine peut aller, et à quoi ressemblera l'année qui vient ;
- **honnête sur l'incertitude** : chaque estimation donne sa fourchette et ses limites, jamais un
  chiffre seul présenté comme une certitude.

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
nette, et des graphiques (historique, répartition, contributions à la variation).
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 4 · Objectifs financiers" badge="Livrée" subheader="Une somme à réunir pour une date" >}}
Les objectifs rangés en pyramide (l'épargne de précaution en fondation, puis le long, le moyen et
le court terme, sous une coiffe dorée pour les envies), financés par des enveloppes prises sur les
lignes de patrimoine, avec leur suivi mensuel et un plan d'effort pour le mois. Depuis : plusieurs
épargnes de précaution par foyer, et des objectifs professionnels.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Refonte v1.0 · Des dépenses plus simples" badge="Livrée" subheader="Ce que je fais vraiment, pas ce que j'avais imaginé" >}}
Plus de comptes, d'import ni de virements : chaque dépense est une ligne saisie à la main, dans
une grille pensée pour le clavier. Un seul niveau de catégories, des dépenses fixes à confirmer,
des cibles mensuelles avec leur matrice et une vue annuelle. Les données des dépenses repartent
de zéro.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 5 · Analyse et data science" badge="Livrée" subheader="Là où mon métier entre en jeu" >}}
L'analyse des objectifs (six vues, la chance d'atteindre chaque objectif et des points à regarder
calculés par des règles), la projection du patrimoine par Monte-Carlo, la retraite sur le même
moteur, et la prévision de trésorerie des douze prochains mois, choisie par back-test parmi des
modèles statistiques, LightGBM et, en option, deux modèles de fondation. Un foyer de démonstration
permet de tout essayer avant d'avoir de l'historique.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 6 · Document d'audit" badge="Livrée" subheader="Les finances du foyer, résumées pour un lecteur" >}}
Un document construit à la demande pour un banquier, un conseiller en gestion de patrimoine, un
comptable ou notaire, ou un assistant conversationnel, imprimé en PDF ou copié en Markdown. Il
remplace l'assistant en langage naturel prévu au départ.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Passe d'ergonomie" badge="Livrée" subheader="Relire l'application comme un nouvel utilisateur" >}}
Un audit de l'interface a ouvert 24 tickets, dont 22 sont traités en 16 pull requests : la
navigation, le téléphone, les pages vides, les chargements, les libellés et le vocabulaire. Deux
restent ouverts, dont une vue d'ensemble plus légère.
{{< /timelineItem >}}

{{< /timeline >}}

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
**mes lignes**. L'application est rangée en trois espaces, **Dépenses** (lignes, budget, rapports,
prévision), **Patrimoine** (suivi mensuel, analyse, projection, retraite, audit) et **Objectifs**
(pyramide, analyse) ; chaque espace a sa barre d'onglets, et la vue d'ensemble, en tête, résume
les trois. Chaque titre de page porte un « ? » qui ouvre le guide intégré à la bonne section, et
une page encore vide dit ce qui y apparaîtra et comment commencer.

Sur un téléphone, une barre en bas de l'écran mène aux trois espaces, et chaque ligne de dépense
devient une carte qui se modifie sur place, comme sur ordinateur.

![La vue d'ensemble de novembre](vue-ensemble.webp "Novembre à l'échelle du foyer : le patrimoine net et sa variation, la progression de chaque étage de la pyramide, puis les chiffres du mois, dont la part des revenus non dépensée. Données fictives.")

### Un foyer de démonstration

Un outil de prévision ne montre rien tant qu'il n'a pas d'historique. Le menu du compte ouvre donc
un **foyer de démonstration** : un couple et son enfant, trois ans de dépenses, de patrimoine,
d'objectifs et de retraite inventés, plausibles pour un foyer français, générés de façon
déterministe (la même graine et le même jour donnent la même démo). Il est partagé par les
membres du foyer et se réinitialise d'un clic. Un invariant testé garantit que la démo et le vrai
foyer ne se croisent jamais : aucune réponse donnée dans la démo ne lit ni n'écrit une ligne du
vrai foyer.

![Le bandeau de la démo](demo-banniere.webp "Les trois espaces en haut ; dans la démo, un bandeau le rappelle sur chaque page, avec de quoi revenir à son foyer ou repartir de zéro. Sur téléphone, il se replie en une ligne. Données fictives.")

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

Sous la ligne rapide, un aperçu dit ce qui a été compris avant la validation. Une ligne ajoutée
s'annonce avec un bouton *Annuler* ; les montants se lisent comme de l'argent, les revenus en vert
précédés d'un « + ».

![La grille des dépenses et la ligne rapide](grille.webp "« cinéma 24,50 vendredi #loisirs », compris comme le 20 novembre, cinéma, 24,50 €, Loisirs, avant même la validation ; en dessous, la box internet à confirmer, la taxe foncière sautée ce mois-ci, puis les lignes du mois. Données fictives.")

Un en-tête rappelle la dernière ligne saisie et quand, et un point la marque dans la grille, pour
reprendre là où l'on s'est arrêté.

![La fin de la grille](derniere-saisie.webp "Le point vert marque la dernière ligne saisie ; la ligne vide attend la suivante, à la même date. Données fictives.")

Une ligne peut aussi être **ventilée** sur plusieurs catégories : la dernière part prend le reste,
si bien que la somme tombe toujours juste.

![Une ligne ventilée](ventilation.webp "Un passage au supermarché : 78,01 € de courses, le reste (20 €) pour le foyer. Données fictives.")

### Des catégories à trois natures

Un seul niveau de catégories, chacune d'une nature :

- **dépense** : le logement, les courses, les loisirs ;
- **épargne** : l'argent mis de côté, qui n'est jamais une dépense mais réduit le reste du mois ;
- **revenu** : salaires, aides, remboursements.

Le revenu d'un mois est la somme de ses lignes de revenu, et le reste vaut revenus moins dépenses
moins épargne. Les catégories **payées en une fois** dans le mois (logement, abonnements) ne sont
jamais jugées sur son rythme.

### Les dépenses fixes

Prêt immobilier, assistante maternelle, abonnements, assurances : une **dépense fixe** décrit une
ligne qui revient chaque mois, trimestre ou année. Chaque échéance due apparaît grisée en haut de
la grille du mois. Entrée la confirme et crée la ligne, modifiable avant ; on peut aussi la sauter
pour le mois. Rien n'est jamais créé tout seul.

![La liste des dépenses fixes](depenses-fixes.webp "Chaque dépense fixe avec sa catégorie, son montant, sa fréquence et son état : la Spotify Family s'est arrêtée en avril, l'assistante maternelle en juin 2025, remplacée par la cantine ; les deux sont marquées terminées. Données fictives.")

La vue d'ensemble liste ce qui reste à confirmer, et sa tuile *Reste* donne le **reste projeté**,
une fois ces dépenses payées.

![Les dépenses fixes encore à confirmer](a-confirmer.webp "La box internet de novembre reste à confirmer ; le reste projeté, 1 772 €, la déduit déjà. Données fictives.")

### Des cibles mensuelles

Chaque catégorie de dépense peut recevoir une **cible mensuelle**, fixée à partir d'un mois et
gardée jusqu'à ce qu'on la change ; les mois passés gardent les leurs. Une catégorie d'épargne
reçoit un minimum à atteindre. (Dans l'interface française, « cible » désigne le budget et
« objectif » seulement une somme à réunir : les deux mots se mélangeaient.)

- **le mois en cours**, sur la vue d'ensemble : seules les catégories à surveiller s'affichent,
  et *Voir tout* les déplie toutes, triées par part consommée, avec un trait qui marque la part
  du mois écoulée, si bien qu'une dépense en avance sur le calendrier se voit avant de dépasser ;
- **la matrice** : une ligne par catégorie, une colonne par mois, chaque case colorée selon
  l'écart à la cible (vert en dessous, gris à ±5 %, terre brûlée au-dessus) ; elle s'ouvre sur
  le mois en cours ;
- **l'année** : les cibles cumulées à date et sur l'année entière, l'écart, et combien de mois
  ont été au-dessus, dans ou sous la cible.

![Les cibles du mois en cours](mois-en-cours.webp "Au 25 novembre, tout déplié : le foyer a dépassé sa cible ; le trait vertical marque la part du mois écoulée, et le logement, payé en une fois dans le mois, n'est pas jugé sur le rythme. Données fictives.")

![La matrice budgétaire](budget-matrice.webp "Six mois de budget : les revenus reçus, chaque catégorie face à sa cible, l'épargne, puis le bilan de chaque mois. Juillet, le mois des vacances, finit en négatif. Données fictives.")

![La vue annuelle](budget-annee.webp "L'année 2026 à date : cible cumulée, dépensé, écart, et combien de mois au-dessus, dans et sous la cible. Les loisirs dépassent de 63 %. Données fictives.")

### Des rapports sur n'importe quelle période

Un mois, un trimestre, une année ou toute période jusqu'à dix ans, comparée à la **précédente de
même longueur**. Une période en cours s'arrête au mois courant : « cette année » se compare aux
mêmes mois de l'an dernier, pas à une année entière.

Le rapport s'ouvre sur les **flux d'argent** de la période : les revenus à gauche ; dépenses,
épargne et reste non alloué à droite, les deux côtés toujours au même total.

![Les flux d'argent de l'année](rapport-flux.webp "Les flux de 2026 : 61 299 € disponibles à gauche ; chaque catégorie, l'épargne (11 000 €) et le non alloué (10 683 €) à droite. Données fictives.")

Viennent ensuite les totaux, le détail par catégorie, un classement des dépenses et un graphique
mensuel empilé par catégorie.

![Les totaux et le détail d'un rapport](rapport.webp "Janvier à novembre 2026 face aux mêmes mois de 2025 : les totaux, puis chaque catégorie avec sa part et son évolution. Les dépenses pour les enfants baissent de 61 % : l'assistante maternelle s'est arrêtée en juin 2025. Données fictives.")

![Les dépenses mois par mois](rapport-mois.webp "2026 mois par mois : les six plus grosses catégories en couleur, les autres en gris, face à la courbe des revenus. Données fictives.")

### Le patrimoine, mois par mois

Le patrimoine se suit comme dans un tableur : une ligne par placement, rangée dans une catégorie,
une colonne par mois, et une valeur saisie à la main une fois par mois.

![La matrice de patrimoine](patrimoine-matrice.webp "Le suivi mensuel, ouvert sur le mois en cours : les lignes par catégorie, avec ce que chacune réserve aux objectifs, puis l'actif brut, les dettes, la valeur nette et sa variation. Les valeurs en italique sont reportées. Données fictives.")

- un mois sans saisie reprend la valeur précédente, affichée comme reportée ;
- « Mettre à jour ce mois-ci » liste toutes les lignes avec leur dernière valeur, marque celles
  déjà mises à jour, et n'enregistre que celles que l'on touche ;
- chaque ligne a un titulaire et une visibilité ;
- un livret réglementé (livret A, LDDS, LEP, PEL, livret jeune) connaît son plafond, et une ligne
  d'actif peut porter son enveloppe fiscale (PEA, assurance-vie…).

![La mise à jour du mois](patrimoine-maj.webp "Cinq lignes sur treize déjà mises à jour en novembre, sur fond teinté ; les autres attendent, avec leur dernière valeur. Données fictives.")

Une page *Analyse* donne trois graphiques, chaque catégorie dans sa couleur. Comme dix teintes
ne peuvent pas toutes rester distinctes pour tous les daltonismes, chaque graphique garde aussi
ses libellés et son tableau de données. Des cases à cocher sortent une catégorie de l'analyse :
sans la résidence principale ni la voiture, on voit enfin comment se répartit l'épargne.

![La valeur nette dans le temps](patrimoine-temps.webp "La valeur nette mois par mois, sur un axe ajusté qui ne part pas de zéro : de 187 387 € en décembre 2025 à 214 664 € en novembre 2026. Une case la montre sans l'immobilier. Données fictives.")

![La répartition en sunburst](patrimoine-repartition.webp "La répartition, immobilier et matériels décochés : les catégories au centre, leurs lignes autour ; les livrets font 54 % de ce qui reste, les obligations 33 %. La mosaïque, qui redisait les anneaux, a été retirée. Données fictives.")

![Ce qui a fait bouger le patrimoine](patrimoine-variation.webp "De décembre 2025 à novembre 2026, la contribution de chaque catégorie à la valeur nette ; les prêts remboursés la font le plus monter. Données fictives.")

### Les objectifs, en pyramide

Un **objectif** est une somme à réunir pour une date : une épargne de précaution, un voyage, un
apport immobilier. Ils sont rangés en pyramide, dessinée en pierre :

- en **fondation**, une colonne romaine : l'épargne de précaution. Le foyer peut en avoir
  plusieurs (une par membre, une commune, une tirelire d'espèces), chacune à combler en priorité
  ou non. L'application propose son montant, six mois de dépenses fixes par défaut ;
- trois **étages**, donnés par l'échéance et jamais choisis : le long terme (au-delà de cinq ans)
  à la base, le moyen terme au milieu, le court terme (douze mois au plus) au sommet. Un objectif
  monte d'étage tout seul à mesure que son échéance approche ;
- une **coiffe dorée** pour les envies (des gants de boxe, une platine, une belle bouteille de
  rhum), sans échéance, **verrouillée** tant que l'essentiel n'est pas en ordre : précaution
  remplie et au moins trois quarts des objectifs en avance.

![La pyramide des objectifs et le plan d'effort](pyramide.webp "La pyramide du foyer : chaque étage avec sa progression écrite en grand, la part professionnelle hachurée, et la coiffe verrouillée ; à droite, le plan d'effort du mois. Données fictives.")

Un objectif ne demande aucune saisie de plus : il est financé par des **enveloppes**, la part
d'une ligne de patrimoine mise de côté pour lui. Quand la ligne monte, chaque objectif reçoit sa
part de la hausse ; quand elle baisse, la baisse sort d'abord de la partie libre, et les objectifs
ne perdent qu'une fois la ligne descendue sous ce qu'ils détiennent, les envies en premier et la
précaution en dernier.

{{< mermaid >}}
flowchart LR
    L["Ligne de patrimoine<br/>Livret A"] -->|60 % des hausses| A["Enveloppe<br/>Épargne de précaution"]
    L -->|20 % des hausses| B["Enveloppe<br/>Ordinateur portable"]
    L -->|20 % des hausses| C["Enveloppe<br/>Week-end spa"]
    L -.->|baisses d'abord| F["Partie libre"]
{{< /mermaid >}}

Chaque objectif a son statut (atteint, en avance, dans les temps, en retard), comparé à une
trajectoire droite du départ à la cible, et ses estimations : l'effort mensuel nécessaire,
l'effort réel des six derniers mois, la date estimée à ce rythme. Le **plan d'effort** du mois
répartit la capacité d'épargne du foyer : la précaution d'abord, dans la limite d'une part
réglable, puis les autres objectifs selon leur effort nécessaire, puis les envies déverrouillées.
C'est une recommandation : rien n'est déplacé.

![Les cartes de l'étage court terme](objectifs-cartes.webp "Le court terme : un voyage en avance, et un ordinateur portable professionnel en retard, à renouveler tous les quatre ans. Données fictives.")

Un **objectif professionnel** sert le travail : un équipement, une formation, la création d'une
entreprise, une reconversion, un déménagement. Il reste à son étage, hachuré, avec son type. Le
formulaire demande son coût et ce que d'autres paient (le CPF, l'employeur, France Travail, un prêt
d'honneur), et la cible est ce qu'il reste au foyer à réunir. Un équipement peut se renouveler
tous les N ans : une fois l'achat fait, le cycle suivant repart tout seul.

Le formulaire d'un nouvel objectif commence par un seul choix, son type : précaution, projet,
plaisir ou professionnel. Un projet peut être *permanent*, gardé en vue une fois atteint.

![Les cartes de l'étage moyen terme](objectifs-moyen.webp "Le moyen terme : une certification de 2 400 €, dont 1 500 € pris en charge par le CPF, ne demande que 900 € au foyer ; elle et la moto prennent du retard. Données fictives.")

![La coiffe et ses envies](coiffe.webp "La coiffe, verrouillée : deux objectifs sur quatre sont en avance, il en faut trois. La guitare d'Alex et le week-end spa attendent que l'essentiel soit en ordre. Données fictives.")

Chaque objectif a aussi sa page : ses estimations, sa trajectoire, ses enveloppes ligne par ligne
et son suivi mois par mois.

![La page d'un objectif](objectif-page.webp "Vacances au Portugal : en avance, atteint un mois avant l'échéance à ce rythme ; la trajectoire montre les valeurs, la ligne attendue et la projection au rythme actuel. Données fictives.")

![Les enveloppes d'un objectif et son suivi mensuel](objectif-enveloppes.webp "Son enveloppe sur le livret joint (1 200 € au départ, 80 % des hausses), puis chaque mois : atteint, gagné, attendu et écart. Données fictives.")

### L'analyse des objectifs

Un onglet *Analyse* regarde les objectifs **ensemble**, à un mois de référence : le dernier mois
où toutes les lignes qui les financent ont une valeur saisie, pour qu'un mois pas encore saisi ne
passe jamais pour un mois sans gain.

- **l'effort nécessaire face à la capacité** sur les deux ans à venir, les mois sur-engagés
  grisés ;
- **une frise** : chaque objectif de son départ à son échéance, avec sa date estimée au rythme
  réel et au rythme du plan ;
- **horizon et risque** : chaque objectif placé selon les mois qui restent et la volatilité de ses
  enveloppes, avec des zones à surveiller (court et volatil, long et rongé par l'inflation) ;
- **la chance d'atteindre chaque objectif** à temps, simulée par le moteur de projection sur ses
  propres lignes, à l'effort du plan et à l'effort requis ;
- **où est l'argent** : un diagramme de flux des catégories aux lignes, puis aux enveloppes et à la
  partie libre ;
- **le statut mois par mois** de chaque objectif.

![L'effort requis face à la capacité](analyse-effort.webp "Les efforts requis empilés par objectif, hachurés pour les objectifs professionnels, face à la capacité : chaque mois tient. Données fictives.")

![La frise des objectifs](analyse-frise.webp "Chaque objectif de son départ à son échéance : la date estimée au rythme réel (●) et au rythme du plan (◇). La moto n'arrivera qu'après son échéance au rythme actuel. Données fictives.")

![Horizon et risque](analyse-risque.webp "Tous les objectifs proches sont sur des livrets sans volatilité ; les études de Léa, à douze ans, tombent dans la zone où l'inflation ronge la cible. Données fictives.")

![La chance d'atteindre chaque objectif](analyse-chances.webp "Pour chaque objectif, la chance d'atteindre sa cible avant l'échéance, au plan et à l'effort requis. Données fictives.")

![Où est l'argent des objectifs](analyse-flux.webp "Des catégories aux lignes, puis aux enveloppes des objectifs et à la partie libre de chaque ligne. Données fictives.")

![Le statut des objectifs mois par mois](analyse-statut.webp "Le statut de chaque objectif, mois après mois : la moto reste en retard depuis des mois. Données fictives.")

Au-dessus, des **points à regarder**, calculés par une quinzaine de règles fixes : un objectif en
retard depuis trois mois, une précaution trop mince ou placée sur des lignes volatiles, un livret
proche de son plafond, de l'argent qui dort sur un compte courant, des objectifs qui demandent
plus que la capacité (avec le report d'échéance qui suffirait), une dette plus chère que ce que
rapportent les placements, des mensualités au-delà de 35 % des revenus. Chaque point donne les
faits, les chiffres, pourquoi c'est important et des options ; jamais une consigne d'achat ou de
vente, ni un produit nommé. Trois au plus s'affichent, et chaque membre peut en reporter ou en
écarter un. Un objectif en retard depuis trois mois est toujours un avertissement, quelle que
soit son échéance.

![Les points à regarder](analyse-points.webp "Trois points à regarder : l'ordinateur portable et la moto en retard depuis trois mois, chacun avec trois façons de rattraper, et une précaution qui couvre 5,8 mois de charges fixes. Données fictives.")

### La projection du patrimoine

L'onglet *Projection* répond à une question : où le patrimoine peut-il être dans 1 à 40 ans ? C'est
un **simulateur** : on règle à gauche, la réponse se recalcule à droite pendant que l'on tape.

- **l'épargne mensuelle**, au choix du foyer : *déclarée* (des versements par catégorie, que l'on
  peut indexer sur l'inflation) ou *mesurée* (la capacité d'épargne réelle des derniers mois) ;
  l'historique ne sert que si on le choisit, pour qu'un mois exceptionnel ne fausse pas tout ;
- **la réponse** : le patrimoine net médian à l'horizon, la fourchette où tombent huit résultats
  sur dix, et le revenu mensuel que les placements liquides pourraient verser à un taux de retrait
  donné ;
- **d'où vient l'argent** : le patrimoine d'aujourd'hui, les versements, le capital remboursé des
  prêts et les plus-values, qui s'additionnent exactement à la médiane ;
- **atteindre un montant** : la chance d'avoir au moins tant à telle date, et quand la moitié puis
  neuf dixièmes des résultats l'atteignent ;
- **et si…** : deux variantes (épargne, rendement, volatilité, inflation), le temps de la visite.

![Le simulateur de projection](projection-simulateur.webp "Avec l'épargne mesurée (1 776 € par mois), un patrimoine net médian de 930 900 € dans 20 ans, en euros d'aujourd'hui, décomposé en ce qu'il est aujourd'hui, les versements, les prêts remboursés et les plus-values. Données fictives.")

![La fourchette des résultats](projection-fourchette.webp "La même projection en éventail : la médiane, la moitié des résultats dans la bande foncée, huit sur dix dans la claire. Données fictives.")

![Atteindre un montant et comparer des variantes](projection-montant.webp "430 000 € en novembre 2046 : atteints dans plus de 99 % des cas, par la moitié des résultats dès septembre 2032, par neuf sur dix en janvier 2035. À droite, deux variantes à comparer. Données fictives.")

Chaque page dit ses limites en clair : une estimation à partir d'hypothèses, ni une prévision ni un
conseil ; une bande à 10–90 % laisse un résultat sur cinq dehors, et la vraie dispersion est plus
large que celle du modèle.

### La retraite

L'onglet *Retraite*, dans l'espace Patrimoine, tourne sur le même moteur : quel niveau de vie le foyer pourra-t-il garder une
fois retraité ? Chaque membre saisit son mois de naissance, quand il arrête de travailler, le
revenu qui s'arrête alors, et la pension estimée sur info-retraite.fr ; l'application ne calcule
aucun droit. Le foyer règle ses dépenses de retraite (80 % des dépenses d'aujourd'hui hors prêts,
par défaut), l'indexation des pensions et l'horizon.

La page donne d'abord la réponse : les pensions plus le **retrait soutenable**, le plus grand
montant mensuel que le patrimoine liquide peut verser jusqu'à l'horizon sans s'épuiser dans neuf
résultats sur dix, face aux dépenses ; puis la chance que le patrimoine tienne, et l'âge auquel il
s'épuiserait sinon.

![Le résumé de la retraite](retraite-resume.webp "Dès mai 2052, 3 400 € de pensions et 5 300 € de retrait soutenable couvrent 2 000 € de dépenses ; la frise montre qui travaille, qui touche sa pension, et jusqu'où le plan est testé. Un horizon à 75 ans fait l'objet d'un avertissement. Données fictives.")

![Les revenus et le patrimoine une fois retraité](retraite-graphiques.webp "À gauche, les pensions et le retrait soutenable face aux dépenses ; à droite, l'éventail du patrimoine net jusqu'à l'horizon et sa part liquide. Données fictives.")

### La prévision de trésorerie

L'onglet *Prévision*, dans l'espace Dépenses, montre les douze prochains mois : revenus, dépenses,
épargne et reste, par catégorie, avec une fourchette, face aux cibles du budget. Les dépenses fixes à venir sont
connues ; le reste est prévu à partir de l'historique du foyer, par la méthode qui s'est le moins
trompée sur les mois déjà saisis (voir [plus bas](#une-prévision-choisie-par-back-test)). Le
calcul prend quelques secondes : la page le dit, et garde la dernière prévision à l'écran pendant
qu'elle se recalcule.

![Le résumé de la prévision](prevision-resume.webp "De novembre 2026 à octobre 2027, un reste attendu de 13 466 €, entre 5 979 € et 18 224 € environ huit fois sur dix ; trois cibles sur dix à risque ce mois-ci, et les revenus, dépenses et épargne des douze mois. Données fictives.")

![Les mois passés et à venir](prevision-mois.webp "Douze mois saisis puis douze mois prévus, en pointillés avec leurs bandes ; en dessous, le reste de chaque mois. Le pic de juillet, les vacances, revient l'été suivant. Données fictives.")

![La prévision face aux cibles du mois](prevision-objectifs.webp "Novembre : chaque catégorie en pourcentage de sa cible, la prévision en point, la fourchette en barre. Le foyer dépassera probablement la sienne. Données fictives.")

![La prévision face aux cibles de l'année](prevision-annee.webp "L'année 2026 : le dépensé à fin octobre, plus la prévision jusqu'à décembre, face à la cible annuelle. Les loisirs finiront autour de 160 %. Données fictives.")

Repliée en bas, la **fiabilité** : pour chaque catégorie, la méthode retenue et ce qu'elle gagne
sur la moyenne des six derniers mois, son biais, puis le back-test des totaux.

![La fiabilité de la prévision](prevision-fiabilite.webp "Pour chaque catégorie, l'erreur en moins face à la moyenne de six mois et le biais ; à droite, les totaux prévus un mois à l'avance face à ce qui a été saisi, avec MASE, WAPE et RMSSE. Données fictives.")

### Le document d'audit

Le dernier onglet du patrimoine, *Audit*, construit un document qui résume les finances du foyer
pour **un lecteur** : un banquier (une demande de prêt immobilier), un conseiller en gestion de
patrimoine, un comptable ou un notaire, ou un assistant conversationnel à qui l'on demande un
audit. Un formulaire règle le lecteur, le périmètre, la période, la langue et la confidentialité
(membres nommés ou *Membre A*, lignes nommées ou par catégorie, montants exacts ou arrondis) ; le
document se reconstruit en dessous à chaque changement, tel qu'il sera imprimé.

![Le formulaire du document d'audit](audit-formulaire.webp "Pour un banquier : le périmètre, la période en mois complets, la langue, la confidentialité, les revenus comptés dans le taux d'endettement, un taux de prélèvement facultatif et un projet immobilier à simuler. Données fictives.")

Chaque lecteur a ses sections :

- **le banquier** : les revenus mois par mois, pour montrer leur régularité, les dépenses fixes,
  les crédits en cours, le taux d'endettement et le reste à vivre, la capacité d'épargne, le
  patrimoine disponible et, s'il le faut, un projet immobilier simulé (mensualité, endettement
  face au plafond de 35 %, apport) ;
- **le conseiller** : le patrimoine par catégorie avec sa liquidité, les livrets et leurs
  plafonds, les objectifs, la retraite et les analyses de l'application, puis tout ce que
  l'application ne sait pas (profil de risque, tranche d'imposition, régime matrimonial…) ;
- **le comptable ou le notaire** : un inventaire par titulaire, tel que classé dans
  l'application, qui rappelle que ce classement n'est pas la propriété juridique ;
- **l'assistant conversationnel** : tout cela en Markdown structuré, anonymisé par défaut, ouvert
  par une consigne qui lui demande d'abord ce qui lui manque, puis de séparer ce qu'il observe de
  ce qu'il suggère, sans nommer de produit.

![Le début du dossier pour un banquier](audit-document.webp "Le dossier pour une demande de prêt : la période, la date, le périmètre et la confidentialité, le sommaire, puis le foyer. Données fictives.")

![Les crédits et le taux d'endettement](audit-endettement.webp "Deux crédits en cours, 1 351 € de mensualités et d'assurances pour 5 721 € de revenus comptés : 23,6 % après prélèvement, dans la limite du plafond de 35 %. Données fictives.")

Rien n'est stocké : le document est refait à partir des données du jour. Il s'imprime en PDF ou,
pour l'assistant, se copie ou se télécharge en Markdown ; chaque impression ou copie laisse une
trace dans le journal d'activité, sans aucun chiffre. Il se termine toujours par des définitions
et par la même phrase : des chiffres saisis par le foyer, non certifiés, qui ne sont pas un
conseil financier.

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
    A --> M["kwak_analytics<br/>Monte-Carlo, prévision"]
    M --> K
    A --> P[("PostgreSQL")]
    S["Sauvegarde nocturne<br/>pg_dump vérifié"] --> P
{{< /mermaid >}}

Côté Python, le code est découpé en paquets avec une règle stricte : `kwak_core` contient
**toutes les règles métier** (montants, ligne rapide, ventilation, cibles mensuelles, dépenses
fixes, rapports, patrimoine, enveloppes et plan d'effort, règles de l'analyse, séries et choix des
modèles de prévision) et ne dépend de rien. Il se teste sans base de données. L'API et la couche
analytique `kwak_analytics` (les simulations et l'ajustement des modèles) en dépendent, jamais
l'inverse : un même chiffre n'a qu'une seule définition.

Le contrat entre l'API et l'interface est le schéma OpenAPI : le client TypeScript en est
**généré**, jamais écrit à la main. La CI échoue si quelqu'un oublie de le régénérer.

Les pages d'analyse ont d'abord été écrites en Dash, servies dans un cadre. Elles sont passées en
React : chaque page appelle un point d'API en lecture seule, qui lance son moteur et renvoie des
chiffres en JSON ; les mots, les formats et les graphiques (Recharts) appartiennent à la page, dans
les deux langues. Dash a été retiré.

### L'argent ne supporte pas l'à-peu-près

Les montants sont des décimaux exacts (`Decimal` en Python, `NUMERIC` en base), jamais des
flottants. Et les règles qui doivent toujours être vraies sont écrites dans les spécifications,
46 à ce jour, puis vérifiées par des **tests de propriété** (Hypothesis) : au lieu de quelques
exemples choisis à la main, le test génère des centaines de cas et cherche celui qui casse la
règle.

| Invariant | Ce que le test vérifie |
|---|---|
| Ligne rapide | Chaque mot tapé finit dans exactement un champ : date, montant, catégorie ou libellé |
| Ventilation | Les parts d'une ligne ventilée font exactement son montant, chacune positive |
| Épargne | L'épargne n'est jamais une dépense, et le reste du mois est la somme de ses lignes |
| Cibles mensuelles | Une seule cible en vigueur par catégorie et par mois, et la cible annuelle est la somme des mois |
| Dépenses fixes | Une ligne honore au plus une échéance, et le reste projeté déduit exactement celles qui restent |
| Cohérence | Un rapport, la matrice, l'année et le mois en cours donnent toujours les mêmes chiffres |
| Flux | Les deux côtés du diagramme de flux ont le même total |
| Patrimoine | La valeur nette d'un mois vaut ses actifs moins ses dettes, et le foyer est la somme exacte de ses périmètres |
| Enveloppes | Les enveloppes d'une ligne ne sont jamais négatives et ne dépassent jamais sa valeur, ni un objectif sa cible |
| Plan d'effort | Le plan ne distribue jamais plus que la capacité, et la précaution est servie la première |
| Objectifs professionnels | Un objectif professionnel se comporte exactement comme l'objectif standard de même cible, et un équipement à renouveler a exactement un cycle suivant |
| Projection | Sans volatilité, tous les chemins coïncident avec le calcul exact ; l'argent est conservé à chaque mois de chaque chemin |
| Retraite | Jusqu'au premier départ, la simulation est exactement la projection ; le retrait soutenable ne baisse jamais quand une pension monte |
| Prévision | Aucune prévision ne lit une ligne postérieure à son origine ; un modèle trop optimiste sur le back-test n'est jamais retenu |
| Démo | Aucune réponse donnée dans la démo ne lit ni n'écrit une ligne du vrai foyer |
| Document d'audit | Jamais la ligne privée d'un autre membre ; anonymisé, aucun nom ni courriel n'apparaît, la consigne comprise |

Les tests d'API tournent contre un **vrai PostgreSQL** lancé dans un conteneur, un par processus
de test, jamais contre une base simulée.

### Une projection par Monte-Carlo

Le même moteur sert la projection, la chance d'atteindre chaque objectif et la retraite. Le point
de départ est le mois courant de la matrice ; chaque catégorie a un rendement attendu et une
volatilité, réglables, et l'épargne mensuelle s'ajoute chaque mois, répartie entre les catégories.

- **5 000 chemins**, mois par mois : chaque catégorie croît d'un rendement log-normal tiré de son
  propre flux aléatoire, calibré pour que douze mois composent exactement la moyenne et la
  volatilité annuelles choisies ;
- **une graine fixe** : les mêmes hypothèses donnent toujours le même résultat, et deux scénarios
  partagent les mêmes tirages, si bien que leur écart ne vient que des hypothèses ;
- **les dettes** se remboursent selon leur mensualité et leur taux, et ce qu'elles libèrent
  rejoint l'épargne ;
- **une épargne négative** puise dans les comptes courants puis les livrets, jamais dans le
  logement ni les placements bloqués ; le manque devient une dette empruntée à 8 %.

Pour la retraite, le **retrait soutenable** est cherché chemin par chemin, par dichotomie, sur les
mêmes tirages : c'est le plus grand multiple de 100 € qui laisse au plus un chemin sur dix à court
d'argent avant l'horizon ; à 100 € de plus, plus d'un chemin sur dix échouerait.

C'est le seul endroit où l'argent passe en flottant, pour la vitesse : les entrées sont des
`Decimal`, les résultats y reviennent au centime.

### Une prévision choisie par back-test

La prévision de trésorerie est traitée comme un problème de séries temporelles, avec un protocole
écrit d'avance :

- **une série par catégorie**, découpée en une part connue (les échéances des dépenses fixes) et
  une part variable, la seule que les modèles apprennent ; une ligne n'est jamais comptée deux fois ;
- **des candidats du plus simple au plus riche** : la moyenne des six derniers mois (la référence),
  d'autres moyennes, le naïf saisonnier, le lissage exponentiel, ETS, Theta, ARIMA, ADIDA pour les
  séries intermittentes (`statsforecast`), un LightGBM global sur toutes les catégories
  (`mlforecast`) et, en option, deux modèles de fondation, Chronos-2 et TimesFM 2.5 ;
- **un back-test sans fuite du futur** : l'historique est coupé à chaque mois, chaque candidat
  n'apprend que sur les mois d'avant et prévoit les douze suivants ; l'erreur se mesure en MASE,
  avec WAPE et RMSSE à côté ;
- **un modèle ne remplace la référence que s'il fait nettement mieux** : au moins 10 % de MASE en
  moins sur les mêmes coupes ;
- **pas d'optimisme** : un candidat qui sous-estime les dépenses ou surestime les revenus de plus
  de 5 % sur le back-test, et plus que la référence, n'est jamais retenu ;
- **des fourchettes conformes** : la bande à 80 % vient des propres erreurs du back-test au même
  nombre de mois d'avance, sans hypothèse de loi, et sa couverture mesurée est affichée.

Sans douze mois complets d'historique, il n'y a pas de prévision. Les modèles de fondation sont
facultatifs : ils ajoutent environ 2,5 Go à l'image, leurs poids sont téléchargés à la construction
à une révision figée et vérifiés par somme de contrôle, puis lus hors ligne. Rien n'est téléchargé
ni envoyé quand une prévision tourne. L'étude qui a fixé ces choix vit dans un dossier de notebooks
à part, sur des foyers synthétiques uniquement : elle a notamment montré que les deux modèles de
fondation étaient les plus précis sur ces foyers, et que la marge de 10 % suffisait comme garde-fou.

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

Les écarts au plan initial sont, eux aussi, journalisés, au jour près. Certains ont rendu une
décision sans objet : DuckDB n'a pas encore servi, les séries d'un foyer tenant en quelques
milliers de nombres, et l'assistant local a laissé la place au document d'audit.

## La suite

La feuille de route prévue est livrée. Vient maintenant l'usage réel, qui dira ce qui manque :
la prévision ne s'appliquera à mes propres données qu'une fois douze mois complets saisis depuis
la v1.0, soit à l'automne 2027. Cette fiche sera mise à jour à chaque étape livrée.

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
la mettre à jour. Une fois connecté, le menu du compte ouvre le foyer de démonstration.
