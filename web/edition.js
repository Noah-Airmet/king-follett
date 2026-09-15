// King Follett Discourse — the only script on the site.
//
// Everything here is an upgrade to something that already works. The witness
// selector, the variant marks and the manuscript view are checkboxes the
// stylesheet reads, so they work with this file blocked; the apparatus is
// reachable by ordinary links; the rail is a list of anchors. What this adds
// is the reader's configuration in the URL, the slip, the rail's sense of
// where you are, a keyboard, and a citation attached to anything you copy.
//
// No dependencies, no build step, no motion.

const SIGLA = ["B", "W", "R", "C", "T"];
const boxes = new Map(SIGLA.map((s) => [s, document.getElementById(`w-${s}`)]));
const variantsBox = document.getElementById("show-variants");
const diplomaticBox = document.getElementById("show-diplomatic");

// --------------------------------------------------------------------------
// state in the URL
// --------------------------------------------------------------------------

// The address bar is the app's only persistence. A link to this edition should
// carry what the sender was looking at — which witnesses, marked or clean,
// manuscript or reading — because that configuration is usually the point of
// sending it. Nothing is stored in the browser.

function readUrl() {
  const params = new URLSearchParams(location.search);
  if (params.has("w")) {
    const lit = params.get("w").toUpperCase();
    for (const [siglum, box] of boxes) {
      if (box) box.checked = lit.includes(siglum);
    }
  }
  if (params.has("v") && variantsBox) variantsBox.checked = params.get("v") !== "0";
  if (params.has("m") && diplomaticBox) diplomaticBox.checked = params.get("m") === "1";
}

function writeUrl() {
  const lit = SIGLA.filter((s) => boxes.get(s)?.checked).join("");
  const params = new URLSearchParams();
  if (lit !== "B") params.set("w", lit);
  if (variantsBox && !variantsBox.checked) params.set("v", "0");
  if (diplomaticBox && diplomaticBox.checked) params.set("m", "1");
  const query = params.toString();
  history.replaceState(null, "", `${location.pathname}${query ? "?" + query : ""}${location.hash}`);
}

if (boxes.size) {
  readUrl();
  for (const box of [...boxes.values(), variantsBox, diplomaticBox]) {
    box?.addEventListener("change", writeUrl);
  }
}

// Restoring the configuration above changes which columns exist, which moves
// every section on the page. A browser that had already honoured the incoming
// fragment would now be pointing at the wrong one, and in a document this long
// it does not reliably honour it at all — so the fragment is applied here,
// after the layout it has to be measured against.
function gotoHash() {
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;
  const target = document.getElementById(id);
  if (!target) return;
  const behavior = matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "instant";
  target.scrollIntoView({ block: "start", behavior });
}

if (location.hash) {
  // Fonts land after first paint and reflow the measure; scroll once now so
  // the reader is not left at the top, and once after they settle.
  gotoHash();
  document.fonts?.ready.then(gotoHash);
}

window.addEventListener("hashchange", gotoHash);

// --------------------------------------------------------------------------
// the slip
// --------------------------------------------------------------------------

// One card, reused. Its content is cloned out of the page itself — the
// apparatus entry for a lemma is already in the section's own list, and a
// footnote is already in the witness's note list — so the slip ships no data
// of its own and can never disagree with what the page says.

let slip = null;
let openFor = null;
let hideTimer = null;

function ensureSlip() {
  if (slip) return slip;
  slip = document.createElement("aside");
  slip.className = "slip";
  slip.setAttribute("role", "tooltip");
  slip.hidden = true;
  slip.addEventListener("mouseenter", () => clearTimeout(hideTimer));
  slip.addEventListener("mouseleave", scheduleHide);
  document.body.appendChild(slip);
  return slip;
}

function scheduleHide() {
  clearTimeout(hideTimer);
  hideTimer = setTimeout(hideSlip, 220);
}

function hideSlip() {
  if (slip) slip.hidden = true;
  openFor = null;
}

function showSlip(anchor, source) {
  if (!source) return;
  const element = ensureSlip();
  const clone = source.cloneNode(true);
  clone.removeAttribute("id");
  for (const node of clone.querySelectorAll("[id]")) node.removeAttribute("id");
  element.replaceChildren(clone);
  element.hidden = false;
  openFor = anchor;

  // Positioned in document coordinates, flipped above the anchor when there is
  // no room below and clamped to the viewport's gutters either way.
  const rect = anchor.getBoundingClientRect();
  const width = element.offsetWidth;
  const height = element.offsetHeight;
  const margin = 12;
  let left = window.scrollX + rect.left;
  left = Math.min(left, window.scrollX + document.documentElement.clientWidth - width - margin);
  left = Math.max(left, window.scrollX + margin);
  // Flipped above the anchor when there is no room below, but never up under
  // the sticky masthead, which would put the card over the site's own nav.
  const masthead = document.querySelector(".masthead")?.offsetHeight ?? 0;
  const below = rect.bottom + height + margin < window.innerHeight;
  const top = window.scrollY + (below ? rect.bottom + 6 : rect.top - height - 6);
  element.style.left = `${left}px`;
  element.style.top = `${Math.max(top, window.scrollY + masthead + margin)}px`;
}

