---
title: "Un agent de code sur un VPS : isolation, secrets et coûts"
date: 2026-11-03
draft: false
description: "Faire travailler Claude Code ou Codex CLI sur un petit serveur européen plutôt que sur son portable : ce que ça apporte, comment l'isoler, où mettre les secrets, comment déployer, et ce que ça coûte en octobre 2026, pour un profil data et MLOps."
summary: "Un VPS CPU dédié à l'agent, joignable seulement par réseau privé, une production séparée et du GPU loué à l'heure : l'état des lieux au 31 octobre 2026, de l'isolation aux secrets et aux coûts."
categories: ["Méthode"]
featureImage: "cover.png"
tags: ["claude code", "IA", "VPS", "sécurité", "MLOps", "tailscale", "docker"]
showTableOfContents: true
---

{{< lead >}}
Un agent de code qui travaille seul pendant une heure a besoin d'une machine qui ne se met pas en
veille, qu'on peut casser sans conséquence, et qui ne détient aucune clé de la production. Un
petit VPS remplit ces trois conditions, à condition de le configurer en conséquence.
{{< /lead >}}

*Temps de lecture : environ 20 minutes. État des lieux au 31 octobre 2026 : prix, versions et
comportements par défaut ont changé plusieurs fois cette année, chaque chiffre est daté.*

{{< note-ia >}}

Dans [ma méthode de travail avec Claude Code]({{< ref "/posts/claude-code-methode-revisee" >}}),
l'agent tourne dans le terminal de mon portable. Ça suffit tant que je reste devant. Dès qu'une
tâche dure, qu'on veut la suivre depuis un téléphone ou lancer plusieurs agents en parallèle, le
portable devient la contrainte : il se met en veille, il contient mes clés et mes documents, et
un `rm -rf` mal placé y coûte cher.

Cet article rassemble ce que j'ai retenu en étudiant la question : documentation de Claude Code,
guides des éditeurs (Doppler, Tailscale), grilles tarifaires des hébergeurs et retours
d'expérience de la communauté. Il vise un profil data scientist ou ingénieur MLOps basé en
France. Les sources sont en fin d'article.

{{< alert icon="lightbulb" >}}
**En bref.** La configuration qui ressort combine trois machines aux rôles distincts :

1. **Un VPS CPU européen dédié à l'agent**, joignable seulement par réseau privé (Tailscale),
   utilisé dans tmux, jetable et sauvegardé par snapshots.
2. **Une machine de production séparée**, déployée par la CI, jamais par l'agent.
3. **Du GPU loué à l'heure**, démarré par script quand un entraînement le demande.

Les secrets sont injectés à l'exécution par un gestionnaire (Doppler ou équivalent), en lecture
seule et à durée limitée. Compter **25 à 130 € par mois** selon l'usage, abonnement à l'agent
compris, qui pèse 70 à 90 % de la facture.
{{< /alert >}}

## Pourquoi faire tourner un agent sur un VPS

| Besoin | Ce que le VPS apporte |
|---|---|
| Sessions longues et persistantes | L'agent continue quand le portable se met en veille ; tmux conserve l'état |
| Travail asynchrone | On lance une tâche, on part, on reçoit une notification |
| Accès mobile | SSH (Termius, Blink) via Tailscale, ou Remote Control vers l'app Claude |
| Isolation du poste personnel | Un `rm -rf` ou une dépendance malveillante touche le VPS, pas les clés ni les documents |
| Mode autonome | Un environnement jetable, restaurable par snapshot |
| Parallélisation | Plusieurs agents en fenêtres tmux ou worktrees, sans saturer sa machine |
| Proximité avec la production | Mêmes images Docker, même architecture |

Deux évolutions de 2026 changent la donne :

- **Remote Control** (février 2026) permet de piloter depuis l'app mobile ou claude.ai/code une
  session Claude Code qui tourne sur le VPS. La session ne fait que des requêtes HTTPS sortantes :
  aucun port à ouvrir. Limites : une connexion distante par session, un terminal ouvert
  obligatoire, une expiration après environ 10 minutes de coupure réseau.
