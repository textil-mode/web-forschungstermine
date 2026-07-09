// Forschungstermine — Formular „Pitch & Connect"

// Innovationsfelder: 5 Themengruppen mit Auswahloptionen (aus dem Google-Formular).
const INNOVATION = [
  {
    title: "1. Materialinnovationen & Neue Fasern",
    opts: [
      "Materialinnovationen & Neue Fasern (allgemein)",
      "Bio-basierte & recycelbare Materialien: Fasern und Polymere aus nachwachsenden, alternativen oder recyclingfähigen Rohstoffen",
      "Neue Fasern, Polymere & Garntechnologien: Polymersynthese, Garnbildung, Filamenttechnologie und Hochleistungspolymere",
      "Nachhaltige Textilchemie & Funktionalisierung: Umweltfreundliche Färbung, Veredlung, Beschichtung und Textilverarbeitung",
      "Funktionale & smarte Textilien: Smarte Stoffe, Sensorik, Aktorik, Membranen und interaktive Fasersysteme",
      "Technische Textilien, Composites & Spezialanwendungen: Textile Lösungen für Leichtbau, Medizin, Schutz, Mobilität oder Industrie",
    ],
  },
  {
    title: "2. Digitale Produktentwicklung & Simulation",
    opts: [
      "Digitale Produktentwicklung & Simulation (allgemein)",
      "3D-Design & virtuelles Prototyping: Software für virtuelle Kollektionserstellung, Musterentwicklung und digitale Produktentwürfe",
      "Digitale Materialzwillinge & Simulation: Digitale Abbildung und Simulation von Stoffeigenschaften, Materialverhalten und Performance",
      "Virtuelle Anprobe, Fitting & Passformoptimierung: Lösungen für digitale Größenberatung, Passformprüfung und virtuelle Produktdarstellung",
      "Trend-, Daten- & KI-Analyse: KI-gestützte Prognosen und Analysen für Design, Sortiment, Nachfrage oder Produktentwicklung",
      "Sensorbasierte Produktvalidierung: Nutzung von Messdaten, Echtzeitdaten und Sensorlösungen zur Prüfung und Optimierung textiler Produkte",
    ],
  },
  {
    title: "3. Vernetzte Produktion & Automatisierung",
    opts: [
      "Vernetzte Produktion & Automatisierung (allgemein)",
      "Robotik & automatisierte Handhabung: Automatisierung von Nähen, Greifen, Legen, Schneiden oder anderen Handlingprozessen",
      "Flexible & modulare Produktionstechnologien: Modulare Maschinen, anpassbare Anlagen, Kleinstserien und On-Demand-Fertigung",
      "Digitale Produktionszwillinge & Assistenzsysteme: Digitale Abbilder von Maschinen oder Prozessen sowie Unterstützung für Bedienung, Wartung und Prozessführung",
      "KI-Qualitätskontrolle, Materialidentifizierung & Echtheitsprüfung: Optische Inspektion, Fehlererkennung, Materialprüfung und Authentifizierung in Echtzeit",
      "Maschinenvernetzung, IoT & Vorausschauende Wartung: Monitoring, Prozessdatenerfassung, Maschinenkommunikation und vorausschauende Wartung",
    ],
  },
  {
    title: "4. Kreislaufwirtschaft & Textilrecycling",
    opts: [
      "Kreislaufwirtschaft & Textilrecycling (allgemein)",
      "Recycling-Technologien: Mechanische, chemische oder thermische Verfahren zur Wiederverwertung textiler Materialien",
      "Sortier-, Trenn- & Materialerkennungssysteme: Automatisierte Erkennung, Sortierung und Trennung von Materialzusammensetzungen",
      "Recycling von Hochleistungsfasern & Spezialmaterialien: Verfahren für technische Fasern, Composites, rCF, rHL oder andere Spezialmaterialien",
      "Rücknahme-, Wiederverkaufs- & Leihsysteme: Lösungen für Rückgabe, Reparatur, Second-Life, Resale, Vermietung oder Sharing",
      "Upcycling & Design for Circularity: Konzepte zur Abfallvermeidung, Wiederverwendung und kreislauffähigen Produktgestaltung",
      "LCA, EPD & Nachhaltigkeitsbewertung: Bewertung von Umweltwirkungen, Lebenszyklusdaten und Nachhaltigkeit von Produkten oder Prozessen",
    ],
  },
  {
    title: "5. Lieferkette & Transparenz",
    opts: [
      "Lieferkette & Transparenz (allgemein)",
      "Rückverfolgbarkeit & Materialnachweise: Traceability, Faseridentität, Herkunftsnachweise und Materialauthentifizierung",
      "Digitaler Produktpass & Produktdaten: Strukturierter Datenaustausch über Materialien, Produkte und Lebenszyklusinformationen",
      "Compliance, Audit & Zertifizierung: Überwachung von Sozial- und Umweltstandards, Prüfeinreichungen, Audits und Nachweisführung",
      "Nachhaltigkeitsreporting & ESG-Daten: Erfassung und Aufbereitung von Nachhaltigkeits-, LCA-, EPD-, ESG- oder CSRD-relevanten Daten",
      "Intelligente Logistik & Beschaffungstransparenz: Transparenz in Einkauf, Beschaffung, Transport, Lagerung und Lieferkettenprozessen",
    ],
  },
];

