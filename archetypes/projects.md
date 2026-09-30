---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
description: ""          # une phrase : le problème résolu
summary: ""
tags: []                 # la stack : ["python", "scikit-learn", "streamlit"]
# featureImage: "cover.png"   # visuel de la carte dans /projects (page bundle)
showTableOfContents: true
---

{{/* Modèle complet : content/projects/demo-prediction-churn/ */}}
{{`{{< lead >}}`}}
Le projet en une phrase : ce qu'il résout, pour qui.
{{`{{< /lead >}}`}}

{{/* Fiche d'identité — tous les paramètres sont facultatifs */}}
{{`{{< fiche-projet
    statut="En cours"
    periode=""
    role=""
    stack="Python, …"
    code="https://github.com/gwils28/REPO" >}}`}}

{{/* Deux à quatre chiffres clés — supprime le bloc s'il n'y en a pas */}}
{{`{{< stats >}}`}}
{{`{{< stat value="" label="" >}}`}}contexte du chiffre{{`{{< /stat >}}`}}
{{`{{< stat value="" label="" >}}`}}contexte du chiffre{{`{{< /stat >}}`}}
{{`{{< stat value="" label="" >}}`}}contexte du chiffre{{`{{< /stat >}}`}}
{{`{{< /stats >}}`}}

## Le problème

Ce que je cherchais à résoudre, et pourquoi ça n'était pas trivial.

## L'approche

{{`{{< steps >}}`}}
{{`{{< step number="1" title="…" >}}`}}
Première étape, et la raison du choix.
{{`{{< /step >}}`}}
{{`{{< step number="2" title="…" >}}`}}
Deuxième étape.
{{`{{< /step >}}`}}
{{`{{< /steps >}}`}}

## Le résultat

Ce que ça donne, chiffres à l'appui.

{{`{{< alert icon="circle-info" >}}`}}
**Limite connue** : …
{{`{{< /alert >}}`}}

## Ce que j'en retiens

- 
