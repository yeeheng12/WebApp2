document.addEventListener("DOMContentLoaded", () => {
  const lazyImages = document.querySelectorAll("img[loading='lazy']");
  lazyImages.forEach((img) => {
    const src = img.dataset.src || img.src; // Use `data-src` if provided, fallback to `src`
    img.src = src;
  });
});
