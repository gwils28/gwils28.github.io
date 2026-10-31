---
title: "Jazzar : des archives de presse jazz interrogeables, citées à la page"
date: 2026-10-31
draft: true
nature: "produit"
description: "Un SaaS en construction qui rend interrogeables des décennies d'archives de presse jazz : réponses citées à la page, dossiers de recherche rédigés par des agents, data-journalisme en Text-to-SQL. En cours : le socle des trois premiers piliers est codé, les premières mesures arrivent."
summary: "Un SaaS d'archives de presse jazz, en construction : recherche hybride avec réponses citées à la page du PDF, dossiers rédigés par une équipe d'agents, data-journalisme en Text-to-SQL sécurisé. Le socle est codé et tourne sur douze numéros de DownBeat ; les mesures de qualité, de coût et de latence sont la prochaine étape."
tags: ["python", "fastapi", "postgresql", "pgvector", "rag", "llm", "agents", "rust", "next.js", "claude code"]
featureImage: "carte.png"
showTableOfContents: true
---

{{< lead >}}
Poser une question en français à des décennies de presse jazz en anglais, et obtenir une réponse
dont chaque phrase renvoie à la page du magazine d'où elle vient. Ou rien, si l'archive ne dit
rien.
{{< /lead >}}

{{< fiche-projet
    statut="En développement · socle des trois premiers piliers codé, mesures à venir"
    periode="Depuis octobre 2026"
    role="Solo : cadrage, architecture, développement"
    stack="Python 3.12, FastAPI, SQLAlchemy async, PostgreSQL 17, pgvector, Redis, bge-m3, Claude Opus 5.5 et Haiku 5.5, Rust (PyO3), sqlglot, Next.js 16, React 19, Tailwind 4, Plotly, Docker Compose"
    code="https://github.com/gwils28/jazzar" >}}

{{< stats >}}
{{< stat value="1 124" label="pages DownBeat indexées" >}}douze numéros de 2025, découpés en 3 381 extraits{{< /stat >}}
{{< stat value="17" label="cas d'évaluation" >}}dont 6 pièges où la seule bonne réponse est de refuser{{< /stat >}}
{{< stat value="0" label="ligne de code généré exécutée" >}}le SQL du modèle est validé, les graphiques sont une spécification{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Projet en cours.** Cette fiche décrit l'état du dépôt au 31 octobre 2026, une semaine après le
premier commit. Le code des trois premiers piliers est écrit et la recherche tourne sur le vrai
corpus, mais la synthèse par Claude n'a pas encore été évaluée en réel : **aucun chiffre de
qualité, de coût ou de latence n'est encore mesuré.** La fiche sera mise à jour à chaque étape de
la feuille de route.
{{< /alert >}}

{{< alert icon="image" >}}
**La couverture est une maquette**, pas une capture : elle reprend la charte de l'application
(palette, typographies, logo) sur une question dont la réponse est vérifiable.
{{< /alert >}}

## Le problème

Le jazz est une musique très documentée par sa presse. DownBeat paraît depuis 1934 : critiques
d'albums notées sur cinq étoiles, interviews, *Blindfold Tests*, résultats des *Critics Poll* et
*Readers Poll*. Pour qui cherche quelque chose de précis (ce qu'un critique pensait d'un album à sa
sortie, l'évolution de la réception d'un musicien sur vingt ans, qui a gagné un poll une année
donnée), cette masse est pourtant difficile à exploiter : des milliers de PDF, une recherche
plein-texte qui bute sur l'OCR, et aucun moyen de poser une question chiffrée sur les notes.

Un assistant conversationnel généraliste ne règle pas le problème. Il répond avec aplomb, y compris
quand il invente, et ne dit pas d'où vient ce qu'il affirme. Sur un sujet où les noms, les dates
et les personnels de session comptent, c'est rédhibitoire.

Je voulais un outil qui parte de l'archive elle-même :

- **cité à la page** : chaque affirmation renvoie à l'extrait et à la page du PDF d'où elle vient ;
- **capable de se taire** : une question à prémisse fausse ou sans réponse dans l'archive doit
  obtenir un refus, pas une invention ;
- **multilingue** : des questions en français sur un corpus en anglais ;
- **économe** : le gros modèle seulement là où il sert, le reste servi par un petit modèle, un cache
  ou une simple requête ;
- **debout sans IA** : si l'API du modèle tombe, l'application continue de chercher et de montrer
  les extraits.

C'est d'abord un outil personnel (le jazz est l'autre moitié de ce site, voir
[le carnet jazz](/jazz/)), hébergé sur ma machine. Mais il est structuré pour devenir un SaaS B2B
sans refonte : labels, documentaristes, programmateurs de festivals, journalistes culturels,
historiens. Le nom vient de là : *jazz* et *quasar*.

## Quatre piliers

Le cahier des charges du 25 octobre a fixé un choix inhabituel pour un MVP : trois piliers « assez
avancés » d'emblée plutôt qu'un seul poli. Un quatrième a été spécifié le 29 octobre.

| Pilier | Ce qu'il fait | État au 31 octobre |
|---|---|---|
| **Demander** | Une question → routage → recherche hybride → réponse en flux, chaque affirmation citée `[n]` et cliquable vers la page du PDF | Codé ; validé en mode sans IA sur le vrai corpus ; synthèse par Claude pas encore testée en réel |
| **Dossiers** | « Prépare-moi un dossier sur la scène de Chicago 1965-1975 » → équipe d'agents → livrable rédigé, chaque phrase sourcée | Codé, jamais exécuté avec une clé API |
| **Insights** | Une question chiffrée → SQL généré et validé → données → graphique et lecture rédigée | Codé ; les tables des critiques et des polls sont encore vides |
| **Découvrir** | Albums, artistes et morceaux recommandés selon les goûts, chaque carte expliquée par une citation de l'archive | Spécifié, pas encore codé |

Deux espaces transversaux complètent l'ensemble : la **Bibliothèque** (documents, extraits, lien
vers la page citée) et l'**Observatoire** (latence, coût par usage, taux de cache, retours 👍/👎,
résultats des évaluations).

