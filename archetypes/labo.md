---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
nature: "labo"           # projet d'apprentissage : bloc Labo de /projects
description: ""          # une phrase : ce que je voulais apprendre
summary: ""
tags: []                 # la techno visée : ["rust", "wasm"]
# featureImage: "cover.png"   # visuel de la carte dans /projects (page bundle)
showTableOfContents: true
---

{{/* Créé par : hugo new --kind labo projects/<slug>/index.md */}}
{{`{{< lead >}}`}}
Ce que je voulais apprendre, et pourquoi maintenant.
{{`{{< /lead >}}`}}

{{/* Fiche d'identité — tous les paramètres sont facultatifs */}}
{{`{{< fiche-projet
    stack="…"
    code="https://github.com/gwils28/REPO" >}}`}}

## L'objectif

La techno ou le concept visé, et ce que « maîtriser » voulait dire ici.

## La démarche

Ce que j'ai construit pour apprendre, étape par étape.

## Ce qui a coincé

Les difficultés, les fausses pistes, ce qui a fini par débloquer.

## Ce que j'en retiens

- 
