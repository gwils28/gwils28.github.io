---
title: "Contextual Retrieval : du RAG naïf aux chunks contextualisés"
date: 2026-10-16
draft: true
description: "Carnet d'apprentissage d'un data scientist débutant en recherche d'information : les fondamentaux du RAG, puis un banc d'essai sur des rapports financiers où chaque couche (hybride, reranker, chunks contextualisés) est mesurée, intervalles de confiance compris."
summary: "Débutant en RAG, j'ai voulu comprendre pourquoi le RAG naïf échoue, puis mesurer ce que rapporte chaque couche sur des rapports financiers. Ce que j'ai appris, et ce qui m'a surpris."
categories: ["Veille"]
featureImage: "cover.png"
tags: ["RAG", "recherche d'information", "Contextual Retrieval", "BM25", "reranking", "évaluation", "LLM", "python"]
showTableOfContents: true
---

{{< katex >}}

{{< alert icon="triangle-exclamation" cardColor="#b45309" textColor="#ffffff" >}}
**Brouillon en cours de rédaction.** Le projet n'est pas terminé. Les deux premiers blocs (la
veille et le banc d'essai) sont faits et racontés ici. Le bloc 3 (conception de système :
pipeline fixe ou agentique) et le bloc 4 (lecture d'une revue sur le RAG agentique) restent à
faire : leurs sections sont marquées « à venir ». Rien ici n'est définitif, en particulier les
conclusions.
{{< /alert >}}

{{< lead >}}
Sur 1 147 questions posées à des rapports financiers, une recherche vectorielle seule retrouve
toutes les pièces nécessaires deux fois sur trois. En empilant trois couches bien connues, on
passe à 94 %. Je voulais savoir d'où venait chaque point, et surtout le comprendre.
{{< /lead >}}

*Temps de lecture : à préciser quand l'article sera complet. Les formules sont toujours suivies
de leur intuition : on peut les survoler sans perdre le fil.*

{{< note-ia >}}

Je suis à l'aise avec le machine learning et la statistique, mais je partais **débutant en
recherche d'information**. Le RAG (*Retrieval-Augmented Generation*), j'en connaissais le
principe, comme tout le monde : on cherche des passages pertinents, on les colle dans le prompt,
le modèle répond. Je n'en connaissais ni les métriques, ni les modes d'échec, ni les ordres de
grandeur. Ce projet est ma façon d'apprendre : partir des fondamentaux, lire les sources de près,
puis **mesurer** sur de vraies données plutôt que de croire sur parole.

Cet article est un carnet de route. Il raconte ce que j'ai appris en chemin, y compris mes
erreurs et ce qui m'a surpris. Tout le code, les notebooks exécutés et les résultats sont dans le
dépôt [contextual-retrieval](https://github.com/gwils28/contextual-retrieval).

{{< alert icon="lightbulb" >}}
**En bref (provisoire).**

1. **Évaluer la recherche à part de la génération.** Sinon on « améliore le prompt » alors que le
   bon passage n'a jamais atteint le modèle.
2. **Chaque couche paie, et les gains s'additionnent.** Recherche vectorielle seule 0,674 →
   hybride 0,726 → + reranker 0,840 → + chunks contextualisés **0,944**, tous significatifs.
3. **Les chunks contextualisés valent autant que le reranker**, et ne coûtent rien au moment de
   la requête : le prix se paie une fois, à l'indexation.
4. **Mon intuition sur les tableaux était fausse.** Découper une ligne de tableau par chunk, avec
   ses en-têtes, *perd* nettement face au découpage naïf.
5. *Quand passer d'un pipeline fixe à un agent qui pilote sa propre recherche ? Réponse au bloc 3,
   à venir.*
{{< /alert >}}

## 1. Le projet en quelques mots

### Ce que je voulais apprendre

Trois choses, dans cet ordre :

1. **construire et mesurer** la qualité de la recherche d'un RAG, couche par couche : recherche
   vectorielle, puis hybride, puis reranking, puis *Contextual Retrieval* ;
2. **savoir quand passer** d'un pipeline fixe (« chercher puis lire ») à une recherche
   *agentique*, où le modèle décide lui-même quoi chercher ;
3. **évaluer la recherche séparément de la génération**.

Le travail est découpé en quatre blocs, qui forment ensemble le premier livrable : une **veille**
(bloc 1), un **banc d'essai** chiffré (bloc 2), un dossier de **conception de système** (bloc 3)
et une **lecture** approfondie (bloc 4). Chaque bloc livre un cours rédigé, des notebooks
exécutés, une fiche de révision et des exercices corrigés. Expliquer, c'est la meilleure façon
que je connaisse de vérifier que j'ai compris.

Un second livrable appliquera ces connaissances à un cas client fictif. Il fera l'objet d'un
projet de labo à part, et n'est pas abordé ici.

### Comment j'ai travaillé

J'ai mené ce projet avec Claude Code, selon la méthode décrite dans
[un article précédent]({{< ref "/posts/claude-code-data-science" >}}). Trois règles ont
compté plus que les autres :

- **le protocole avant les résultats** : pour le banc d'essai, toutes les décisions (données,
  métriques, tests statistiques) sont écrites dans un fichier YAML et figées *avant* de voir le
  moindre chiffre ;
- **un point de validation par bloc** : je relis le plan et le protocole avant qu'une ligne de
  code soit écrite, puis les résultats et le diff avant chaque commit ;
- **tout chiffre publié sort de code versionné** : cibles `make`, graines fixées, versions
  épinglées, empreinte `sha256` des données brutes.

## 2. Ce qu'on mesure vraiment

### Deux étages, deux pannes

Un RAG naïf tient en quatre étapes : **découper** les documents en morceaux (*chunks*),
**encoder** chaque morceau en vecteur, **récupérer** les *k* plus proches de la question,
**générer** la réponse à partir de ces morceaux.

{{< mermaid >}}
flowchart LR
    subgraph Indexation["Indexation (une fois)"]
        D[Documents] --> C[Découpage en chunks] --> E[Encodage] --> V[(Index)]
    end
    subgraph Requete["À chaque question"]
        Q[Question] --> QE[Encodage] --> S[Top-k]
        V --> S
        S --> P[Prompt] --> G[Réponse du LLM]
    end
{{< /mermaid >}}

N'importe qui peut le monter en un après-midi. Le difficile, c'est qu'il soit *fiable*. Et la
première leçon de ce projet tient en un tableau : une mauvaise réponse a deux causes possibles,
qui appellent des remèdes opposés.

| Panne | Ce qui s'est passé | Où est le remède |
|---|---|---|
| **De recherche** | le passage qui contient la réponse n'était pas dans le top-k | découpage, représentation, classement |
| **De génération** | le bon passage était là, mais le modèle l'a mal lu, ignoré ou contredit | prompt, modèle, vérifications |

Si l'on ne regarde que la réponse finale, on ne peut pas les distinguer. On finit par retoucher
le prompt alors que le bon passage n'a jamais atteint le modèle. **Tout ce projet mesure donc la
recherche seule**, avec une question simple : *le bon passage a-t-il été retrouvé ?*

### Les métriques dont on a besoin

On suppose que chaque question de test a un **passage de référence** connu (le *golden chunk*),
celui qui contient la réponse.

- **Pass@k** : la part des questions dont le passage de référence figure dans les *k* premiers
  résultats.
- **recall@k** : la part de *tous* les passages pertinents qui figurent dans le top-k, moyennée
  sur les questions. Elle diffère de Pass@k quand une question a besoin de plusieurs passages.
- **Taux d'échec@k** = 1 − recall@k. C'est la métrique que rapporte Anthropic, à k = 20.

Le choix de *k* n'est pas anodin. Plus *k* est grand, plus on a de chances d'inclure le bon
passage, mais plus on envoie de texte au modèle : plus de coût, plus de latence, plus de
distracteurs. Le bon *k* se mesure.

## 3. Les fondamentaux que j'ai dû apprendre

### La recherche dense : comparer des sens

Un **modèle d'embedding** transforme un texte en un vecteur de quelques centaines de nombres (768
pour `bge-base`), entraîné pour que des textes de sens proche tombent près l'un de l'autre.
Chercher devient alors de la géométrie : on classe les chunks par **similarité cosinus** avec le
vecteur de la question.