function sourceFor(anchor) {
  const variant = anchor.dataset.variant;
  if (variant) return document.getElementById(variant);
  const note = anchor.dataset.note;
  if (note) return document.getElementById(`n${note.slice(1)}`);
  return null;
}

// Hover and keyboard focus open the slip. On a touch screen the first tap
// opens it and the second follows the link, so nothing is unreachable.
document.addEventListener("pointerover", (event) => {
  const anchor = event.target.closest?.(".lemma, .fn");
  if (!anchor || anchor === openFor) return;
  if (anchor.matches(".lemma") && variantsBox && !variantsBox.checked) return;
  clearTimeout(hideTimer);
  showSlip(anchor, sourceFor(anchor));
});

document.addEventListener("pointerout", (event) => {
  if (event.target.closest?.(".lemma, .fn")) scheduleHide();
});

document.addEventListener("focusin", (event) => {
  const anchor = event.target.closest?.(".lemma, .fn");
  if (anchor) showSlip(anchor, sourceFor(anchor));
});

document.addEventListener("click", (event) => {
  const anchor = event.target.closest?.(".lemma, .fn");
  if (!anchor) {
    if (!event.target.closest?.(".slip")) hideSlip();
    return;
  }
  if (window.matchMedia("(hover: none)").matches && openFor !== anchor) {
    event.preventDefault();
    showSlip(anchor, sourceFor(anchor));
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") hideSlip();
});

// --------------------------------------------------------------------------
// the rail knows where you are
// --------------------------------------------------------------------------

const rows = new Map(
  [...document.querySelectorAll(".rail-row")].map((g) => [g.dataset.section, g])
);
const sections = [...document.querySelectorAll(".spine > .sec")];

if (rows.size && sections.length && "IntersectionObserver" in window) {
  let current = null;
  const seen = new Set();
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) seen.add(entry.target.id);
        else seen.delete(entry.target.id);
      }
      const next = sections.find((s) => seen.has(s.id))?.id ?? current;
      if (next === current) return;
      rows.get(current)?.classList.remove("on");
      rows.get(next)?.classList.add("on");
      current = next;
    },
    { rootMargin: "-20% 0px -60% 0px" }
  );
  for (const section of sections) observer.observe(section);
}

// --------------------------------------------------------------------------
// keyboard
// --------------------------------------------------------------------------

const KEYS = { 1: "B", 2: "W", 3: "R", 4: "C", 5: "T" };

document.addEventListener("keydown", (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey) return;
  if (event.target.matches("input, textarea, select, [contenteditable]")) return;

  if (KEYS[event.key]) {
    const box = boxes.get(KEYS[event.key]);
    if (box) {
      box.checked = !box.checked;
      writeUrl();
      event.preventDefault();
    }
    return;
  }
  if (event.key === "v" && variantsBox) {
    variantsBox.checked = !variantsBox.checked;
    writeUrl();
    return;
  }
  if (event.key === "m" && diplomaticBox) {
    diplomaticBox.checked = !diplomaticBox.checked;
    writeUrl();
    return;
  }
  if ((event.key === "j" || event.key === "k") && sections.length) {
    const top = window.scrollY + 120;
    const index = sections.findIndex((s) => s.offsetTop > top);
    const here = index === -1 ? sections.length - 1 : Math.max(index - 1, 0);
    const target = sections[event.key === "j" ? Math.min(here + 1, sections.length - 1) : Math.max(here - 1, 0)];
    target?.scrollIntoView({ block: "start" });
    history.replaceState(null, "", `#${target.id}`);
  }
});

// --------------------------------------------------------------------------
// copy carries the witness
// --------------------------------------------------------------------------

// The reason this edition exists is that quotations of this sermon circulate
// without saying which of five texts they came from. Anything copied out of a
// witness column leaves with its siglum, its section and its manuscript page.

document.addEventListener("copy", (event) => {
  const selection = document.getSelection();
  if (!selection || selection.isCollapsed) return;
  const node = selection.anchorNode;
  const host = (node?.nodeType === 1 ? node : node?.parentElement)?.closest("[data-siglum]");
  if (!host) return;

  const siglum = host.dataset.siglum;
  const section = host.closest(".sec");
  const page = host.querySelector(".wit-page")?.textContent?.trim();
  const label = section?.querySelector(".sec-head h2")?.textContent?.trim();
  const url = `${location.origin}/#${section?.id ?? ""}`;

  const cite = [
    `— King Follett Discourse, 7 April 1844, ${siglum}`,
    label ? `${section.id} ${label}` : section?.id,
    page,
    url,
  ]
    .filter(Boolean)
    .join(", ");

  event.clipboardData.setData("text/plain", `${selection.toString()}\n\n${cite}`);
  event.preventDefault();
});
