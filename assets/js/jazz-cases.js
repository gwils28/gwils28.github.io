// Cases à cocher des notes jazz : Goldmark rend les listes « - [ ] » en
// cases désactivées. On les rend cliquables et on garde leur état dans le
// navigateur (localStorage, par note) : c'est un pense-bête personnel, rien
// ne part sur un serveur. La même note partage son état entre le tableau et
// sa page, la clé étant son adresse. La clé porte aussi les coches par défaut
// (« - [x] ») : si on les change dans la note, l'ancien état est ignoré.
document.querySelectorAll(".jz-papier").forEach((carte) => {
  const cases = carte.querySelectorAll('.jz-papier-contenu input[type="checkbox"]');
  if (!cases.length) return;
  const lien = carte.querySelector(".jz-papier-titre a");
  const defaut = [...cases].map((c) => (c.defaultChecked ? "x" : "-")).join("");
  const cle = "jz-cases:" + (lien ? lien.getAttribute("href") : location.pathname) + ":" + defaut;
  let etat = [];
  try { etat = JSON.parse(localStorage.getItem(cle)) || []; } catch (e) {}
  cases.forEach((c, i) => {
    c.disabled = false;
    if (typeof etat[i] === "boolean") c.checked = etat[i];
    c.addEventListener("change", () => {
      try { localStorage.setItem(cle, JSON.stringify([...cases].map((x) => x.checked))); } catch (e) {}
    });
  });
});