$$
\cos(q, d) = \frac{q \cdot d}{\lVert q \rVert\,\lVert d \rVert}
$$

Avec des vecteurs normalisés, c'est un simple produit scalaire : noter un million de chunks
revient à une multiplication matrice-vecteur.

Cette architecture s'appelle un **bi-encodeur** : question et document sont encodés *séparément*.
C'est ce qui la rend rapide (les vecteurs des documents sont calculés une fois pour toutes), et
c'est aussi ce qui la limite : la question ne « voit » jamais le document, et toute la nuance d'un
passage doit tenir dans un seul vecteur.

Elle excelle sur les paraphrases (« share buyback » ↔ « repurchased shares »). Elle peine sur les
identifiants rares, les nombres exacts, les sigles que le modèle a peu vus.

{{< alert icon="circle-info" >}}
**Un piège silencieux.** Les modèles BGE attendent un préfixe d'instruction fixe *côté question*
(`"Represent this sentence for searching relevant passages: "`). L'oublier ne fait rien planter.
La recherche est juste un peu moins bonne, sans que rien ne le signale.
{{< /alert >}}

### BM25 : compter des mots, intelligemment

**BM25** classe les documents selon les mots qu'ils partagent *littéralement* avec la question.
C'est un TF-IDF raffiné par deux idées. Pour une question \(q\) et un document \(d\) :

$$
\text{BM25}(q,d)=\sum_{t\in q}\text{IDF}(t)\cdot\frac{tf(t,d)\,(k_1+1)}{tf(t,d)+k_1\left(1-b+b\,\dfrac{|d|}{\text{avgdl}}\right)}
$$

La formule fait peur ; lue terme à terme, elle est très intuitive.

| Morceau | Sens | Intuition |
|---|---|---|
| \(tf(t,d)\) | nombre d'occurrences du mot \(t\) dans \(d\) | plus il est cité, plus c'est pertinent… |
| \(k_1\) (≈ 1,2 à 2) | **saturation** | … mais la dixième mention apporte bien moins que la première |
| \(\lvert d \rvert / \text{avgdl}\) | longueur du document rapportée à la moyenne | un long document contient plus de mots par hasard |
| \(b\) (≈ 0,75) | force de la **normalisation par la longueur** | \(b = 1\) : pénaliser pleinement ; \(b = 0\) : ignorer |
| \(\text{IDF}(t)\) | rareté du mot dans le corpus | un mot rare est informatif, « the » ne l'est pas |