## Où en est le projet

{{< timeline >}}

{{< timelineItem icon="check" header="Socle initial" badge="25 octobre" subheader="Les trois premiers piliers d'un coup" >}}
Monorepo backend Python, frontend Next.js et extension Rust. Ingestion Markdown, Wikipedia et PDF,
recherche hybride, routeur, cache sémantique, pipeline Dossiers, moteur Text-to-SQL, golden set
et Observatoire. Un corpus d'exemple fictif sert de bouchon pour développer sans archives.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Le vrai corpus" badge="28 octobre" subheader="Douze numéros de DownBeat 2025" >}}
Préparation OCR, nommage des numéros reconnu, en-têtes de page filtrés, extraits trop courts
écartés : 1 124 pages et 3 381 extraits indexés. Validation de la recherche en mode sans IA.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Identité visuelle et cahier des charges" badge="28-29 octobre" subheader="Une référence qui suit le code" >}}
Logo croche-quasar, palette et typographies validés. Le cahier des charges devient la référence du
périmètre, avec son journal des décisions. Le pilier Découvrir y est spécifié.
{{< /timelineItem >}}

{{< timelineItem icon="lightbulb" header="Brancher Claude et mesurer" badge="Prochaine étape" subheader="Une ligne de base chiffrée" >}}
Rejouer les questions qui échouent en mots-clés, lancer l'évaluation complète : fidélité, pièges,
coût et latence, pour la première fois sur de vraies réponses.
{{< /timelineItem >}}

{{< timelineItem icon="list" header="Données structurées, catalogue, Découvrir" badge="À venir" subheader="Ce qui débloque la BI et la recommandation" >}}
Extraire les notes des critiques et les résultats des polls, segmenter les numéros en articles,
relier critiques et albums à MusicBrainz, puis construire la recommandation.
{{< /timelineItem >}}

{{< /timeline >}}

## Comment ça marche

{{< mermaid >}}
flowchart TD
    subgraph Ingestion
        direction LR
        P["PDF DownBeat<br/>Wikipedia · Markdown"] --> T["Nettoyage OCR, découpage, simhash<br/>(Rust, repli Python)"]
        T --> E["Embeddings bge-m3<br/>locaux, GPU"]
        E --> DB[("PostgreSQL<br/>pgvector + plein-texte")]
    end
    subgraph Demander
        direction TD
        Q[Question] --> R["Routeur<br/>Haiku, sortie structurée"]
        R --> C{Cache<br/>sémantique}
        C -->|"cosinus ≥ 0,95"| A
        C -->|absent| H["Recherche hybride<br/>vecteurs ∪ mots-clés, RRF"]
        DB --> H
        H --> A["Réponse citée [n]<br/>Opus ou Haiku selon la route"]
    end
{{< /mermaid >}}

### Ingestion : la page comme unité de citation

Un PDF de DownBeat devient un document, et **la page est l'unité de citation** : c'est ce qui
permet d'ouvrir le PDF exactement là où se trouve l'extrait cité. Les numéros fournis par
l'éditeur ont du texte embarqué sur environ 83 % des pages ; les autres passent par `ocrmypdf` en
mode `--skip-text`, qui garde le texte natif et n'océrise que les pages image. J'ai essayé
`--force-ocr` : le fichier grossit de 2,3 fois et le texte obtenu est moins bon que celui de
l'éditeur. Les publicités pleine page restent sans texte, un choix assumé pour l'instant.