const VERBAENDE = [
  "ICH BIN KEIN MITGLIED IN EINEM TEXTILVERBAND",
  "Verband der Nordwestdeutschen Textil- und Bekleidungsindustrie e. V.",
  "Südwesttextil e. V.",
  "Verband der Bayerischen Textil- und Bekleidungsindustrie e. V.",
  "Verband der Rheinischen Textil- und Bekleidungsindustrie e. V.",
  "Verband der Textil- und Bekleidungsindustrie Hessen, Rheinland-Pfalz und Saarland e. V.",
  "Verband der Nord-Ostdeutschen Textil- und Bekleidungsindustrie e. V.",
  "GermanFashion Modeverband Deutschland e. V.",
  "HDS/L Bundesverband der Schuh- und Lederwarenindustrie e. V.",
  "Industrieverband Veredlung – Garne – Gewebe – Technische Textilien e. V.",
  "Verband der Deutschen Heimtextilien-Industrie e. V.",
  "Gesamtverband der deutschen Maschen-Industrie – Gesamtmasche e. V.",
  "Fachvereinigung Wirkerei-Strickerei Albstadt e. V.",
  "Arbeitgeberverband der Textilindustrie Düren, Jülich, Euskirchen und Umgebung e. V.",
  "Verband der Textil- und Bekleidungsindustrie Berlin und Brandenburg e. V.",
  "Deutscher Textilreinigungs-Verband e. V.",
  "Gesamtvereinigung Bekleidungsindustrie Niedersachsen und Bremen e. V.",
  "Industrieverband Technische Textilien – Rolladen – Sonnenschutz e. V.",
  "Verein Deutscher Kammgarnspinner",
  "Fachverband Matratzen-Industrie e. V.",
  "Deutscher Pelz- Groß- und Außenhandelsverband e. V.",
  "BVMed – Bundesverband Medizintechnologie e. V.",
  "Branchenverband Plauener Spitze und Stickereien e. V.",
  "Initiative Handarbeit e. V.",
  "Industrieverband Textil-Service – intex e. V.",
];

const form = document.getElementById("company-form");
const btn = document.getElementById("submit-btn");
const note = document.getElementById("form-msg");

renderInnovation();
renderVerbaende();

function renderInnovation() {
  const root = document.getElementById("innovation");
  root.innerHTML = INNOVATION.map(g => `
    <fieldset class="checks">
      <legend>${esc(g.title)}</legend>
      ${g.opts.map(o => {
        const [head, ...rest] = o.split(": ");
        const desc = rest.join(": ");
        return `<label class="opt"><input type="checkbox" name="innovation" value="${esc(o)}">
          <span><b>${esc(head)}</b>${desc ? " — " + esc(desc) : ""}</span></label>`;
      }).join("")}
    </fieldset>`).join("");
}

function renderVerbaende() {
  const sel = document.getElementById("association");
  sel.innerHTML = VERBAENDE.map((v, i) =>
    `<option value="${i === 0 ? "" : esc(v)}"${i === 0 ? " selected" : ""}>${esc(v)}</option>`).join("");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setNote("", "");

  // Pflichtfelder prüfen (inkl. Radiogruppen)
  const required = ["company", "first_name", "last_name", "email", "website", "company_desc", "challenge_desc"];
  for (const name of required) {
    if (!form[name].value.trim()) { setNote("Bitte alle Pflichtfelder (*) ausfüllen.", "err"); form[name].focus(); return; }
  }
  for (const name of ["request_type", "anonymous", "newsletter"]) {
    if (!form.querySelector(`input[name="${name}"]:checked`)) {
      setNote("Bitte alle Pflichtfelder (*) ausfüllen.", "err"); return;
    }
  }

  btn.disabled = true;
  const label = btn.innerHTML;
  btn.textContent = "Sende …";

  try {
    const res = await fetch("api/companies", { method: "POST", body: new FormData(form) });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.ok) {
      form.reset();
      renderVerbaende();
      setNote("Vielen Dank! Wir haben Ihr Interesse vermerkt und melden uns nach der Auswertung.", "ok");
      btn.textContent = "Gesendet ✓";
      return;
    }
    setNote(data.error || "Senden fehlgeschlagen. Bitte später erneut versuchen.", "err");
  } catch (err) {
    setNote("Netzwerkfehler. Bitte später erneut versuchen.", "err");
  }
  btn.disabled = false;
  btn.innerHTML = label;
});

function setNote(text, kind) {
  note.textContent = text;
  note.className = "fnote " + kind;
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
