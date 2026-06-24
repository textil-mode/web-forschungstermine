// Forschungstermine — Liste + Kalender aus data/events.json
const MONTHS = ["Januar","Februar","März","April","Mai","Juni","Juli","August",
  "September","Oktober","November","Dezember"];
const MONTHS_SHORT = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"];
const DOW = ["Mo","Di","Mi","Do","Fr","Sa","So"];

let EVENTS = [];

init();

async function init(){
  try{
    const res = await fetch("data/events.json", {cache:"no-store"});
    const data = await res.json();
    EVENTS = (data.events || []);
    const ts = data.generated_at ? new Date(data.generated_at) : null;
    if(ts) document.getElementById("updated").textContent =
      "Zuletzt aktualisiert am " + ts.toLocaleDateString("de-DE",
        {day:"2-digit",month:"long",year:"numeric"});
  }catch(e){
    EVENTS = [];
  }
  if(EVENTS.length === 0){
    document.getElementById("empty").classList.remove("hidden");
  }
  renderList();
  renderCalendar();
  wireToggle();
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

function ymKey(iso){ return iso.slice(0,7); }       // "2026-09"
function parseISO(iso){
  const [y,m,d] = iso.split("-").map(Number);
  return {y, m, d};                                  // m: 1-12
}

function renderList(){
  const root = document.getElementById("view-list");
  root.innerHTML = "";
  let lastYM = null;
  for(const ev of EVENTS){
    const ym = ymKey(ev.start);
    if(ym !== lastYM){
      lastYM = ym;
      const {y,m} = parseISO(ev.start);
      const lbl = document.createElement("div");
      lbl_set(lbl, MONTHS[m-1] + " " + y);
      root.appendChild(lbl);
    }
    root.appendChild(eventRow(ev));
  }
}

function lbl_set(el, text){ el.className = "monthlabel"; el.textContent = text; }

function eventRow(ev){
  const {d,m} = parseISO(ev.start);
  const a = document.createElement("a");
  a.className = "event";
  a.href = "event.html?id=" + encodeURIComponent(ev.id);
  const place = ev.online ? "online" : (ev.location || "");
  const kind = ev.kind ? `<span class="kind">${esc(ev.kind)}</span>` : "";
  const sep = (kind && place) ? " · " : "";
  a.innerHTML = `
    <div class="date"><div class="d">${String(d).padStart(2,"0")}</div><div class="m">${MONTHS_SHORT[m-1]}</div></div>
    <div>
      <div class="ev-title">${esc(ev.title)}</div>
      <div class="ev-meta"><span class="inst">${esc(ev.institute)}</span>${kind}${sep}${esc(place)}</div>
    </div>
    <div class="arrow">→</div>`;
  return a;
}

function renderCalendar(){
  const root = document.getElementById("view-cal");
  root.innerHTML = "";
  // Gruppiere Events nach Monat
  const byMonth = new Map();
  for(const ev of EVENTS){
    const k = ymKey(ev.start);
    if(!byMonth.has(k)) byMonth.set(k, []);
    byMonth.get(k).push(ev);
  }
  for(const [k, evs] of byMonth){
    root.appendChild(calMonth(k, evs));
  }
}

function calMonth(ymk, evs){
  const [y, m] = ymk.split("-").map(Number);      // m: 1-12
  const wrap = document.createElement("div");
  wrap.className = "cal-month";

  const lbl = document.createElement("div");
  lbl_set(lbl, MONTHS[m-1] + " " + y);
  lbl.style.textAlign = "left";
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

  const firstDow = (new Date(y, m-1, 1).getDay() + 6) % 7;  // Mo=0
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