J'ai écrit BM25 de zéro, en gardant la bibliothèque `rank-bm25` comme simple oracle de test. Ce
n'était pas nécessaire pour le banc d'essai, mais c'est en l'écrivant que j'ai vraiment compris
chaque terme. Et j'y ai appris quelque chose que les manuels ne disent pas : quand un mot apparaît
dans plus de la moitié des documents, son IDF brut devient **négatif**. `rank-bm25` le remplace
alors par un plancher, \(0{,}25 \times\) l'IDF moyen. Sur un tout petit corpus jouet où presque
tous les mots sont fréquents, cette moyenne peut elle-même être négative, et le plancher aussi.
Mes premiers tests échouaient pour cette raison. La leçon : **vérifier l'implémentation de
référence, pas seulement la formule du manuel.**

### Deux familles qui ratent des choses différentes

| | Dense (bi-encodeur) | BM25 |
|---|---|---|
| Rapproche | des sens | des mots exacts |
| Gagne sur | paraphrases, synonymes, questions vagues | codes, nombres, références, noms rares |
| Perd sur | identifiants rares, sigles inconnus | synonymes, flexions, reformulations |

Elles échouent sur des questions *différentes*. C'est tout l'argument pour les combiner.

### Une première leçon d'humilité

Dans le notebook du bloc 1, sur un corpus jouet de douze phrases, je voulais montrer le cas
d'école : la recherche dense confond deux identifiants proches, BM25 les distingue. Sur la
requête `KX-4417 borrowing limit`, BM25 sépare bien `KX-4417` de `KX-4471`, d'un facteur 2,4. Mais
la recherche dense… **ne s'est pas trompée**. Elle a classé le bon document en premier, avec une
marge de 0,04 en cosinus seulement.

Les échecs nets que j'ai trouvés étaient ailleurs : une paraphrase (BM25 rate « share buyback »
face à « repurchased 2.1 million shares », aucun mot commun) et un sigle inconnu (les deux
ratent). J'en ai tiré une règle pour la suite : « la recherche dense rate les termes exacts » est
une affirmation sur les **grands corpus pleins de quasi-doublons**. Il fallait la démontrer sur
de vraies données, pas la supposer. Le bloc 2 l'a fait (§ 9).

## 4. Pourquoi le RAG naïf échoue

En lisant les sources, j'ai retenu cinq modes d'échec :

1. **Le découpage casse le sens.** Une fenêtre fixe de 512 tokens coupe les paragraphes et, en
   finance surtout, **tranche les tableaux** : une cellule perd ses en-têtes de ligne et de
   colonne.
2. **Les chunks perdent leur contexte.** Prenons *« Le chiffre d'affaires de la société a
   progressé de 3 % sur le trimestre. »* Quelle société ? Quel trimestre ? Le passage est exact,
   mais il n'est plus *trouvable*.
3. **Similaire ne veut pas dire pertinent.** Un passage peut parler du même sujet sans répondre.
4. **Le top-k est grossier.** Les *k* passages les plus *similaires* ne sont pas forcément les *k*
   plus *utiles*.
5. **La question n'est pas comprise.** Elle part brute vers l'index, avec ses ambiguïtés.

Le champ a convergé vers trois familles de réponses : **réparer la représentation**, **réparer le
classement**, et **laisser le modèle piloter la recherche**.

## 5. Bloc 1 : trois familles de réponses

J'ai lu trois sources de près : l'article d'Anthropic sur *Contextual Retrieval* (2024), le
papier A-RAG de Du et al. (2026) sur le RAG agentique, et un article de praticien sur dev.to qui
passe en revue les techniques qui marchent en 2026.

### Réparer la représentation : Contextual Retrieval

L'idée est d'une simplicité désarmante. Avant d'indexer, on demande à un LLM d'écrire **un court
contexte (50 à 100 tokens) qui situe chaque chunk dans son document**, et on le colle devant le
chunk. Puis on construit les deux index, dense et BM25, sur ce texte enrichi.

Avant : *« Le chiffre d'affaires de la société a progressé de 3 % sur le trimestre. »*
Après : *« Ce passage est tiré du rapport d'ACME sur le deuxième trimestre 2023 ; le chiffre
d'affaires du trimestre précédent était de 314 millions de dollars. Le chiffre d'affaires de la
société a progressé de 3 % sur le trimestre. »*

« ACME », « 2023 » et « chiffre d'affaires » sont maintenant dans le texte indexé. Le passage peut
être trouvé par les deux moteurs.

Le prompt d'Anthropic donne au LLM **le document entier** et le chunk, et lui demande un contexte
succinct « pour améliorer la recherche du chunk ». Envoyer le document entier pour chaque chunk
serait ruineux sans la **mise en cache du prompt** : tous les chunks d'un même document partagent
le même long préfixe, traité une seule fois. Anthropic estime le coût à environ 1 dollar par
million de tokens de documents, **payé une fois, à l'indexation**.

C'est un contraste économique que je garde en tête pour la suite : le contexte se paie une fois
par chunk, le reranker (plus bas) se paie à *chaque* requête.

