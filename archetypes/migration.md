---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}       # date du voyage : sert au tri et à l'affichage « mois année »
draft: true
place: ""               # ex. « Kyoto, Japon »
coords: ""              # ex. « 35.01° N · 135.77° E » (facultatif, affiché en petit)
# cover: "01.jpg"       # photo de couverture ; par défaut la première par ordre alphabétique
# Légendes facultatives : une entrée par photo à légender.
# resources:
#   - src: "01.jpg"
#     title: "Le lac au lever du jour"
---

Deux ou trois phrases sur le voyage (facultatif).

<!-- Dépose les photos (.jpg, .png, .webp) à côté de ce fichier : elles
     s'affichent toutes, dans l'ordre alphabétique des noms de fichier. -->
