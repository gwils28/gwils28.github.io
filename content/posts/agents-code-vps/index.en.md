---
title: "A coding agent on a VPS: isolation, secrets and costs"
date: 2026-10-31
draft: false
description: "Running Claude Code or Codex CLI on a small European server rather than on your laptop: what it brings, how to isolate it, where to put the secrets, how to deploy, and what it costs in October 2026, for a data and MLOps profile."
summary: "A CPU VPS dedicated to the agent, reachable only over a private network, a separate production machine and GPUs rented by the hour: the state of play on 31 October 2026, from isolation to secrets and costs."
categories: ["Method"]
featureImage: "cover.png"
tags: ["claude code", "AI", "VPS", "security", "MLOps", "tailscale", "docker"]
showTableOfContents: true
---

{{< lead >}}
A coding agent working on its own for an hour needs a machine that doesn't go to sleep, that can
be broken without consequence, and that holds none of the production keys. A small VPS meets all
three conditions, provided it is set up accordingly.
{{< /lead >}}

*Reading time: about 20 minutes. State of play on 31 October 2026: prices, versions and defaults
have changed several times this year, so every figure is dated.*

{{< note-ia >}}

In [my way of working with Claude Code]({{< ref "/posts/claude-code-methode-revisee" >}}), the
agent runs in my laptop's terminal. That's enough as long as I stay at the keyboard. As soon as a
task runs long, you want to follow it from a phone, or run several agents in parallel, the laptop
becomes the constraint: it goes to sleep, it holds my keys and documents, and a misplaced
`rm -rf` is expensive there.

This article gathers what I took away from looking into the question: the Claude Code
documentation, vendor guides (Doppler, Tailscale), hosting price lists and community write-ups.
It targets a data scientist or MLOps engineer based in France, hence European hosting. Sources are
at the end.

{{< alert icon="lightbulb" >}}
**In short.** The setup that emerges combines three machines with distinct roles:

1. **A European CPU VPS dedicated to the agent**, reachable only over a private network
   (Tailscale), used through tmux, disposable and backed up by snapshots.
2. **A separate production machine**, deployed by CI, never by the agent.
3. **GPUs rented by the hour**, started by a script when training needs one.

Secrets are injected at runtime by a manager (Doppler or equivalent), read-only and time-limited.
Expect **€25 to €130 a month** depending on use, agent subscription included, which makes up 70 to
90% of the bill.
{{< /alert >}}

## Why run an agent on a VPS

| Need | What the VPS brings |
|---|---|
| Long, persistent sessions | The agent keeps going when the laptop sleeps; tmux keeps the state |
| Asynchronous work | Start a task, walk away, get a notification |
| Mobile access | SSH (Termius, Blink) over Tailscale, or Remote Control from the Claude app |
| Isolation from the personal machine | An `rm -rf` or a malicious dependency hits the VPS, not your keys or documents |
| Autonomous mode | A disposable environment, restorable from a snapshot |
| Parallelism | Several agents in tmux windows or worktrees, without overloading your machine |
| Closeness to production | Same Docker images, same architecture |

Two 2026 changes shift the picture:

- **Remote Control** (February 2026) lets you drive, from the mobile app or claude.ai/code, a Claude
  Code session running on the VPS. The session only makes outbound HTTPS requests: no port to
  open. Limits: one remote connection per session, a terminal that must stay open, and expiry after
  about 10 minutes without network.
- **Auto mode by default** (14 August 2026) replaces the permission prompt at every step with a
  classifier that reviews actions. In an Anthropic test with 1,053 testers, human review caught
  13.6% of dangerous commands, auto mode 89%. `permissions.deny` and `ask` rules apply before the
  classifier. Since v2.1.302, headless runs (`claude -p`) start in manual mode: you have to pass
  `--permission-mode auto` explicitly.

Auto mode reduces the need to run the agent with no permissions at all ("YOLO mode"), but it
remains a probabilistic filter. It doesn't replace isolation, which is what the rest is about.

## The choices that shape the setup

Twelve ideas come up from one source to the next. I treat them as a coherent whole rather than as
rules: each answers a specific risk, and you can relax one knowing what you give up.

