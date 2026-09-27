---
title: "À propos"
description: "Data Scientist et ML Engineer à Rennes. Biostatisticien de formation, spécialisé en prévision de séries temporelles et industrialisation de modèles."
layout: "simple"
showDate: false
showAuthor: false
showReadingTime: true
showTableOfContents: true
showPagination: false
---

Je suis **Wilson Goma**, Data Scientist et ML Engineer, basé à Rennes.

Biostatisticien de formation, j'ai commencé par des cohortes de recherche
médicale avant de passer à l'industrie. Aujourd'hui chez **Orange**, je construis
des modèles de prévision qui anticipent les flux d'activité des techniciens sur
le réseau télécom français — et je les maintiens en production.

Je travaille sur la partie du métier que les assistants de code n'ont pas
absorbée : décider *quelle* question mérite d'être traitée, établir *quelle*
décision elle modifie, et livrer un système dont quelqu'un répond.

## Ce que je sais faire

Le titre « Data Scientist » recouvre trois professions aux socles incompatibles.
Personne ne les exerce au même niveau, et prétendre le contraire est le meilleur
moyen d'être médiocre partout. Voici honnêtement où je me situe.

### Mes deux profondeurs

**Prévision et séries temporelles.** C'est le fil rouge de mon parcours.
Prévision de température dans des conteneurs frigorifiques pour sécuriser une
chaîne du froid ; estimation de capacité restante de batteries IoT pour
planifier la maintenance ; aujourd'hui, anticipation des flux d'activité
techniciens à l'échelle d'un réseau national. À chaque fois, la prévision n'est
pas la fin : elle alimente une décision de stock, de capacité ou
d'ordonnancement dont les coûts sont asymétriques.

**Industrialisation et MLOps.** Je déploie et je maintiens ce que je conçois.
J'ai contribué à une librairie Python interne qui standardise le packaging et le
déploiement des modèles à l'échelle d'un groupe bancaire, mené une migration de
cas d'usage vers Google Cloud, et mis en place CI/CD, monitoring et suivi de
versions sur des systèmes qui tournent. Certifié *Google Cloud Professional
Machine Learning Engineer*.

### Mon socle

**La statistique inférentielle**, par la formation et les trois premières années.
Un master en biostatistique et un passage à l'INSERM — analyses de cohortes,
modélisation de l'impact clinique de biomarqueurs, modèle de propagation
épidémique — laissent des réflexes que le machine learning appliqué n'enseigne
pas : la méfiance devant un résultat trop beau, le souci de l'intervalle, la
distinction entre ce qu'on a mesuré et ce qu'on voudrait conclure.

### Mon pari en cours

**Les systèmes d'IA générative.** J'explore en R&D l'orchestration d'agents et de
LLM pour automatiser des processus métier en backoffice. C'est le domaine où je
suis en apprentissage, pas en expertise — et je préfère l'écrire que le laisser
supposer.

### Ma stack

Python, SQL, Bash · Scikit-learn, PyTorch, PySpark · Airflow, Docker, Terraform,
GitLab · Google Cloud (BigQuery, Vertex AI) · Dash · LangChain / LangGraph

## Parcours

**Data Scientist & ML Engineer — Orange, Rennes**<br>
*depuis décembre 2023*

Prévision des flux d'activité techniciens sur le réseau télécom France. R&D sur
les architectures d'agents IA pour le backoffice. Pipelines de données, MLOps sur
GCP, application Dash pour l'interaction métier avec les modèles. Référent
technique et encadrement d'alternants et de stagiaires.

**Data Scientist & MLOps — BPCE-SI, Aix-en-Provence**<br>
*2021 – 2023*

Segmentation client, prédiction de churn, moteur de recommandation, prédiction
des « moments de vie » du parcours client. Contribution à **Packta**, librairie
interne de packaging et déploiement des modèles. Industrialisation, CI/CD,
monitoring. Migration des cas d'usage vers Google Cloud.

**Data Scientist & IoT Analytics — Traxens, Marseille**<br>
*2019 – 2020*

Prévision de température pour la surveillance de la chaîne du froid. Estimation
de capacité de batteries pour la planification de maintenance. Détection
d'événements par capteurs. Traitement d'images satellites pour le transport
maritime. Gouvernance et qualité des données.

**Data Scientist — IT-CE, Marseille**<br>
*2017 – 2019*

Détection non supervisée d'anomalies pour la fraude sur chèques. Modèles de
churn pour la rétention. Structuration du data lake, tableaux de bord d'aide à
la décision.

**Ingénieur Biostatistique — INSERM, Paris**<br>
*2014 – 2017*

Analyses inférentielles et regroupement de profils génomiques sur cohortes de
recherche. Modélisation de l'impact clinique de biomarqueurs dans la leucémie.
Modèle de propagation de la dengue.

**Master en Biostatistique** — Aix-Marseille Université, 2016

## Ma doctrine

J'ai écrit un manifeste sur ce que devient ce métier maintenant que produire du
code analytique est quasi gratuit. Sept principes en résument la substance.

### 1. La décision précède la donnée

Aucun travail ne commence avant qu'on ait nommé la décision qu'il modifie, la
personne qui la prend, sa fréquence, et ce qui serait fait sans aucun modèle.
Les projets data qui échouent partagent tous le même trait : personne n'a jamais
posé la question « qui fera quoi différemment quand ce système existera ? »