- **L'auto mode par défaut** (14 août 2026) remplace la demande de permission à chaque étape par
  un classifieur qui examine les actions. Dans un test d'Anthropic sur 1 053 testeurs, la revue
  humaine interceptait 13,6 % des commandes dangereuses, l'auto mode 89 %. Les règles
  `permissions.deny` et `ask` s'appliquent avant le classifieur. Depuis la v2.1.302, les
  exécutions headless (`claude -p`) démarrent en mode manuel : il faut passer
  `--permission-mode auto` explicitement.

L'auto mode réduit le besoin de lancer l'agent sans aucune permission (le « mode YOLO »), mais il
reste un filtre probabiliste. Il ne remplace pas l'isolation, ce qui motive la suite.

## Les choix qui structurent la configuration

Douze idées reviennent d'une source à l'autre. Je les reprends comme un ensemble cohérent plutôt
que comme des règles : chacune répond à un risque précis, et on peut en assouplir une en sachant
ce qu'on perd.

1. **Le VPS est un poste de travail jetable.** Ce qui compte vit dans git, dans le gestionnaire
   de secrets et dans des sauvegardes externes ; la machine se reconstruit en un quart d'heure.
2. **La machine de l'agent et la production sont distinctes.** L'agent peut casser son VPS, pas
   la production.
3. **Pas de port public sans raison.** Tailscale ou WireGuard pour l'accès, Cloudflare Tunnel ou
   un reverse proxy pour ce qui doit être public.
4. **L'autonomie se paie en isolation.** `--dangerously-skip-permissions` seulement dans un
   conteneur ou une VM sans secret de valeur ; ailleurs, auto mode et sandbox.
5. **Les secrets sont injectés à l'exécution**, limités, en lecture seule, à durée limitée.
   L'agent ne remplit jamais ses propres secrets.
6. **La « trifecta létale » est cassée** : données privées, contenu non fiable et communication
   externe ne sont pas réunis sans garde-fou réseau.
7. **La persistance se gère au niveau du terminal** : tmux ou zellij, mosh pour les réseaux
   instables, Remote Control en option.
8. **On parallélise par worktrees**, pas par copies : un agent par branche, un humain qui relit
   les diffs.
9. **Les notifications remplacent la surveillance** : hooks Stop et Notification vers ntfy ou
   Telegram.
10. **Le CPU tourne en permanence, le GPU à la demande.** Louer un GPU 24 h/24 pour coder ne se
    justifie pas.
11. **Le déploiement reste ennuyeux** : Compose, PaaS auto-hébergé ou Kamal, avec une CI. Pas de
    `docker run` improvisé par l'agent en production.
12. **Tout est daté.** Prix, versions et comportements par défaut changent chaque trimestre.

## L'architecture d'ensemble

{{< mermaid >}}
flowchart TD
    T["Téléphone ou portable<br/>Termius · mosh · VS Code Remote-SSH · Remote Control"]
    T -->|Tailscale| A
    subgraph A["VPS agent · UE · aucun port public"]
        direction TB
        A1["utilisateur non root · tmux · worktrees"]
        A2["Claude Code : auto mode + sandbox"]
        A3["Doppler : config dev_agent, jeton lecture seule"]
        A4["Docker · uv · MLflow"]
        A5["hooks → ntfy privé · snapshots + restic → S3"]
        A1 ~~~ A2 ~~~ A3 ~~~ A4 ~~~ A5
    end
    A -->|"git push (jeton limité au dépôt)"| G["GitHub + Actions<br/>tests · build · revue de PR · registre"]
    G -->|"déploiement Kamal / Coolify / Compose"| P["VPS production · séparé<br/>Caddy · API FastAPI · base · Uptime Kuma"]
    A -.->|"script de démarrage"| GPU["GPU à l'heure · Scaleway L4/L40S<br/>entraînement → MLflow → arrêt automatique"]
{{< /mermaid >}}

Le point clé du schéma : **aucune flèche ne va du VPS de l'agent vers la production.** Le code
transite par git et la CI, qui détient seule la clé de déploiement.

## Choisir son VPS

2026 a été une année de hausses, attribuées au coût de la RAM et des disques. Hetzner a augmenté
ses prix cloud deux fois (1er avril et 15 juin) ; OVHcloud a fait passer son VPS-1 de 4,49 € à
6,49 € avant de lancer une gamme « VPS 2027 » ; Scaleway et netcup ont aussi relevé leurs tarifs.

### Comparatif d'entrée de gamme

