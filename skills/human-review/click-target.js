export function navigationHref(target) {
  const link = target?.closest?.("a[href]");
  if (link) return link.getAttribute("href") || "";
  const control = target?.closest?.("[data-href]");
  return control ? control.getAttribute("data-href") || "" : "";
}