### 2. La métrique métier est la seule fonction de perte qui compte

Une AUC, un RMSE, un F1 ne valent rien tant qu'une chaîne explicite ne les relie
pas à des euros ou à un risque évité. Une métrique sans traduction est un
indicateur de confort : elle rassure l'équipe et n'informe personne.

Le monde n'est jamais symétrique. Sous-estimer une demande coûte une rupture, la
surestimer coûte du stock. Optimiser un RMSE symétrique dans ce contexte n'est
pas une approximation, c'est une faute méthodologique.

### 3. Corréler n'est pas décider

Dès qu'une décision consiste à **agir sur** une variable, un modèle prédictif
observationnel devient invalide comme support de décision. La plupart des
demandes métier à forte valeur sont des demandes d'action déguisées en demandes
de prédiction : « prédis le churn » signifie en réalité « qui dois-je contacter,
et le contact réduit-il le churn ? »

### 4. Un modèle non déployé n'existe pas

Un modèle à 0,94 d'AUC qui dort dans un notebook vaut moins qu'une règle métier à
0,71 utilisée tous les jours. La modélisation représente une fraction minoritaire
de l'effort réel d'un système mené à terme ; ne s'intéresser qu'à elle, c'est
s'intéresser à un dixième de son métier.

Mon premier livrable est donc la chaîne de bout en bout la plus simple possible,
**en production**. Une moyenne mobile, une constante. Elle révèle les vrais
obstacles — toujours ailleurs qu'on les attendait — et elle établit le baseline
réel contre lequel tout gain sera mesuré.

### 5. L'incertitude est un livrable

Une prédiction ponctuelle sans quantification d'incertitude est une information
incomplète, souvent dangereuse. La bonne décision de stock ne se prend pas sur la
prévision médiane mais sur un quantile déterminé par le ratio entre coût de
rupture et coût de possession — le modèle du vendeur de journaux le dit depuis
1888.

Je distingue trois incertitudes : le bruit irréductible, la méconnaissance du
modèle, et le fait que le modèle soit peut-être simplement faux. Confondre les
deux premières conduit à promettre des améliorations impossibles ; ignorer la
troisième conduit aux ruines les plus spectaculaires.

### 6. La simplicité est un choix d'ingénierie, jamais un aveu

Le modèle retenu est le plus simple qui atteint le seuil de performance utile.
Chaque étage de complexité doit battre le précédent d'une marge définie **à
l'avance**.

La complexité se paie tous les mois — temps de compréhension pour chaque nouvel
arrivant, surface d'échec, difficulté d'audit, fragilité au changement de
distribution. Le gain, lui, n'est mesuré qu'une fois, et souvent avec optimisme.

### 7. Locataire de mon poste, propriétaire de mes compétences

Un poste est un contexte temporaire ; une compétence est un actif personnel qui
se déprécie sans entretien. Toutes ne se déprécient pas au même rythme : la
syntaxe d'une bibliothèque tient deux ans, une méthode statistique en tient
trente. J'investis en conséquence — ce blog en est l'instrument.

## Ce que je refuse

Un refus argumenté est un livrable à part entière : il fait économiser un projet
à l'organisation.

- **Je ne démarre pas un projet dont la décision cible n'est pas nommée.** Si le
  commanditaire ne peut pas la nommer, mon premier livrable est un atelier de
  cadrage, pas un modèle.
- **Je ne livre pas de métrique de performance sans sa traduction métier.** Si la
  traduction est impossible, je l'écris dans le livrable plutôt que de laisser
  croire à une valeur non démontrée.
- **Je ne recommande pas d'action sur la base d'un modèle purement prédictif
  observationnel.** Soit j'obtiens un design d'identification, soit je livre
  l'analyse avec un avertissement de non-causalité en tête de document — pas en
  note de bas de page.
- **Je ne livre pas de prévision ponctuelle nue quand la décision aval est
  asymétrique.** Je livre le quantile qui correspond à la décision, et je
  documente lequel.
- **Je ne déploie pas un modèle plus complexe que nécessaire** pour des raisons de
  prestige technique ou de demande de « faire de l'IA ». Si la demande porte sur
  la technologie plutôt que sur le résultat, je la requalifie.

## Mon rapport aux assistants

Je les utilise massivement — refuser de le faire serait une faute de
productivité, pas une preuve de rigueur. Mais selon un protocole strict.

Je ne délègue jamais la **définition du problème** : l'assistant reçoit une
spécification, il ne la produit pas. Je ne délègue jamais la **validation** :
tout code généré est relu et testé, tout résultat vérifié par un chemin
indépendant. Je délègue la production, jamais la compréhension — mettre en
production du code qu'on ne saurait pas expliquer ligne à ligne, c'est signer un
chèque sans lire le montant.

## En dehors

Je joue de la contrebasse jazz, à l'occasion en jam sessions entre amis. C'est
le seul domaine où je ne cherche pas à mesurer ma progression.

---

On peut me joindre sur [LinkedIn](https://www.linkedin.com/in/wilson-goma/) ou
suivre mon code sur [GitHub](https://github.com/gwils28).
