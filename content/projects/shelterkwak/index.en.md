---
title: "Shelterkwak: tracking a household's crisis preparedness, tier by tier"
date: 2026-11-09
draft: false
nature: "produit"
description: "A local, offline app to track how ready a household is for civil emergencies (outages, storms, evacuation): 280 goals across 14 areas, nine tiers that can be earned and lost, an inventory measured in days of self-sufficiency whose items prove goals, and a screen for the day itself."
summary: "An app installed on the phone, with no account and no third-party service: 280 goals in nine blocking tiers, a level that drops when supplies expire, a card inventory that computes days of self-sufficiency and validates what it proves, buying guides, and an offline Crisis screen for the day itself."
tags: ["python", "fastapi", "sqlite", "react", "typescript", "pwa", "claude code"]
featureImage: "carte-en.png"
showTableOfContents: true
---

{{< lead >}}
Knowing where the household stands in the face of a water cut, a storm or an evacuation: what is
ready, what is missing, what has expired. The app runs on the phone, without a network, and syncs
with a PC at home.
{{< /lead >}}

{{< fiche-projet
    statut="In development · offline v2 shipped, catalogue reviewed at each council"
    periode="Since November 2026"
    role="Solo: specification, content framework, development"
    stack="Python 3.13, FastAPI, SQLModel, SQLite, React, TypeScript, Vite, PWA, IndexedDB, GSAP, Tailscale"
    code="https://github.com/gwils28/Shelterkwak" >}}

{{< stats >}}
{{< stat value="280" label="goals" >}}across 14 areas and 9 tiers, written in YAML{{< /stat >}}
{{< stat value="2" label="scoring engines" >}}Python and TypeScript, kept identical by shared test cases{{< /stat >}}
{{< stat value="141" label="automated tests" >}}91 on the server, 50 in the app{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Work in progress.** This page describes the repository as of 14 November 2026, twelve days
after the first commit (17 merged pull requests). Since the first version of this page
(9 November), three councils and a market review have brought in **proofs** (an item or a talent
validates on its own what it guarantees), **buying guides**, a **model basket** for the pantry,
skills counted **per person** and a redesigned Goals tab. The figures are counted in the catalogue
and the tests, and will be updated as the project moves on.
{{< /alert >}}

{{< alert icon="image" >}}
**Every screenshot shows a fictional household** (Camille, Sam, their daughter Léa and Moka the
cat), entered on a demo instance. The app only exists in French, so the screenshots show its
French interface.
{{< /alert >}}

## The problem

Official preparedness guides (government, Red Cross) say what to do: a water supply, a first-aid
kit, a go-bag, contacts on paper. They do not say **where my household stands**, or what has
stopped being true since: the bottles that expire, the power bank never recharged, the first-aid
course from three years ago, the baby who has arrived in the meantime.

I wanted a tool that:

- **measures** preparedness with checkable criteria ("14 days of water for this household"),
  not with a feeling;
- **regresses** when reality changes: an expired supply no longer counts, a skill not practised
  expires;
- **fits the household**: a 6th-floor flat does not have the same priorities as an isolated
  house, nor does a household with a child or a hard-to-refill prescription;
- **works without a network**, since the day the network is down is precisely the day it is
  needed;
- **keeps the data at home**: the household's members, their health conditions and where their
  equipment is stored have no business on a third-party server.

## Where the project stands

{{< timeline >}}

{{< timelineItem icon="check" header="v1 · The engine and the catalogue" badge="2 November" subheader="A specification drawn from an interview" >}}
A specification written from an interview, then a YAML catalogue (levels, areas, goals, needs,
questionnaire), a level engine in pure Python, a FastAPI API and a React interface with the
column drawn in SVG.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="v2 · Offline on the phone" badge="2 November" subheader="The engine ported to TypeScript" >}}
An installable app (PWA), an operation log in the browser, sync with the PC's server over
Tailscale. The Python engine remains the reference; its TypeScript copy replays the same test
cases.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Four review councils" badge="6 to 9 November" subheader="The catalogue tested against three viewpoints" >}}
At each council, three agents review the app and the catalogue, each from a different angle, then
debate; I approve the plan before it is implemented. They brought the Crisis screen, the 30-day
grace period, the Morale, Self-defence and Cybersecurity areas, physical fitness, and corrected
content that was wrong or dangerous.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Card inventory and skills" badge="8 and 9 November" subheader="Cards with five grades, talent trees" >}}
The inventory becomes a deck of cards with five grades each and a quantified overview; skills
become nine talent trees.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Sensitive cards and buying guides" badge="9 and 10 November" subheader="The 9 November council and a market review" >}}
Weapon, alcohol and tobacco cards now only show for households that declare them; some content is
corrected. A separate expert, the Quartermaster, adds checked buying guides per grade. Seven
monuments and six declarable risks are added.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Proofs and skills per person" badge="11 and 12 November" subheader="Two councils on the same day" >}}
Owning an item or mastering a talent now validates the goals it guarantees: 283 links audited one
by one. Talents are counted per person, with critical talents to double up. The pantry gets its
model basket.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Goals tab redesigned" badge="14 November" subheader="The current tier first" >}}
The tab opens on the tier to build, with its progress and foldable groups. Two cards join the
inventory: rope and barter goods.
{{< /timelineItem >}}