| Fournisseur | Offre | Prix indicatif (oct. 2026) | Localisation | Remarques |
|---|---|---|---|---|
| Hetzner | CX23 : 2 vCPU, 4 Go, 40 Go | 5,49 € HT/mois (hors IPv4) | Allemagne, Finlande | Meilleur rapport prix/RAM ; gammes CX/CAX souvent indisponibles |
| Hetzner | CAX11 (Arm) : 2 vCPU, 4 Go | 5,99 €/mois | Allemagne, Finlande | Vérifier la compatibilité Arm des wheels Python et ML |
| OVHcloud | VPS-1 2027 : 2 vCores, 4 Go, 40 Go NVMe | 3,81 à 4,49 € HT selon engagement | France | Sauvegarde quotidienne incluse |
| OVHcloud | VPS-2 : 6 vCores, 12 Go, 100 Go | ≈ 11,99 € HT | France | Bon candidat pour plusieurs agents et MLflow |
| Scaleway | DEV1-M | ≈ 14,74 € HT hors stockage | Paris, Amsterdam, Varsovie | GPU à l'heure dans le même compte |
| Hostinger | KVM 1/2, modèle Claude Code préinstallé | Promotions ; renouvellement ×2 à ×3 | Plusieurs, dont UE | Le plus simple pour débuter ; serveur MCP officiel ; performances moyennes |
| DigitalOcean, Vultr, Linode | 1 vCPU, 2 Go | ≈ 12 $/mois (DO) | Francfort, Amsterdam, Paris | Plus cher à RAM égale, excellente API |
| Contabo | Gros VPS | Très bas | Allemagne | Beaucoup de RAM ; I/O et support irréguliers selon la communauté |
| Oracle Free Tier | Arm Ampere | 0 € | Francfort, Paris, Marseille | Capacité aléatoire ; peu adapté comme poste principal |

Les sources se contredisent sur certains prix (CX23, gamme OVH 2027) : ce sont des ordres de
grandeur, à vérifier sur la grille officielle avant de commander. Le prix de **renouvellement**
compte plus que le prix promotionnel.

### Dimensionnement

- **Un agent, développement web ou Python léger** : 2 vCPU, 4 Go, 40 Go. La mémoire de Claude Code
  se surveille avec `htop`.
- **Deux à quatre agents en parallèle** : 4 à 8 vCPU, 8 à 16 Go, 80 à 160 Go NVMe.
- **Data science** (pandas, scikit-learn, LightGBM) : au moins 16 Go. La RAM est presque toujours
  le facteur limitant.
- **Avec un PaaS sur la même machine** : Coolify ou Dokploy demandent au moins 2 Go de plus.
- **Disque** : images Docker, environnements uv et jeux de données remplissent 40 Go en quelques
  semaines. Un volume séparé ou un stockage S3 évite la saturation.

### Localisation et RGPD

Un VPS chez un fournisseur européen garde les données **au repos** dans l'UE, hors des lois
extraterritoriales américaines. Mais le code et les extraits que l'agent lit partent vers l'API
du modèle (Anthropic, OpenAI, Google), où que soit le VPS : l'hébergement européen ne règle pas
ce transfert. Pour des données personnelles réelles, les options sont de travailler sur des
échantillons pseudonymisés ou synthétiques, de vérifier la rétention de son offre (options *Zero
Data Retention* en Team et Enterprise), ou d'utiliser un modèle auto-hébergé.

### Le GPU à la demande

| Option | Prix (oct. 2026) | Usage |
|---|---|---|
| Scaleway L4 24 Go | à partir de 0,79 €/h | Inférence de LLM 7-8B quantifiés, vision, LoRA léger |
| Scaleway L40S 48 Go | à partir de 1,46 €/h | Inférence plus lourde, génération d'images |
| Scaleway H100 PCIe | ≈ 2,73 €/h | Entraînement sérieux |
| Modal | à la seconde | Jobs GPU ponctuels depuis Python |
| GPU loué au mois | L4 24 h/24 ≈ 577 €/mois | Rarement rentable en solo |

Vingt heures de L4 par mois coûtent environ 16 €, contre près de 580 € pour une instance
permanente. Le VPS de l'agent reste en CPU ; l'agent écrit les scripts qui démarrent l'instance
GPU, lancent l'entraînement, journalisent dans MLflow puis éteignent l'instance.

## Mise en place et sécurité

### Le durcissement de base

