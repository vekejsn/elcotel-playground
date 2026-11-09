"use strict";
const $ = id => document.getElementById(id);
let original = null, opened = null, filename = "edited.C94";
let changes = {}, shutdownChanges = {};
let savedSignature = "";
function signature() { return JSON.stringify([changes, shutdownChanges, $("description").value]); }
function dirty() { return opened && signature() !== savedSignature; }

function text(tag, content, className) {
  const el = document.createElement(tag);
  el.textContent = content;
  if (className) el.className = className;
  return el;
}
function message(content, error = false) {
  $("message").textContent = content;
  $("message").classList.toggle("error", error);
}
function same(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function updateCount() {
  const total = Object.keys(changes).length + Object.keys(shutdownChanges).length +
    Number($("description").value !== opened.description);
  $("count").textContent = `${total} changed setting(s). The original file is unchanged.`;
}
function record(setting, value, element) {
  if (same(value, setting.value)) delete changes[setting.id];
  else changes[setting.id] = value;
  element.classList.toggle("changed", Object.hasOwn(changes, setting.id));
  updateCount();
}
function display(setting) {
  if (setting.kind === "program") return "Inline macro program (read-only)";
  if (setting.kind === "boolean") return setting.boolean_labels?.[setting.value ? "1" : "0"] || (setting.value ? "ON" : "OFF");
  if (setting.value === null) return "Cannot decode current value";
  return String(setting.value);
}
function control(setting, row) {
  const area = document.createElement("div");
  area.className = "value";
  if (setting.read_only) {
    area.append(text("span", display(setting), "readonly-value"));
    return area;
  }
  const value = Object.hasOwn(changes, setting.id) ? changes[setting.id] : setting.value;
  let input;
  if (setting.kind === "choice") {
    input = document.createElement("select");
    const choices = { ...setting.choices };
    if (!Object.hasOwn(choices, String(value))) choices[String(value)] = "Current value (not a confirmed choice)";
    for (const [key, label] of Object.entries(choices)) {
      const option = text("option", `${label} (${key})`);
      option.value = key;
      input.append(option);
    }
    input.value = String(value);
    input.addEventListener("change", () => record(setting, Number(input.value), row));
  } else {
    input = document.createElement("input");
    if (setting.kind === "boolean") {
      input.type = "checkbox";
      input.checked = Boolean(value);
      const stateLabel = () => setting.boolean_labels?.[input.checked ? "1" : "0"] || (input.checked ? "ON" : "OFF");
      const label = text("span", stateLabel());
      input.addEventListener("change", () => {
        label.textContent = stateLabel();
        record(setting, input.checked, row);
      });
      area.append(label);
    } else {
      input.type = ["time", "number"].includes(setting.kind) ? setting.kind : "text";
      if (setting.kind === "number") { input.min = "0"; input.step = setting.units.includes("dollars") ? "0.05" : "1"; }
      input.value = value ?? "";
      input.addEventListener("input", () => {
        const number = Number(input.value);
        record(setting, setting.kind === "number" && input.value !== "" && Number.isFinite(number) ? number : input.value, row);
      });
    }
  }
  input.setAttribute("aria-label", `${setting.id}: ${setting.name}`);
  area.prepend(input);
  return area;
}
function render() {
  const query = $("search").value.toLowerCase().trim(), category = $("category").value;
  const container = $("settings");
  container.replaceChildren();
  for (const setting of opened.settings) {
    if (setting.kind === "shutdown") continue;
    if (setting.read_only && !$("advanced").checked) continue;
    if (category && category !== setting.category) continue;
    if (query && !`${setting.id} ${setting.name} ${setting.category}`.toLowerCase().includes(query)) continue;
    const row = document.createElement("div");
    row.className = "setting";
    row.classList.toggle("readonly", Boolean(setting.read_only));
    row.classList.toggle("changed", Object.hasOwn(changes, setting.id));
    const heading = document.createElement("div");
    const name = text("div", "", "name");
    name.append(text("span", setting.id, "reg"), document.createTextNode(setting.name));
    heading.append(name);
    if (setting.rule) heading.append(text("p", setting.rule, "help"));
    if (setting.units && !setting.units.startsWith("not established")) heading.append(text("p", setting.units, "help"));
    if (setting.read_only) heading.append(text("p", setting.read_only, "help"));
    if (setting.error) heading.append(text("p", setting.error, "help"));
    row.append(heading, control(setting, row));
    if (setting.notes.length) {
      const details = document.createElement("details");
      details.className = "notes";
      details.append(text("summary", "What this setting does"));
      setting.notes.forEach(note => details.append(text("p", note)));
      row.append(details);
    }
    container.append(row);
  }
  if (!container.children.length) container.append(text("p", "No matching settings."));
}
function renderShutdown() {
  const setting = opened.settings.find(s => s.kind === "shutdown");
  $("shutdown-section").hidden = !setting;
  const container = $("shutdown");
  container.replaceChildren();
  if (!setting) return;
  for (const option of setting.call_options) {
    if (option.name === "Undocumented parameter" && option.unknown_bits_hex === "00" &&
        !option.restrict_during_interval_1 && !option.restrict_during_interval_2) continue;
    const row = document.createElement("div");
    row.className = "shutdown-row";
    row.append(text("span", `${option.register_num}: ${option.name}`));
    for (let interval = 1; interval <= 2; interval++) {
      const key = `interval${interval}`, current = option[`restrict_during_interval_${interval}`];
      const label = text("label", `Period ${interval}`), checkbox = document.createElement("input");
      checkbox.type = "checkbox"; checkbox.checked = current; checkbox.disabled = Boolean(setting.read_only);
      checkbox.addEventListener("change", () => {
        const id = String(option.call_type);
        if (checkbox.checked === current) {
          if (shutdownChanges[id]) { delete shutdownChanges[id][key]; if (!Object.keys(shutdownChanges[id]).length) delete shutdownChanges[id]; }
        } else { (shutdownChanges[id] ??= {})[key] = checkbox.checked; }
        updateCount();
      });
      label.prepend(checkbox); row.append(label);
    }
    container.append(row);
  }
}
function reset() {
  changes = {}; shutdownChanges = {};
  $("description").value = opened.description;
  render(); renderShutdown(); updateCount();
  savedSignature = signature();
}
async function request(path, body, type) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": type }, body });
  if (!response.ok) {
    const payload = await response.json();
    throw new Error(payload.error || "Request failed");
  }
  return response;
}
$("file").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  if (dirty() && !window.confirm("Discard your unsaved edits and open another file?")) {
    event.target.value = "";
    return;
  }
  try {
    if (file.size > 65536) throw new Error("This file is too large to be a supported C94 image.");
    const bytes = new Uint8Array(await file.arrayBuffer());
    const response = await request("/api/open", bytes, "application/octet-stream");
    const data = await response.json();
    let binary = ""; bytes.forEach(byte => { binary += String.fromCharCode(byte); });
    original = btoa(binary); opened = data; filename = file.name.replace(/\.c94$/i, "") + "-edited.C94";
    $("firmware").textContent = `${file.name} — ${data.firmware}`;
    $("category").replaceChildren();
    const all = text("option", "All categories"); all.value = ""; $("category").append(all);
    [...new Set(data.settings.map(s => s.category))].sort().forEach(category => {
      const option = text("option", category); option.value = category; $("category").append(option);
    });
    $("search").value = ""; $("editor").hidden = false;
    $("save").disabled = false; $("reset").disabled = false;
    reset(); message("Ready. Change the settings you want, then download a new C94 file.");
  } catch (error) { message(error.message, true); }
  event.target.value = "";
});
$("save").addEventListener("click", async () => {
  if (!opened) return;
  $("save").disabled = true;
  try {
    const edits = { ...changes };
    if (Object.keys(shutdownChanges).length) edits.R468 = shutdownChanges;
    const response = await request("/api/save", JSON.stringify({ original, changes: edits, description: $("description").value }), "application/json");
    const url = URL.createObjectURL(await response.blob()), link = document.createElement("a");
    link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove();
    URL.revokeObjectURL(url);
    savedSignature = signature();
    message("Edited C94 verified and downloaded. Your original file was not overwritten.");
  } catch (error) { message(error.message, true); }
  finally { $("save").disabled = false; }
});
$("reset").addEventListener("click", () => { reset(); message("Edits discarded. Showing the original settings."); });
$("description").addEventListener("input", updateCount);
$("search").addEventListener("input", render);
$("category").addEventListener("change", render);
$("advanced").addEventListener("change", render);
window.addEventListener("beforeunload", event => {
  if (dirty()) {
    event.preventDefault(); event.returnValue = "";
  }
});