{{< /timeline >}}

## What the app does

### A monument with nine tiers

The household's level is a monument with nine tiers, a Roman column by default. Each tier stands
for a resilience horizon:

| Level | Name | What the household can withstand |
|---|---|---|
| 1 | Initiate | A few hours of outage: 24 h of water and food, a light, the emergency numbers |
| 2 | Aware | Knows its risks, has its papers, its contacts and a basic plan |
| 3 | Ready | 3 days without running water, electricity or resupply |
| 4 | Provident | 14 days confined or cut off from the grid |
| 5 | Enduring | 3 months of partial disruption, an emergency savings fund |
| 6 | Seasoned | 6 months of supplies, practical skills kept up |
| 7 | Self-reliant | Produces part of its own water, food and energy |
| 8 | Resilient | Part of a mutual-aid community, passes on what it knows |
| 9 | Antifragile | Everything is tested for real, each crisis improves the plan |

The tiers are **blocking**: level 4 is reached only once every required goal of levels 1 to 4 is
validated, in every area. A household far ahead on water but with no evacuation plan stays at the
tier of its weakest link, and the home screen says which one.

![The home screen: the monument, the next step and self-sufficiency](monument.webp "The fictional household is at level 3, with 25 of the 38 goals of level 4. Drum III is cracked: the power-bank validation has expired and the household has until 8 December to redo it. On the right, the most useful actions and the days of self-sufficiency.")

