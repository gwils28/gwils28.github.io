// Filtre de l'onglet Notes : les boutons (layouts/jazz/list.html) masquent
// les notes d'un autre type. Le type choisi est reporté dans l'adresse
// (?genre=grille) pour qu'un lien filtré se partage. Sans JavaScript, la
// barre reste cachée et toutes les notes s'affichent.
(() => {
  const barre = document.querySelector(".jz-filtres");
  if (!barre) return;
  const boutons = barre.querySelectorAll(".jz-filtre");
  const notes = document.querySelectorAll(".jz-tableau .jz-papier");

  const filtrer = (genre) => {
    if (genre && !barre.querySelector(`[data-genre="${CSS.escape(genre)}"]`)) genre = "";
    boutons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.genre === genre)));
    notes.forEach((n) => { n.hidden = Boolean(genre) && n.dataset.genre !== genre; });
    return genre;
  };

  boutons.forEach((b) => b.addEventListener("click", () => {
    const genre = filtrer(b.dataset.genre);
    const url = new URL(location.href);
    if (genre) url.searchParams.set("genre", genre); else url.searchParams.delete("genre");
    history.replaceState(null, "", url);
  }));

  filtrer(new URLSearchParams(location.search).get("genre") || "");
  barre.hidden = false;
})();
