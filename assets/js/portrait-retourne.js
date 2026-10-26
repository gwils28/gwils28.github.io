// Portrait chinois (page À propos) : un clic sur une carte qui a un
// « pourquoi » la retourne, un second clic la remet côté recto. Une seule
// carte retournée à la fois : en retourner une remet les autres au recto.
// La classe portrait--retournable affiche l'indice « pourquoi ? ».
document.querySelectorAll(".portrait").forEach((portrait) => {
  portrait.classList.add("portrait--retournable");
  portrait.addEventListener("click", (e) => {
    const carte = e.target.closest("button.portrait-carte");
    if (!carte) return;
    const retournee = carte.getAttribute("aria-pressed") === "true";
    portrait.querySelectorAll('button.portrait-carte[aria-pressed="true"]')
      .forEach((autre) => autre.setAttribute("aria-pressed", "false"));
    carte.setAttribute("aria-pressed", String(!retournee));
  });
});