1. **The VPS is a disposable workstation.** What matters lives in git, in the secrets manager and
   in external backups; the machine can be rebuilt in a quarter of an hour.
2. **The agent's machine and production are separate.** The agent can break its VPS, not
   production.
3. **No public port without a reason.** Tailscale or WireGuard for access, Cloudflare Tunnel or a
   reverse proxy for what must be public.
4. **Autonomy is paid for in isolation.** `--dangerously-skip-permissions` only in a container or
   VM with no valuable secret; elsewhere, auto mode and sandbox.
5. **Secrets are injected at runtime**, scoped, read-only, time-limited. The agent never fills in
   its own secrets.
6. **The "lethal trifecta" is broken**: private data, untrusted content and external communication
   are not brought together without a network guard.
7. **Persistence is handled at the terminal level**: tmux or zellij, mosh for unstable networks,
   Remote Control as an option.
8. **Parallelise with worktrees**, not copies: one agent per branch, a human who reviews the diffs.
9. **Notifications replace watching**: Stop and Notification hooks to ntfy or Telegram.
10. **CPU runs all the time, GPU on demand.** Renting a GPU around the clock to write code isn't
    worth it.
11. **Deployment stays boring**: Compose, a self-hosted PaaS or Kamal, with CI. No improvised
    `docker run` by the agent in production.
12. **Everything is dated.** Prices, versions and defaults change every quarter.

## The overall architecture

{{< mermaid >}}
flowchart TD
    T["Phone or laptop<br/>Termius · mosh · VS Code Remote-SSH · Remote Control"]
    T -->|Tailscale| A
    subgraph A["Agent VPS · EU · no public port"]
        direction TB
        A1["non-root user · tmux · worktrees"]
        A2["Claude Code: auto mode + sandbox"]
        A3["Doppler: dev_agent config, read-only token"]
        A4["Docker · uv · MLflow"]
        A5["hooks → private ntfy · snapshots + restic → S3"]
        A1 ~~~ A2 ~~~ A3 ~~~ A4 ~~~ A5
    end
    A -->|"git push (token scoped to the repo)"| G["GitHub + Actions<br/>tests · build · PR review · registry"]
    G -->|"deploy via Kamal / Coolify / Compose"| P["Production VPS · separate<br/>Caddy · FastAPI API · database · Uptime Kuma"]
    A -.->|"start script"| GPU["Hourly GPU · Scaleway L4/L40S<br/>training → MLflow → automatic shutdown"]
{{< /mermaid >}}

The key point of the diagram: **no arrow goes from the agent's VPS to production.** Code goes
through git and CI, which alone holds the deployment key.

## Choosing a VPS

2026 was a year of price rises, attributed to the cost of RAM and disks. Hetzner raised its cloud
prices twice (1 April and 15 June); OVHcloud took its VPS-1 from €4.49 to €6.49 before launching a
"VPS 2027" range; Scaleway and netcup raised prices too.

### Entry-level comparison

| Provider | Plan | Indicative price (Oct. 2026) | Location | Notes |
|---|---|---|---|---|
| Hetzner | CX23: 2 vCPU, 4 GB, 40 GB | €5.49/month excl. VAT (excl. IPv4) | Germany, Finland | Best price per GB of RAM; CX/CAX ranges often out of stock |
| Hetzner | CAX11 (Arm): 2 vCPU, 4 GB | €5.99/month | Germany, Finland | Check Arm support for Python and ML wheels |
| OVHcloud | VPS-1 2027: 2 vCores, 4 GB, 40 GB NVMe | €3.81 to €4.49 excl. VAT depending on commitment | France | Daily backup included |
| OVHcloud | VPS-2: 6 vCores, 12 GB, 100 GB | ≈ €11.99 excl. VAT | France | Good candidate for several agents plus MLflow |
| Scaleway | DEV1-M | ≈ €14.74 excl. VAT, storage extra | Paris, Amsterdam, Warsaw | Hourly GPUs in the same account |
| Hostinger | KVM 1/2, Claude Code template preinstalled | Promotions; renewal ×2 to ×3 | Several, incl. EU | Simplest to start; official MCP server; average performance |
| DigitalOcean, Vultr, Linode | 1 vCPU, 2 GB | ≈ $12/month (DO) | Frankfurt, Amsterdam, Paris | Pricier for the same RAM, excellent API |
| Contabo | Large VPS | Very low | Germany | Lots of RAM; uneven I/O and support according to the community |
| Oracle Free Tier | Arm Ampere | €0 | Frankfurt, Paris, Marseille | Capacity hit-and-miss; ill-suited as a main workstation |

