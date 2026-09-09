(() => {
  "use strict";

  const root = document.documentElement;
  const storage = {
    get(key) {
      try { return window.localStorage.getItem(key); } catch (_) { return null; }
    },
    set(key, value) {
      try { window.localStorage.setItem(key, value); } catch (_) { /* optional */ }
    }
  };

  const savedTheme = storage.get("just-so-theme") || "auto";
  const savedScale = Number(storage.get("just-so-text-scale") || "1");
  root.dataset.theme = ["auto", "light", "dark"].includes(savedTheme) ? savedTheme : "auto";
  root.style.setProperty("--text-scale", String(Math.min(1.3, Math.max(0.9, savedScale))));

  document.querySelector('[data-action="toggle-theme"]')?.addEventListener("click", () => {
    const themes = ["auto", "light", "dark"];
    const next = themes[(themes.indexOf(root.dataset.theme) + 1) % themes.length];
    root.dataset.theme = next;
    storage.set("just-so-theme", next);
  });

  const adjustText = (amount) => {
    const current = Number.parseFloat(getComputedStyle(root).getPropertyValue("--text-scale")) || 1;
    const next = Math.min(1.3, Math.max(0.9, Math.round((current + amount) * 10) / 10));
    root.style.setProperty("--text-scale", String(next));
    storage.set("just-so-text-scale", String(next));
  };

  document.querySelector('[data-action="decrease-text"]')?.addEventListener("click", () => adjustText(-0.1));
  document.querySelector('[data-action="increase-text"]')?.addEventListener("click", () => adjustText(0.1));

  const { storyId, storyTitle, storyUrl } = document.body.dataset;
  if (storyId && storyTitle && storyUrl) {
    storage.set("just-so-bookmark", JSON.stringify({ id: storyId, title: storyTitle, url: storyUrl }));
  }

  const continueLink = document.querySelector("[data-continue-reading]");
  if (continueLink) {
    try {
      const bookmark = JSON.parse(storage.get("just-so-bookmark") || "null");
      if (bookmark?.url && bookmark?.title) {
        continueLink.href = bookmark.url;
        continueLink.textContent = `Continue reading: ${bookmark.title}`;
        continueLink.hidden = false;
      }
    } catch (_) { /* optional */ }
  }
})();
