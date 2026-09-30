// Surcharge de themes/blowfish/assets/js/chart.js — concaténé après Chart.js
// et chargé en defer, donc après le script d'apparence : la classe « dark »
// est déjà posée quand ce fichier s'exécute.

function css(name) {
  return "rgb(" + getComputedStyle(document.documentElement).getPropertyValue(name) + ")";
}

// Exposé aux graphiques des pages ({{< chart >}}) pour choisir leurs couleurs :
//   borderColor: css(modeSombre ? "--color-primary-400" : "--color-primary-700")
var modeSombre = document.documentElement.classList.contains("dark");

// Réglages du thème, inchangés.
Chart.defaults.font.size = 14;
Chart.defaults.backgroundColor = css("--color-primary-300");
Chart.defaults.elements.point.borderColor = css("--color-primary-400");
Chart.defaults.elements.bar.borderColor = css("--color-primary-500");
Chart.defaults.elements.bar.borderWidth = 1;
Chart.defaults.elements.line.borderColor = css("--color-primary-400");
Chart.defaults.elements.arc.backgroundColor = css("--color-primary-200");
Chart.defaults.elements.arc.borderColor = css("--color-primary-500");
Chart.defaults.elements.arc.borderWidth = 1;

// Ajouts : la police du site, et un texte et une grille lisibles dans les
// deux modes (le gris par défaut de Chart.js disparaît sur fond sombre).
Chart.defaults.font.family = getComputedStyle(document.documentElement).getPropertyValue("--font-sans");
Chart.defaults.color = css(modeSombre ? "--color-neutral-300" : "--color-neutral-600");
Chart.defaults.borderColor = modeSombre ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.08)";
