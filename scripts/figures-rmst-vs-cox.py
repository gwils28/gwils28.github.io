"""Figures FR de l'article RMST vs Cox (content/posts/rmst-vs-cox/), en SVG pur, calcul analytique.

Usage : python3 scripts/figures-rmst-vs-cox.py content/posts/rmst-vs-cox
"""
import math
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
L = 0.05                      # risque de base, par mois
CP, HB, HA = 8.0, 1.0, 0.4    # effet différé : HR 1 avant 8 mois, 0,4 après
TAU = 24.0

SURFACE, TEXT, TEXT2, GRID, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#8a8984"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = ["#9ec5f4", "#6da7ec", "#256abf", "#0d366b"]
FONT = "Inter, Helvetica, Arial, sans-serif"


def fr(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


# ---------- modèle ----------
def hr_at(t, delayed=True, hr_ph=1.0):
    if not delayed:
        return hr_ph
    return HB if t < CP else HA


def surv(t, delayed=True, hr_ph=1.0):
    if not delayed:
        return math.exp(-L * hr_ph * t)
    if t < CP:
        return math.exp(-L * HB * t)
    return math.exp(-L * HB * CP - L * HA * (t - CP))


def rmst(tau, **kw):
    n = 4000
    h = tau / n
    return sum((surv(i * h, **kw) + surv((i + 1) * h, **kw)) / 2 * h for i in range(n))


def cox_limit(admin, grid_step=0.02, horizon=None):
    """HR* : point fixe de l'équation de score limite, censure administrative à `admin`."""
    horizon = admin if horizon is None else horizon
    ts = [(i + 0.5) * grid_step for i in range(int(horizon / grid_step))]
    hr = 0.7
    for _ in range(200):
        num = den = 0.0
        for t in ts:
            p0, p1 = math.exp(-L * t), surv(t)
            w = p0 * p1 / (p0 + p1 * hr) * L
            num += w * hr_at(t)
            den += w
        new = num / den
        if abs(new - hr) < 1e-10:
            break
        hr = new
    return hr


def cox_weights(admin, grid_step=0.1):
    hr = cox_limit(admin)
    ts = [i * grid_step for i in range(int(admin / grid_step) + 1)]
    ws = []
    for t in ts:
        p0, p1 = math.exp(-L * t), surv(t)
        ws.append(p0 * p1 / (p0 + p1 * hr) * L)
    tot = sum(ws) * grid_step
    ws = [w / tot for w in ws]
    late = sum(w for t, w in zip(ts, ws) if t >= CP) * grid_step
    return ts, ws, late, hr


# ---------- SVG ----------
class Plot:
    def __init__(self, x0, y0, w, h, xlim, ylim):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xlim, self.ylim = xlim, ylim

    def X(self, x):
        return self.x0 + (x - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * self.h

    def axes(self, xticks, yticks, xlabel, ylabel, yfmt=lambda v: fr(v, 1)):
        s = []
        for v in yticks:
            y = self.Y(v)
            s.append(f"<line x1='{self.x0}' y1='{y:.1f}' x2='{self.x0 + self.w}' y2='{y:.1f}' stroke='{GRID}' stroke-width='1'/>")
            s.append(f"<text x='{self.x0 - 8}' y='{y + 4:.1f}' font-size='11' fill='{TEXT2}' text-anchor='end'>{yfmt(v)}</text>")
        for v in xticks:
            x = self.X(v)
            s.append(f"<text x='{x:.1f}' y='{self.y0 + self.h + 18}' font-size='11' fill='{TEXT2}' text-anchor='middle'>{v:g}</text>")
        s.append(f"<line x1='{self.x0}' y1='{self.y0 + self.h}' x2='{self.x0 + self.w}' y2='{self.y0 + self.h}' stroke='{MUTED}' stroke-width='1'/>")
        s.append(f"<text x='{self.x0 + self.w / 2}' y='{self.y0 + self.h + 38}' font-size='11.5' fill='{TEXT2}' text-anchor='middle'>{xlabel}</text>")
        s.append(f"<text transform='translate({self.x0 - 44} {self.y0 + self.h / 2}) rotate(-90)' font-size='11.5' fill='{TEXT2}' text-anchor='middle'>{ylabel}</text>")
        return s

    def path(self, xs, ys):
        return " ".join(("M" if i == 0 else "L") + f"{self.X(x):.1f} {self.Y(y):.1f}" for i, (x, y) in enumerate(zip(xs, ys)))

    def line(self, xs, ys, color, width=2.2, dash=None):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        return f"<path d='{self.path(xs, ys)}' fill='none' stroke='{color}' stroke-width='{width}' stroke-linejoin='round'{d}/>"

    def band(self, xs, lo, hi, color, op):
        pts = [f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in zip(xs, hi)]
        pts += [f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in zip(reversed(xs), reversed(lo))]
        return f"<polygon points='{' '.join(pts)}' fill='{color}' fill-opacity='{op}' stroke='none'/>"


def svg(w, h, title, subtitle, label, body):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' "
            f"font-family='{FONT}' role='img' aria-label='{label}'>\n"
            f"<rect width='{w}' height='{h}' fill='{SURFACE}'/>\n"
            f"<text x='24' y='32' font-size='15' font-weight='600' fill='{TEXT}'>{title}</text>\n"
            f"<text x='24' y='52' font-size='11.5' fill='{TEXT2}'>{subtitle}</text>\n"
            + "\n".join(body) + "\n</svg>\n")


def txt(x, y, s, size=11, color=TEXT2, anchor="start", weight=None):
    wt = f" font-weight='{weight}'" if weight else ""
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' fill='{color}' text-anchor='{anchor}'{wt}>{s}</text>"


# ---------- 1. effet différé ----------
def fig_effet_differe():
    b = []
    # panneau gauche : HR(t)
    p = Plot(80, 90, 230, 250, (0, 48), (0, 1.1))
    b += p.axes([0, 12, 24, 36, 48], [0, 0.2, 0.4, 0.6, 0.8, 1.0], "Mois depuis la randomisation", "Rapport des risques HR(t)")
    b.append(p.line([0, CP, CP, 48], [1, 1, 0.4, 0.4], TEXT, 2.2))
    b.append(f"<line x1='{p.X(CP):.1f}' y1='{p.y0}' x2='{p.X(CP):.1f}' y2='{p.y0 + p.h}' stroke='{MUTED}' stroke-dasharray='3 3'/>")
    b.append(txt(p.X(CP) + 6, p.Y(0.72), "l’effet démarre", 10.5))
    b.append(txt(p.X(CP) + 6, p.Y(0.72) + 14, "à 8 mois", 10.5))
    b.append(txt(p.X(1), p.Y(1.0) - 8, "HR = 1", 10.5, TEXT))
    b.append(txt(p.X(30), p.Y(0.4) - 8, "HR = 0,4", 10.5, TEXT))
    b.append(txt(p.x0, 80, "Le risque relatif change avec le temps", 12, TEXT, weight=600))
    # panneau droit : survie
    q = Plot(420, 90, 310, 250, (0, 48), (0, 1.02))
    b += q.axes([0, 12, 24, 36, 48], [0, 0.2, 0.4, 0.6, 0.8, 1.0], "Mois depuis la randomisation", "Probabilité sans événement")
    ts = [i * 0.1 for i in range(481)]
    s0 = [surv(t, delayed=False) for t in ts]
    s1 = [surv(t) for t in ts]
    tin = [t for t in ts if t <= TAU]
    b.append(q.band(tin, s0[:len(tin)], s1[:len(tin)], ORANGE, 0.28))
    tout = [t for t in ts if t >= TAU]
    b.append(q.band(tout, s0[-len(tout):], s1[-len(tout):], GRID, 0.9))
    b.append(q.line(ts, s0, BLUE))
    b.append(q.line(ts, s1, ORANGE, dash="7 4"))
    b.append(f"<line x1='{q.X(TAU):.1f}' y1='{q.y0}' x2='{q.X(TAU):.1f}' y2='{q.y0 + q.h}' stroke='{MUTED}' stroke-dasharray='3 3'/>")
    b.append(txt(q.X(TAU) + 5, q.y0 + 12, "τ = 24 mois", 10.5))
    b.append(txt(q.X(9), q.Y(0.86), f"ΔRMST(24) = {fr(1.796)} mois (zone orange)", 10.5, TEXT))
    b.append(txt(q.X(36), q.Y(0.27), "ignoré par", 10, anchor="middle"))
    b.append(txt(q.X(36), q.Y(0.27) + 13, "RMST(24)", 10, anchor="middle"))
    b.append(txt(q.X(30), q.Y(surv(30)) - 12, "huile enrichie", 11, ORANGE, weight=600))
    b.append(txt(q.X(1), q.Y(0.08), "huile témoin", 11, BLUE, weight=600))
    b.append(txt(q.x0, 80, "Les courbes de survie se séparent tard", 12, TEXT, weight=600))
    return svg(760, 400, "Un effet différé : rien pendant 8 mois, puis un risque divisé par 2,5",
               "Essai simulé de prévention nutritionnelle — risque de base 0,05 événement par mois dans le bras témoin",
               "Rapport des risques en marche d’escalier et courbes de survie qui se séparent après 8 mois", b)


# ---------- 2. HR selon la durée de suivi ----------
def fig_hr_selon_suivi():
    cuts = list(range(8, 121, 2))
    hs = [cox_limit(c, grid_step=0.05) for c in cuts]
    pts = {12: 0.834, 24: 0.666, 48: 0.584, 120: 0.554}
    p = Plot(80, 80, 640, 270, (0, 125), (0.3, 1.08))
    b = p.axes([0, 20, 40, 60, 80, 100, 120], [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
               "Durée du suivi administratif (mois)", "Hazard ratio de Cox")
    for v, lab in ((1.0, "HR(t) avant 8 mois"), (0.4, "HR(t) après 8 mois")):
        b.append(f"<line x1='{p.x0}' y1='{p.Y(v):.1f}' x2='{p.x0 + p.w}' y2='{p.Y(v):.1f}' stroke='{MUTED}' stroke-width='1'/>")
        b.append(txt(p.x0 + p.w, p.Y(v) - 6, lab, 10.5, anchor="end"))
    b.append(p.line([6, 8] + cuts, [1.0, 1.0] + hs, BLUE))
    for c, v in pts.items():
        b.append(f"<circle cx='{p.X(c):.1f}' cy='{p.Y(v):.1f}' r='5.5' fill='{ORANGE}' stroke='{SURFACE}' stroke-width='2'/>")
        b.append(txt(p.X(c) + 8, p.Y(v) - 8, fr(v), 11, TEXT))
    b.append(f"<line x1='470' y1='150' x2='496' y2='150' stroke='{BLUE}' stroke-width='2.2'/>")
    b.append(txt(504, 154, "HR limite de Cox (théorie)", 11, TEXT))
    b.append(f"<circle cx='483' cy='172' r='5.5' fill='{ORANGE}' stroke='{SURFACE}' stroke-width='2'/>")
    b.append(txt(504, 176, "Cox ajusté, 20 000 patients par bras", 11, TEXT))
    return svg(760, 410, "Le même traitement, quatre hazard ratios",
               "Le HR de Cox dépend de la durée pendant laquelle on suit les patients, pas seulement du traitement",
               "Le hazard ratio de Cox passe de 0,83 à 12 mois de suivi à 0,55 à 120 mois", b), dict(zip(cuts, hs))


# ---------- 3. poids derrière le HR ----------
def fig_poids():
    p = Plot(80, 80, 640, 260, (0, 50), (0, 0.13))
    b = p.axes([0, 8, 12, 24, 36, 48], [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12], "Mois",
               "Densité des poids w(t)", yfmt=lambda v: fr(v, 2))
    b.insert(0, f"<rect x='{p.X(0):.1f}' y='{p.y0}' width='{p.X(CP) - p.X(0):.1f}' height='{p.h}' fill='{GRID}' fill-opacity='0.6'/>")
    b.append(txt(p.X(4), p.y0 + 16, "HR = 1", 10.5, TEXT, anchor="middle"))
    b.append(txt(p.X(9), p.y0 + 16, "HR = 0,4 →", 10.5, TEXT))
    shares = {}
    for k, c in enumerate((12, 24, 48)):
        ts, ws, late, hr = cox_weights(c)
        shares[c] = (late, hr)
        b.append(p.line(ts, ws, RAMP[k + 1], 2.2))
        b.append(txt(p.X(c) + 4, p.Y(ws[-1]) + 4, f"{c} mois", 10.5, RAMP[k + 1], weight=600))
    y = 130
    b.append(txt(430, y, "Poids sur la période où HR = 0,4", 11, TEXT, weight=600))
    for k, c in enumerate((12, 24, 48)):
        late, hr = shares[c]
        b.append(txt(430, y + 18 * (k + 1),
                     f"suivi {c} mois : {round(late * 100)} %  →  HR* = {fr(hr, 3)}", 11, RAMP[k + 1]))
    return svg(760, 400, "D’où vient le HR : une moyenne pondérée de HR(t)",
               "HR* ≈ 1 × (poids avant 8 mois) + 0,4 × (poids après) — et les poids dépendent du suivi",
               "Densité des poids de Cox pour trois durées de suivi", b), shares


# ---------- 4. ΔRMST selon τ ----------
def fig_delta_tau():
    taus = [1 + i * 0.5 for i in range(95)]
    ph = [rmst(t, delayed=False, hr_ph=0.65) - rmst(t, delayed=False) for t in taus]
    de = [rmst(t) - rmst(t, delayed=False) for t in taus]
    p = Plot(80, 80, 640, 260, (0, 50), (0, 7.5))
    b = p.axes([0, 12, 24, 36, 48], [0, 1, 2, 3, 4, 5, 6, 7], "τ (mois)", "ΔRMST (mois gagnés)", yfmt=lambda v: f"{v:g}")
    b.append(f"<line x1='{p.X(TAU):.1f}' y1='{p.y0}' x2='{p.X(TAU):.1f}' y2='{p.y0 + p.h}' stroke='{MUTED}' stroke-dasharray='3 3'/>")
    b.append(txt(p.X(TAU) - 5, p.y0 + 14, "τ = 24 (protocole)", 10.5, anchor="end"))
    b.append(p.line(taus, ph, BLUE))
    b.append(p.line(taus, de, ORANGE, dash="7 4"))
    for x in (12, 24, 36, 48):
        vals = {"ph": rmst(x, delayed=False, hr_ph=0.65) - rmst(x, delayed=False),
                "de": rmst(x) - rmst(x, delayed=False)}
        hi = max(vals, key=vals.get)
        for sc, v in vals.items():
            off = -8 if sc == hi else 15
            b.append(f"<circle cx='{p.X(x):.1f}' cy='{p.Y(v):.1f}' r='3.5' fill='{TEXT2}'/>")
            b.append(txt(p.X(x) + 5, p.Y(v) + off, fr(v), 10, TEXT2))
    b.append(txt(p.X(2), p.Y(6.9), "Risques proportionnels, HR 0,65", 11, BLUE, weight=600))
    b.append(txt(p.X(2), p.Y(6.4), "Effet différé, HR 1 → 0,4 à 8 mois", 11, ORANGE, weight=600))
    return svg(760, 400, "ΔRMST(τ) vrai : l’effet différé a besoin de temps",
               "Valeurs exactes (calcul analytique) pour les deux scénarios alternatifs du protocole",
               "Différence de RMST en fonction de tau pour un effet proportionnel et un effet différé", b)


# ---------- 5. τ choisi après coup ----------
def fig_tau_post_hoc():
    rows = [("τ = 24, fixé à l’avance", 0.051, 0.010, BLUE), ("meilleur des 9 τ, choisi après coup", 0.091, 0.013, ORANGE)]
    x0, w, xmax = 290, 400, 0.12
    b = []
    X = lambda v: x0 + v / xmax * w
    for v in (0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12):
        b.append(f"<line x1='{X(v):.1f}' y1='80' x2='{X(v):.1f}' y2='200' stroke='{GRID}'/>")
        b.append(txt(X(v), 218, f"{round(v * 100)} %", 11, anchor="middle"))
    for k, (lab, v, e, col) in enumerate(rows):
        y = 95 + k * 55
        b.append(f"<rect x='{x0}' y='{y}' width='{X(v) - x0:.1f}' height='32' fill='{col}'/>")
        b.append(txt(x0 - 10, y + 21, lab, 11.5, TEXT, anchor="end"))
        b.append(txt(X(v) + 8, y + 21, f"{fr(v * 100, 1)} % ± {fr(e * 100, 1)}", 11.5, TEXT))
    b.append(f"<line x1='{X(0.05):.1f}' y1='80' x2='{X(0.05):.1f}' y2='200' stroke='{TEXT}' stroke-width='1.2'/>")
    b.append(txt(X(0.05) + 4, 76, "5 % nominal", 10.5))
    b.append(txt(X(0.06), 245, "Erreur de type I sur 2 000 essais sans effet (± = intervalle Monte-Carlo à 95 %)", 11, anchor="middle"))
    return svg(760, 270, "Choisir τ après avoir vu les courbes : presque deux fois plus de faux positifs",
               "Aucun effet simulé ; l’analyste essaie τ = 12, 15, …, 36 mois et garde le plus significatif",
               "Erreur de type I de 5,1 % avec tau fixé contre 9,1 % avec tau choisi après coup", b)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "effet_differe.svg").write_text(fig_effet_differe())
    s, hs = fig_hr_selon_suivi()
    (OUT / "hr_selon_suivi.svg").write_text(s)
    print("HR* 12/24/48/120:", [round(hs.get(c, cox_limit(c, 0.05)), 3) for c in (12, 24, 48, 120)])
    s, shares = fig_poids()
    (OUT / "poids_cox.svg").write_text(s)
    print("parts tardives:", {c: (round(a, 3), round(b, 3)) for c, (a, b) in shares.items()})
    (OUT / "delta_rmst_tau.svg").write_text(fig_delta_tau())
    (OUT / "tau_post_hoc.svg").write_text(fig_tau_post_hoc())
