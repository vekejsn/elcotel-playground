// Dependency-free UI event tests. Run: node --test tests/test_c94_editor_ui.cjs
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

class Element {
  constructor(tag = "div") {
    this.tagName = tag; this.children = []; this.value = ""; this.checked = false;
    this.hidden = false; this.disabled = false; this.textContent = ""; this.listeners = {};
    this.classes = new Set();
    this.classList = { toggle: (name, on) => on ? this.classes.add(name) : this.classes.delete(name) };
  }
  append(...children) { this.children.push(...children); }
  prepend(...children) { this.children.unshift(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this[name] = value; }
  addEventListener(name, callback) { (this.listeners[name] ??= []).push(callback); }
  remove() {}
  click() {}
  async emit(name, event = { target: this }) {
    for (const callback of this.listeners[name] || []) await callback(event);
  }
}

function setup() {
  const ids = Object.fromEntries(["file", "firmware", "save", "reset", "message", "description",
    "search", "category", "advanced", "settings", "shutdown", "shutdown-section", "editor", "count"]
    .map(id => [id, new Element()]));
  const doc = { getElementById: id => ids[id], createElement: tag => new Element(tag),
    createTextNode: value => Object.assign(new Element("#text"), { textContent: value }), body: new Element() };
  const win = new Element(); win.confirm = () => true;
  const settings = [
    { id: "R100", name: "Enable incoming calls", kind: "boolean", value: false },
    { id: "R437", name: "Timed call home", kind: "number", value: 0, units: "days (stored as hours)" },
    { id: "R472", name: "Default language", kind: "choice", value: 0, choices: { 0: "English", 1: "Spanish" } },
    { id: "R403", name: "Communications password", kind: "text", value: "secret42" },
    { id: "R340", name: "Undocumented parameter", kind: "text", value: "", read_only: "Unconfirmed meaning" },
    { id: "R468", name: "Shutdown", kind: "shutdown", value: [], call_options: [
      { call_type: 4, register_num: 204, name: "Paid local calls", restrict_during_interval_1: false,
        restrict_during_interval_2: false, unknown_bits_hex: "80" }] },
  ].map(s => ({ category: "Configuration", rule: "", units: "", notes: [], ...s }));
  let saved, failSave = false;
  const context = vm.createContext({ document: doc, window: win, Uint8Array,
    btoa: value => Buffer.from(value, "binary").toString("base64"),
    URL: { createObjectURL: () => "blob:test", revokeObjectURL: () => {} },
    fetch: async (route, request) => {
      if (route === "/api/open") return { ok: true, json: async () => ({ firmware: "LP 05.04.00", description: "test", settings }) };
      saved = JSON.parse(request.body);
      if (failSave) return { ok: false, json: async () => ({ error: "R437: Allowed range is 0 to 9" }) };
      return { ok: true, blob: async () => Buffer.from("edited C94") };
    } });
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../c94file/web/editor.js"), "utf8"), context);
  async function open() {
    ids.file.files = [{ name: "phone.C94", size: 4, arrayBuffer: async () => Uint8Array.from([1, 2, 3, 4]).buffer }];
    await ids.file.emit("change");
  }
  function input(register) {
    const row = ids.settings.children.find(r => r.children[0]?.children[0]?.children[0]?.textContent === register);
    assert.ok(row, `Expected visible row ${register}`);
    return row.children[1].children[0];
  }
  return { ids, win, open, input, saved: () => saved, fail: () => { failSave = true; } };
}

test("open, edit human controls, restrict call types, and download", async () => {
  const app = setup();
  await app.open();
  assert.equal(app.ids.settings.children.length, 4); // Unknown setting hidden, shutdown in separate section.
  assert.equal(app.input("R403").type, "text");
  assert.equal(app.input("R403").value, "secret42");
  assert.equal(app.ids.save.disabled, false);
  const flag = app.input("R100"); flag.checked = true; await flag.emit("change");
  const days = app.input("R437"); days.value = "3"; await days.emit("input");
  const language = app.input("R472"); language.value = "1"; await language.emit("change");
  const interval = app.ids.shutdown.children[0].children[1].children[0];
  interval.checked = true; await interval.emit("change");
  app.ids.description.value = "My phone"; await app.ids.description.emit("input");
  await app.ids.save.emit("click");
  assert.deepEqual(app.saved().changes, { R100: true, R437: 3, R472: 1, R468: { 4: { interval1: true } } });
  assert.equal(app.saved().description, "My phone");
  assert.equal(app.saved().original, "AQIDBA==");
  assert.match(app.ids.message.textContent, /verified and downloaded/);
  let prevented = false;
  await app.win.emit("beforeunload", { preventDefault() { prevented = true; } });
  assert.equal(prevented, false); // A completed download is no longer an unsaved edit.
});

test("search, show read-only settings, reset, and display save errors", async () => {
  const app = setup(); await app.open();
  app.ids.search.value = "language"; await app.ids.search.emit("input");
  assert.equal(app.ids.settings.children.length, 1);
  app.ids.search.value = ""; app.ids.advanced.checked = true; await app.ids.advanced.emit("change");
  assert.equal(app.ids.settings.children.length, 5);
  const days = app.input("R437"); days.value = "99"; await days.emit("input");
  app.fail(); await app.ids.save.emit("click");
  assert.match(app.ids.message.textContent, /Allowed range is 0 to 9/);
  assert.equal(app.ids.save.disabled, false);
  let prevented = false;
  await app.win.emit("beforeunload", { preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  await app.ids.reset.emit("click");
  assert.equal(app.input("R437").value, 0);
  assert.match(app.ids.count.textContent, /0 changed/);
});
