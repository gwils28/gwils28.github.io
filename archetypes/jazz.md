---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
support: "postit"   # postit · mousse · papier · ardoise
genre: "libre"      # libre · grille · transcription · impro · partition · audio
tags: []            # ex. ["blues", "walking", "mingus"]
# Écris librement en dessous : texte, listes, image de partition (à côté du .md).
# Grille d'accords (une ligne = une ligne de grille, « | » sépare les mesures) :
#   {{ "{{<" }} grille {{ ">}}" }}
#   Dm7 | G7 | Cmaj7 | Cmaj7
#   {{ "{{<" }} /grille {{ ">}}" }}
# Enregistrement (fichier à côté du .md) :
#   {{ "{{<" }} audio src="prise.mp3" legende="Ce que j'ai joué" {{ ">}}" }}
---

