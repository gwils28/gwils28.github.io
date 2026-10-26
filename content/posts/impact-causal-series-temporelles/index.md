---
title: "L'impact causal en séries temporelles : le contrefactuel et ses placebos"
date: 2026-10-26
draft: false
description: "Une journée de veille active sur l'estimation de l'effet d'une intervention sur une série temporelle : un contrefactuel structurel construit à la main, validé par des tests placebo sur un panel à vérité connue et sur le dieselgate de Volkswagen, puis comparé au CausalImpact de Google."
summary: "Un contrefactuel est une prévision. Ce que j'ai observé en le construisant à la main, en mesurant sa couverture sur 100 panels à vérité connue, en plantant quatre violations du design et en l'appliquant au cours de Volkswagen après le dieselgate."
categories: ["Veille"]
featureImage: "cover.png"
tags: ["inférence causale", "séries temporelles", "contrefactuel", "BSTS", "CausalImpact", "tests placebo", "espace d'états", "python", "forecasting"]
showTableOfContents: true
---

{{< katex >}}

{{< lead >}}
Quel a été l'effet d'une promotion, d'un changement de prix, d'une annonce, sur une série que l'on
n'a pas pu randomiser ? La réponse habituelle est un contrefactuel : une prévision de ce que la
série aurait fait sans l'intervention. En la construisant à la main, j'ai surtout appris ce que
cette prévision ne peut pas dire d'elle-même, et ce que les tests placebo permettent d'en vérifier.
{{< /lead >}}

*Temps de lecture : environ 40 minutes. Les formules sont toujours suivies de leur intuition : on
peut les survoler sans perdre le fil. Le dépôt est en anglais, ses figures aussi.*

{{< note-ia >}}

