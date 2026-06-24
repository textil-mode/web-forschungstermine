// Forschungstermine — Liste + Kalender mit Filter (Innovationsfelder + Textsuche)
const MONTHS = ["Januar","Februar","März","April","Mai","Juni","Juli","August",
  "September","Oktober","November","Dezember"];
const MONTHS_SHORT = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"];
const DOW = ["Mo","Di","Mi","Do","Fr","Sa","So"];

let EVENTS = [];
let FIELDS = [];
const FIELD_LABEL = {};
const selectedFields = new Set();
let searchTerm = "";

init();

async function init(){
  try{
    const res = await fetch("data/events.json", {cache:"no-store"});
    const data = await res.json();
    EVENTS = data.events || [];
    FIELDS = data.fields || [];
    FIELDS.forEach(f => FIELD_LABEL[f.key] = f.label);
    const ts = data.generated_at ? new Date(data.generated_at) : null;
    if(ts) document.getElementById("updated").textContent =
      "Zuletzt aktualisiert am " + ts.toLocaleDateString("de-DE",
        {day:"2-digit",month:"long",year:"numeric"});
  }catch(e){
    EVENTS = [];
  }
  renderChips();
  wireControls();
  wireToggle();
  update();
}

function wireToggle(){
  const bL = document.getElementById("btn-list");
  const bC = document.getElementById("btn-cal");
  const vL = document.getElementById("view-list");
  const vC = document.getElementById("view-cal");
  bL.addEventListener("click", ()=>{
    bL.classList.add("active"); bC.classList.remove("active");
    vL.classList.remove("hidden"); vC.classList.add("hidden");
  });
  bC.addEventListener("click", ()=>{
    bC.classList.add("active"); bL.classList.remove("active");
    vC.classList.remove("hidden"); vL.classList.add("hidden");
  });
}

function renderChips(){
  const root = document.getElementById("chips");
  root.innerHTML = "";
  for(const f of FIELDS){
    const b = document.createElement("button");
    b.className = "chip";
    b.type = "button";
    b.textContent = f.label;
    b.dataset.key = f.key;
    b.addEventListener("click", ()=>{
      if(selectedFields.has(f.key)){ selectedFields.delete(f.key); b.classList.remove("active"); }
      else { selectedFields.add(f.key); b.classList.add("active"); }
      update();
    });
    root.appendChild(b);
  }
}

function wireControls(){
  const s = document.getElementById("search");
  s.addEventListener("input", ()=>{ searchTerm = s.value.toLowerCase().trim(); update(); });
}

function applyFilters(){
  return EVENTS.filter(ev=>{
    const fields = ev.fields || [];
    const inField = selectedFields.size === 0 || fields.some(k => selectedFields.has(k));
    const hay = [ev.title, ev.institute, ev.description, ev.kind, ev.location]
      .filter(Boolean).join(" ").toLowerCase();
    const inText = !searchTerm || hay.includes(searchTerm);
    return inField && inText;
  });
}

function update(){
  const filtered = applyFilters();
  renderList(filtered);
  renderCalendar(filtered);
  document.getElementById("empty").classList.toggle("hidden", filtered.length !== 0);
  const rc = document.getElementById("resultCount");
  const total = EVENTS.length;
  rc.textContent = filtered.length === total
    ? `${total} Termine`
    : `${filtered.length} von ${total} Terminen`;
}

function ymKey(iso){ return iso.slice(0,7); }
function parseISO(iso){ const [y,m,d] = iso.split("-").map(Number); return {y, m, d}; }

function renderList(events){
  const root = document.getElementById("view-list");
  root.innerHTML = "";
  let lastYM = null;
  for(const ev of events){
    const ym = ymKey(ev.start);
    if(ym !== lastYM){
      lastYM = ym;
      const {y,m} = parseISO(ev.start);
      const lbl = document.createElement("div");
      lbl.className = "monthlabel"; lbl.textContent = MONTHS[m-1] + " " + y;
      root.appendChild(lbl);
    }
    root.appendChild(eventRow(ev));
  }
}

function eventRow(ev){
  const {d,m} = parseISO(ev.start);
  const a = document.createElement("a");
  a.className = "event";
  a.href = "event.html?id=" + encodeURIComponent(ev.id);
  const place = ev.online ? "online" : (ev.location || "");
  const kind = ev.kind ? `<span class="kind">${esc(ev.kind)}</span>` : "";
  const sep = (kind && place) ? " · " : "";
  const tags = (ev.fields || []).map(k =>
    `<span class="ftag">${esc(FIELD_LABEL[k] || k)}</span>`).join("");
  a.innerHTML = `
    <div class="date"><div class="d">${String(d).padStart(2,"0")}</div><div class="m">${MONTHS_SHORT[m-1]}</div></div>
    <div>
      <div class="ev-title">${esc(ev.title)}</div>
      <div class="ev-meta"><span class="inst">${esc(ev.institute)}</span>${kind}${sep}${esc(place)}</div>
      ${tags ? `<div class="ev-fields">${tags}</div>` : ""}
    </div>
    <div class="arrow">→</div>`;
  return a;
}

function renderCalendar(events){
  const root = document.getElementById("view-cal");
  root.innerHTML = "";
  const byMonth = new Map();
  for(const ev of events){
    const k = ymKey(ev.start);
    if(!byMonth.has(k)) byMonth.set(k, []);
    byMonth.get(k).push(ev);
  }
  for(const [k, evs] of byMonth){
    root.appendChild(calMonth(k, evs));
  }
}

function calMonth(ymk, evs){
  const [y, m] = ymk.split("-").map(Number);
  const wrap = document.createElement("div");
  wrap.className = "cal-month";

  const lbl = document.createElement("div");
  lbl.className = "monthlabel"; lbl.textContent = MONTHS[m-1] + " " + y;
  wrap.appendChild(lbl);

  const grid = document.createElement("div");
  grid.className = "cal-grid";
  for(const dow of DOW){
    const h = document.createElement("div");
    h.className = "cal-dow"; h.textContent = dow;
    grid.appendChild(h);
  }

  const evByDay = new Map();
  for(const ev of evs){
    const day = parseISO(ev.start).d;
    if(!evByDay.has(day)) evByDay.set(day, []);
    evByDay.get(day).push(ev);
  }

  const firstDow = (new Date(y, m-1, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(y, m, 0).getDate();
  for(let i=0;i<firstDow;i++){
    const c = document.createElement("div");
    c.className = "cal-cell empty";
    grid.appendChild(c);
  }
  for(let day=1; day<=daysInMonth; day++){
    const c = document.createElement("div");
    c.className = "cal-cell";
    const dayEvs = evByDay.get(day) || [];
    if(dayEvs.length) c.classList.add("has");
    let html = `<div class="cal-day">${day}</div>`;
    for(const ev of dayEvs){
      html += `<a class="cal-ev" title="${esc(ev.title)} · ${esc(ev.institute)}" href="event.html?id=${encodeURIComponent(ev.id)}">${esc(ev.title)}</a>`;
    }
    c.innerHTML = html;
    grid.appendChild(c);
  }
  wrap.appendChild(grid);
  return wrap;
}

function esc(s){
  return String(s ?? "").replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