- un utilisateur non root avec sudo ; l'agent tourne sous cet utilisateur, jamais en root ;
- SSH par clé uniquement : `PasswordAuthentication no`, `PermitRootLogin no` ;
- UFW en refus par défaut des connexions entrantes ; SSH n'est ensuite autorisé que sur l'interface
  `tailscale0` ;
- fail2ban tant que SSH reste exposé, unattended-upgrades pour les correctifs de sécurité ;
- Tailscale ou WireGuard pour l'accès ; Cloudflare Tunnel, Caddy ou Traefik sur 80/443 pour ce qui
  doit être public ;
- un snapshot avant chaque grosse session autonome, et des sauvegardes externes (restic ou borg
  vers S3).

La séquence d'installation correspondante, pour Ubuntu 24.04 (à adapter) :

```bash
# --- En root, une seule fois ---
adduser dev && usermod -aG sudo dev
mkdir -p /home/dev/.ssh && cp ~/.ssh/authorized_keys /home/dev/.ssh/ && chown -R dev:dev /home/dev/.ssh
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/; s/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh
apt update && apt -y upgrade
apt -y install ufw fail2ban unattended-upgrades tmux mosh git curl jq bubblewrap socat
dpkg-reconfigure -plow unattended-upgrades
ufw default deny incoming && ufw default allow outgoing && ufw allow OpenSSH && ufw --force enable

# --- Réseau privé ---
curl -fsSL https://tailscale.com/install.sh | sh && tailscale up --ssh
# Une fois la connexion via l'IP Tailscale vérifiée :
ufw allow in on tailscale0 && ufw delete allow OpenSSH

# --- En tant que dev ---
curl -fsSL https://claude.ai/install.sh | bash      # Claude Code
curl -LsSf https://astral.sh/uv/install.sh | sh      # Python/uv
# Doppler : config dev_agent_claude, jeton lecture seule expirant,
# puis : doppler configure set token <jeton> --scope .
# Dans le projet : /sandbox, règles deny (~/.ssh, push --force, infra/prod)
tmux new -s projet "doppler run -- claude"
```

L'ordre des deux lignes Tailscale compte : on ne retire l'accès SSH public qu'après avoir vérifié
que la connexion par le réseau privé fonctionne, sinon on s'enferme dehors.

### Authentifier l'agent

Claude Code s'installe avec le script officiel, puis `claude` et `/login`. Si l'OAuth bloque faute
de navigateur sur le serveur, un tunnel `ssh -L 15735:localhost:15735 user@vps` depuis le portable
fonctionne. Une clé API ne va jamais dans `.bashrc` ; à défaut de gestionnaire de secrets, un
fichier en `chmod 600` chargé par le service.

### Les secrets

