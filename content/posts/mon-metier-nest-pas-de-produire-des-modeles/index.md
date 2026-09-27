---
title: "Mon métier n'est pas de produire des modèles"
date: 2026-09-27
draft: false
description: "Écrire du code analytique est devenu quasi gratuit. Ce qui reste cher — et ce que ça change pour un Data Scientist en 2026."
summary: "Écrire du code analytique est devenu quasi gratuit. Ce qui reste cher — et ce que ça change pour un Data Scientist en 2026."
categories: ["Métier"]
tags: ["manifeste", "ia-générative", "mlops", "inférence-causale"]
showTableOfContents: true
---

Il y a un moment, dans la vie d'un métier, où l'accumulation d'outils cesse
d'être une amélioration progressive et devient un changement de nature. Le
métier de Data Scientist a connu ce moment entre 2023 et 2026.

Ce n'est pas parce que les modèles sont devenus plus gros. C'est parce
qu'**écrire du code analytique est devenu quasi gratuit**. Une pipeline de
features, un baseline gradient boosting, un notebook d'exploration, une API
FastAPI, un dashboard : ces tâches qui constituaient encore en 2021 l'essentiel
de la valeur observable d'un junior confirmé se produisent aujourd'hui en
quelques minutes, pilotées par n'importe qui sachant formuler une intention.

La conséquence est brutale et mal digérée par la profession : **la production
n'est plus le goulot d'étranglement. Le jugement l'est.**

Un métier dont la valeur reposait sur la capacité à produire un artefact
technique voit cette valeur s'effondrer quand l'artefact devient gratuit. Un
métier dont la valeur repose sur la capacité à décider *quel* artefact produire,
*à quelle question* il répond et *combien vaut* la décision qu'il modifie, voit
sa valeur augmenter dans le même mouvement.

J'ai passé un an à mettre cette conviction par écrit. Voici ce que j'en retiens.

## Ce qui ne vaut plus rien

Il faut nommer précisément ce qui s'est effondré, sans complaisance et sans
catastrophisme.

- **La syntaxe.** Connaître par cœur l'API de pandas, l'ordre des arguments de
  `train_test_split`, la façon d'écrire une fenêtre glissante en SQL. Valeur
  strictement nulle en 2026.
- **Le code de plomberie.** Parsers, connecteurs, transformations de format,
  scripts d'export, boilerplate de tests.
- **Le baseline.** Un LightGBM correctement paramétré sur un tableau propre, un
  ARIMA sur une série. La machine produit cela mieux et plus vite que la médiane
  des humains.
- **La documentation descriptive.** Docstrings, README de structure, résumés de
  notebook.
- **L'exploration de première passe.** Distributions, valeurs manquantes,
  cardinalités, corrélations.
- **La veille de surface.** Résumer un papier, comparer trois bibliothèques.

Dans beaucoup d'organisations, cette liste représentait entre 50 et 70 % du
temps réellement passé par les équipes data en 2021. C'est l'ampleur du choc.

## Ce qui a pris de la valeur

Symétriquement, certaines compétences ont vu leur valeur relative augmenter,
précisément parce que le reste s'est effondré.

**Le cadrage.** Traduire un problème métier flou en une question statistiquement
traitable, avec une unité d'analyse, une population, une fenêtre temporelle, une
métrique de succès et un critère d'arrêt. Aucun assistant ne fait cela, parce
que cela demande de savoir ce que l'organisation ne dit pas.

**Le jugement sur la validité.** Savoir qu'un résultat est faux *avant* de
savoir pourquoi. L'odeur du surapprentissage, la sensation qu'un R² de 0,97 sur
des données réelles est une fuite, la méfiance devant un uplift de 40 %. C'est
une compétence bayésienne construite par l'expérience répétée de l'échec, et
elle ne s'externalise pas.

**L'identification causale.** Choisir entre A/B test, différence-de-différences,
contrôle synthétique, discontinuité de régression ; savoir quelles hypothèses
chacun exige et lesquelles sont réfutables dans le contexte donné. C'est un
travail d'argumentation scientifique, pas un travail de calcul.

**La responsabilité.** Signer. Dire « je réponds de ce chiffre ». Aucun modèle
ne peut porter cela, pour des raisons qui ne sont ni techniques ni négociables.

## Le piège du milieu

Entre les deux se trouve un espace dangereux : les compétences qui *semblent*
commoditisées mais dont la commoditisation est une illusion. Ce sont les plus
coûteuses à mal évaluer.

Un assistant génère cent features en trente secondes. Il ne sait pas que la
variable `date_saisie_dossier` est renseignée *après* l'événement à prédire dans
8 % des cas, à cause d'un correctif manuel effectué par le service client. Cette
connaissance-là est la seule qui compte, et elle est locale, non écrite, sociale.

Il propose un ensemble de gradient boosting. Il ne sait pas que le comité de
crédit exige une monotonie stricte sur trois variables pour des raisons
réglementaires.

Il nettoie. Mais décider si une valeur aberrante est une erreur de saisie, un
événement réel rare, ou un signal précurseur est une décision de modélisation
déguisée en tâche de nettoyage.

D'où la règle générale : **ce qui est commoditisé, c'est la manipulation des
symboles. Ce qui ne l'est pas, c'est le raccordement des symboles au monde.**

## Les quatre déplacements

Si je devais résumer le changement en quatre phrases :

1. **Du modèle à la décision.** Un modèle n'a pas de valeur. Une décision
   modifiée a une valeur. La question utile est : quelle décision serait prise
   sans mon travail, quelle décision est prise avec, et quelle est la différence
   en euros ou en risque évité ?
