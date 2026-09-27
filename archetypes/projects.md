---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
description: ""          # une phrase : le problème résolu
summary: ""
tags: []                 # la stack : ["python", "scikit-learn", "streamlit"]
# featureImage: "cover.png"   # capture d'écran du projet (page bundle)
showTableOfContents: true
---

{{/* Boutons vers le code et la démo — supprime ceux qui ne servent pas */}}
{{`{{< button href="https://github.com/wilson-goma/REPO" target="_blank" >}}Code source{{< /button >}}`}}

## Le problème

Ce que je cherchais à résoudre, et pourquoi ça n'était pas trivial.

## L'approche

La démarche, les choix techniques et leurs raisons.

## Le résultat

Ce que ça donne, chiffres à l'appui. Et les limites connues.

## La stack

- **Langage** :
- **Librairies** :
- **Infra** :