Deux filtres comptent plus qu'ils n'en ont l'air. Les folios du type « 12 DOWNBEAT JULY 2025 »,
répétés en tête de chaque page, sont retirés à l'extraction : sans cela, une question sur
juillet 2025 remonte toutes les pages de ce numéro. Et les extraits de moins de 60 caractères ne
sont pas indexés : ce sont surtout des légendes et des fragments de mise en page.

Le nettoyage, le découpage et la détection de quasi-doublons (simhash) tournent dans une extension
Rust appelée depuis Python (PyO3). Un repli Python à interface identique existe, et un test de
parité vérifie que les deux produisent la même chose. Toute modification de l'algorithme se fait
dans les deux, sinon le test casse.

Les embeddings viennent de `BAAI/bge-m3`, en local sur le GPU : 1 024 dimensions, multilingue (une
question en français trouve un passage en anglais), et aucun coût d'API.

### Demander : router avant de chercher

Toutes les questions ne méritent pas le même traitement. Un petit modèle (Claude Haiku 5.5, effort
bas, sortie structurée validée par Pydantic) classe d'abord la question en cinq routes :

| Route | Exemple | Traitement |
|---|---|---|
| `lookup` | « Qui joue du piano sur *Freddie Freeloader* ? » | Peu d'extraits, petit modèle |
| `semantic` | « Que disait la critique de *Bitches Brew* à sa sortie ? » | Recherche hybride, grand modèle |
| `synthesis` | « Résume l'évolution de la critique sur Monk sur vingt ans » | Recherche élargie, grand modèle, effort élevé |
| `bi` | « Note moyenne du free jazz contre le hard bop dans les années 60 » | Text-to-SQL (pilier Insights) |
| `clarify` | Une entité ambiguë sans contexte | Demande de précision |

Le même appel extrait les **filtres exacts** que contient la question (bornes d'années, types de
document, auteurs) et une liste de mots-clés **en anglais** pour la recherche plein-texte. Si le
modèle est indisponible, une heuristique prend le relais : expressions régulières sur les années
et les décennies, quelques mots déclencheurs pour la BI.

La recherche est **hybride** : une recherche vectorielle (pgvector, HNSW, cosinus) et une recherche
plein-texte (`tsvector` de PostgreSQL) tournent avec les mêmes filtres SQL, puis leurs classements
sont fusionnés par *Reciprocal Rank Fusion* (k = 60). La RRF ne combine que des rangs, ce qui
évite d'avoir à calibrer deux échelles de score incomparables. Une dernière passe limite à trois
extraits par document, pour qu'un long article ne monopolise pas la réponse.

Le modèle de réponse ne peut citer que les extraits fournis, et l'interface relie chaque `[n]` à sa
source. Devant la réponse, un **cache sémantique** Redis sert les questions déjà posées : si une
question passée a un embedding à plus de 0,95 de cosinus, avec les mêmes filtres et la même
langue, la réponse et ses citations reviennent sans appel au modèle.

Enfin, le **mode dégradé** : sans clé API ou si l'API tombe, l'application démarre quand même et
renvoie les extraits classés par la recherche plein-texte. C'est ce mode qui a servi à valider
l'ingestion du vrai corpus. Il a aussi montré sa limite : une question comme « qui a gagné le
Critics Poll 2025 ? » échoue en mots-clés seuls, ce qui fait d'elle le premier test de la synthèse.

### Dossiers : une équipe d'agents, chaque phrase sourcée

Le cas d'usage visé est celui d'un professionnel qui n'a pas le temps de poser cinquante questions :
un producteur, une documentariste, un programmateur qui veut un livrable rédigé et sourcé. Le
pipeline enchaîne quatre rôles :

{{< steps >}}
{{< step number="1" title="Planificateur" >}}
Une sortie structurée : un titre, des sections, et pour chaque section deux à quatre questions de
recherche précises.
{{< /step >}}
{{< step number="2" title="Chercheur" >}}
Une boucle agentique (le *tool runner* du SDK Anthropic, quatorze itérations au plus) avec trois
outils : la recherche hybride, la lecture d'un document entier à partir d'un extrait, et une requête
SQL sur les métadonnées, qui passe par la même validation que le pilier Insights. Chaque extrait vu
reçoit un identifiant court `[S-xxxxxxxx]`, dérivé de l'identifiant réel de l'extrait en base.
{{< /step >}}
{{< step number="3" title="Rédacteur" >}}
Il rédige le dossier en Markdown à partir des notes du chercheur, chaque affirmation suivie de sa
référence `[S-…]`, copiée telle quelle.
{{< /step >}}
{{< step number="4" title="Critique" >}}
Il vérifie chaque référence : absente de la liste des extraits vus, ou qui n'étaye pas la phrase,
elle est corrigée ou l'affirmation est supprimée.
{{< /step >}}
{{< /steps >}}