Sources disagree on some prices (CX23, the OVH 2027 range): treat them as orders of magnitude and
check the official price list before ordering. The **renewal** price matters more than the
promotional one.

### Sizing

- **One agent, web development or light Python**: 2 vCPU, 4 GB, 40 GB. Watch Claude Code's memory
  with `htop`.
- **Two to four agents in parallel**: 4 to 8 vCPU, 8 to 16 GB, 80 to 160 GB NVMe.
- **Data science** (pandas, scikit-learn, LightGBM): at least 16 GB. RAM is almost always the
  limiting factor.
- **With a PaaS on the same machine**: Coolify or Dokploy need at least 2 GB more.
- **Disk**: Docker images, uv environments and datasets fill 40 GB in a few weeks. A separate
  volume or S3 storage avoids running out.

### Location and GDPR

A VPS with a European provider keeps data **at rest** in the EU, outside US extraterritorial laws.
But the code and excerpts the agent reads go to the model's API (Anthropic, OpenAI, Google),
wherever the VPS sits: European hosting doesn't settle that transfer. For real personal data, the
options are to work on pseudonymised or synthetic samples, to check your plan's data retention
(*Zero Data Retention* options on Team and Enterprise), or to use a self-hosted model.

### GPUs on demand

| Option | Price (Oct. 2026) | Use |
|---|---|---|
| Scaleway L4 24 GB | from €0.79/h | Inference of quantised 7-8B LLMs, vision, light LoRA |
| Scaleway L40S 48 GB | from €1.46/h | Heavier inference, image generation |
| Scaleway H100 PCIe | ≈ €2.73/h | Serious training |
| Modal | per second | One-off GPU jobs from Python |
| GPU rented by the month | L4 around the clock ≈ €577/month | Rarely worth it solo |

Twenty hours of L4 a month cost about €16, against nearly €580 for a permanent instance. The agent's
VPS stays on CPU; the agent writes the scripts that start the GPU instance, run training, log to
MLflow, then shut the instance down.

## Setup and security

### Basic hardening

- a non-root user with sudo; the agent runs as that user, never as root;
- key-only SSH: `PasswordAuthentication no`, `PermitRootLogin no`;
- UFW denying incoming connections by default; SSH is then only allowed on the `tailscale0`
  interface;
- fail2ban while SSH is still exposed, unattended-upgrades for security patches;
- Tailscale or WireGuard for access; Cloudflare Tunnel, Caddy or Traefik on 80/443 for what must be
  public;
- a snapshot before every big autonomous session, and external backups (restic or borg to S3).

The matching install sequence, for Ubuntu 24.04 (to adapt):

```bash
# --- As root, once ---
adduser dev && usermod -aG sudo dev
mkdir -p /home/dev/.ssh && cp ~/.ssh/authorized_keys /home/dev/.ssh/ && chown -R dev:dev /home/dev/.ssh
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/; s/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh
apt update && apt -y upgrade
apt -y install ufw fail2ban unattended-upgrades tmux mosh git curl jq bubblewrap socat
dpkg-reconfigure -plow unattended-upgrades
ufw default deny incoming && ufw default allow outgoing && ufw allow OpenSSH && ufw --force enable

# --- Private network ---
curl -fsSL https://tailscale.com/install.sh | sh && tailscale up --ssh
# Once the connection over the Tailscale IP is confirmed:
ufw allow in on tailscale0 && ufw delete allow OpenSSH

# --- As dev ---
curl -fsSL https://claude.ai/install.sh | bash      # Claude Code
curl -LsSf https://astral.sh/uv/install.sh | sh      # Python/uv
# Doppler: dev_agent_claude config, read-only expiring token,
# then: doppler configure set token <token> --scope .
# In the project: /sandbox, deny rules (~/.ssh, push --force, infra/prod)
tmux new -s project "doppler run -- claude"
```

