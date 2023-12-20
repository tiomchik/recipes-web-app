function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

// Change theme
let htmlTag = document.documentElement;
let recipes_theme = getCookie("recipes_theme");

if (recipes_theme != undefined) {
  htmlTag.setAttribute("data-bs-theme", recipes_theme);
}

document.getElementById("theme").addEventListener("click", () => {
  if (htmlTag.getAttribute("data-bs-theme") == "dark") {
    htmlTag.setAttribute("data-bs-theme", "light");
    document.cookie = encodeURIComponent("recipes_theme") + "=" + encodeURIComponent("light") + "; path=/;"
  }
  else {
    htmlTag.setAttribute("data-bs-theme", "dark");
    document.cookie = encodeURIComponent("recipes_theme") + "=" + encodeURIComponent("dark") + "; path=/;"
  }
});

function moveObject(obj) {
  let top = Math.random() * window.innerHeight;
  let right = Math.random() * window.innerWidth;
  Object.assign(obj, {
    style: `
    position: absolute;
    top: ${top}px;
    right: ${right}px;
    `
  })
}

// Moving delete button at click 3 times
let deleteButton = document.getElementById("offcanvasDeleteButton");

let i = 0;
if (deleteButton != null) {
  deleteButton.addEventListener("click", () => {
    if (i < 3) {
      moveObject(deleteButton);
      i++;
    }
    else {
      let dataHref = deleteButton.getAttribute("data-href");
      deleteButton.setAttribute("href", dataHref);
    };
  })
};