#### Lire les résultats d'Anthropic avec soin

| Configuration | Taux d'échec @20 | Réduction relative |
|---|---|---|
| Embeddings de base | 5,7 % | — |
| + embeddings contextuels | 3,7 % | −35 % |
| + BM25 contextuel (hybride) | 2,9 % | **−49 %** |
| + reranking | 1,9 % | **−67 %** |

Les fameux **49 %** et **67 %** sont des réductions *relatives* d'un taux d'échec déjà bas. En
absolu, c'est −2,8 et −3,8 points. Toujours important, mais ce n'est pas la même chose à dire à un
client. C'est le genre de détail que je n'aurais pas vu sans relire la source plutôt que les
résumés qui en circulent.

### Réparer le classement : hybride, RRF et reranking

**La recherche hybride** lance les deux moteurs, dense et BM25, puis fusionne leurs listes. Le
problème est la fusion : les scores BM25 vont de 0 à 30 et plus, les cosinus vivent dans
\([-1, 1]\). Les additionner n'a aucun sens sans normalisation, et la normalisation est fragile.

**La Reciprocal Rank Fusion (RRF)** contourne le problème en oubliant les scores et en ne gardant
que les **rangs** :

$$
\text{RRF}(d)=\sum_{\text{listes }L} \frac{1}{k+\text{rang}_L(d)}\qquad(k=60\text{ par convention})
$$

Un document bien classé dans les **deux** listes cumule deux contributions. La constante \(k\)
écrase le haut du classement : avec \(k = 60\), le rang 1 vaut \(1/61\) et le rang 10 vaut
\(1/70\), à peine 1,15 fois moins. Le consensus compte plus qu'une première place isolée.
L'implémentation tient en une dizaine de lignes.

J'y ai trouvé mon deuxième piège : si BM25 donne un score **nul** à tous les documents (aucun mot
commun), son « classement » n'est que l'ordre du corpus. Le passer à la RRF injecte du bruit. Il
ne faut lui transmettre que les documents de score strictement positif.

**Le reranking par cross-encodeur** est l'autre levier. Un cross-encodeur lit la question **et**
un passage candidat *ensemble*, en une seule passe, et sort un score de pertinence. Chaque mot de
la question peut « regarder » chaque mot du passage : il juge bien plus finement qu'un
bi-encodeur. Le prix : rien ne peut être précalculé. Noter N candidats coûte N passes **par
requête**. D'où le schéma en deux étages :

{{< mermaid >}}
flowchart LR
    Q[Question] --> R1["Étage 1 : bon marché, rappel élevé<br/>hybride dense + BM25 + RRF<br/>→ top-50"]
    R1 --> R2["Étage 2 : coûteux, précis<br/>cross-encodeur sur les paires (question, chunk)<br/>→ top-k"]
    R2 --> LLM[LLM]
{{< /mermaid >}}

Le reranker ne peut que réordonner ce que l'étage 1 a trouvé. **L'étage 1 maximise le rappel,
l'étage 2 la précision.**

### Laisser le modèle chercher : le RAG agentique

Tout ce qui précède est un **pipeline fixe** : les mêmes étapes pour chaque question. Le **RAG
agentique** donne au LLM des **outils de recherche** et le laisse décider quoi chercher, juger si
ce qu'il a trouvé suffit, et chercher encore sinon.

A-RAG pousse l'idée loin : aucun enchaînement prédéfini, juste trois outils à des granularités
différentes (`keyword_search`, `semantic_search`, `chunk_read`) et une boucle « raisonner →
appeler un outil → observer ». Deux idées m'ont marqué :

- **La divulgation progressive.** Les recherches renvoient des *extraits*, pas des chunks
  complets. Le modèle ne lit un chunk entier que si l'extrait semble prometteur. Sans ce
  mécanisme, la variante la plus simple consomme 4 à 10 fois plus de tokens.
- **Le goulot se déplace.** Avec un RAG naïf, environ la moitié des erreurs viennent de la
  recherche. Avec A-RAG, l'essentiel devient des erreurs de *raisonnement* (82 % sur MuSiQue),
  souvent des confusions d'entités. Mieux chercher déplace le problème, sans le supprimer.

Le papier rapporte des gains nets sur des questions « multi-sauts » : avec GPT-5-mini, 74,1 % de
réponses justes sur MuSiQue contre 52,8 % pour un RAG naïf. Mais l'agent coûte plus de tokens et
a une **latence imprévisible**. Savoir quand ce surcoût se justifie est la question du bloc 3.

### Ce que la lecture attentive m'a appris

Mon plan d'étude résumait ces sources. Les lire en entier a fait apparaître des écarts, que j'ai
consignés dans le cours du bloc :

- les 49 % et 67 % sont relatifs (ci-dessus) ;
- l'outil `keyword_search` d'A-RAG **n'est pas BM25** : c'est une correspondance exacte, pondérée
  par la longueur du mot-clé, sans index ;
- A-RAG n'utilise pas moins de tokens que le RAG naïf partout, contrairement à ce que je croyais :
  c'est vrai sur 2 des 5 benchmarks, pas sur les 3 autres ;
- l'article de praticien ne précise pas la constante de la RRF ; j'ai pris \(k = 60\), la valeur
  du papier d'origine.