The order of the two Tailscale lines matters: public SSH access is only removed once the connection
over the private network is confirmed to work, otherwise you lock yourself out.

### Authenticating the agent

Claude Code installs with the official script, then `claude` and `/login`. If OAuth fails for lack
of a browser on the server, an `ssh -L 15735:localhost:15735 user@vps` tunnel from the laptop works.
An API key never goes in `.bashrc`; without a secrets manager, a `chmod 600` file loaded by the
service.

### Secrets

[Doppler's guide for Claude Code](https://www.doppler.com/agents-claude-code) spells out a practice
that carries over to other managers:

- a configuration reserved for the agent, derived from the development environment (for example
  `dev_agent_claude`), with only the secrets the task needs;
- the agent never creates or edits its own secrets;
- a read-only, expiring service token, scoped to the directory (`--scope .`);
- launching through `doppler run`: secrets become environment variables and vanish when the process
  ends;
- Doppler's MCP server, if used, with that same token and `--read-only`;
- never live credentials: development and test only.

Alternatives are Infisical (open source), 1Password CLI (`op run`), sops with age, or the network
secrets of Claude Code on the web.

{{< alert icon="triangle-exclamation" >}}
**Limit.** A secret in an environment variable can still be read by the agent (`env`). The manager
shortens lifetime, narrows scope and prevents file leaks, but doesn't stop a compromised agent from
exfiltrating what it sees. Hence network filtering and low-privilege tokens: a GitHub token scoped
to one repository, a test database.
{{< /alert >}}

### Prompt injection and exfiltration

In June 2025 Simon Willison named the "*lethal trifecta*": **private data, untrusted content,
external communication**. Meta's "*Rule of Two*" (October 2025) follows from it: never more than two
of the three in one session. A coding agent combines all three by default: the repository and its
secrets, READMEs, issues and dependencies written by others, and `curl` or `git push` to talk to the
outside.

Concrete levers to break at least one branch:

- **Claude Code's native sandbox** (Linux: `sudo apt-get install bubblewrap socat`, then
  `/sandbox`). It isolates files and network through a domain allow-list proxy. Two traps: if the
  sandbox fails to start, Claude Code carries on without it with a mere warning; and the
  `dangerouslyDisableSandbox` escape hatch exists. Check at startup, and forbid it if needed
  ([documentation](https://code.claude.com/docs/en/sandboxing)).
- **`@anthropic-ai/sandbox-runtime`** wraps the whole process, MCP and hooks included, with network
  and writes denied by default.
- **A container or devcontainer** with a network policy and seccomp; for kernel-level isolation,
  gVisor or a separate VM.
- **Codex CLI**: `workspace-write` mode cuts the network by default; `--yolo` means
  `--dangerously-bypass-approvals-and-sandbox`.
- **MCP hygiene**: don't put an MCP that reads outside content (mail, tickets, web) in the same
  session as an MCP that holds secrets or write access.

### The isolation ladder

| Level | Implementation | When |
|---|---|---|
| 0 | Agent directly on the VPS, manual mode | Getting started |
| 1 | Auto mode, bubblewrap sandbox, deny rules | Everyday use |
| 2 | Agent in a container with no production secrets, filtered network | Autonomous mode, long tasks |
| 3 | Disposable VM or VPS per project, or microVM (E2B, Firecracker) | Untrusted code, several clients |
| 4 | Managed cloud sandbox (Claude Code on the web, None or Trusted network) | Asynchronous tasks from mobile |

Level 1 covers most everyday use; you move up a notch when you drop permissions or when the code
comes from outside.

## Day-to-day work

### Persistence and access

- **tmux** is the standard: one session per project, `tmux attach -t project`. Dedicated configs
  (for example [tmux-claude-code](https://github.com/sethdford/tmux-claude-code)) enable
  `allow-passthrough on` and a high `history-limit`.
- **zellij** as a modern alternative, **mosh** to survive the phone switching networks.
- **On mobile**: Termius, Blink or Echo on the Tailscale address, or Remote Control
  (`claude remote-control` or `/rc`) for chat access from the Claude app.
- **VS Code Remote-SSH** or remote Cursor to review diffs and open the VPS's notebooks without
  exposing JupyterLab.

### Parallelising

`git worktree add ../project-feature-x feature-x` gives each agent its own directory and branch, in
its own tmux window, with separate dev ports and PRs reviewed by a human. Two agents in the same
working directory trip over each other. Subagents parallelise within a task; worktrees, across
tasks.

### Context and automation

- **CLAUDE.md or AGENTS.md**: test commands, conventions, prohibitions ("never touch
  `infra/prod`"). In auto mode, this file also feeds the classifier: it is part of the security
  policy.
- **Hooks**: `PreToolUse` to block, `Stop` and `Notification` to alert through ntfy
  ([claude-ntfy-hook](https://github.com/nickknissen/claude-ntfy-hook)), on a hard-to-guess topic or
  a self-hosted ntfy.
- **MCP**: the bare minimum, read-only. A Coolify or Dokploy MCP that drives production from the
  agent's VPS cancels the separation.
- **Headless**: `claude -p "…" --permission-mode auto` from cron or a systemd timer, for a drift
  report or a dependency update.
- **Claude Code on the web and routines**: `claude --cloud` and `/schedule`, with a None, Trusted,
  Custom or Full network level ([documentation](https://code.claude.com/docs/en/claude-code-on-the-web.md)).
- **GitHub Actions**: the Claude Code action or `codex exec` for PR review, with minimally scoped
  tokens.

### For a data and MLOps profile

- **Environments**: uv and a base Docker image shared by development and production.
- **Data**: S3 object storage (Scaleway, OVHcloud); DVC or lakeFS if datasets change.
- **Experiment tracking**: MLflow on the VPS (SQLite or Postgres, artefacts on S3), reachable over
  Tailscale only. The agent logs its runs there, which leaves an auditable trail.
- **Pipelines**: Prefect, Dagster, or a Makefile or `just`.
- **Notebooks**: the agent writes tested modules; notebooks stay for exploration, as jupytext or
  Marimo, easier to edit and to review as diffs.
- **Light serving**: FastAPI or BentoML on CPU (scikit-learn, LightGBM, ONNX Runtime); quantised LLMs
  on hourly GPUs (vLLM).

## Deploying

### Same VPS or a separate one?

The same VPS is defensible for a prototype or staging. Once there are real users or real data,
separating machines costs €5 to €10 a month, little against the risk of an agent restarting
containers or reading production secrets.

### Self-hosted tools

| Tool | Licence | Recent version | Model | For whom |
|---|---|---|---|---|
| Docker Compose + Caddy | free | — | Versioned files, automatic HTTPS | Simplest; 1 to 3 ML services |
| Coolify | Apache-2.0 | v4.4.6 (9 Oct. 2026) | Web panel, Traefik, one-click apps | A "Heroku at home" |
| Dokploy | Apache-2.0 + proprietary part | v0.30.8 (29 Sept. 2026) | Web panel, Swarm, Traefik | Compose projects, clustering needs |
| Kamal | MIT | v2.12.0 (18 June 2026) | CLI + YAML, SSH deployment, no panel | Minimal attack surface |
| CapRover, Dokku | Apache-2.0 / MIT | — | Swarm, Heroku-style | Small machines |

A [comparison](https://pethost.dev/blog/coolify-vs-dokploy-vs-caprover-vs-dokku/) counts, in 2026,
61 GitHub security advisories for Coolify (16 critical) and 56 for Dokploy (33 critical), against
none for Kamal and CapRover. An admin panel therefore belongs behind Tailscale, and kept up to date.

### The deployment chain

1. The agent pushes a branch.
2. CI (GitHub Actions) tests, builds the image and pushes it to a registry.
3. CI deploys (Kamal, a Coolify or Dokploy webhook, or `docker compose pull && up -d` with a
   restricted deploy key); the agent doesn't deploy from its VPS.
4. A reverse proxy (Caddy, Traefik or Nginx) serves the application.
5. Observability follows: Uptime Kuma, logs (Loki or `docker logs`), metrics (Prometheus and Grafana,
   or Netdata); on the ML side, latency, errors and input drift (Evidently).
6. Production backups go to S3, and restoring them is tested.

## Alternatives to a VPS

| Option | Strengths | Weaknesses | Indicative cost | When to choose it |
|---|---|---|---|---|
| VPS dedicated to the agent | Control, persistence, fixed price, EU | Admin and security are on you | €5 to €15/month | Daily use, technical profile |
| Local machine | Zero latency, local GPU, free | Sleep, weak isolation, no async | €0 | Interactive exploration, with sandbox |
| Home server, mini-PC | Lots of RAM, consumer GPU | Electricity, residential IP, home network exposed | €300 to €1,000 upfront | Large RAM or GPU needs |
| Claude Code on the web | Nothing to administer, mobile, routines | Depends on GitHub, constrained environment | Included in the subscription | Well-scoped async tasks |
| Codespaces, Gitpod/Ona, Coder | Standardised devcontainers, teams | Hourly billing, long sessions expensive | Variable | Teams, onboarding |
| E2B, Daytona | microVMs, fast start, SDK | Built for products, not a dev workstation | ≈ $0.05/vCPU-h | Building an agent |
| Modal | GPU per second, Python-native | CPU sandbox 3 times pricier than functions | ≈ $0.14/core-h | One-off GPU jobs |
| Fly.io Machines/Sprites | Fast start, pay as you go | Less EU/GDPR-oriented | ≈ $0.04/CPU-h | Ephemeral environments |

For an individual, a VPS remains the most flexible base; managed sandboxes complement it for async
work, GPUs or a product.

## What it costs

Claude subscriptions in October 2026: Pro at $20/month, Max 5x at $100, Max 20x at $200, Claude Code
included with shared limits (a 5-hour window and a weekly cap). Some sources describe a restructuring
into "Max $100 / Ultra $200": the official price list is the reference.

| Scenario | Agent | Agent VPS | Production | GPU | Indicative total |
|---|---|---|---|---|---|
| Getting started | Pro $20 | ≈ €4 to €5.5 | — | — | ≈ €25/month |
| Regular solo data scientist | Max 5x $100 | 8-12 GB, €10 to €15 | €5 to €6 | 20 h of L4 ≈ €16 | ≈ €120 to €130/month |
| Heavy use, several agents | Max 20x $200 (+ another agent) | 16 GB, €20 to €30 | ≈ €10 | 50 h of L4 ≈ €40 | ≈ €250 to €300/month |

Excluding VAT, with $1 ≈ €0.9. The subscription makes up 70 to 90% of the bill: saving a few euros
on the VPS matters little, forgetting a GPU that's running matters a lot.

## Common pitfalls

- an agent running as root on the production machine, next to the panel, the database and the
  secrets;
- the production `.env` copied onto the agent's VPS, or keys in `.bashrc`;
- a sandbox you believe is active when it disabled itself for lack of bubblewrap or socat;
- `--dangerously-skip-permissions` outside a disposable container, or blanket "allow" rules
  (`Bash(*)`);
- JupyterLab, MLflow, ttyd or the Coolify panel on the public IP, even behind a password;
- a public ntfy topic carrying code summaries;
- a GPU instance left running, for lack of a `trap` or an automatic shutdown timeout;
- two agents in the same directory instead of two worktrees;
- backups never tested by restoring them;
- a VPS picked on its promotional price without looking at renewal;
- "external content reader" and "secret holder" MCPs in the same session;
- a `claude -p` cron job assumed to run in auto mode, when it has started in manual mode since
  v2.1.302.

## My checklist

**Choices**
- [ ] European provider, at least 4 GB of RAM (8 to 16 GB for data or several agents), renewal price checked.
- [ ] Separate production VPS; GPUs rented by the hour.

**Hardening**
- [ ] Non-root user, key-based SSH, root disabled.
- [ ] UFW denying by default, SSH over Tailscale only, fail2ban, unattended-upgrades.
- [ ] No admin service on the public IP.

**Agent**
- [ ] bubblewrap and socat installed, `/sandbox` active and checked.
- [ ] Auto mode (or manual for sensitive work), explicit deny rules, no-permission mode only in a disposable container.
- [ ] CLAUDE.md or AGENTS.md with commands, conventions and prohibitions.
- [ ] Minimal, read-only MCPs, no trifecta.
- [ ] Headless scripts with an explicit `--permission-mode`.

**Secrets**
- [ ] Secrets manager, agent-specific config, read-only expiring token.
- [ ] No production secret on the agent's VPS; minimally scoped tokens.

**Workflow**
- [ ] tmux or zellij and mosh, mobile client over Tailscale.
- [ ] One worktree per agent, human review of PRs.
- [ ] Notifications on a private topic.
- [ ] Private MLflow, artefacts on S3, reproducible uv environments.

**Deployment and operations**
- [ ] CI that tests and builds; deployment goes through CI.
- [ ] HTTPS reverse proxy, monitoring, logs.
- [ ] Snapshots before autonomous sessions; backups tested by restoring them.
- [ ] Quarterly review of prices, versions and defaults.

## Caveats

- **Dates.** State as of 31 October 2026; prices, ranges and defaults changed several times this
  year.
- **Fact or practice.** The tmux configs, ntfy tools, Marimo and jupytext, the preference for Kamal
  and the views on Contabo and Oracle are community practice. The auto mode figures come from
  Anthropic.
- **Secondary sources.** Several prices come from aggregators that sometimes contradict each other;
  the Coolify and Dokploy security advisory counts come from a single comparison.
- **Coverage.** Codespaces, Gitpod/Ona, Gemini CLI, Cursor, OpenCode and Aider were not examined in
  detail; the isolation, secrets and network principles apply to them in the same way.

## Sources

- [Hostinger: Claude plugin](https://github.com/hostinger/claude-plugin)
- [Hostinger: installing Claude Code on a VPS](https://www.hostinger.com/support/11929523-installing-claude-code-on-a-vps-at-hostinger/)
- [Doppler: agents and Claude Code](https://www.doppler.com/agents-claude-code)
- [Claude Code: sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Claude Code: sandbox environments](https://code.claude.com/docs/en/sandbox-environments)
- [Claude Code: secure deployment (Agent SDK)](https://code.claude.com/docs/en/agent-sdk/secure-deployment)
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web.md)
- [Claude Code: cloud environments](https://code.claude.com/docs/en/cloud-environments)
- [Claude Code: routines](https://code.claude.com/docs/en/routines)
- [Anthropic: auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- [Help Net Security: auto mode](https://www.helpnetsecurity.com/2026/08/10/anthropic-claude-code-auto-mode/)
- [VentureBeat: Remote Control](https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote)
- [Hetzner: price adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)
- [stackvaluelab: Hetzner price increase 2026](https://stackvaluelab.com/hetzner-price-increase-2026/)
- [zen-cloud: OVH price increase 2026](https://zen-cloud.cloud/blog/ovh-augmente-prix-45-pourcent-alternatives-2026)
- [Scaleway: choosing the right GPU](https://www.scaleway.com/en/choose-the-right-gpu/)
- [Qovery: GPU pricing comparison 2026](https://www.qovery.com/blog/gpu-pricing-comparison-method-aws-gcp-azure-scaleway-2026)
- [The lethal trifecta for coding agents](https://munderdiffl.in/blog/the-lethal-trifecta-for-coding-agents/)
- [AI coding CLI sandbox modes compared](https://inventivehq.com/blog/ai-coding-cli-sandbox-approval-modes-compared)
- [NetworkChuck: remote-claude-code](https://github.com/theNetworkChuck/remote-claude-code)
- [Claude Code on a VPS guide (Medium)](https://medium.com/@0xmega/claude-code-on-a-vps-the-complete-setup-security-tmux-mobile-access-2d214f5a0b3b)
- [pethost: Coolify vs Dokploy vs CapRover vs Dokku](https://pethost.dev/blog/coolify-vs-dokploy-vs-caprover-vs-dokku/)
- [haloy: self-hosted deployment tools compared](https://haloy.dev/blog/self-hosted-deployment-tools-compared)
- [Fly.io: AI sandbox pricing](https://fly.io/learn/ai-sandbox-pricing/)
- [ssdnodes: Claude plans](https://www.ssdnodes.com/learn/claude-plans-which-one-do-you-need)