2. **De la prédiction à l'intervention.** Prédire est devenu bon marché.
   Répondre à « que se passe-t-il si j'agis » reste cher, parce que cela demande
   un raisonnement contrefactuel que les données observationnelles ne donnent
   jamais gratuitement.
3. **De la précision à la fiabilité.** Le monde ne manque pas de modèles précis
   un mardi de mars sur un jeu de test. Il manque de systèmes qui restent
   honnêtes dix-huit mois, sous dérive, sous incident amont, sous rotation
   d'équipe.
4. **De l'exécution au cadrage.** Quand l'exécution est gratuite, le coût de la
   mauvaise question explose en proportion. Un système parfaitement exécuté qui
   répond à la mauvaise question est plus coûteux en 2026 qu'en 2019, parce
   qu'il est produit, déployé et adopté plus vite avant que l'erreur ne soit
   détectée.

## Le test du tiroir

Un test simple pour évaluer où l'on en est : que se passe-t-il si on ferme votre
ordinateur pendant un mois ?

- **Si tout s'arrête** : vous *êtes* le système. Vous n'avez rien construit,
  vous opérez.
- **Si tout continue mais rien ne progresse** : vous avez construit un système,
  pas une équipe.
- **Si tout continue et que quelqu'un d'autre a amélioré votre travail sans vous
  demander** : vous avez construit un actif.

Le troisième cas est le seul qui compose dans le temps. C'est celui que je vise.

## Dix-huit façons de se tromper

Une liste de diagnostic. Cinq occurrences ou plus dans une équipe indiquent un
problème structurel, pas individuel.

**Sur le cadrage**

1. **Le projet orphelin** — pas de décision cible, pas d'utilisateur nommé.
2. **La solution en quête de problème** — on a choisi la technologie avant la
   question.
3. **Le périmètre élastique** — chaque réunion ajoute une demande, aucune n'en
   retire.

**Sur les données**

4. **Le nettoyage sans hypothèse** — on impute, on supprime, on plafonne sans se
   demander ce que la valeur signifiait.
5. **L'historique inexistant** — on découvre au bout de six semaines que les
   tables sont écrasées.
6. **La définition flottante** — trois chiffres pour la même grandeur, aucun
   arbitrage.

**Sur la modélisation**

7. **La fuite non détectée** — performance de rêve, effondrement en production.
8. **Le concours de Kaggle** — trois mois d'optimisation d'une métrique
   déconnectée de la décision.
9. **Le modèle sans baseline** — on ne sait pas ce qu'on améliore.
10. **La complexité de prestige** — architecture profonde là où un modèle à
    trois étages suffisait.
11. **Le SHAP causal** — présentation d'importances de features comme des
    leviers d'action.

**Sur la production**

12. **Le notebook déployé** — orchestration d'un notebook comme s'il s'agissait
    d'un service.
13. **Le modèle zombie** — en production, plus personne ne l'utilise, personne
    ne l'éteint.
14. **Le monitoring décoratif** — des tableaux de bord que personne ne regarde,
    aucune alerte actionnable.
15. **Le réentraînement aveugle** — automatique, sans validation de promotion.

**Sur l'organisation**

16. **L'équipe centrale isolée** — techniquement excellente, sans accès au
    métier, produit des travaux non adoptés.
17. **Le héros indispensable** — une personne détient tout, rien n'est
    documenté, le départ est une catastrophe.
18. **La démonstration permanente** — une succession de prototypes
    impressionnants, aucun système en exploitation. Devenu dominant depuis 2024
    avec les systèmes génératifs.

## Contre le mythe de la veille

Je tiens ce blog, donc autant être clair sur ce que j'en attends.

La veille passive — lire des articles, suivre des fils, regarder des conférences
— produit une **illusion de progression**. Elle génère de la reconnaissance
(« je connais ce terme ») sans générer de compétence (« je sais le faire »). Un
professionnel qui consacre cinq heures par semaine à la veille et zéro à la
pratique régresse.

Le ratio défendable est de l'ordre d'**un pour quatre** : une heure de lecture
pour quatre heures de production. Et toute lecture significative doit se
terminer par une implémentation minimale, même jetable. C'est le passage à
l'implémentation qui révèle ce qu'on n'avait pas compris.

C'est la règle que je m'applique ici. Chaque note doit produire un artefact
vérifiable — un commit, un test qui passe, un backtest chiffré. Sans artefact,
la session est comptée comme non faite.

## Ce qui ne changera pas

Les outils cités dans ce texte seront obsolètes en 2030. Les modèles auront
changé deux ou trois fois. Le titre du métier aura peut-être encore bougé.

Ce qui ne bougera pas : la variabilité d'échantillonnage, l'asymétrie des coûts,
l'impossibilité d'inférer une causalité sans hypothèse, le fait qu'un système
non utilisé ne produit rien, et le fait qu'une organisation fait confiance à des
personnes, pas à des modèles.

{{< alert icon="quote" cardColor="#2e6218" iconColor="#f3b73f" textColor="#f3f9f0" >}}
Mon métier n'est pas de produire des modèles, mais de **réduire l'incertitude
sur laquelle des humains engagent de l'argent, du temps et du risque** — et de
le faire d'une manière que d'autres peuvent vérifier, contester et reprendre
après moi.

Tout le reste est de l'outillage.
{{< /alert >}}

## Pour aller plus loin

Ce texte est la version courte. Le manifeste complet développe sept axiomes,
huit piliers techniques, une grille de maturité et les refus qui vont avec.

{{< button href="/manifeste-data-scientist-2026.pdf" target="_blank" >}}Télécharger le manifeste (PDF, 51 p.){{< /button >}}

Les principes qui en découlent et la façon dont je les applique au quotidien
sont résumés sur ma page [À propos]({{< ref "/about" >}}).
