// Forschungstermine — Detailansicht eines Termins (?id=)
const MONTHS = ["Januar","Februar","März","April","Mai","Juni","Juli","August",
  "September","Oktober","November","Dezember"];

init();

async function init(){
  const id = new URLSearchParams(location.search).get("id");
  const root = document.getElementById("detail");
  let events = [];
  try{
    const res = await fetch("data/events.json", {cache:"no-store"});
    events = (await res.json()).events || [];
  }catch(e){ events = []; }

  const ev = events.find(e => e.id === id);
  if(!ev){
    root.innerHTML = `
      <h1>Termin nicht gefunden</h1>
      <p class="detail-desc">Dieser Termin ist nicht (mehr) verfügbar. Vielleicht ist er bereits vorbei.</p>
      <a class="cta" href="index.html">Zur Terminübersicht</a>`;
    return;
  }
  document.title = ev.title + " — Forschungstermine";
  root.innerHTML = render(ev);
}

function fmtDate(iso){
  const [y,m,d] = iso.split("-").map(Number);
  return `${String(d).padStart(2,"0")}. ${MONTHS[m-1]} ${y}`;
}

function render(ev){
  const dateStr = ev.end && ev.end !== ev.start
    ? `${fmtDate(ev.start)} – ${fmtDate(ev.end)}`
    : fmtDate(ev.start);
  const place = ev.online ? "Online" : (ev.location || "—");
  const rows = [
    ["Institut", esc(ev.institute)],
    ["Datum", esc(dateStr)],
    ev.kind ? ["Art", esc(ev.kind)] : null,
    ["Ort", esc(place)],
  ].filter(Boolean);
  const meta = rows.map(([k,v]) => `<div><b>${k}</b><br>${v}</div>`).join("");
  const desc = ev.description
    ? `<p class="detail-desc">${esc(ev.description)}</p>`
    : `<p class="detail-desc">Details und Anmeldung auf der Original-Seite des Instituts.</p>`;
  return `
    <div class="eyebrow">${esc(ev.institute)}</div>
    <h1>${esc(ev.title)}</h1>
    <div class="ornament">❦</div>
    <div class="detail-meta">${meta}</div>
    ${desc}
    <a class="cta" href="${esc(ev.url)}" target="_blank" rel="noopener">Zur Original-Seite &amp; Anmeldung →</a>`;
}

function esc(s){
  return String(s ?? "").replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