Rien de dramatique. Mais chacun de ces écarts aurait pu devenir une affirmation fausse dans un
dossier client.

## 6. Bloc 2 : mettre des chiffres sur chaque couche

### Le protocole avant le premier chiffre

Un banc d'essai comporte beaucoup de choix libres : quelles questions, quel *k*, quelle métrique,
ce qui compte comme un succès. Si on les fait *après* avoir vu les résultats, on choisit, sans le
vouloir, ceux qui racontent l'histoire attendue. Le remède est ennuyeux et efficace : **tout
écrire, figer le fichier, puis lancer.** Tout changement ultérieur devient un *amendement* daté et
justifié.

Trois amendements ont été faits pendant l'implémentation, tous avant la lecture du moindre
chiffre. Le plus instructif est né d'un audit à la main de 25 questions : dans certains tableaux
FinQA, la première ligne est une ligne de *données*, pas d'en-têtes. Mon découpage la prenait pour
un en-tête et écrivait « $ 2800: » devant chaque valeur de 38 tableaux. Il a fallu corriger, et
**jeter une première exécution** arrêtée avant toute lecture de métrique. C'est ce que coûte « le
protocole d'abord » en pratique, et c'est pour ça qu'il vaut la peine : sans l'audit, j'aurais
publié des chiffres faux sans le savoir.

### Faire de FinQA un banc d'essai de recherche

**FinQA** (Chen et al., 2021) est un jeu de questions-réponses sur des rapports annuels
d'entreprises américaines : des questions qui demandent un calcul (« quelle est la variation des
loyers entre 2015 et 2016 ? »), chacune annotée avec ses **faits support**, les phrases ou lignes
de tableau qui contiennent les opérandes. Il n'a pas été conçu pour évaluer la recherche, et ça
se voit de trois façons.

**Des pages, pas des rapports.** Chaque exemple contient *une page* de rapport. Mon corpus est
fait des 380 pages uniques du jeu de test (100 entreprises), mises dans **un seul index**. C'est
petit, mais ça a la propriété qui compte : des **quasi-doublons**. 71 entreprises ont des pages de
plusieurs années, avec les mêmes tableaux et les mêmes formulations.

