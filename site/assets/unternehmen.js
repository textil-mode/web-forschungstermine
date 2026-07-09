// Forschungstermine — Formular „Für Unternehmen"
const form = document.getElementById("company-form");
const btn = document.getElementById("submit-btn");
const note = document.getElementById("form-msg");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  note.textContent = "";
  note.className = "fnote";

  const company = form.company.value.trim();
  const email = form.email.value.trim();
  if (!company || !email) {
    setNote("Bitte Firma und E-Mail ausfüllen.", "err");
    return;
  }

  btn.disabled = true;
  const label = btn.textContent;
  btn.textContent = "Sende …";

  try {
    const res = await fetch("api/companies", { method: "POST", body: new FormData(form) });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.ok) {
      form.reset();
      setNote("Vielen Dank! Ihre Anfrage ist eingegangen — wir melden uns.", "ok");
      btn.textContent = "Gesendet ✓";
      return;
    }
    setNote(data.error || "Senden fehlgeschlagen. Bitte später erneut versuchen.", "err");
  } catch (err) {
    setNote("Netzwerkfehler. Bitte später erneut versuchen.", "err");
  }
  btn.disabled = false;
  btn.textContent = label;
});

function setNote(text, kind) {
  note.textContent = text;
  note.className = "fnote " + kind;
}
