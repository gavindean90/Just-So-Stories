(() => {
  "use strict";

  const root = document.documentElement;
  const storage = {
    get(key) {
      try { return window.localStorage.getItem(key); } catch (_) { return null; }
    },
    set(key, value) {
      try { window.localStorage.setItem(key, value); } catch (_) { /* optional */ }
    },
    remove(key) {
      try { window.localStorage.removeItem(key); } catch (_) { /* optional */ }
    }
  };

  const savedTheme = storage.get("just-so-theme") || "auto";
  const savedScale = Number(storage.get("just-so-text-scale") || "1");
  const initialScale = Number.isFinite(savedScale)
    ? Math.min(1.3, Math.max(0.9, savedScale))
    : 1;
  root.dataset.theme = ["auto", "light", "dark"].includes(savedTheme) ? savedTheme : "auto";
  root.style.setProperty("--text-scale", String(initialScale));
  if (!Number.isFinite(savedScale)) {
    storage.remove("just-so-text-scale");
  }

  const themes = ["auto", "light", "dark"];
  const themeButton = document.querySelector('[data-action="toggle-theme"]');
  const updateThemeButton = () => {
    if (!themeButton) return;
    const currentIndex = themes.indexOf(root.dataset.theme);
    const current = currentIndex >= 0 ? themes[currentIndex] : "auto";
    const next = themes[(themes.indexOf(current) + 1) % themes.length];
    const label = `Theme: ${current[0].toUpperCase()}${current.slice(1)}. Switch to ${next[0].toUpperCase()}${next.slice(1)}.`;
    themeButton.setAttribute("aria-label", label);
    themeButton.title = label;
  };

  updateThemeButton();
  themeButton?.addEventListener("click", () => {
    const next = themes[(themes.indexOf(root.dataset.theme) + 1) % themes.length];
    root.dataset.theme = next;
    storage.set("just-so-theme", next);
    updateThemeButton();
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

  document.querySelector("[data-finish-reading]")?.addEventListener("click", () => {
    storage.remove("just-so-bookmark");
  });

  const storyLinks = Array.from(document.querySelectorAll(".story-list a[href]"));
  const randomStoryLink = document.querySelector("[data-random-story]");
  const contents = document.querySelector(".contents");
  const contentsHeading = contents?.querySelector("h2");
  if (randomStoryLink && contents && contentsHeading) {
    const headingRow = document.createElement("div");
    headingRow.className = "contents-heading-row";
    contents.insertBefore(headingRow, contentsHeading);
    headingRow.append(contentsHeading, randomStoryLink);
  }

  randomStoryLink?.addEventListener("click", (event) => {
    if (!storyLinks.length) return;
    const choice = storyLinks[Math.floor(Math.random() * storyLinks.length)];
    const href = choice.getAttribute("href");
    if (!href) return;
    event.preventDefault();
    window.location.assign(href);
  });

  const editionLinks = document.querySelector(".hero .edition-links");
  const siteFooter = document.querySelector(".site-footer");
  if (editionLinks && siteFooter) {
    siteFooter.append(editionLinks);
  }

  const continueLink = document.querySelector("[data-continue-reading]");
  if (continueLink) {
    const validStoryUrls = new Set(storyLinks.map((link) => link.getAttribute("href")));
    try {
      const bookmark = JSON.parse(storage.get("just-so-bookmark") || "null");
      if (bookmark?.url && bookmark?.title && validStoryUrls.has(bookmark.url)) {
        continueLink.href = bookmark.url;
        continueLink.textContent = `Continue reading: ${bookmark.title}`;
        continueLink.hidden = false;
      } else if (bookmark) {
        storage.remove("just-so-bookmark");
      }
    } catch (_) {
      storage.remove("just-so-bookmark");
    }
  }
})();