Comme chaque référence pointe vers un extrait réel, le livrable final garde des liens cliquables
vers la page source. Chaque étape est journalisée avec le dossier. Le plan d'origine prévoyait
LangGraph ou CrewAI ; le *tool runner* du SDK suffit pour une boucle de cette taille, et garde
toute l'orchestration lisible dans un seul fichier.

### Insights : le SQL généré traité comme une entrée non fiable

La question « montre-moi l'évolution de la note moyenne du free jazz face au hard bop dans les
années 60 » ne se répond pas avec des extraits, mais avec un calcul sur les métadonnées (notes,
années, genres, labels). Le grand modèle produit un plan structuré : la requête SQL et la forme du
graphique. Ce SQL est ensuite traité comme n'importe quelle entrée venue de l'extérieur :

- analysé par `sqlglot` : **une seule instruction**, et ce doit être un `SELECT` (CTE et `UNION`
  admis) ;
- tout nœud `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER` ou `SET`, même imbriqué, est
  refusé ;
- les tables lues doivent figurer dans une **liste blanche** de cinq tables analytiques ;
- un `LIMIT 500` est ajouté, ou imposé s'il était plus grand ;
- l'exécution passe par un rôle PostgreSQL **en lecture seule**, avec un `statement_timeout` de
  huit secondes.

Les deux premières protections attrapent les erreurs du modèle ; les deux dernières tiennent même
si la validation laissait passer quelque chose. Le graphique, lui, n'est pas du code : c'est une
spécification Plotly en JSON rendue par le navigateur, qui applique la palette. Le plan d'origine
prévoyait un *Code Interpreter* qui aurait écrit et exécuté du Python ; je l'ai écarté, parce
qu'exécuter du code généré ouvre une surface de risque sans rien apporter de plus pour des
graphiques standards. Un petit modèle rédige ensuite la lecture du résultat.

### Évaluer et observer

Le golden set contient 17 cas : 10 questions factuelles simples, une question qui demande de
relier plusieurs sources, et **6 pièges**. Un piège pose une question à prémisse fausse (« Sur quel
album John Coltrane et Jimi Hendrix ont-ils enregistré ensemble ? », « Quel Grammy Charlie Parker
a-t-il remporté en 1953 ? ») : la seule réponse correcte est de refuser, et certaines formulations
sont interdites dans la réponse.

L'évaluation ne produit pas seulement un score : elle a des **seuils bloquants**.

| Seuil | Valeur exigée |
|---|---|
| Pièges réussis (`refusal_trap_pass_rate`) | 100 % |
| Couverture des citations sur les questions factuelles | 100 % |
| Fidélité aux sources, notée par un juge Haiku | ≥ 95 % |
| Bon document retrouvé (`retrieval_passk`) | ≥ 85 % |

Un seul piège raté fait échouer l'évaluation, quel que soit le reste. Côté observabilité, chaque
appel au modèle est tracé en base avec ses tokens, son usage du cache et son coût réel ; chaque
question l'est avec sa route, sa latence et le retour 👍/👎 de l'utilisateur. L'Observatoire affiche
le tout.

## Ce qui a changé par rapport au plan de départ

Le projet est parti d'une note de conception rédigée avant tout code (`plan.md` dans le dépôt).
Le cahier des charges consigne chaque écart.

| Sujet | Plan de départ | Choix retenu | Raison |
|---|---|---|---|
| Base vectorielle | Qdrant ou GCP Vector Search | pgvector dans PostgreSQL | Un seul service, les filtres SQL exacts dans la même requête ; suffisant jusqu'à plusieurs millions d'extraits |
| Modèles | Llama 3 8B en petit, Gemini 1.5 Pro ou GPT-4o en grand | Claude Haiku 5.5 et Opus 5.5 | Un seul fournisseur, sorties structurées, cache de prompt |
| Orchestration | LangGraph ou CrewAI | *Tool runner* du SDK Anthropic | Une boucle de cette taille n'a pas besoin d'un framework |
| Graphiques | Code Interpreter | Spécification Plotly JSON | Aucun code généré exécuté |
| Évaluation | RAGAS | Golden set maison, juge Haiku, seuils bloquants | Des pièges spécifiques au jazz, et un échec qui bloque |
| Observabilité | LangSmith ou Datadog | Tables `llm_calls` et `queries` | Suffisant en local ; un outil externe reste branchable |