**Des questions écrites devant la page.** Seules **7,6 %** des questions nomment leur entreprise.
« Quelle est la variation des loyers entre 2015 et 2016 ? » est une bonne question quand on a la
page sous les yeux, et une question sans espoir dans un index commun : des dizaines de pages y
répondent. Le protocole rend à la question ce qu'un analyste sait toujours, **de quelle
entreprise on parle**, en préfixant son nom : `"Global Payments: what percentage of lease
payments will be paid out in the first year?"`. Deux variantes encadrent cet effet : la question
brute (le plafond d'ambiguïté) et un **filtre** sur l'entreprise (l'alternative de production).

**Le passage de référence dépend du découpage.** Un fait support est une phrase ou une ligne de
tableau ; le chunk qui le contient dépend de la façon dont on a coupé la page. Les références sont
donc définies au niveau du **fait**, puis rattachées aux chunks pour chaque découpage. Les deux
découpages sont jugés sur les mêmes preuves.

### Deux découpages, et le problème des tableaux

| | naïf | « table-aware » |
|---|---|---|
| Règle | page mise à plat, fenêtres fixes de 200 tokens | phrases groupées jusqu'à 200 tokens ; **un chunk par ligne de tableau**, avec ses en-têtes |
| Ligne de tableau | `2015 net revenue \| $ 5829` (en-têtes peut-être ailleurs) | `2015 net revenue \| amount ( in millions ): $ 5829` |
| Nombre de chunks | 1 702 | 4 024 |
| Tokens par chunk | 178 en moyenne | 80 en moyenne |

Avec le découpage naïf, **9,9 %** des faits support sont coupés entre deux chunks, et **27 %** des
lignes de tableau de référence se retrouvent dans un chunk **sans leur ligne d'en-têtes** : la
cellule perd son unité (« en millions ») et sa colonne (quelle année). Je pensais tenir là
l'argument décisif pour le découpage « table-aware ». La suite m'a donné tort.

#### Le piège du k égal

Les chunks naïfs sont deux fois plus longs et contiennent souvent plusieurs faits support à la
fois. À **k égal**, le découpage naïf *paraît* meilleur : il envoie deux fois plus de texte et a
besoin de moins de succès. Comparer deux découpages à k égal, c'est comparer deux tailles de
prompt. La comparaison juste se fait à **budget de tokens égal** : on prend les chunks dans
l'ordre jusqu'à 1 000 ou 2 000 tokens, et on regarde si tout y est. C'est aussi la vraie
contrainte : la fenêtre de contexte du LLM, et le prix au token.

### Les configurations

| Configuration | Étage 1 | Étage 2 |
|---|---|---|
| `bm25` | BM25 (\(k_1 = 1{,}5\), \(b = 0{,}75\)), scores positifs seulement | — |
| `dense` | cosinus sur `bge-base-en-v1.5`, recherche exacte, préfixe BGE | — |
| `hybrid` | RRF (\(k = 60\)) du top-100 dense et du top-100 BM25 | — |
| `hybrid_rerank` | top-50 de l'hybride | `bge-reranker-v2-m3` note les 50 paires |
| `contextual_*` | les mêmes, sur des **chunks contextualisés** | |

Les contextes ont été écrits par un modèle ouvert, **Qwen 2.5 7B**, sur ma carte graphique : 5 726
chunks, environ un par seconde, soit 1,5 heure de GPU. Voici un exemple réel de contexte : *« This
chunk provides receivables from the money pool for Entergy Gulf States Louisiana as of December
31 for 2011–2008. »* L'entreprise, les années et le tableau, tout ce qui manquait au chunk.

Comme un LLM n'est pas reproductible au bit près, ces contextes sont **versionnés dans le dépôt** :
relancer le banc d'essai les réutilise au lieu de les régénérer.

### La métrique principale : tout ou rien

Une question FinQA a souvent plusieurs faits support : les deux opérandes d'une soustraction, par
exemple. En retrouver un seul ne suffit pas pour calculer. La métrique principale est donc
**`pass_all@k`** : 1 si **tous** les faits support sont dans le top-k, 0 sinon. Je rapporte aussi
`pass_any@k` (au moins un), le rappel, le MRR, et `pass_all` à budget de tokens fixe.

### Les statistiques : de combien est-on sûr ?

C'est la partie où mon bagage de statisticien m'a le plus servi.

**Des intervalles par bootstrap.** Les 1 147 questions sont un *échantillon* de celles qu'un
analyste pourrait poser. Pour estimer la variabilité, on rééchantillonne les questions avec
remise 10 000 fois et on prend les quantiles 2,5 % et 97,5 % de la moyenne. Avec ce nombre de
questions et un taux autour de 60 %, l'intervalle à 95 % fait environ ±2,8 points.

**Des tests appariés.** Deux configurations sont jugées sur **les mêmes** questions. La plupart
sont faciles pour les deux, ou difficiles pour les deux : elles ne disent rien. Seules comptent
les questions **discordantes**, réussies par l'une et ratées par l'autre. Sous l'hypothèse « pas
de différence », chacune a une chance sur deux de favoriser A ou B : c'est le **test exact de
McNemar**. Il est bien plus sensible que de regarder si deux intervalles se chevauchent, parce
qu'il retire la difficulté commune des questions.

**Une correction pour comparaisons multiples.** Je fais dix tests appariés. Avec dix hypothèses
nulles vraies au seuil de 5 %, la probabilité d'au moins un faux positif peut atteindre 40 %. La
**correction de Holm** la ramène à 5 %. Seuls les écarts significatifs après correction sont
présentés comme des gains.

## 7. Les résultats

Réglage principal : nom de l'entreprise devant la question, `pass_all@10`, intervalle bootstrap à
95 % entre crochets.

| Configuration | naïf | table-aware | latence médiane (naïf) |
|---|---|---|---|
| `bm25` | 0,735 [0,709 ; 0,760] | 0,480 [0,452 ; 0,509] | 4 ms |
| `dense` | 0,674 [0,646 ; 0,701] | 0,516 [0,486 ; 0,545] | 6 ms |
| `hybrid` | 0,726 [0,700 ; 0,752] | 0,542 [0,514 ; 0,571] | 9 ms |
| `hybrid_rerank` | 0,840 [0,818 ; 0,860] | 0,605 [0,576 ; 0,633] | 355 ms |
| `contextual_bm25` | 0,874 [0,854 ; 0,893] | 0,734 [0,708 ; 0,759] | 4 ms |
| `contextual_dense` | 0,853 [0,831 ; 0,873] | 0,783 [0,759 ; 0,806] | 6 ms |
| `contextual_hybrid` | 0,892 [0,874 ; 0,909] | 0,790 [0,765 ; 0,813] | 9 ms |
| `contextual_hybrid_rerank` | **0,944** [0,930 ; 0,957] | **0,811** [0,788 ; 0,833] | 446 ms |

### Ce que chaque couche rapporte

| Comparaison | Écart | Gagnées | Perdues | p (Holm) |
|---|---|---|---|---|
| naïf : dense → hybride | +5,2 pts | 96 | 36 | < 10⁻⁴ |
| naïf : hybride → + reranker | +11,3 pts | 141 | 11 | < 10⁻⁴ |
| naïf : + reranker → + contexte | +10,5 pts | 131 | 11 | < 10⁻⁴ |
| table-aware : dense → hybride | +2,6 pts | 64 | 34 | 0,003 |
| table-aware : hybride → + reranker | +6,3 pts | 100 | 28 | < 10⁻⁴ |
| table-aware : + reranker → + contexte | +20,6 pts | 259 | 23 | < 10⁻⁴ |

Les colonnes « gagnées » et « perdues » sont celles que je regarde en premier maintenant. Passer
de l'hybride au reranker, en découpage naïf, résout 141 nouvelles questions et en perd 11. **Une
couche n'est jamais gratuite en régressions** ; ici, simplement, le bilan est très déséquilibré.

Trois enseignements :

- **L'hybride aide moins que le reranker.** La RRF ne peut que réordonner ce que BM25 et le dense
  ont déjà trouvé. Le reranker lit la question et le chunk ensemble, et corrige l'ordre *à
  l'intérieur* de la liste de candidats.
- **Le contexte aide tous les moteurs, le dense plus que tous** : +17,9 points en naïf, +26,7 en
  table-aware. Le vecteur d'un chunk récupère l'entreprise, l'année et le tableau qui lui
  manquaient.
- **Seules les étapes de la chaîne ont été testées.** L'écart entre `contextual_hybrid` et
  `contextual_hybrid_rerank` en table-aware (+2,1 points) n'était pas dans le protocole : je ne le
  présente donc pas comme un gain. C'est frustrant, et c'est exactement le rôle d'un protocole.

## 8. La surprise : le découpage « table-aware » perd

Je m'attendais à ce que le découpage table-aware gagne : il ne sépare jamais une ligne de ses
en-têtes. Il perd, **avec toutes les configurations**, et tous les tests appariés sont
significatifs (de −13 à −23 points).

**Ce n'est pas un artefact du k égal.** À budget de tokens égal, l'écart se réduit, mais reste :

| `pass_all` à 2 000 tokens | naïf | table-aware |
|---|---|---|
| `hybrid_rerank` | 0,840 | 0,657 |
| `contextual_hybrid_rerank` | 0,926 | 0,848 |

**C'est un effet de granularité.** Le détail par nombre de chunks de référence par question
(configuration complète) éclaire le mécanisme :

| Chunks de référence par question | naïf : n | naïf | table-aware : n | table-aware |
|---|---|---|---|---|
| 1 | 912 | 0,981 | 607 | 0,952 |
| 2 | 224 | 0,808 | 427 | 0,719 |
| 3 et plus | 11 | 0,636 | 113 | 0,398 |

Deux effets s'additionnent. Un chunk par ligne transforme beaucoup de questions à un seul chunk
en questions à plusieurs (540 questions à deux chunks ou plus, contre 235), et chaque chunk
supplémentaire est une chance de plus d'en manquer un. Le `pass_any@10` du table-aware reste
élevé (0,958) : il trouve **la bonne page**, puis rate une des lignes.

Ce que j'en retiens : « table-aware » n'est pas *un* choix de conception. Un chunk par ligne est
trop fin pour des questions qui combinent plusieurs lignes. D'autres variantes restent à tester :
un chunk par tableau, un chunk par groupe de lignes avec l'en-tête, ou retrouver une ligne puis
remonter à son tableau entier (*small-to-big retrieval*). Je n'ai testé qu'une seule variante, et
je me garde bien de conclure contre toutes les autres.

## 9. Mettre l'entité dans la question, ou en filtre

`pass_all@10` selon la forme de la question :

| | question brute | entreprise dans la question | filtre sur l'entreprise |
|---|---|---|---|
| naïf, `hybrid_rerank` | 0,813 | 0,840 | 0,935 |
| naïf, `contextual_hybrid_rerank` | 0,873 | 0,944 | 0,970 |
| table-aware, `hybrid_rerank` | 0,616 | 0,605 | 0,761 |
| table-aware, `contextual_hybrid_rerank` | 0,717 | 0,811 | 0,851 |

- **Filtrer sur les métadonnées est le levier le plus fort** quand l'entité est connue : +9,5
  points pour la recherche naïve, sans aucun coût. En production, il faut extraire l'entreprise
  (et idéalement l'exercice fiscal) de la question et filtrer dessus.
- **Contexte + entreprise dans la question (0,944) fait mieux que le filtre sans contexte
  (0,935).** Le contexte met le nom de l'entreprise dans chaque chunk, la question peut donc
  l'apparier.
- Contexte et filtre se recouvrent : avec le filtre, le contexte n'ajoute plus que 3,5 points.
  Une grande part de sa valeur, ici, c'est de distinguer les entreprises et les années.

## 10. Regarder les échecs un par un

### Cinq façons de rater

Pour chaque échec à k = 10, on regarde ce qui s'est passé. Cette typologie est **exploratoire** :
je l'ai définie après avoir vu les résultats. Elle décrit les échecs, elle ne sert jamais à
classer les configurations.

| Mode (sur 1 147) | naïf + reranker | naïf + contexte | table-aware + reranker | table-aware + contexte |
|---|---|---|---|---|
| succès | 963 | 1 083 | 694 | 930 |
| partiel (une partie des faits) | 94 | 46 | 253 | 169 |
| 1er résultat d'une **autre entreprise** | 39 | 2 | 77 | 3 |
| même entreprise, **autre page** (autre année) | 25 | 9 | 47 | 18 |
| bonne page, mauvais chunk | 26 | 7 | 76 | 27 |

Les chunks contextualisés suppriment presque toutes les confusions d'entreprise (39 → 2) et la
plupart des confusions d'année. Ce qui reste, c'est surtout du *partiel* : le moteur a trouvé le
bon endroit, pas tous les chiffres dont la question a besoin.

### Quand BM25 rattrape la recherche dense

Souvenez-vous du corpus jouet où la recherche dense ne s'était pas trompée (§ 3). Sur FinQA, la
démonstration a lieu : **148 questions** où BM25 trouve tous les faits dans le top-10 et la
recherche dense non (découpage naïf). Un cas typique, chez Adobe :

> *« Le montant cumulé des intérêts et pénalités liés aux positions fiscales… représentait quel
> pourcentage du solde final au 28 novembre 2008 ? »*

Le bon chunk est le tableau des avantages fiscaux non comptabilisés. BM25 le classe 2e : la
question partage avec lui des mots rares (« tax positions », « ending balance », « 2008 »). La
recherche dense classe en premier un tableau de charges de restructuration tiré des mêmes notes :
même entreprise, même registre de langue, mauvais tableau. **Le dense capte le sujet ; il brouille
les postes comptables exacts.** Les questions financières en sont pleines, ce qui explique que BM25
seul batte le dense seul en découpage naïf (0,735 contre 0,674). Je ne m'y attendais pas.

## 11. Coûts et limites

**Les coûts**, sur un portable avec une RTX 5070 de 8 Go :

- **La contextualisation** : 1,5 heure de GPU, **une fois par chunk, à l'indexation**. Aucun coût
  au moment de la requête.
- **Le reranker** : une passe de cross-encodeur sur 50 candidats par requête, 355 ms en médiane.
  Les chunks contextualisés sont plus longs, donc il ralentit : 446 ms.
- Dense, BM25 et RRF restent sous les 15 ms.

**Les limites**, à garder en tête en lisant les chiffres :

- **Un petit corpus.** 380 pages dans un index. Un vrai fonds documentaire contient beaucoup plus
  de distracteurs : les scores absolus seraient plus bas, et la valeur des filtres et du contexte
  sans doute plus haute.
- **Un contextualiseur local.** Les contextes viennent d'un modèle ouvert de 7 milliards de
  paramètres. Une exécution de référence avec un modèle Claude était prévue, puis abandonnée : je
  ne sais pas ce qu'un modèle plus fort ajouterait.
- **La recherche seulement.** Retrouver le bon chunk ne garantit pas une bonne réponse. La
  génération sera mesurée plus tard.
- **Une seule variante table-aware**, et **aucun hyperparamètre ajusté** sur les questions de
  test, par construction. Un système ajusté ferait mieux, et aurait besoin d'un jeu de
  développement séparé pour rester honnête.

## 12. Bloc 3 : pipeline fixe ou recherche agentique (à venir)

{{< alert icon="pencil" >}}
**À venir.** Le bloc 3 est un dossier de conception : dans quels cas passer d'un pipeline fixe à
une recherche agentique, comment évaluer séparément la recherche et la génération dans un même
système, et ce que coûte chaque couche par requête et à l'indexation. Cette section sera écrite
quand le bloc sera fait.
{{< /alert >}}

## 13. Bloc 4 : une carte du RAG agentique (à venir)

{{< alert icon="pencil" >}}
**À venir.** Le bloc 4 est une lecture approfondie de la revue de Singh et al. sur le RAG
agentique (version 4, 2026), pour en tirer une taxonomie qui serve de carte mentale. Cette
section sera écrite quand le bloc sera fait.
{{< /alert >}}

## Ce que j'en retiens, à mi-parcours

Sur le RAG lui-même, à ce stade :

- **Ne pas faire confiance à la recherche dense seule** sur des documents financiers : BM25 attrape
  les postes comptables exacts, et l'hybride ne coûte presque rien.
- **Mettre l'entité dans la recherche** : un filtre sur les métadonnées quand la question nomme
  l'entreprise, des chunks contextualisés sinon.
- **Contextualiser à l'indexation** si le budget permet un passage de LLM sur le corpus : +10 à
  +20 points ici, sans aucune latence.
- **Ajouter un reranker** quand 400 ms par requête sont acceptables.
- **Tester le découpage sur ses propres questions** avant de croire une étiquette : le découpage
  le plus fin n'est pas le meilleur quand les questions combinent plusieurs chiffres.

Sur la façon d'apprendre, surtout :

- **Écrire les choses soi-même** (BM25, la RRF) prend plus de temps qu'importer une bibliothèque,
  mais c'est là que j'ai trouvé les pièges que les tutoriels ne mentionnent pas.
- **Lire les sources plutôt que leurs résumés.** Les chiffres qui circulent sont souvent exacts et
  mal compris.
- **Figer le protocole avant de regarder** m'a obligé à jeter une exécution, et m'a empêché de
  présenter un gain que je n'avais pas prévu de tester. Les deux fois, c'était la bonne décision.
- **Accepter d'avoir tort.** Mon intuition sur les tableaux était fausse, et ma démonstration
  jouet n'a pas montré ce que je voulais. C'est précisément ce que les mesures étaient censées
  révéler.

La suite, quand les blocs 3 et 4 seront faits.

## Sources

- Anthropic, [*Introducing Contextual Retrieval*](https://www.anthropic.com/engineering/contextual-retrieval), 2024.
- Du et al., [*A-RAG: Scaling Agentic RAG via Hierarchical Retrieval Interfaces*](https://arxiv.org/abs/2602.03442), arXiv 2602.03442, 2026.
- Young Gao, [*RAG Is Not Dead: Advanced Retrieval Patterns That Actually Work in 2026*](https://dev.to/young_gao/rag-is-not-dead-advanced-retrieval-patterns-that-actually-work-in-2026-2gbo), dev.to, 2026.
- Chen et al., *FinQA: A Dataset of Numerical Reasoning over Financial Data*, EMNLP 2021.
- Cormack, Clarke et Büttcher, *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods*, SIGIR 2009.
- Le dépôt du projet : [gwils28/contextual-retrieval](https://github.com/gwils28/contextual-retrieval).