Level 9 cannot be bought: it requires **testing** the household (7 days without mains water,
72 hours with the main breaker off, a real evacuation in under 15 minutes, a surprise drill with
one's group), and almost all its criteria must be redone every year.

The monument is chosen from twenty-one: a pyramid, a tree, the Eiffel Tower, the Great Mosque of
Djenné, a moai, a rocket, an undersea volcano, a lighthouse, the Iguazú Falls, the Burj Khalifa, a
basketball hoop… Changing monument changes nothing about the level.

![The twenty-one monuments](monuments.webp "Each monument has its nine tiers and its crown, which lights up at level 9.")

### A level that can drop

The level is not kept for good. It goes down when:

- **a supply expires**: an expired item immediately stops counting towards self-sufficiency;
- **a validation expires**: a skill to practise, a piece of equipment to test, a drill to repeat
  each have a period of validity;
- **a seasonal deadline passes**: firewood stored before November, the chimney swept before
  October;
- **the household changes**: one more member raises the needs and can make new goals apply.

So that a single forgotten power bank does not bring down several tiers at once, an expired
validation first enters a 30-day **grace period**: the drum cracks but stays up. Expired supplies
get no grace period. That compromise came out of the first council: a supply that is not renewed
does not exist, but a sudden drop makes people give up on the tool.

![The household's history](parcours.webp "The fictional household climbs to level 3 in early October, falls back to level 1 when a grandmother on a limited-supply prescription joins it (new goals become required), then climbs back up when she leaves. Below, the log of every action.")

### 280 goals that fit the household

The goals are spread over 14 areas: water, food, energy, health, shelter, safety, communication,
mobility, skills, finances, community, morale, self-defence and cybersecurity. Each has a level,
an explanation ("why it matters") and a kind: an action ticked by hand, a skill to revalidate, or
a supply computed from the inventory.

A goal only shows up for the households it concerns:

- **where they live**: a flat does not need a campfire or fuel stored in the cellar, but must know
  how to use a camping stove without poisoning itself;
- **the members**: child, baby, senior, pet;
- **health conditions**: twelve in total, from glasses to a prescription that is dispensed in
  limited amounts. For glasses: a spare pair and a copy of the prescription at level 2, a pair in
  the go-bag at level 3, two spare pairs and a repair kit at level 5;
- **declared risks**: flooding, cold, heatwave, industrial hazard; six more (storms, landslides,
  epidemic, cyberattack, terrorism, war) can already be declared, without changing the catalogue
  yet.

Physical tests (walking 15 km with a pack, being able to swim) have an **adapted variant** for
households with a member who has reduced mobility: the requirement is about the household's
capability, not about each person's fitness.

The Goals tab opens on the **current tier**, the one to build: its horizon, the progress of its
required goals, then To do, To revalidate and Validated tabs, an area filter and foldable groups.
Each line unfolds into the why, the revalidation rhythm, the dates and what validated it.

![The Goals tab](objectifs.webp "Tier IV, Provident, under way: 25 of 38 required, fourteen goals to do, filterable by area. Fictional data.")

![Goals validated by the inventory](objectif-preuve.webp "Tier II, fully validated: several goals were validated thanks to an item owned at the stated grade (« Grâce à … »). Fictional data.")

At sign-up, an adaptive questionnaire of 26 questions describes the household, where it lives now
and where it plans to live ("a house in the countryside in two years"), what is already in place
and the target level. The app infers a starting level from it. Goals specific to the planned home
are offered separately, in a "Prepare for what's next" section.

### An inventory measured in days of self-sufficiency

The inventory answers one question: **how many days can the household hold out**? Each item has a
quantity, an expiry date and a storage place; self-sufficiency is the sum of unexpired items
divided by the household's daily need, computed member by member (4 L of water per adult, 2.5 L
per child, 0.3 L for a cat; 2,200 kcal per adult).

Equipment takes the form of **101 cards** in ten categories, each with five grades (rustic, common,
confirmed, epic, legendary). A card's grade depends on its quality, its options, the quantity, the
minimum contents (for a first-aid kit or a bag) or, for a supply, the days of self-sufficiency.
Sensitive cards are kept aside: weapons only show for households that declare them; alcohol,
tobacco and self-defence weapons are "on request", behind "See also".

![The card inventory](inventaire.webp "36 cards owned out of the 72 that concern this household, in colour with their grade; the others stay greyed out. Fictional data.")

![A supply's card](fiche-objet.webp "The water supply: its grade follows from self-sufficiency (20 days, confirmed grade), and the card lists the goals it serves, validated or still to do. Fictional data.")

### What an item or a talent proves

At first, owning an item validated nothing: the goal had to be ticked separately, at the risk of
validating the same thing twice or forgetting it. The 11 November council classified the 283
links between items, talents and goals one by one: a link **proves** when owning the item or the
talent is enough, and **contributes** when it helps without being enough. The three experts
agreed on their own on 93 % of the links; the main agent settled the 19 disagreements. A few
principles came out of it:

- **owning proves a state, never a know-how**: having the tool is not knowing how to use it, and
  no item proves a skill (a rule checked at load time);
- **a talent proves a know-how, not a possession**;
- **the link sits at the grade that covers the whole goal**: a radio proves "a radio, tested, with
  spare batteries" from the common grade up, not before;
- **a misleading link is removed**: it is worse than no link.

A proof is not a recorded operation: it is recomputed at every replay of the log, dated from when
the item was declared or the talent acquired. Removing the item makes the goal fall again, unless
it was also validated by hand.

![An item's card and its proofs](fiche-radio.webp "The radio: owned at the common grade, it validates on its own \"battery or wind-up radio, tested\" (✓ auto); at the epic grade it would validate the CB set. Relaying news to the neighbourhood, by contrast, only gets a contribution. Fictional data.")

### Buying guides and a model basket

For some cards, an item's sheet also opens **buying guides** grade by grade: the criteria that
matter, then two or three models with a price range and the market where they are sold. They come
from a separate expert, the Quartermaster, in charge of a market review: 70 grades across 23
cards, checked on 9 November. The session was capped at 200 web searches and many sites refused
access: whatever could not be checked was left empty, nothing was filled in from memory. A command
lists the guides checked more than a year ago.

![A card's buying guides](reperes-achat.webp "The radio, at the confirmed grade: the criteria, the Quartermaster's pick and two other models, with their price and market. \"Guides, not obligations.\" Fictional data.")

The pantry has a **model basket** at the common grade: thirteen foods to hold out three days
without cooking, with their share of the calories, how long they keep and precautions if the
household has a child. Quantities are computed for the household, and a line is ticked when a
linked item is in stock.

![The pantry's model basket](panier-type.webp "The pantry at 15 days: the supply's five grades, then the model basket, three lines out of thirteen already covered. Fictional data.")

The overview sums up the inventory: the weakest link, self-sufficiency per category against the
3-day, 14-day, 3-month and 6-month marks, a **twelve-month projection** showing when
self-sufficiency drops as items expire, assuming nothing is consumed or bought, and the most
useful purchases.

![The inventory overview](etat-des-lieux.webp "The weakest link is cooking fuel (5 days). In the projection, water drops to zero in autumn 2027, when the water jugs expire. Fictional data.")

### Nine skill trees

Skills are grouped into nine specialities (physical fitness, healer, handyman, cook, protector,
gatherer…), each a talent tree with five ranks, on three or four branches: 122 talents, 121 of
them in the grid. A talent can be ticked once its prerequisites are acquired, with what proves it
(a certificate, a test), a date and the **number of people in the household** who master it.

Nine life-saving skills are **critical** (raising the alarm, basic life-saving, PSC1 first aid,
cutting off water and power, the camping stove, a fire starting, getting out of smoke, heat and
cold, treating water): at the top of the tab, the app says how many have a stand-in, and a
household that doubles them all validates the redundancy goal. Some talents get a "keep it up"
badge after a year, without anything being removed.

![The Skills tab](competences.webp "Twelve talents acquired out of 119 for a flat; four critical talents out of five have a stand-in, only one person knows how to get out of smoke. Fictional data.")

![The Healer's tree](competences-soigneur.webp "The Healer and its fourth branch, Accidents and climate: \"×2\" when two people master a skill, an orange \"1\" when only one does. Fictional data.")

### A screen for the day itself

The red "Crise" button stays visible on every page. It opens a screen designed for someone under
stress, which works offline and can be printed:

- call buttons (15, 112, 18, 17, and 114 by text message, the French emergency numbers) and a
  breathing reminder;
- folded reflex sheets: **first aid** (cardiac arrest, bleeding, carbon monoxide, heatstroke…) then
  **situations** (water cut, flood, evacuation, intrusion, lost or hacked phone…), filtered by the
  household's risks and members;
- the household's own sheets: contacts, meeting points, who does what, medical sheets;
- where the equipment is, from the inventory, and the drinking-water supply.

![The Crisis screen on a computer](crise.webp "Emergency numbers first, then the first-aid sheets and the situations that concern this household. Fictional data.")

### On the phone, without a network

The app installs on Android like a native app. The engine, the catalogue and the data live on the
phone: in airplane mode, everything works. The PC's server is used to install it, to sync the
phone and the computer, and as a backup. It is reachable over Tailscale, in HTTPS, at home or
away, with nothing exposed to the Internet.

![The app on a phone](telephone.webp "Left, the home screen and its tab bar; right, the Crisis screen with the cardiac-arrest sheet open. Fictional data.")

## How it is built

### An operation log rather than a state

Nothing is stored as is: every change is an immutable **operation** (validate a goal, add an
item, change the household), timestamped and identified. The household's state, its level and
its whole history are rebuilt by replaying the log in order.

{{< mermaid >}}
flowchart LR
    T["Phone<br/>PWA + IndexedDB"] -->|operations| S["PC server<br/>FastAPI + SQLite"]
    P["PC browser<br/>PWA + IndexedDB"] -->|operations| S
    S -->|other devices' operations| T
    S -->|other devices' operations| P
    T --> M1["TypeScript engine<br/>replays the log"]
    S -.->|read only| M2["Python engine<br/>the reference"]
{{< /mermaid >}}

That choice settles four problems at once:

- **sync**: each device sends the operations the server does not know and receives the others'.
  Two changes to the same thing are settled by timestamp: the last one written wins;
- **history**: the level curve is not recorded but recomputed, including on the dates when a
  supply expires or a grace period ends, the only moments the level changes without any action;
- **rule changes**: when a council moves a goal to another tier, the level is recomputed over the
  whole log, with no data migration. The one constraint: a goal's identifier is never renamed,
  since it is stored;
- **new features without new operations**: proofs, the model basket and the number of people who
  master a talent are added as optional fields or as computations at replay; older operations
  stay valid.

The server computes nothing for the app: it keeps the shared copy of the log and serves the
files. A JSON backup of the log can be exported from the Household tab.

### Two engines, one behaviour

To work offline, the level engine has to run on the phone, so in TypeScript. But the Python
engine is easier to test and to review. Both exist, and Python is the reference: a script
generates test cases from it (households, logs, dates), which the front-end tests replay to check
that the TypeScript engine gives exactly the same result, proofs included. A test fails if the
cases were not regenerated after a catalogue change.

### Content outside the code

Goals, daily needs, the questionnaire, item cards, talents, Crisis sheets and buying guides live
in YAML files, not in the code. Adding a goal means adding an entry:

```yaml
  - id: eau.exemple
    level: 4                 # tier
    kind: check              # check | skill | stock
    required: true           # false: bonus, does not block the tier
    contexts: [periurbain, rural]
    revalidate_days: 365     # expires and lowers the level
    title: …
    why: …
```

The catalogue is validated at start-up (references, levels, the order of an item's grades, no item
proving a skill, basket shares adding up to 100 %), and a test checks that every type of home keeps
at least one required goal per tier, so that no household reaches the top through empty tiers.

### A catalogue reviewed in council

The catalogue is the most delicate part: a misplaced criterion discourages, wrong content can be
dangerous. I had it reviewed by a **council of three AI agents**, each with an angle: the Tracker
(self-reliance in rural settings), the Tactician (urban crisis and logistics) and the Sentinel
(health, vulnerable people, psychology). Each analyses alone, without knowing the others' views;
the main agent checks their findings in the code, leads the debate and writes a summary that I
approve or not. Seven councils each have their dated report in the repository, as does the
Quartermaster's market review.

A few corrections that came out of it:

| Finding | Decision |
|---|---|
| A campfire required in a flat | Fire and fuel kept for suburban and rural homes, a safe stove in town |
| Physical tests blocked a household with a member of reduced mobility for good | An adapted variant, the requirement stays for the others |
| Level 3 had 27 required criteria, several unrelated to "holding out 72 h" | Cut to 19, the rest moved to level 4 |
| A PSC1 first-aid course required at level 3, to be booked weeks ahead | "Gestes qui sauvent" (2 h, free) at level 3, PSC1 at level 4 |
| Supplies estimated at sign-up never expired | They expire after six months unless confirmed |
| Silver tablets given to purify water, an FFP2 mask against smoke | Chlorine or chlorine dioxide for water; FFP2 stops particles, not CO or gases |
| Weapon, alcohol and tobacco cards offered to every household | Weapons only with the matching tag; alcohol, tobacco and self-defence weapons on request |
| Pepper spray kept in the safe room | Advised against with an asthmatic or a baby, kept out of the confinement room |
| A ticked talent did not say how many people master it | Now it does; an "every adult" goal is proven only when they are as many as the adults |

{{< alert icon="triangle-exclamation" >}}
**Known limitation**: these reviews are done by AI agents, not by first-aiders, doctors or
lawyers. The first-aid sheets repeat publicly taught gestures and point to the official courses
(Gestes qui sauvent, PSC1), but the catalogue has not been validated by a professional. The buying
guides are guides, not tested recommendations. The app helps get organised; it replaces neither
training nor the authorities' instructions.
{{< /alert >}}

## What's next

The councils left postponed work: lightening level 4 (34 required goals in a flat), tracking
talents member by member, adapted variants for physical talents (reduced mobility, pregnancy,
respiratory illness), and above all a **review by a first-aider** of the first-aid sheets and the
Healer's tree. About thirty cards still await their buying guides, and the six new declarable
risks do not change the goals offered yet.

The end-to-end scenario (phone and PC, airplane mode, sync) is in the repository, but it no
longer follows the app (it expects a different level after the interview and the Inventory tab's
old name): it needs fixing before it can run in continuous integration. Then come revalidation
reminders and a trial on a small home server.

## Try it

```bash
git clone https://github.com/gwils28/Shelterkwak
cd Shelterkwak
make install   # Python (uv) and Node dependencies
make check     # lint, tests, engine parity, build
make run       # the app on http://127.0.0.1:8000
```

Installing on an Android phone, with Tailscale, is described in `docs/telephone.md` (in French).