Cet article restitue une **journée de veille active** sur l'inférence causale appliquée aux séries
temporelles, annoncée à la fin de [l'article sur la fréquence de
réentraînement]({{< ref "/posts/frequence-reentrainement" >}}). Je suis parti d'un plan de travail
en quatre blocs : deux articles récents à lire à la source, un contrefactuel à construire et à
valider par placebo, une décision d'architecture pour une mesure d'incrémentalité en continu, et
l'article fondateur de Brodersen et ses collègues à relire équation par équation. Le plan proposait
un critère de réussite simple : un effet réel dont l'intervalle exclut zéro, un effet placebo dont
l'intervalle contient zéro. Je l'ai atteint, puis j'ai cherché ce qu'il garantit vraiment, sur un
panel où la vérité est connue. Tout est reproductible dans le dépôt
[time_series_causal_statistics](https://github.com/gwils28/time_series_causal_statistics).

{{< alert icon="lightbulb" >}}
**En bref.** Les principaux résultats, avec leur périmètre :

1. **Le critère du plan est atteint sur une vérité connue et sur Volkswagen** : −20,9 %
   [−33,9 % ; −1,7 %] sur le cours de VW après l'avis de l'EPA, et douze fausses dates
   d'intervention toutes propres.
2. **Le placebo dans le temps ne valide que le modèle pré-intervention.** Sur 100 panels où un
   contrôle est contaminé par l'intervention, il est vert exactement aussi souvent que sur des
   panels propres (17 % de fausses alertes dans les deux cas). La contamination demande le placebo
   dans l'espace ; une relation qui casse à la date de l'intervention n'est vue par rien.
3. **Un placebo qui « trouve » un effet est en partie une propriété du placebo lui-même** : avec
   une pré-période de 243 jours, l'intervalle au maximum de vraisemblance sous-couvre, et le placebo
   se déclenche sur 11 à 17 % des panels propres, pour un nominal de 5 %.
4. **Les estimateurs statiques (OLS sur les contrôles, contrôle synthétique convexe, différence de
   différences) sont aussi précis que le niveau local sur l'estimation ponctuelle, et six à sept
   fois trop confiants** : 80 % de faux positifs à effet nul.
5. **Le port Python du CausalImpact de Google donne les mêmes estimations ponctuelles avec des
   intervalles deux fois plus étroits.** C'est son a priori par défaut sur l'écart-type du niveau
   (0,01), pas les données : sur 30 panels à vérité connue, son intervalle à 95 % couvre 77 % du
   temps, celui construit à la main 90 %.
{{< /alert >}}

## 1. Le problème : une unité, deux mondes

L'effet causal d'une intervention sur une unité à la date \(t\) est la différence entre ce qu'on
observe, \(y_t\), et ce qu'on aurait observé sans l'intervention, \(y^0_t\). La seconde quantité
n'existe plus dès que l'intervention a eu lieu. Une analyse contrefactuelle est donc une
**prévision** de \(y^0_t\) sur la période post-intervention, et l'effet est l'écart entre
l'observé et cette prévision.

![L'unité traitée : observée et contrefactuelle](nb01_two_worlds.svg "Sur le panel synthétique, le contrefactuel y0 est connu (en vert) : la différence avec l'observé (en bleu) est l'effet réel, ici une hausse de 10 % plantée sur 90 jours. En pratique, seule la courbe bleue existe.")

Tout l'enjeu est de rendre cette prévision crédible, et honnête sur son incertitude. Mais une
bonne prévision n'est pas un modèle causal. Le plan de travail le formulait comme un réflexe à
acquérir : savoir quand une prévision a un contenu causal, et le prouver par des tests placebo.

Le contrefactuel se construit à partir de **séries de contrôle** : des unités comparables, non
touchées par l'intervention, dont la relation avec l'unité traitée, apprise avant la date,
est extrapolée après. Trois hypothèses portent le résultat, et aucune n'est visible dans la qualité
de l'ajustement pré-intervention :

| Hypothèse | Ce qu'elle signifie pour une série traitée | Ce qui la teste |
|---|---|---|
| la date d'intervention est « comme aléatoire » étant donné le passé | pas d'anticipation, pas d'événement simultané propre à l'unité traitée | **placebo dans le temps** : une fausse date dans la pré-période doit donner un effet dont l'intervalle contient zéro |
| les contrôles ne sont pas affectés, directement ni par ricochet | pas d'interférence : la promotion sur A ne cannibalise pas B, utilisé comme contrôle | **placebo dans l'espace** : chaque contrôle traité comme s'il était l'unité d'intérêt, à la vraie date |
| la relation pré-intervention persiste | les coefficients qui lient contrôles et cible restent valables après la date | diagnostics de stabilité sur la pré-période, et couverture sur un panel à vérité connue |

Le protocole du plan tient en trois étapes : ajuster un modèle structurel sur la pré-période
seulement, prévoir le contrefactuel et estimer l'effet ponctuel et cumulé avec un intervalle à
95 %, puis rejouer exactement la même analyse avec une fausse date d'intervention placée dans la
pré-période. Je l'ai fait deux fois : sur un panel semi-synthétique où la vérité est connue, pour
pouvoir noter la méthode et pas seulement l'exécuter, et sur le panel Volkswagen du dieselgate.

## 2. Ce que disent les travaux récents

J'ai lu deux articles de 2026 et relu celui de 2015 qui fonde la méthode. Pour chacun, je suis allé
vérifier dans le corps du texte ce que le plan en disait.

**Time-Aware Synthetic Control** (Rho, Illick, Narasipura, Abadie, Hsu et Misra,
[arXiv 2601.03099](https://arxiv.org/abs/2601.03099), janvier 2026). Le contrôle synthétique
classique traite les indices temporels de la pré-période comme interchangeables : permuter les
colonnes ne change pas les poids. TASC garde la structure de rang faible du contrôle synthétique
mais encode le temps par un modèle espace-état linéaire gaussien à tendance constante, appris par
EM (filtre de Kalman et lisseur de Rauch-Tung-Striebel). Le contrefactuel vient du chargement de la
cible sur les états lissés, pas d'une combinaison convexe de donneurs. Ce que j'ai retenu des
simulations : TASC gagne quand le bruit d'observation est fort, perd face au contrôle synthétique
robuste quand il est faible, et apporte peu sans tendance. Permuter l'ordre de la pré-période fait
monter son erreur de 48,5 %, ce qui est bien la preuve qu'il utilise la structure temporelle.

Deux écarts entre le plan et la source. Le plan présentait l'article comme « signé par Abadie
lui-même » : Alberto Abadie est le quatrième de six auteurs. Et le plan retenait que TASC « produit
des intervalles de confiance plus étroits » que le CausalImpact bayésien : c'est bien ce que les
auteurs écrivent pour la Proposition 99 et le cricket, mais c'est une affirmation sur la
**largeur**, et aucune couverture n'est rapportée dans l'article. Un intervalle plus étroit n'est
pas montré meilleur. Ce point revient en partie 9, où je mesure ce qu'un intervalle étroit coûte.

**When are time series predictions causal?** (Carlson et Shephard,
[arXiv 2603.20394](https://arxiv.org/abs/2603.20394), mars 2026). L'article conceptuel. Son
« système potentiel » indexe les résultats potentiels par des trajectoires d'assignation, avec deux
restrictions structurelles : non-anticipation (le résultat en \(t\) ne dépend que des assignations
jusqu'à \(t\)) et triangularité (les variables explicatives en \(t\) ne dépendent que des
assignations jusqu'à \(t-1\)). Le résultat central, le théorème 2, se dit en une phrase : **sous
une condition d'assignation adaptée, une différence de prévisions est un effet causal.** Sans
cette condition, c'est une différence de prévisions. Le tableau de la partie 1 est ma traduction
de cette condition en trois exigences concrètes pour une seule série traitée. L'article relie
aussi fonctions de réponse impulsionnelle, projections locales et SVAR à ce cadre, et rappelle que
la causalité de Granger « ne porte pas vraiment sur la causalité, mais sur la prévision ».
L'affiliation « Harvard » indiquée dans le plan n'est pas sur la page du résumé ; je ne l'ai pas
vérifiée.

**Brodersen, Gallusser, Koehler, Remy et Scott (2015)**,
[*Inferring causal impact using Bayesian structural time-series models*](https://arxiv.org/abs/1506.00356),
Annals of Applied Statistics. Le modèle : un espace d'états dont l'observation est une lecture
linéaire d'un état latent, assemblé par blocs (niveau local, tendance, saisonnalité, régression
statique ou dynamique sur les contrôles), avec des a priori sur les variances et un a priori
*spike-and-slab* sur les coefficients de régression, inféré par Gibbs. Ce qui compte pour l'impact
causal est la distribution prédictive a posteriori, conditionnée à la série traitée avant la date et
aux contrôles avant et après, définie **conjointement** sur la post-période pour que la structure
sérielle se propage dans l'effet cumulé.

Trois choses de cet article m'ont servi dans la suite. Leur étude de simulation note la méthode par
deux courbes, la puissance et la couverture, et montre qu'une hausse de 1 % est manquée dans 90 %
des cas. Leur troisième analyse empirique applique le modèle aux **régions non traitées** et exige
un résultat nul : c'est le placebo dans l'espace, avec leur propre phrase, « si l'effet de la
campagne était vraiment propre aux régions traitées, il ne devrait y avoir aucun effet dans les
contrôles ». Et leur avertissement central, repris mot pour mot par le plan : toutes ces inférences
dépendent de l'hypothèse que les covariables n'ont pas elles-mêmes été affectées par
l'intervention. L'article en nomme deux autres, que le plan ne citait pas : la relation
pré-intervention persiste, et la structure du modèle reste intacte. La figure 4 de l'article montre
ce qui arrive sinon : tripler l'écart-type de marche aléatoire d'un coefficient 90 jours après le
début de la campagne fait exploser l'erreur.

## 3. Le modèle : un niveau local et une régression sur les contrôles

Le plan proposait `tfcausalimpact` ou `pycausalimpact`, et sinon `statsmodels` à la main. J'ai
choisi la main, pour savoir ce qu'il y a dedans, et gardé le port de Google comme contrôle croisé
(partie 9). Le modèle est celui de Brodersen sans sa couche bayésienne :

$$
y_t = \mu_t + \beta' x_t + \varepsilon_t, \qquad \mu_{t+1} = \mu_t + \eta_t,
\qquad \varepsilon_t \sim \mathcal N(0, \sigma^2_\varepsilon),\ \eta_t \sim \mathcal N(0, \sigma^2_\eta).
$$

**L'intuition.** La régression \(\beta' x_t\) explique la part que l'unité traitée partage avec
ses contrôles. Le niveau \(\mu_t\), une marche aléatoire, absorbe le reste : ce que la cible fait
toute seule et que les contrôles ne voient pas. Les deux variances sont estimées par maximum de
vraisemblance sur la pré-période seulement ; le contrefactuel est la prévision du filtre de Kalman
sur la post-période, étant donné les contrôles observés après la date. Comme cette distribution
est gaussienne, je simule des trajectoires **conjointes** du contrefactuel, ce dont l'intervalle de
l'effet cumulé a besoin ; un test du dépôt vérifie que les quantiles simulés retombent sur
l'intervalle analytique.

Pour voir ce que chaque composante apporte, j'ai ajusté trois modèles sur le même panel : une
régression statique seule, le niveau local plus régression, et une tendance linéaire locale plus
régression.

| | statique | niveau local | tendance locale |
|---|---|---|---|
| RMSE à un pas (pré-période) | 3,10 | 2,94 | 2,98 |
| R² à un pas | 0,57 | 0,61 | 0,61 |
| Ljung-Box sur les résidus (p) | **0,000** | 0,94 | 0,90 |
| effet cumulé estimé (vérité 831) | 681 [617 ; 748] | 569 [207 ; 926] | 530 [120 ; 947] |

Les résidus de la régression statique sont autocorrélés : il reste une composante lente que la
régression ne voit pas, et c'est elle que le niveau local absorbe. Mais la différence entre les
modèles n'est pas dans l'ajustement, qui se ressemble. Elle est dans la **prévision** : le modèle
statique suppose que la part inexpliquée est un bruit indépendant chaque jour, le niveau local
suppose qu'elle peut dériver. Ces deux croyances donnent des incertitudes très différentes à 90
jours.

![Trois modèles, trois contrefactuels, trois incertitudes](nb01_three_models.svg "Même panel, même pré-période. La régression statique (à gauche) donne un intervalle étroit qui manque la vérité ; le niveau local (au centre) un intervalle large qui la contient ; la tendance locale (à droite) un intervalle plus large encore.")

La variance de prévision d'une régression statique est constante. Un niveau local ajoute une
variance de marche aléatoire qui croît linéairement avec l'horizon \(h\), donc l'intervalle sur un
jour croît en \(\sqrt h\). Une tendance linéaire locale ajoute une pente aléatoire et la variance
croît en \(h^3\). Pour l'effet **cumulé**, ces puissances montent de deux.

![Vitesse à laquelle chaque modèle admet qu'il ne sait pas](nb01_interval_width.svg "Largeur de l'intervalle à 95 % sur un jour, en fonction de l'horizon : plate pour la régression statique, en racine de h pour le niveau local, plus rapide encore pour la tendance locale.")

Sur ce panel, l'intervalle statique est étroit et manque la vérité ; l'intervalle du niveau local
est large et la contient. Lequel est le bon n'est pas une question de goût : c'est une question de
couverture, que la partie 5 mesure sur 100 panels.

**Une deuxième source d'incertitude.** La distribution de prévision au maximum de vraisemblance
tient compte des chocs futurs et de l'incertitude sur l'état courant. Elle ne tient pas compte de ce
que les variances et les coefficients sont eux-mêmes estimés. CausalImpact intègre les paramètres
par MCMC ; l'équivalent fréquentiste bon marché est de tirer les paramètres dans la normale
asymptotique du maximum de vraisemblance et de mélanger la prévision sur ces tirages. Sur ce panel,
avec 365 jours de pré-période, cela change à peine l'intervalle cumulé : [207 ; 926] devient
[203 ; 914]. La partie 5 montre où ces tirages comptent.

## 4. Le protocole sur une vérité connue

Le panel : une unité traitée et cinq contrôles, 365 jours avant l'intervention et 90 après. Toutes
les unités chargent sur deux facteurs latents (des marches aléatoires) et un motif hebdomadaire,
avec des poids propres ; chaque unité a aussi un petit niveau en marche aléatoire que personne
d'autre ne voit, et un bruit d'observation. Les contrôles sont donc des proxys bruités de ce qui
fait bouger la cible, pas des copies. L'effet planté est une hausse de 10 % sur la post-période, soit
831 unités cumulées. Le contrefactuel \(y^0\) est conservé, ce qui permet de noter chaque
estimateur.

| | effet relatif, IC 95 % | effet cumulé | probabilité de queue |
|---|---|---|---|
| intervention réelle (vérité 10 %, 831) | **+6,6 % [+2,3 % ; +11,3 %]** | 569 [207 ; 926] | 0,000 |
| placebo au jour 243, données tronquées à la vraie date | +0,3 % [−5,3 % ; +6,7 %] | 38 [−655 ; 742] | 0,461 |

![L'intervention réelle et son placebo dans le temps](nb02_real_vs_placebo.svg "En haut, l'analyse à la vraie date : l'intervalle cumulé exclut zéro et contient la vérité. En bas, la même analyse avec une fausse date à deux tiers de la pré-période, sur des données qui s'arrêtent à la vraie date : l'effet cumulé reste autour de zéro.")

Le critère (a) est atteint : l'intervalle réel exclut zéro et contient la vérité. Le critère (b)
aussi : l'intervalle placebo contient zéro confortablement, et son estimation ponctuelle est une
petite fraction de l'estimation réelle. Un détail de mise en œuvre compte ici : le placebo est
calculé sur des données **tronquées à la vraie date**, pour qu'aucune donnée traitée n'entre dans
l'analyse.

Un panel ne prouve rien sur la méthode ; il prouve que le protocole tourne. Deux extensions
rendent le placebo plus informatif :

- **Le placebo dans le temps comme balayage.** Une fausse date est un tirage. Huit fausses dates
  réparties sur la pré-période donnent la distribution des « effets » que le design produit quand
  il ne se passe rien, et c'est le bon étalon pour l'effet réel. Sur ce panel, les huit intervalles
  contiennent zéro, et les faux effets ont un écart-type de 1,8 point.
- **Le placebo dans l'espace comme classement.** Chaque contrôle est traité à son tour comme
  l'unité d'intérêt, à la vraie date, avec les autres contrôles comme donneurs ; l'unité traitée
  réelle n'est jamais utilisée comme contrôle de personne. L'unité réelle se classe première sur
  six par effet absolu.

![Balayage placebo dans le temps et classement placebo dans l'espace](nb02_placebo_sweep_space.svg "À gauche, huit fausses dates avec des fenêtres post de 90 jours : les intervalles contiennent zéro, l'effet réel (en orange) est en dehors du nuage. À droite, chaque unité traitée comme si elle était la cible : l'unité réelle est la seule dont l'intervalle exclut zéro.")

## 5. L'intervalle à 95 % est-il un intervalle à 95 % ?

Brodersen et ses collègues notent leur méthode par deux courbes : la part des intervalles qui
excluent zéro en fonction de l'effet réel (la puissance, et à effet nul le taux de faux positifs),
et la part des intervalles qui contiennent la vérité (la couverture, qui doit rester près de 95 %
quel que soit l'effet). J'ai tracé les mêmes courbes sur 100 panels par taille d'effet, pour
l'intervalle au maximum de vraisemblance, pour l'intervalle mélangé sur des tirages de paramètres,
et pour le placebo dans le temps calculé sur les mêmes panels.

Une propriété du dispositif simplifie la lecture : avec une pré-période fixe, l'erreur
d'estimation ne dépend pas de l'effet planté. Le contrefactuel est ajusté sur la pré-période et
prévu à partir des contrôles post-intervention, que l'effet ne touche ni l'un ni l'autre.
Couverture, largeur et biais sont donc les mêmes à toutes les tailles d'effet ; seule la détection
bouge.

| estimateur | couverture | faux positifs à 0 % | détection à 1 % | 2 % | 5 % | 10 % | largeur moyenne |
|---|---|---|---|---|---|---|---|
| niveau local, intervalle MLE | 0,92 | 0,08 | 0,10 | 0,15 | 0,51 | 0,94 | 874 |
| niveau local, 40 tirages de paramètres | 0,93 | 0,07 | 0,07 | 0,13 | 0,47 | 0,92 | 912 |
| placebo dans le temps sur les mêmes panels (pré-période de 243 jours, vérité 0) | 0,89 | **0,11** | | | | | 1 321 |

![Puissance et couverture sur 100 panels](nb02_power_coverage.svg "À gauche, la part des intervalles qui excluent zéro selon l'effet réel. À droite, la part qui contient la vérité : un peu sous 95 % pour l'intervalle MLE, un point de plus avec les tirages de paramètres, 89 % pour le placebo.")

Trois observations.

**La détection est modeste.** Une hausse de 1 % est invisible, une hausse de 5 % est vue une fois
sur deux, une hausse de 10 % presque toujours, avec 90 jours de post-période et ce niveau de bruit.
C'est le même ordre de grandeur que la simulation de Brodersen, où 1 % est manqué dans 90 % des
cas.

**Le placebo se déclenche plus souvent que 5 %.** Les fenêtres placebo ont une pré-période plus
courte (243 jours au lieu de 365), et leur intervalle est en moyenne plus large mais moins bien
calibré : 11 % de faux positifs. Le plan disait « si ton placebo trouve un effet, ton design est
invalide ». Sur ces panels, un placebo sur neuf trouve un effet sur un design parfaitement valide.
Lire un placebo comme une date isolée contre un seuil de 5 % revient donc à rejeter un design
correct une fois sur neuf. Lire le **balayage** contre son propre taux sur panels propres est plus
juste, et erre du côté prudent.

**La longueur de la pré-période compte, parce qu'une variance demande plus de points qu'une
moyenne.** Sur 50 panels par cellule, à 5 % d'effet :

| pré-période (jours) | 60 | 120 | 240 | 365 | 730 |
|---|---|---|---|---|---|
| niveau local, MLE | 0,72 | 0,84 | 0,92 | 0,88 | 0,92 |
| niveau local, tirages de paramètres | 0,88 | 0,90 | 0,92 | 0,92 | 0,92 |
| OLS sur les contrôles | 0,18 | 0,20 | 0,22 | 0,10 | 0,16 |

![Couverture, largeur et erreur selon la longueur de la pré-période](nb02_pre_length.svg "L'intervalle MLE sous-couvre sur les pré-périodes courtes ; les tirages de paramètres le corrigent. OLS reste autour de 0,2 à toutes les longueurs.")

Les tirages de paramètres servent sur les pré-périodes courtes et deviennent inutiles vers un an
de données quotidiennes. La raison est connue : sur un échantillon court, le maximum de
vraisemblance d'une variance de niveau peut s'écraser à zéro, et un niveau de variance nulle est
un modèle statique avec un intervalle plat et trop confiant. Tirer des paramètres autour d'un
maximum nul ne corrige pas cela ; un a priori le fait, et c'est une raison honnête pour laquelle
CausalImpact en met un sur l'écart-type du niveau. La partie 9 montre le revers de cet a priori.

## 6. Neuf estimateurs sur les mêmes panels

Chaque estimateur s'ajuste sur la pré-période et renvoie l'effet cumulé avec l'intervalle qu'un
praticien calculerait pour lui (erreurs indépendantes pour les plus simples). Mêmes 100 panels,
deux tailles d'effet, 0 et 5 %.

| estimateur | couverture | faux positifs à 0 % | détection à 5 % | largeur | RMSE |
|---|---|---|---|---|---|
| moyenne de la pré-période | 0,10 | 0,90 | 0,88 | 262 | 954 |
| tendance seule (tendance locale, sans contrôle) | 0,96 | 0,04 | 0,15 | 2 224 | 559 |
| différence de différences (moyenne des contrôles) | 0,12 | 0,88 | 0,90 | 148 | 400 |
| OLS sur les contrôles, intervalle iid | 0,19 | 0,81 | 0,93 | 124 | 274 |
| contrôle synthétique convexe, intervalle iid | 0,17 | 0,83 | 0,91 | 142 | 335 |
| régression statique en espace d'états | 0,21 | 0,79 | 0,93 | 135 | 274 |
| **niveau local + régression (MLE)** | **0,94** | **0,06** | 0,57 | 886 | **227** |
| niveau local + régression, tirages de paramètres | 0,95 | 0,05 | 0,53 | 938 | 227 |
| tendance locale + régression | 0,92 | 0,08 | 0,44 | 1 065 | 280 |

![Couverture et faux positifs des neuf estimateurs](nb02_baselines.svg "En rouge, les estimateurs dont la couverture est sous 90 % (à gauche) ou le taux de faux positifs au-dessus de 10 % (à droite). Seuls les modèles à niveau stochastique et la tendance seule passent les deux.")

Ce que j'ai observé :

- **OLS sur les contrôles et la régression statique en espace d'états sont le même estimateur**
  (biais et RMSE identiques). Leur estimation ponctuelle est presque aussi précise que celle du
  niveau local (RMSE 274 contre 227). Leur intervalle est six à sept fois trop étroit : couverture
  autour de 20 %, et **80 % de faux positifs à effet nul**. Quatre promotions sur cinq qui n'ont
  rien fait seraient déclarées efficaces. C'est la version mesurée des « inférences
  sur-optimistes » que Brodersen cite, d'après Bertrand, Duflo et Mullainathan, contre la
  différence de différences statique.
- **Le contrôle synthétique convexe est presque sans biais mais hérite du même intervalle iid**,
  et des mêmes 80 % de faux positifs. La méthode classique le sait : c'est pourquoi elle rapporte
  des rangs de permutation plutôt que des intervalles.
- **La différence de différences est moins bonne sur les deux tableaux** (RMSE 400, couverture
  12 %) : la moyenne des contrôles est un mauvais contrôle synthétique quand les chargements
  diffèrent d'une unité à l'autre.
- **L'extrapolation de tendance sans contrôle couvre**, parce que son intervalle fait deux fois et
  demie celui du niveau local, et elle détecte une hausse de 5 % une fois sur sept.
- **Le niveau local est le seul estimateur avec une couverture proche du nominal et des faux
  positifs près de 5 %.** La tendance locale paie sa composante supplémentaire par un intervalle
  plus large et une puissance plus faible.

Ce tableau est, de toute la journée, le meilleur argument pour le placebo : sur ces panels, le
placebo dans le temps d'un design OLS se déclencherait lui aussi quatre fois sur cinq, et c'est
ainsi que le praticien le découvrirait.

## 7. Quand le design casse : qui attrape quoi

Le plan disait que le vrai livrable n'est pas l'effet, mais la capacité à dire pourquoi une mesure
est invalide. J'ai planté quatre violations une à une dans le panel, avec une hausse de 5 %, et j'ai
fait tourner quatre vérifications sur chacune, 100 panels par scénario :

- **contrôle cannibalisé** : l'effet traité est retranché, un pour un, des contrôles c0 et c1
  (une promotion sur A qui mange les ventes de B et C, utilisés comme contrôles) ;
- **halo sur les contrôles** : la même quantité est ajoutée à c0 et c1 ;
- **tendance propre** : l'unité traitée dérive de +0,1 par jour toute seule, depuis le premier
  jour (environ 36 % par an sur un niveau de 100), et pas les contrôles ;
- **rupture de relation** : les chargements de l'unité traitée sur les facteurs communs changent
  de +30 % à la date de l'intervention.

Les vérifications : le placebo dans le temps, le placebo dans l'espace (chaque contrôle comme s'il
était traité, à la vraie date), un test de Chow sur les différences entre les deux moitiés de la
pré-période, et le biais de l'estimation contre la vérité, qu'on voudrait connaître en pratique et
qu'on ne connaît jamais. La ligne « propre » donne le taux de fausse alerte de chaque vérification,
et c'est contre elle que les autres lignes se lisent.

| scénario | couverture | biais relatif | placebo temps se déclenche | placebo espace signale c0 / c1 | signale un contrôle propre | Chow rejette |
|---|---|---|---|---|---|---|
| propre | 0,89 | −0,5 % | 0,17 | 0,10 / 0,08 | 0,24 | 0,15 |
| contrôle cannibalisé | 0,86 | **+26 %** | 0,17 | **0,39 / 0,36** | 0,34 | 0,15 |
| halo sur les contrôles | 0,82 | **−27 %** | 0,17 | **0,38 / 0,45** | 0,31 | 0,15 |
| tendance propre | 0,69 | **+71 %** | **0,39** | 0,10 / 0,08 | 0,24 | 0,15 |
| rupture de relation | **0,56** | −11 % | 0,17 | 0,10 / 0,08 | 0,24 | 0,15 |

![Qui attrape quoi : part des panels où chaque vérification se déclenche, et le biais qu'elle est censée protéger](nb03_who_catches_what.svg "À gauche, le taux de déclenchement de chaque vérification par scénario. À droite, le biais relatif de l'effet cumulé et la couverture. La rupture de relation est biaisée et sous-couverte sans qu'aucune vérification ne dépasse son taux de fausse alerte.")

Lecture ligne par ligne :

- **Contrôle cannibalisé et halo.** Le biais est grand (+26 % et −27 % de l'effet réel) et la
  couverture glisse. Pourtant **le placebo dans le temps est exactement aussi souvent vert que sur
  les panels propres** : rien ne cloche dans la pré-période, la contamination commence à
  l'intervention. Le placebo dans l'espace signale chaque contrôle contaminé environ quatre fois
  plus souvent qu'un contrôle propre (39 % et 36 % contre 10 % et 8 %) : la vérification a de la
  puissance, mais loin de la certitude pour une contamination de cette taille. Elle signale aussi
  plus souvent des contrôles propres (34 % contre 24 %) : un donneur contaminé contamine les
  placebos qui l'utilisent.
- **Tendance propre.** Le placebo dans le temps se déclenche dans 39 % des panels, plus de deux
  fois son taux propre. C'est le design qui fait son travail : une unité qui dérive toute seule par
  rapport à ses contrôles produit des « effets » à n'importe quelle date. Le biais est de +71 %,
  parce que le niveau local prévoit à plat et que la dérive continue.
- **Rupture de relation.** Biaisée, sous-couverte, et **aucune vérification ne se déclenche
  au-dessus de son taux propre**. Une relation qui cesse de tenir à la date de l'intervention est
  indiscernable, dans les données, d'un effet de l'intervention. C'est l'hypothèse que Brodersen
  nomme comme celle sur laquelle tout repose, et elle est intestable par construction. Les seules
  défenses sont extérieures aux données : une raison de croire que la relation persiste, et la
  réconciliation métier de la partie 10.

### Isoler un contrôle contaminé

Quand le placebo dans l'espace signale plusieurs contrôles, l'un d'eux peut être le coupable et les
autres ses victimes. La procédure du dépôt retire le pire (la plus petite probabilité de queue),
relance la vérification sur le reste, et recommence jusqu'à ce que rien ne soit signalé.

![Vérification de contamination sur un panel cannibalisé](nb03_isolation.svg "Effet propre de chaque contrôle à la vraie date, avec son intervalle. Les contrôles retirés par l'isolation sont marqués ; c0 et c1 sont les deux contrôles contaminés par construction.")

Sur ce panel, le premier tour ne signale que c1 ; c0, pourtant contaminé lui aussi, a un intervalle
qui touche tout juste zéro ([−10,3 % ; +0,2 %]). L'isolation retire c1, puis c0, puis un contrôle
propre, c2, et garde c3 et c4. Avec tous les contrôles, l'effet est estimé à 601 [283 ; 937] pour
une vérité de 503 : l'intervalle couvre, mais l'estimation est 20 % trop haute. Avec les deux
contrôles gardés : 118 [−416 ; 676]. L'intervalle couvre toujours, mais l'estimation est devenue
très imprécise. Retirer des contrôles échange du biais contre de la variance, et avec cinq donneurs
l'échange est mauvais. C'est ce qui m'a fait écrire, dans la partie 10, qu'il faut partir d'un
réservoir de 10 à 20 donneurs éligibles, choisis **avant** la campagne parmi des produits qui ne
peuvent pas interagir avec le produit promu : la vérification est une garde, pas une procédure de
sélection.

## 8. Un cas réel : Volkswagen, 18 septembre 2015

Le plan proposait une série du jeu Favorita. Sans identifiants Kaggle sur la machine, j'ai pris le
panel public que le port de CausalImpact utilise comme fixture de test : les cours hebdomadaires de
clôture de Volkswagen, BMW et Allianz, 325 semaines de janvier 2011 à mars 2017. L'intervention est
datée : l'avis de violation de l'EPA américaine contre Volkswagen, publié le vendredi 18 septembre
2015. Ici aucune vérité n'est disponible, et chaque affirmation doit être défendue par un placebo
ou une analyse de sensibilité.

![Cours hebdomadaires de clôture, 2011 à 2017](nb04_series.svg "VW, BMW et Allianz, avec la date de l'avis de l'EPA. Le cours de VW perd 28 % en une semaine.")

### La première chose à remarquer

La ligne datée du dimanche 20 septembre 2015 contient déjà le krach : VW passe de 155,4 à 111,3,
soit −28 %, puis à 97,4 la semaine suivante. Les lignes sont étiquetées par le dimanche qui ouvre
la semaine, et cette semaine contient les séances du lundi 21 et du mardi 22. La pré-période
s'arrête donc au 13 septembre (246 semaines) et la post-période commence au 20 septembre (79
semaines, jusqu'en mars 2017), comme dans l'exemple du paquet.

Mais **BMW baisse la même semaine** : −8 %, de 75,5 à 69,5, pendant qu'Allianz gagne 1 %. Le titre
BMW a chuté après des articles de presse, le 24 septembre, sur les émissions d'un de ses modèles,
et tout le secteur a été re-tarifé avant de se reprendre en octobre. Si BMW a réagi au même
événement, ce n'est pas un contrôle non traité. La question est traitée plus bas.

### La relation pré-intervention est-elle stable ?

Le contrefactuel extrapole la relation entre VW et ses contrôles. Si elle dérivait déjà avant la
date, l'extrapoler est une supposition. Une régression glissante sur 52 semaines montre des
coefficients qui se promènent et un R² loin d'être constant : en niveaux, trois cours co-évoluent
par le facteur de marché, mais les chargements ne sont pas une loi. Un test de Chow entre les deux
moitiés de la pré-période, calculé sur les **différences** hebdomadaires pour qu'un niveau qui
dérive ne se fasse pas passer pour un changement de chargements, ne rejette pas la stabilité
(F = 0,95, p = 0,42). La lecture que j'en fais : assez stable pour essayer, pas assez pour s'en
remettre au résultat sans placebo.

### L'effet, avec BMW et Allianz comme contrôles

| | valeur |
|---|---|
| effet moyen par semaine | −33,5 [−65,1 ; −2,1] |
| effet cumulé sur 79 semaines | −2 650 [−5 140 ; −169] |
| **effet relatif** | **−20,9 % [−33,9 % ; −1,7 %]** |
| probabilité de queue | 0,018 |
| ajustement à un pas sur la pré-période | R² 0,99, couverture 0,92, Ljung-Box p = 1,0 |
| coefficients | BMW 0,63, Allianz 0,30 |

![VW, niveau local et régression sur BMW et Allianz](nb04_impact_bmw_allianz.svg "Les trois panneaux habituels : observé et contrefactuel, effet ponctuel, effet cumulé. L'intervalle s'élargit vite : 79 semaines est un long horizon pour un niveau en marche aléatoire.")

L'intervalle exclut zéro, mais de peu, et il s'élargit vite : 79 semaines est un long horizon pour
un niveau en marche aléatoire dont la variance hebdomadaire, estimée sur les données, n'est pas
négligeable. L'estimation ponctuelle dit que VW a coté environ un cinquième sous son contrefactuel
pendant les dix-huit mois suivants.

Le R² à un pas de 0,99 ne dit rien sur les contrôles : un cours de bourse est proche d'une marche
aléatoire, et la prévision à un pas d'une marche aléatoire est toujours excellente. Un autre chiffre
est plus parlant : le rapport entre la dispersion des résidus après et avant la date vaut 3,4. La
post-période se comporte très différemment de la pré-période.

### Le placebo dans le temps, un an plus tôt

Je fais comme si l'intervention avait eu lieu le 14 septembre 2014 et je rejoue l'analyse identique
sur des données qui s'arrêtent au 13 septembre 2015, pour qu'aucune donnée post-avis ne soit vue.
Rien n'est arrivé à VW en particulier à cette date ; l'effet estimé doit être indiscernable de
zéro : **+5,4 % [−8,2 % ; +23,1 %]**, probabilité de queue 0,24.

Puis le balayage : douze fausses dates entre février 2012 et mars 2015, chacune avec une fenêtre
post de 26 semaines.

![Balayage placebo dans le temps sur Volkswagen](nb04_placebo_sweep.svg "Douze fausses dates, fenêtres post de 26 semaines, intervalles à 95 %. Tous contiennent zéro ; l'effet réel sur 79 semaines (en orange) est en dehors du nuage.")

Les douze intervalles contiennent zéro, et les estimations placebo se dispersent des deux côtés,
entre −7,6 % et +9,0 %. L'effet réel est bien en dehors de cette dispersion. C'est la moitié (b) du
critère, et c'est elle qui rend la moitié (a) rapportable.

Ce placebo valide le modèle pré-intervention. Il ne dit rien sur BMW, parce que dans les fenêtres
placebo, BMW n'a été touché par rien.

### Les contrôles ont-ils été traités eux-mêmes ?

La troisième analyse de Brodersen : faire tourner le modèle sur chaque contrôle comme s'il était
l'unité traitée, avec l'autre contrôle comme donneur, à la vraie date.

| | effet propre sur 79 semaines | sur les 14 semaines après l'avis |
|---|---|---|
| BMW (contrefactuel depuis Allianz) | −11,3 % [−27,3 % ; +13,8 %] | −1,5 % [−10,5 % ; +9,6 %] |
| Allianz (contrefactuel depuis BMW) | +14,7 % [−3,7 % ; +41,6 %] | **+9,4 % [+1,0 % ; +19,3 %]** |

![Chaque contrôle traité comme s'il était la cible](nb04_control_check.svg "BMW prévu depuis Allianz, et Allianz prévu depuis BMW, sur les 14 semaines après l'avis. Allianz « monte » de 9,4 % par rapport à BMW : c'est BMW qui a baissé.")

Avec seulement deux contrôles, cette vérification est un miroir : « BMW a baissé par rapport à
Allianz » et « Allianz a monté par rapport à BMW » sont le même fait vu des deux côtés, et les
intervalles sont larges parce qu'un seul donneur est un mauvais contrefactuel. Les lignes
hebdomadaires autour de l'avis sont la preuve la plus directe : BMW a perdu 8 % la semaine du 20
septembre et repris 12 % deux semaines plus tard, Allianz n'a pas bougé. Le secteur a bien été
re-tarifé pendant quelques semaines, et BMW est un contrôle douteux, au moins pour l'effet à court
terme. Plutôt que de trancher, j'ai rapporté l'effet sous chaque jeu de contrôles.

### Sensibilité : quelle part de la réponse est un choix de modélisation ?

| spécification | effet relatif | IC 95 % | exclut zéro |
|---|---|---|---|
| BMW + Allianz, niveau local (référence) | −20,9 % | [−33,9 ; −1,7] | oui |
| Allianz seul | −27,2 % | [−41,8 ; −2,8] | oui |
| BMW seul | −16,8 % | [−31,5 ; +5,9] | non |
| sans contrôle, tendance linéaire locale | −22,9 % | [−45,0 ; +27,2] | non |
| BMW + Allianz, régression statique | −30,1 % | [−31,0 ; −29,1] | oui |
| BMW + Allianz, tendance linéaire locale | −19,7 % | [−35,1 ; +4,4] | non |
| BMW + Allianz, log des cours | −4,3 % | [−8,4 ; +0,2] | non |
| BMW + Allianz, pré-période depuis 2013 | −21,5 % | [−34,9 ; −1,2] | oui |
| BMW + Allianz, pré-période depuis 2014 | −21,4 % | [−34,6 ; −1,5] | oui |

![Sensibilité de l'effet à la spécification](nb04_sensitivity.svg "Neuf spécifications. En gris, celles dont l'intervalle contient zéro. Le signe ne change jamais ; c'est l'intervalle qui bouge.")

Toute spécification en prix avec un contrôle place l'estimation entre −15 % et −30 % environ, et le
signe ne change jamais. Ce qui bouge, c'est l'intervalle. La régression statique est étroite avec
assurance, et la partie 6 a montré que cette assurance n'est pas méritée sur des données
autocorrélées. BMW seul n'est pas significatif. La tendance linéaire locale ajoute une pente
stochastique à un cours de bourse, et sa prévision à 79 semaines est trop incertaine pour conclure.
Allianz seul, la référence et les pré-périodes plus courtes sont significatifs et concordent. La
spécification en logarithme est dans le tableau pour son signe seulement : un effet relatif sur
l'échelle log n'est pas un effet relatif sur le prix.

Le rapport défendable est un **intervalle de −17 % à −27 %**, avec la question du jeu de contrôles
signalée.

### Le modèle utilise-t-il l'ordre du temps ?

Une vérification bon marché, inspirée de TASC : mélanger les lignes de la pré-période et réajuster.
Une régression statique donne la même réponse. Un modèle à niveau stochastique ne le fait pas,
parce qu'une marche aléatoire mélangée n'est plus une marche aléatoire, et la variance du niveau
s'effondre.

![Mélanger la pré-période : la réponse du niveau local change, celle de la régression statique ne peut pas](nb04_time_order.svg "Sur 20 permutations de la pré-période, l'effet cumulé du niveau local converge vers la réponse statique, avec un intervalle dix fois plus étroit que l'original.")

Sur les permutations, l'effet cumulé du niveau local converge vers −4 305 (écart-type 64), avec un
intervalle moyen de largeur 518 contre 4 971 dans l'ordre original. Les ajustements mélangés
convergent vers la réponse statique et son intervalle étroit. Autrement dit, l'intervalle plus
large du niveau local est le prix de la prise en compte de la dépendance sérielle de la
pré-période, et l'intervalle étroit de la régression statique est ce qu'on obtient en faisant comme
si les semaines étaient échangeables.

## 9. Comparaison avec le CausalImpact de Google

Le modèle construit à la main est un cousin fréquentiste de CausalImpact : même espace d'états,
maximum de vraisemblance au lieu d'a priori et de MCMC. Si les deux sont en désaccord, la
différence est instructive. J'ai fait tourner `tfcausalimpact`, le port TensorFlow Probability
(inférence variationnelle par défaut), sur le panel Volkswagen et sur des panels synthétiques.

| cas | méthode | effet cumulé, IC 95 % | largeur |
|---|---|---|---|
| VW, BMW + Allianz | construit à la main, MLE | −2 650 [−5 140 ; −169] | 4 971 |
| | tfcausalimpact, a priori par défaut sur l'écart-type du niveau (0,01) | −3 355 [−4 427 ; −2 233] | **2 193** |
| | tfcausalimpact, a priori à 0,1 | −2 878 [−5 212 ; −428] | 4 784 |

![Volkswagen : même espace d'états, moitié de l'intervalle](nb05_vw_intervals.svg "Effet cumulé et intervalle à 95 % sous quatre variantes, pour les deux jeux de contrôles. Les estimations ponctuelles sont dans les intervalles les unes des autres ; les largeurs non.")

Mêmes données, même espace d'états, estimations ponctuelles chacune dans l'intervalle de l'autre,
et un intervalle moitié moins large. L'a priori par défaut de CausalImpact sur l'écart-type du
niveau est 0,01, en unités de la série standardisée, hérité du paquet R. Sur un cours hebdomadaire,
l'écart-type du niveau au maximum de vraisemblance vaut environ 0,085 dans les mêmes unités, huit
fois plus. L'a priori gagne l'argument sur 246 semaines de données, parce qu'une inférence
variationnelle avec un a priori serré autour d'une petite valeur garde le niveau presque
déterministe, et un niveau presque déterministe prévoit à 79 semaines avec une variance presque
constante. En desserrant l'a priori à 0,1, l'intervalle s'ouvre jusqu'à celui construit à la main.
**L'intervalle étroit était l'a priori, pas les données.**

Ce n'est un défaut d'aucune des deux implémentations. Un a priori est l'affirmation que les cours de
bourse ne dérivent pas, que l'on peut vouloir faire ou non ; le maximum de vraisemblance est
l'affirmation que la pré-période est la seule information sur l'ampleur de cette dérive. Ce que
j'en retiens est que la largeur de l'intervalle sur un cas réel est un choix de modélisation, et
qu'il doit être rapporté comme tel.

Sur une vérité connue, on peut aller plus loin et demander qui couvre :

| 30 panels, hausse de 5 % | couverture | détection | largeur moyenne | RMSE | secondes par ajustement |
|---|---|---|---|---|---|
| construit à la main, MLE | **0,90** | 0,53 | 887 | 219 | 0,1 |
| tfcausalimpact, a priori par défaut | 0,77 | 0,80 | 494 | 262 | 15,7 |

![Intervalles centrés sur la vérité, 30 panels](nb05_coverage_side_by_side.svg "Chaque segment est un intervalle à 95 % recentré sur la vérité : un segment qui manque zéro a manqué la vérité. Les intervalles de tfcausalimpact sont plus courts et en manquent davantage.")

L'a priori par défaut achète un intervalle 45 % plus étroit et une détection plus élevée (80 %
contre 53 %) au prix de la couverture : son intervalle à 95 % contient la vérité dans 77 % des
panels, celui construit à la main dans 90 %. Les estimations ponctuelles sont d'une précision
voisine. L'a priori est un défaut raisonnable pour les séries marketing quotidiennes pour lesquelles
la méthode a été conçue, avec une petite variance de niveau relativement à la régression sur de
nombreux contrôles, et un mauvais défaut pour une série avec une grande marche aléatoire propre, ce
que sont ce panel et un cours de bourse. Un balayage placebo dans le temps le révélerait : son taux
de faux positifs se situerait bien au-dessus de 5 %.

Ni « étroit » ni « bayésien » ne sont des synonymes de « calibré ». La couverture sur une vérité
connue, ou un balayage placebo sur des données réelles, sont les seules preuves que j'ai trouvées.
Et c'est ce qui me ramène à TASC : ses intervalles « plus étroits que CIM » sont une affirmation sur
la largeur, et cette journée m'a montré ce que la largeur sans la couverture peut cacher. Un point
pratique, enfin : 0,1 seconde par ajustement contre 12 à 16, ce qui compte pour les balayages
placebo et les études de Monte-Carlo.

## 10. Mesurer l'incrémentalité des promotions en continu

Le troisième bloc du plan était une décision d'architecture, sans code : un moteur de promotions
lance des campagnes sur des produits en magasin, et pour chaque campagne on veut l'effet causal sur
les ventes, par contrefactuel plutôt que par groupe témoin, parce que le métier n'acceptera pas de
retenir des magasins ou des clients à chaque promotion. Trois points décident si le chiffre vaut
quelque chose. Les nombres cités sont ceux des parties 5 à 7.

**Sélection et intégrité des contrôles.** Avec une part de la hausse du produit promu cannibalisée
sur un produit utilisé comme contrôle, l'effet est surestimé d'un quart et le placebo dans le temps
reste vert dans 83 % des cas. L'interférence est invisible à la vérification que tout le monde
fait. Ma réponse est double. Avant la campagne, les candidats contrôles viennent d'un **registre de
donneurs éligibles** construit sur le graphe produit : même groupe de magasins et même classe de
saisonnalité que la cible, mais une catégorie différente et aucune arête de substitution (issue des
co-occurrences de paniers et des élasticités croisées passées). Un produit de la même catégorie, de
la même famille de marque, ou substitut ou complément connu est exclu quelle que soit la qualité de
son ajustement sur la pré-période, parce que le contrôle qui s'ajuste le mieux est souvent le
substitut le plus proche. Tout donneur lui-même promu, en rupture, déréférencé ou re-tarifé dans la
fenêtre est exclu. Et le réservoir compte 10 à 20 donneurs, pour pouvoir en perdre. Après la
campagne, le placebo dans l'espace à la vraie date, en isolation *leave-one-out* (partie 7), signale
les donneurs qui ont bougé avec la campagne. Un effet propre négatif sur un produit du même rayon
est un constat de cannibalisation en soi, et il fait partie de l'effet net de la promotion ; un
effet positif est un halo. Les deux vont dans le rapport de campagne, et l'effet est rapporté sur le
réservoir conservé.

**Surveiller l'hypothèse causale dans le temps.** Le contrefactuel est inobservable, donc rien ne
se surveille directement. Quatre substituts, chacun lié à un mode de défaillance que le panel
reproduit :

| Signal | Ce qu'il protège | Règle |
|---|---|---|
| ajustement pré-période du modèle déployé (R² à un pas, Ljung-Box, couverture de l'intervalle à un pas), par campagne | le modèle est de la bonne taille pour la série | couverture à un pas hors de [0,90 ; 0,98] ou Ljung-Box p < 0,01 bloque le rapport |
| placebo dans le temps glissant sur des produits **jamais traités**, même modèle, mêmes longueurs, chaque semaine | la calibration du design là où la vérité est zéro | part des intervalles placebo excluant zéro sur les 50 derniers runs au-dessus de 10 % (le panel a mesuré 11 % sur pré-périodes courtes) lève une alerte ; le taux sur panels propres est la référence |
| placebo dans l'espace sur chaque campagne | l'interférence | tout tour d'isolation au-delà du premier sur une cible déclenche une revue |
| stabilité de la relation donneur-cible : Chow sur les différences, dérive des coefficients entre campagnes successives de la même cible | la relation qui est extrapolée | p < 0,01 ou changement de signe d'un coefficient bloque le donneur |

Ce que cette surveillance ne peut pas voir, et le tableau de bord le dit : une relation qui casse à
la date de la campagne. Le scénario de la partie 7 est biaisé et sous-couvert sans qu'aucune
vérification ne se déclenche au-dessus de son taux propre. Ce mode de défaillance n'est attrapé que
par le troisième point.

**Le garde-fou métier.** L'effet estimé est un résidu de prévision. Il est relié à l'argent par une
quantité qui, elle, est observée plus tard : la **marge incrémentale réalisée**, réconciliée par
campagne et par mois. Chaque rapport porte les unités incrémentales estimées avec leur intervalle,
converties en marge avec la marge unitaire de la promotion, et la marge *implicite* que le grand
livre devrait montrer sur l'ensemble produit-magasin pendant la fenêtre post. Chaque mois, la somme
des marges contrefactuelles et incrémentales estimées est comparée à la marge réalisée des
ensembles promus. L'écart de réconciliation est une série temporelle : son niveau est bruité par
nature, sa **dérive** est l'alarme. Un écart qui croît dans une direction pendant trois mois
signifie que les contrefactuels sont systématiquement faux, et c'est à cela que ressemble, vu de
l'extérieur, un modèle qui dérive en silence, y compris une rupture de relation que rien d'autre
ne voit. Deux ancres de plus : un vrai groupe témoin occasionnel, sur une petite part des campagnes
choisies par le moteur, avec un témoin randomisé de magasins, dont l'effet expérimental est comparé
à l'effet contrefactuel sur la même campagne, comme Brodersen et ses collègues ont validé leur
estimation observationnelle contre l'estimation randomisée ; et la somme des effets sur les
campagnes d'une même catégorie, qui ne peut pas dépasser longtemps la croissance observée de la
catégorie sans une cannibalisation que les contrôles ont manquée. Tant que l'écart de
réconciliation n'est pas refermé pour une famille de produits, l'effet qui entre dans une décision
est la borne basse de l'intervalle, pas l'estimation ponctuelle.

## 11. Ce que j'en retiens

Ces constats valent pour les dispositifs étudiés ici : un panel semi-synthétique à deux facteurs
latents, cinq contrôles et 90 jours de post-période, et un panel de trois cours de bourse. Je les
présente comme tels.

1. **Le contrefactuel est une prévision, et son incertitude est celle du modèle sur ce que fait la
   part inexpliquée dans le temps.** Une régression statique la croit indépendante chaque jour ; un
   niveau local la laisse dériver. Sur ces panels, seule la seconde croyance donne un intervalle à
   95 % qui couvre à 95 %.
2. **Les estimateurs statiques sont précis et trop confiants** : même RMSE que le niveau local à
   peu de chose près, et 80 % de faux positifs à effet nul. C'est, de la journée, l'argument le
   plus fort pour ne pas sauter le placebo.
3. **Le placebo dans le temps valide le modèle pré-intervention, et rien de ce qui commence à la
   date de l'intervention.** Il attrape une unité qui dérive toute seule (deux fois son taux
   propre) ; il est aveugle à un contrôle contaminé et à une rupture de relation.
4. **Le placebo dans l'espace est la vérification de l'interférence**, avec une puissance modeste
   (environ 40 % par contrôle contaminé contre 10 % de fausse alerte, pour une contamination un
   pour un sur un effet de 5 %), et il demande une isolation *leave-one-out* parce qu'un donneur
   contaminé signale ses voisins.
5. **Une relation qui casse à la date de l'intervention n'est vue par aucune vérification sur les
   données.** Nommer cette limite est ce qui sépare une prévision d'une affirmation causale : la
   rendre plausible par construction (choix des contrôles) et auditable après coup (réconciliation
   métier) est le seul traitement que j'ai trouvé.
6. **Un placebo qui se déclenche n'invalide pas forcément le design.** Avec une pré-période
   raccourcie, l'intervalle sous-couvre et le placebo se déclenche sur 11 à 17 % de panels propres.
   Je lis désormais un balayage contre son taux propre, pas une date contre 5 %.
7. **Sur Volkswagen, l'effet de l'avis de l'EPA est de −17 % à −27 % sur 79 semaines, selon le jeu
   de contrôles**, placebo propre à douze fausses dates, avec BMW signalé comme contrôle douteux
   dans les semaines qui suivent.
8. **La largeur de l'intervalle sur un cas réel est un choix de modélisation.** L'a priori par
   défaut de CausalImpact donne un intervalle moitié moins large que le maximum de vraisemblance,
   et couvre 77 % au lieu de 90 % sur une vérité connue. Desserrer l'a priori réconcilie les deux.

**Questions encore ouvertes.** Je n'ai pas implémenté TASC, ni mesuré sa couverture. Le panel
synthétique a un effet en marche d'escalier ; le générateur sait produire une rampe et une impulsion,
que je n'ai pas étudiées. Le placebo dans l'espace a été mesuré pour une seule taille de
contamination. Et la surveillance de la partie 10 est un raisonnement, pas un système en
production : ses seuils viennent du panel, pas de données de promotion.

{{< alert icon="circle-question" >}}
**Une question pour vérifier sa compréhension.** *Une promotion sur un produit A est mesurée par
contrefactuel avec, comme contrôles, trois produits du même rayon choisis pour la qualité de leur
ajustement sur la pré-période. L'effet est de +12 % [+4 % ; +20 %], et le placebo dans le temps à
trois fausses dates est propre. Que vaut ce chiffre ?* Le placebo dans le temps ne teste que la
pré-période, où les trois contrôles n'étaient contaminés par rien (partie 7). Si la promotion sur A
a pris des ventes aux produits du même rayon, le contrefactuel est tiré vers le bas et l'effet
surestimé, sans qu'aucun placebo dans le temps ne le voie. Il faut le placebo dans l'espace à la
vraie date sur chacun des trois contrôles, et, si le rayon est le même, une bonne raison d'avoir
choisi ces contrôles autre que leur ajustement, puisque le contrôle qui s'ajuste le mieux est
souvent le substitut le plus proche.
{{< /alert >}}

## Reproduire et aller plus loin

Le code, les cinq notebooks et les 22 tests sont dans le dépôt
[gwils28/time_series_causal_statistics](https://github.com/gwils28/time_series_causal_statistics)
(Python 3.13, versions verrouillées par `uv`). Chaque tableau de cet article sort d'une commande
`cts synth`, `cts vw`, `cts study all` ou `cts tfci`, avec des graines fixées ; les études de
Monte-Carlo prennent une quinzaine de minutes et le contrôle croisé une dizaine. Le panel Volkswagen
est téléchargé une fois depuis la fixture de test du port de CausalImpact.

**Sources**

- Brodersen, Gallusser, Koehler, Remy et Scott, [*Inferring causal impact using Bayesian structural time-series models*](https://arxiv.org/abs/1506.00356), The Annals of Applied Statistics, 9(1), 2015, et l'implémentation [CausalImpact](https://google.github.io/CausalImpact/).
- Rho, Illick, Narasipura, Abadie, Hsu et Misra, [*Time-Aware Synthetic Control*](https://arxiv.org/abs/2601.03099), arXiv, janvier 2026.
- Carlson et Shephard, [*When are time series predictions causal? The potential system and dynamic causal effects*](https://arxiv.org/abs/2603.20394), arXiv, mars 2026.
- [tfcausalimpact](https://github.com/WillianFuks/tfcausalimpact), port Python de CausalImpact sur TensorFlow Probability, et sa fixture de test pour le panel Volkswagen.
