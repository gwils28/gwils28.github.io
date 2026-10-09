// Bascule du CV entre expériences salariées, freelance et bénévoles (shortcode cv,
// section="parcours"). Onglets ARIA : clic, flèches gauche/droite, Début/Fin.
// La vue choisie est reportée dans l'adresse (?parcours=freelance) pour qu'un
// lien se partage. Sans JavaScript, les onglets restent cachés et les deux
// frises s'affichent l'une sous l'autre.
(() => {
  const bloc = document.querySelector(".cv-bascule");
  if (!bloc) return;
  const barre = bloc.querySelector(".cv-bascule-onglets");
  const onglets = [...barre.querySelectorAll('[role="tab"]')];
  const panneaux = [...bloc.querySelectorAll('[role="tabpanel"]')];

  const afficher = (vue, { focus = false, animer = true } = {}) => {
    if (!onglets.some((o) => o.dataset.vue === vue)) vue = onglets[0].dataset.vue;
    onglets.forEach((o) => {
      const actif = o.dataset.vue === vue;
      o.setAttribute("aria-selected", String(actif));
      o.tabIndex = actif ? 0 : -1;
      if (actif && focus) o.focus();
    });
    panneaux.forEach((p) => {
      const actif = p.dataset.vue === vue;
      p.hidden = !actif;
      p.classList.toggle("cv-bascule-entree", actif && animer);
    });
    bloc.dataset.vue = vue;
    bloc.style.setProperty("--cv-index", onglets.findIndex((o) => o.dataset.vue === vue));
    return vue;
  };

  const choisir = (vue, focus) => {
    vue = afficher(vue, { focus });
    const url = new URL(location.href);
    if (vue === onglets[0].dataset.vue) url.searchParams.delete("parcours");
    else url.searchParams.set("parcours", vue);
    history.replaceState(null, "", url);
  };

  onglets.forEach((o, i) => {
    o.addEventListener("click", () => choisir(o.dataset.vue, false));
    o.addEventListener("keydown", (e) => {
      const cible = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: onglets.length - 1 }[e.key];
      if (cible === undefined) return;
      e.preventDefault();
      choisir(onglets[(cible + onglets.length) % onglets.length].dataset.vue, true);
    });
  });

  afficher(new URLSearchParams(location.search).get("parcours") || "", { animer: false });
  bloc.classList.add("cv-bascule--active");
  barre.hidden = false;
})();