Le [guide de Doppler pour Claude Code](https://www.doppler.com/agents-claude-code) formalise une
pratique qui se transpose à d'autres gestionnaires :

- une configuration réservée à l'agent, dérivée de l'environnement de développement (par exemple
  `dev_agent_claude`), avec seulement les secrets nécessaires à la tâche ;
- l'agent ne crée ni ne modifie jamais ses propres secrets ;
- un jeton de service en lecture seule, expirant, limité au répertoire (`--scope .`) ;
- un lancement via `doppler run` : les secrets passent en variables d'environnement et
  disparaissent à la fin du processus ;
- le serveur MCP de Doppler, s'il est utilisé, avec ce même jeton et `--read-only` ;
- jamais d'identifiants de production : seulement développement et test.

Les alternatives sont Infisical (open source), 1Password CLI (`op run`), sops avec age, ou les
secrets réseau de Claude Code on the web.

{{< alert icon="triangle-exclamation" >}}
**Limite.** Un secret en variable d'environnement reste lisible par l'agent (`env`). Le
gestionnaire réduit la durée de vie, la portée et les fuites par fichier, mais n'empêche pas un
agent compromis d'exfiltrer ce qu'il voit. D'où le filtrage réseau et des jetons à faible
privilège : un jeton GitHub limité à un dépôt, une base de test.
{{< /alert >}}

### Injection de prompt et exfiltration

Simon Willison a nommé en juin 2025 la « *lethal trifecta* » : **données privées, contenu non
fiable, communication externe**. La « *Rule of Two* » de Meta (octobre 2025) en découle : jamais
plus de deux des trois dans une même session. Un agent de code réunit les trois par défaut : le
dépôt et ses secrets, des README, issues et dépendances écrits par d'autres, et `curl` ou
`git push` pour communiquer.

Les leviers concrets pour casser au moins une branche :

- **Le sandbox natif de Claude Code** (Linux : `sudo apt-get install bubblewrap socat`, puis
  `/sandbox`). Il isole fichiers et réseau via un proxy à liste de domaines. Deux pièges : si le
  sandbox ne démarre pas, Claude Code continue sans lui avec un simple avertissement ; et
  l'échappatoire `dangerouslyDisableSandbox` existe. Vérifier au démarrage, et l'interdire si
  besoin ([documentation](https://code.claude.com/docs/en/sandboxing)).
- **`@anthropic-ai/sandbox-runtime`** enveloppe tout le processus, MCP et hooks compris, avec
  réseau et écriture refusés par défaut.
- **Un conteneur ou un devcontainer** avec politique réseau et seccomp ; pour une isolation au
  niveau du noyau, gVisor ou une VM séparée.
- **Codex CLI** : le mode `workspace-write` coupe le réseau par défaut ; `--yolo` équivaut à
  `--dangerously-bypass-approvals-and-sandbox`.
- **L'hygiène MCP** : ne pas réunir dans une même session un MCP qui lit du contenu externe
  (mails, tickets, web) et un MCP qui détient des secrets ou des droits d'écriture.

### L'échelle d'isolation

| Niveau | Mise en œuvre | Quand |
|---|---|---|
| 0 | Agent directement sur le VPS, mode manuel | Découverte |
| 1 | Auto mode, sandbox bubblewrap, règles deny | Usage quotidien |
| 2 | Agent dans un conteneur sans secrets de production, réseau filtré | Mode autonome, tâches longues |
| 3 | VM ou VPS jetable par projet, ou microVM (E2B, Firecracker) | Code non fiable, plusieurs clients |
| 4 | Sandbox cloud managé (Claude Code on the web, réseau None ou Trusted) | Tâches asynchrones depuis le mobile |

Le niveau 1 couvre l'essentiel d'un usage quotidien ; on monte d'un cran quand on retire les
permissions ou quand le code vient de l'extérieur.

## Le travail au quotidien

### Persistance et accès

- **tmux** est le standard : une session par projet, `tmux attach -t projet`. Des configurations
  dédiées (par exemple [tmux-claude-code](https://github.com/sethdford/tmux-claude-code)) activent
  `allow-passthrough on` et un `history-limit` élevé.
- **zellij** en alternative moderne, **mosh** pour résister aux changements de réseau du téléphone.
- **Sur mobile** : Termius, Blink ou Echo sur l'adresse Tailscale, ou Remote Control
  (`claude remote-control` ou `/rc`) pour un accès en chat depuis l'app Claude.
- **VS Code Remote-SSH** ou Cursor en distant pour relire les diffs et ouvrir les notebooks du VPS
  sans exposer JupyterLab.

### Paralléliser

`git worktree add ../projet-feature-x feature-x` donne à chaque agent son répertoire et sa
branche, dans sa fenêtre tmux, avec des ports de développement distincts et des PR relues par un
humain. Deux agents sur le même répertoire de travail se marchent dessus. Les sous-agents
parallélisent à l'intérieur d'une tâche ; les worktrees, entre les tâches.

### Contexte et automatisation

- **CLAUDE.md ou AGENTS.md** : commandes de test, conventions, interdits (« ne jamais toucher à
  `infra/prod` »). En auto mode, ce fichier alimente aussi le classifieur : il fait partie de la
  politique de sécurité.
- **Hooks** : `PreToolUse` pour bloquer, `Stop` et `Notification` pour prévenir via ntfy
  ([claude-ntfy-hook](https://github.com/nickknissen/claude-ntfy-hook)), sur un topic difficile à
  deviner ou un ntfy auto-hébergé.
- **MCP** : le strict minimum, en lecture seule. Un MCP Coolify ou Dokploy qui pilote la
  production depuis le VPS de l'agent annule la séparation.
- **Headless** : `claude -p "…" --permission-mode auto` en cron ou timer systemd, pour un rapport de
  dérive ou une mise à jour de dépendances.
- **Claude Code on the web et routines** : `claude --cloud` et `/schedule`, avec un niveau réseau
  None, Trusted, Custom ou Full ([documentation](https://code.claude.com/docs/en/claude-code-on-the-web.md)).
- **GitHub Actions** : l'action Claude Code ou `codex exec` pour la revue de PR, avec des jetons à
  portée minimale.

### Pour un profil data et MLOps

- **Environnements** : uv et une image Docker de base commune au développement et à la production.
- **Données** : stockage objet S3 (Scaleway, OVHcloud) ; DVC ou lakeFS si les jeux évoluent.
- **Suivi d'expériences** : MLflow sur le VPS (SQLite ou Postgres, artefacts sur S3), accessible
  par Tailscale seulement. L'agent y journalise ses runs, ce qui laisse une trace auditable.
- **Pipelines** : Prefect, Dagster, ou un Makefile ou `just`.
- **Notebooks** : l'agent écrit des modules testés ; les notebooks restent pour l'exploration, au
  format jupytext ou Marimo, plus faciles à éditer et à relire en diff.
- **Serving léger** : FastAPI ou BentoML en CPU (scikit-learn, LightGBM, ONNX Runtime) ; LLM
  quantifiés sur GPU à l'heure (vLLM).

## Déployer

### Même VPS ou VPS séparé ?

Le même VPS se défend pour un prototype ou une préproduction. Dès qu'il y a de vrais utilisateurs
ou de vraies données, séparer les machines coûte 5 à 10 € par mois, peu face au risque d'un agent
qui redémarre des conteneurs ou lit les secrets de production.

### Les outils auto-hébergés

| Outil | Licence | Version récente | Modèle | Pour qui |
|---|---|---|---|---|
| Docker Compose + Caddy | libre | — | Fichiers versionnés, HTTPS automatique | Le plus simple ; 1 à 3 services ML |
| Coolify | Apache-2.0 | v4.4.6 (9 oct. 2026) | Panneau web, Traefik, applications en un clic | Un « Heroku chez soi » |
| Dokploy | Apache-2.0 + partie propriétaire | v0.30.8 (29 sept. 2026) | Panneau web, Swarm, Traefik | Projets en Compose, besoin de clustering |
| Kamal | MIT | v2.12.0 (18 juin 2026) | CLI + YAML, déploiement par SSH, pas de panneau | Surface d'attaque minimale |
| CapRover, Dokku | Apache-2.0 / MIT | — | Swarm, style Heroku | Petites machines |

Un [comparatif](https://pethost.dev/blog/coolify-vs-dokploy-vs-caprover-vs-dokku/) recense en 2026
61 avis de sécurité GitHub pour Coolify (dont 16 critiques) et 56 pour Dokploy (33 critiques),
contre aucun pour Kamal et CapRover. Un panneau d'administration a donc sa place derrière
Tailscale, et à jour.

### La chaîne de déploiement

1. L'agent pousse une branche.
2. La CI (GitHub Actions) teste, construit l'image et la pousse vers un registre.
3. La CI déploie (Kamal, webhook Coolify ou Dokploy, ou `docker compose pull && up -d` avec une clé
   de déploiement restreinte) ; l'agent ne déploie pas depuis son VPS.
4. Un reverse proxy (Caddy, Traefik ou Nginx) sert l'application.
5. L'observabilité suit : Uptime Kuma, logs (Loki ou `docker logs`), métriques (Prometheus et
   Grafana, ou Netdata) ; côté ML, latence, erreurs et dérive des entrées (Evidently).
6. Les sauvegardes de production partent vers S3, et leur restauration est testée.

## Les alternatives au VPS

| Option | Points forts | Points faibles | Coût indicatif | Quand la choisir |
|---|---|---|---|---|
| VPS dédié à l'agent | Contrôle, persistance, prix fixe, UE | Administration et sécurité à sa charge | 5 à 15 €/mois | Usage quotidien, profil technique |
| Machine locale | Zéro latence, GPU local, gratuit | Veille, isolation faible, pas d'asynchrone | 0 € | Exploration interactive, avec sandbox |
| Serveur maison, mini-PC | Beaucoup de RAM, GPU grand public | Électricité, IP résidentielle, réseau domestique exposé | 300 à 1 000 € à l'achat | Gros besoins en RAM ou GPU |
| Claude Code on the web | Rien à administrer, mobile, routines | Dépend de GitHub, environnement contraint | Inclus dans l'abonnement | Tâches asynchrones délimitées |
| Codespaces, Gitpod/Ona, Coder | Devcontainers standardisés, équipe | Facturation horaire, sessions longues coûteuses | Variable | Équipes, onboarding |
| E2B, Daytona | microVM, démarrage rapide, SDK | Pensés pour des produits, pas un poste de dev | ≈ 0,05 $/vCPU-h | Construire un agent |
| Modal | GPU à la seconde, natif Python | Sandbox CPU 3 fois plus cher que les fonctions | ≈ 0,14 $/cœur-h | Jobs GPU ponctuels |
| Fly.io Machines/Sprites | Démarrage rapide, à l'usage | Moins orienté UE et RGPD | ≈ 0,04 $/CPU-h | Environnements éphémères |

Pour un individu, le VPS reste la base la plus souple ; les sandboxes managés viennent en
complément pour l'asynchrone, le GPU ou un produit.

## Ce que ça coûte

Abonnements Claude en octobre 2026 : Pro à 20 $/mois, Max 5x à 100 $, Max 20x à 200 $, Claude Code
inclus avec des limites partagées (fenêtre de 5 heures et plafond hebdomadaire). Certaines sources
décrivent une restructuration en « Max 100 $ / Ultra 200 $ » : la grille officielle fait foi.

| Scénario | Agent | VPS agent | Production | GPU | Total indicatif |
|---|---|---|---|---|---|
| Découverte | Pro 20 $ | ≈ 4 à 5,5 € | — | — | ≈ 25 €/mois |
| Data scientist solo régulier | Max 5x 100 $ | 8-12 Go, 10 à 15 € | 5 à 6 € | 20 h de L4 ≈ 16 € | ≈ 120 à 130 €/mois |
| Usage intensif, plusieurs agents | Max 20x 200 $ (+ un autre agent) | 16 Go, 20 à 30 € | ≈ 10 € | 50 h de L4 ≈ 40 € | ≈ 250 à 300 €/mois |

Hors TVA, avec 1 $ ≈ 0,9 €. L'abonnement représente 70 à 90 % de la facture : gagner quelques
euros sur le VPS compte peu, oublier un GPU allumé compte beaucoup.

## Les pièges fréquents

- un agent en root sur la machine de production, à côté du panneau, de la base et des secrets ;
- le `.env` de production copié sur le VPS de l'agent, ou des clés dans `.bashrc` ;
- un sandbox qu'on croit actif alors qu'il s'est désactivé faute de bubblewrap ou de socat ;
- `--dangerously-skip-permissions` hors d'un conteneur jetable, ou des règles « allow » génériques
  (`Bash(*)`) ;
- JupyterLab, MLflow, ttyd ou le panneau Coolify sur l'IP publique, même avec un mot de passe ;
- un topic ntfy public qui contient des résumés de code ;
- une instance GPU laissée allumée, faute d'un `trap` ou d'un délai d'arrêt automatique ;
- deux agents sur le même répertoire au lieu de deux worktrees ;
- des sauvegardes jamais testées en restauration ;
- un VPS choisi sur son prix promotionnel sans regarder le renouvellement ;
- des MCP « lecteurs de contenu externe » et « détenteurs de secrets » dans la même session ;
- un `claude -p` en cron qu'on suppose en auto mode, alors qu'il démarre en manuel depuis la
  v2.1.302.

## Ma liste de vérification

**Choix**
- [ ] Fournisseur européen, au moins 4 Go de RAM (8 à 16 Go pour la data ou plusieurs agents), prix de renouvellement vérifié.
- [ ] VPS de production distinct ; GPU loué à l'heure.

**Durcissement**
- [ ] Utilisateur non root, SSH par clé, root désactivé.
- [ ] UFW en refus par défaut, SSH via Tailscale seulement, fail2ban, unattended-upgrades.
- [ ] Aucun service d'administration sur l'IP publique.

**Agent**
- [ ] bubblewrap et socat installés, `/sandbox` actif et vérifié.
- [ ] Auto mode (ou manuel pour le sensible), règles deny explicites, mode sans permission seulement en conteneur jetable.
- [ ] CLAUDE.md ou AGENTS.md avec commandes, conventions et interdits.
- [ ] MCP minimaux, en lecture seule, sans trifecta.
- [ ] Scripts headless avec `--permission-mode` explicite.

**Secrets**
- [ ] Gestionnaire de secrets, configuration propre à l'agent, jeton en lecture seule et expirant.
- [ ] Aucun secret de production sur le VPS de l'agent ; jetons à portée minimale.

**Workflow**
- [ ] tmux ou zellij et mosh, client mobile sur Tailscale.
- [ ] Un worktree par agent, revue humaine des PR.
- [ ] Notifications sur un topic privé.
- [ ] MLflow privé, artefacts sur S3, environnements uv reproductibles.

**Déploiement et exploitation**
- [ ] Une CI qui teste et construit ; le déploiement passe par la CI.
- [ ] Reverse proxy HTTPS, supervision, logs.
- [ ] Snapshots avant les sessions autonomes ; sauvegardes testées en restauration.
- [ ] Revue trimestrielle des prix, des versions et des comportements par défaut.

## Réserves

- **Dates.** État au 31 octobre 2026 ; prix, gammes et comportements par défaut ont changé
  plusieurs fois cette année.
- **Fait ou pratique.** Les configurations tmux, les outils ntfy, Marimo et jupytext, la préférence
  pour Kamal et les avis sur Contabo et Oracle relèvent de pratiques communautaires. Les chiffres
  de l'auto mode viennent d'Anthropic.
- **Sources secondaires.** Plusieurs prix viennent d'agrégateurs qui se contredisent parfois ; les
  compteurs d'avis de sécurité de Coolify et Dokploy viennent d'un seul comparatif.
- **Couverture.** Codespaces, Gitpod/Ona, Gemini CLI, Cursor, OpenCode et Aider n'ont pas été
  examinés en détail ; les principes d'isolation, de secrets et de réseau s'y appliquent de la
  même façon.

## Sources

- [Hostinger : plugin Claude](https://github.com/hostinger/claude-plugin)
- [Hostinger : installer Claude Code sur un VPS](https://www.hostinger.com/support/11929523-installing-claude-code-on-a-vps-at-hostinger/)
- [Doppler : agents et Claude Code](https://www.doppler.com/agents-claude-code)
- [Claude Code : sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Claude Code : sandbox environments](https://code.claude.com/docs/en/sandbox-environments)
- [Claude Code : secure deployment (Agent SDK)](https://code.claude.com/docs/en/agent-sdk/secure-deployment)
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web.md)
- [Claude Code : cloud environments](https://code.claude.com/docs/en/cloud-environments)
- [Claude Code : routines](https://code.claude.com/docs/en/routines)
- [Anthropic : auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- [Help Net Security : auto mode](https://www.helpnetsecurity.com/2026/08/10/anthropic-claude-code-auto-mode/)
- [VentureBeat : Remote Control](https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote)
- [Hetzner : ajustement des prix](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)
- [stackvaluelab : hausse Hetzner 2026](https://stackvaluelab.com/hetzner-price-increase-2026/)
- [zen-cloud : hausse OVH 2026](https://zen-cloud.cloud/blog/ovh-augmente-prix-45-pourcent-alternatives-2026)
- [Scaleway : choisir son GPU](https://www.scaleway.com/en/choose-the-right-gpu/)
- [Qovery : comparatif des prix GPU 2026](https://www.qovery.com/blog/gpu-pricing-comparison-method-aws-gcp-azure-scaleway-2026)
- [La trifecta létale pour les agents de code](https://munderdiffl.in/blog/the-lethal-trifecta-for-coding-agents/)
- [Modes sandbox des CLI d'IA comparés](https://inventivehq.com/blog/ai-coding-cli-sandbox-approval-modes-compared)
- [NetworkChuck : remote-claude-code](https://github.com/theNetworkChuck/remote-claude-code)
- [Guide Claude Code sur VPS (Medium)](https://medium.com/@0xmega/claude-code-on-a-vps-the-complete-setup-security-tmux-mobile-access-2d214f5a0b3b)
- [pethost : Coolify, Dokploy, CapRover et Dokku comparés](https://pethost.dev/blog/coolify-vs-dokploy-vs-caprover-vs-dokku/)
- [haloy : outils de déploiement auto-hébergés](https://haloy.dev/blog/self-hosted-deployment-tools-compared)
- [Fly.io : prix des sandboxes IA](https://fly.io/learn/ai-sandbox-pricing/)
- [ssdnodes : plans Claude](https://www.ssdnodes.com/learn/claude-plans-which-one-do-you-need)