## Les données, et ce que je ne fais pas avec

Les douze numéros de 2025 viennent de mon abonnement personnel, pour un usage privé : ils ne sont
ni publiés ni redistribuables, et le dépôt ne les contient pas. Un corpus d'exemple sert au
développement : les faits discographiques y sont exacts, mais les notes et les formulations
critiques sont inventées et marquées comme telles (`source: sample`), pour être retirées dès que
les vraies archives suffisent.

Pour les archives historiques, j'ai catalogué les 1 280 PDF de DownBeat (1937-1999) hébergés par
worldradiohistory.com. Le site a retiré son index public, bloque les clients qui ne sont pas des
navigateurs et interdit les robots d'IA dans son `robots.txt`. Je n'ai donc pas écrit de
téléchargeur : l'acquisition se fera à la main ou avec l'accord du responsable du site.

## Les objectifs chiffrés, et ce qu'ils valent aujourd'hui

Le plan fixe des objectifs précis. Aucun n'est encore mesuré, et l'un d'eux n'est probablement pas
tenable tel quel.

| Objectif | Cible | État au 31 octobre |
|---|---|---|
| Aucune affirmation sans source | Citations obligatoires, critique des dossiers | Implémenté, à vérifier par l'évaluation |
| Pièges anti-hallucination | 100 % | Implémenté, pas de première mesure |
| Fonctionnement sans IA | Recherche et extraits sans clé API | Validé sur le vrai corpus |
| Latence | p95 < 1,5 s | Non mesurée |
| Coût | < 0,01 $ par requête complexe | Estimé de 0,04 à 0,15 $ selon la route : non tenu sur Opus |

L'estimation de coût est faite à partir de la taille des prompts : moins d'un dixième de centime
pour un `lookup`, quatre à six centimes pour une question `semantic`, dix à quinze pour une
synthèse, cinquante centimes à un dollar et demi pour un dossier. Les leviers sont connus (effort
bas sur la route `semantic`, modèle intermédiaire en grand modèle, configurable par variable
d'environnement), mais je préfère les arbitrer sur une évaluation réelle que sur une estimation.

## La suite

La feuille de route du cahier des charges est ordonnée par dépendances :

1. **Brancher Claude et mesurer** : une première ligne de base chiffrée de la fidélité, des pièges,
   du coût et de la latence.
2. **Remplir les critiques et les polls** : dans les PDF, les notes sont des glyphes d'étoiles dans
   une police à symboles (`HHHH` pour quatre étoiles), extractibles sans modèle avec l'artiste,
   l'album, le label et l'auteur. C'est ce qui donnera au pilier Insights de vraies données.
3. **Segmenter les numéros en articles** et extraire les entités citées (artistes, albums,
   morceaux), pour des citations complètes avec titre et auteur.
4. **Relier l'archive à MusicBrainz** : chaque critique rattachée à son album et à ses musiciens,
   ce qui sert à la fois la BI et la recommandation.
5. **Découvrir** : une recommandation en couches, du contenu (profil construit à partir des
   embeddings, diversité par MMR) vers le graphe (PageRank personnalisé sur artistes, albums et
   sidemen), puis le comportement quand il y aura des utilisateurs. L'archive n'y est pas l'objet
   recommandé mais sa preuve : une carte sans citation à l'appui n'est pas affichée.

Le chemin vers le SaaS (authentification, organisations, quotas, paiement, déploiement) vient
ensuite. Les colonnes et le traçage des coûts sont pensés pour l'accueillir sans refonte, mais le
critère pour s'y engager est simple : que l'outil me convainque d'abord, moi.

## Ce que j'en retiens pour l'instant

- **Le mode sans IA a servi avant l'IA.** Je l'avais prévu comme une sécurité en production ; il a
  surtout permis de valider l'ingestion du vrai corpus, et de trouver les questions qui ont
  réellement besoin du modèle.
- **Le nettoyage des PDF pèse autant que la recherche.** Les folios répétés et les fragments de
  mise en page dégradaient les résultats plus que n'importe quel réglage de la fusion.
- **Écrire les écarts au plan au fur et à mesure.** Six choix techniques ont changé par
  rapport à la note de départ ; le journal des décisions garde la trace du pourquoi, ce qui m'a
  aussi servi à écrire cette fiche. Le projet suit
  [ma méthode de travail avec Claude Code](/posts/claude-code-methode-revisee/).
