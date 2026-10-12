/* Re-identify me! — logique du jeu (aucune dépendance).
   Les données viennent de web/data/kerdata.json, généré par `just generate`. */
(() => {
  "use strict";

  const root = document.documentElement;
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") el.className = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) if (kid !== null && kid !== undefined && kid !== false) el.append(kid);
    return el;
  };

  // ---------- langue ----------
  let lang = "fr";
  try { lang = localStorage.getItem("kerdata-lang") || "fr"; } catch { /* stockage indisponible */ }
  if (lang !== "fr" && lang !== "en") lang = "fr";
  const L = (fr, en) => (lang === "fr" ? fr : en);
  const locale = () => (lang === "fr" ? "fr-FR" : "en-GB");
  const fmtInt = (n) => n.toLocaleString(locale());
  const fmtNum = (x, d = 1) => x.toLocaleString(locale(), { minimumFractionDigits: d, maximumFractionDigits: d });
  const pct = (x, d = 0) => (x * 100).toLocaleString(locale(), { maximumFractionDigits: d }) + (lang === "fr" ? " %" : "%");
  const listJoin = (items) => items.length < 2 ? items.join("") : `${items.slice(0, -1).join(", ")} ${L("et", "and")} ${items.at(-1)}`;

  // ---------- données ----------
  let D, C, N;
  const lab = (col, code) => D.dict[col][code][lang];
  const codeOf = (col, key) => D.dict[col].findIndex((e) => e.key === key);
  const ageText = (a) => (a === 0 ? L("moins d'un an", "under 1 yr") : `${a} ${a > 1 ? L("ans", "yrs") : L("an", "yr")}`);
  const val = (col, i, src = C) => {
    const v = src[col][i];
    switch (col) {
      case "age": return ageText(v);
      case "weight_kg": return `${v} kg`;
      case "length_cm": return `${v} cm`;
      case "name": case "pseudo": return v;
      default: return lab(col, v);
    }
  };
  const Q = (key) => D.questions.find((x) => x.key === key);
  const qLabel = (key) => Q(key)[lang];
  const qAsk = (key) => Q(key)[`ask_${lang}`];
  const qHuman = (key) => Q(key)[`human_${lang}`];
  const all = () => [...Array(N).keys()];

  const uniqueShare = (cols) => {
    const keyOf = (i) => cols.map((c) => C[c][i]).join("|");
    const m = new Map();
    for (let i = 0; i < N; i++) { const k = keyOf(i); m.set(k, (m.get(k) || 0) + 1); }
    let u = 0;
    for (let i = 0; i < N; i++) if (m.get(keyOf(i)) === 1) u++;
    return u / N;
  };
  const sample = (arr, k) => {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a.slice(0, k);
  };

  // ce que le joueur a découvert, pour le rapport final
  const R = { a1: null, a2: null, a3: null };

  // ======================================================================
  // ACTE I — Devine qui
  // ======================================================================
  const A1 = { board: [], target: -1, asked: [], found: false, wrong: 0, eliminated: new Set() };

  function newBoard() {
    A1.board = sample(all(), 24);
    A1.target = A1.board[Math.floor(Math.random() * 24)];
    A1.asked = []; A1.found = false; A1.wrong = 0; A1.eliminated = new Set();
    renderA1();
  }
  const matches = (i) => A1.asked.every((c) => C[c][i] === C[c][A1.target]);
  const colonyMatches = () => { let n = 0; for (let i = 0; i < N; i++) if (matches(i)) n++; return n; };

  function renderA1() {
    const qs = $("#questions"); qs.replaceChildren();
    for (const q of D.questions) {
      const asked = A1.asked.includes(q.key);
      qs.append(h("button", {
        type: "button", class: "q", disabled: asked || A1.found,
        onclick: () => { A1.asked.push(q.key); renderA1(); },
      }, q[`ask_${lang}`], asked ? h("span", {}, " → ", h("span", { class: "ans" }, val(q.key, A1.target))) : null));
    }

    const board = $("#board"); board.replaceChildren();
    const male = codeOf("sex", "M");
    for (const i of A1.board) {
      const down = !matches(i) || A1.eliminated.has(i);
      board.append(h("button", {
        type: "button", class: `card${down ? " down" : ""}${A1.found && i === A1.target ? " found" : ""}`,
        "aria-disabled": down ? "true" : null,
        "aria-label": `${C.name[i]}${down ? L(" (écarté)", " (ruled out)") : ""}`,
        onclick: (e) => {
          if (down || A1.found) return;
          if (i === A1.target) { A1.found = true; renderA1(); }
          else { A1.wrong++; A1.eliminated.add(i); e.currentTarget.classList.add("wrong"); setTimeout(renderA1, 380); }
        },
      },
        h("span", { class: "top" }, h("span", { class: "emo", "aria-hidden": "true" }, "🦭"), h("span", { class: "nm" }, C.name[i])),
        h("span", { class: "attrs" },
          `${C.sex[i] === male ? "♂" : "♀"} · ${val("age", i)} · ${val("birth_month", i)}`, h("br"),
          val("zone", i), h("br"),
          `${val("coat", i)} · ${val("mark", i)}`, h("br"),
          val("temper", i), h("br"),
          `${val("weight_kg", i)} · ${val("length_cm", i)}`)));
    }

    const left = A1.board.filter((i) => matches(i) && !A1.eliminated.has(i)).length;
    let msg;
    if (A1.found) msg = L("Bravo, tu l'as trouvé ! Le résultat est juste en dessous.", "Well done, you found it! The result is just below.");
    else if (left === 1) msg = L("Il ne reste qu'une fiche. Clique dessus !", "Only one card left. Click it!");
    else if (!A1.asked.length) msg = L("Astuce : certaines questions éliminent beaucoup plus de fiches que d'autres.", "Tip: some questions rule out many more cards than others.");
    else msg = L("Continue, ou clique sur une fiche si tu penses avoir trouvé.", "Keep going, or click a card if you think you know.");
    $("#side").replaceChildren(
      h("div", {}, h("h4", {}, L("Questions posées", "Questions asked")),
        h("div", { class: "big" }, String(A1.asked.length), A1.wrong ? h("small", {}, L(` + ${A1.wrong} erreur(s)`, ` + ${A1.wrong} miss(es)`)) : null)),
      h("div", {}, h("h4", {}, L("Phoques encore possibles", "Seals still possible")),
        h("div", { class: `big${left === 1 ? " good" : ""}` }, String(left), h("small", {}, " / 24"))),
      h("p", { class: "msg" }, msg),
      h("button", { type: "button", class: "btn", onclick: newBoard }, L("Nouvelle partie", "New game")));

    const res = $("#a1-result");
    if (!A1.found) { res.replaceChildren(); return; }
    const t = A1.target, n = A1.asked.length, col = colonyMatches();
    const names = A1.asked.map((k) => qLabel(k).toLowerCase());
    R.a1 = { name: C.name[t], n, col };
    res.replaceChildren(h("div", { class: "result" },
      h("h4", {}, L(`Trouvé : c'était ${C.name[t]} !`, `Found it: it was ${C.name[t]}!`)),
      h("p", {}, L(`Avec seulement ${n} information${n > 1 ? "s" : ""} (${listJoin(names)}), tu as reconnu ${C.name[t]} parmi les 24 phoques du plateau. Tu ne connaissais pas son nom : ce sont ses attributs qui l'ont trahi.`,
        `With just ${n} piece${n > 1 ? "s" : ""} of information (${listJoin(names)}), you recognised ${C.name[t]} among the 24 seals on the board. You didn't know its name: its attributes gave it away.`)),
      h("p", {}, col === 1
        ? L(`Et même dans toute la colonie de ${fmtInt(N)} phoques, ces ${n} informations ne désignent que ${C.name[t]} : il est unique.`,
            `And even across the whole colony of ${fmtInt(N)} seals, these ${n} pieces of information point only to ${C.name[t]}: it is unique.`)
        : L(`Dans toute la colonie de ${fmtInt(N)} phoques, ces ${n} informations désignent encore ${fmtInt(col)} phoques. Il faudrait quelques questions de plus… mais pas beaucoup, regarde juste en dessous.`,
            `Across the whole colony of ${fmtInt(N)} seals, these ${n} pieces of information still match ${fmtInt(col)} seals. You'd need a few more questions… but not many, see just below.`))));
    renderReport();
  }

  function renderCurve() {
    const ol = $("#curve"); ol.replaceChildren();
    for (const p of D.curve) {
      ol.append(h("li", { title: `${qLabel(p.column)} : ${pct(p.unique, 1)}` },
        h("span", { class: "lab" }, `+ ${qLabel(p.column)}`, h("span", { class: "hum" }, qHuman(p.column))),
        h("span", { class: "track" }, h("span", { class: "fill", style: `width:${(p.unique * 100).toFixed(2)}%` })),
        h("span", { class: "val" }, pct(p.unique, 1))));
    }
    const four = D.curve[3].unique;
    const firstFull = D.curve.findIndex((p) => p.unique >= 0.999) + 1;
    const c = $("#curve-callout"); c.replaceChildren(
      L("Avec 4 informations banales (lieu de repos, sexe, âge, mois de naissance), ", "With 4 ordinary pieces of information (resting spot, sex, age, birth month), "),
      h("b", {}, pct(four)), L(" des phoques sont déjà uniques. Avec ", " of the seals are already unique. With "),
      h("b", {}, String(firstFull)), L(" attributs, pratiquement tous le sont.", " attributes, practically all of them are."));
  }

  // ======================================================================
  // ACTE II — le test du registre
  // ======================================================================
  const A2 = { used: [] };
  let target, known;

  const clueDefs = () => {
    const a = known.age;
    return [
      { col: "zone", src: L("Photo géolocalisée", "Geotagged photo"),
        txt: L(`« Gwen fait la sieste à l'endroit habituel : ${lab("zone", known.zone)} ☀️ »`, `“Gwen napping at her usual spot: ${lab("zone", known.zone)} ☀️”`) },
      { col: "coat", src: L("Photo du soigneur", "Keeper's photo"),
        txt: L(`On voit bien son pelage : ${lab("coat", known.coat).toLowerCase()}.`, `You can clearly see her coat: ${lab("coat", known.coat).toLowerCase()}.`) },
      { col: "mark", src: L("Photo en gros plan", "Close-up photo"),
        txt: L(`Signe particulier bien visible : ${lab("mark", known.mark).toLowerCase()}.`, `Clearly visible mark: ${lab("mark", known.mark).toLowerCase()}.`) },
      { col: "age", src: L("Légende d'une photo", "Photo caption"),
        txt: L(`« Joyeux anniversaire à ma chouchoute, déjà ${a} ans ! »`, `“Happy birthday to my favourite, ${a} already!”`) },
    ];
  };
  const countWith = (cols) => { let n = 0; for (let i = 0; i < N; i++) if (cols.every((c) => C[c][i] === known[c])) n++; return n; };
  const REG_COLS = ["pseudo", "zone", "sex", "age", "birth_month", "coat", "mark", "temper", "weight_kg", "length_cm", "secret"];
  const NUM = ["age", "weight_kg", "length_cm"];
  const colHead = (c) => c === "pseudo" ? L("Pseudonyme", "Pseudonym") : c === "secret" ? L("Petit secret 🔒", "Little secret 🔒") : qLabel(c);

  function renderA2() {
    const clues = $("#clues"); clues.replaceChildren();
    for (const cl of clueDefs()) {
      const on = A2.used.includes(cl.col);
      clues.append(h("button", {
        type: "button", class: "clue", "aria-pressed": on ? "true" : "false",
        onclick: () => { A2.used = on ? A2.used.filter((c) => c !== cl.col) : [...A2.used, cl.col]; renderA2(); },
      }, h("span", { class: "src" }, cl.src), h("span", { class: "txt" }, cl.txt),
        h("span", { class: "use" }, on ? L("✓ indice ajouté (clique pour l'enlever)", "✓ clue added (click to remove)") : L("+ ajouter cet indice", "+ add this clue"))));
    }

    const cand = []; for (let i = 0; i < N; i++) if (A2.used.every((c) => C[c][i] === known[c])) cand.push(i);
    const n = cand.length;
    const f = $("#funnel"); f.replaceChildren(h("span", { class: `step${A2.used.length ? "" : " now"}` }, fmtInt(N)));
    A2.used.forEach((c, k) => {
      const cnt = countWith(A2.used.slice(0, k + 1));
      const last = k === A2.used.length - 1;
      f.append(h("span", { class: "arrow" }, "→"), h("span", { class: `step${last ? " now" : ""}${last && cnt === 1 ? " one" : ""}`, title: qLabel(c) }, fmtInt(cnt)));
    });
    f.append(h("span", { class: "what" }, n === 1 ? L("ligne. Une seule !", "row. Just one!")
      : A2.used.length ? L(`lignes possibles. Ajoute un indice.`, `possible rows. Add a clue.`) : L("lignes dans le registre.", "rows in the register.")));

    const shown = cand.slice().sort((x, y) => (C.pseudo[x] < C.pseudo[y] ? -1 : 1)).slice(0, 6);
    const table = $("#registry");
    table.replaceChildren(
      h("caption", {}, L("Registre publié par le soigneur", "Register published by the keeper")),
      h("thead", {}, h("tr", {}, REG_COLS.map((c) => h("th", { scope: "col", class: NUM.includes(c) ? "num" : null }, colHead(c))))),
      h("tbody", {}, shown.map((i) => h("tr", { class: n === 1 ? "hit" : null },
        REG_COLS.map((c) => h("td", { class: c === "secret" ? "secret" : NUM.includes(c) ? "num" : null },
          c === "secret" && n !== 1 ? "░░░░░░░░░░░░" : val(c, i)))))));
    if (n > shown.length) table.append(h("tfoot", {}, h("tr", {}, h("td", { colspan: REG_COLS.length, class: "more" },
      L(`… et ${fmtInt(n - shown.length)} autres lignes`, `… and ${fmtInt(n - shown.length)} more rows`)))));

    const res = $("#a2-result");
    if (n !== 1) { res.replaceChildren(); return; }
    const i = cand[0];
    R.a2 = { clues: A2.used.length, pseudo: C.pseudo[i] };
    res.replaceChildren(h("div", { class: "result bad" },
      h("h4", {}, L("Résultat du test : Gwen est retrouvée.", "Test result: Gwen has been found.")),
      h("p", {}, L(`Avec ${A2.used.length} informations publiques, il ne reste qu'une ligne dans le registre : ${C.pseudo[i]}. C'est forcément Gwen. Et puisqu'on a sa ligne, on lit aussi son petit secret :`,
        `With ${A2.used.length} pieces of public information, only one register row remains: ${C.pseudo[i]}. It has to be Gwen. And since we have her row, we can also read her little secret:`)),
      h("p", { class: "secret-text" }, `« ${val("secret", i)} »`),
      h("p", {}, L("Le pseudonyme n'a pas protégé Gwen. Le registre du soigneur n'est donc pas anonyme.", "The pseudonym didn't protect Gwen. So the keeper's register isn't anonymous."))));
    renderReport();
  }

  // ======================================================================
  // ACTE III — à toi de protéger
  // ======================================================================
  const SEASON = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0]; // jan→hiver … déc→hiver
  const KNOBS = {
    zone: [["exact", "Exact", "Exact"], ["side", "Côté de l'île", "Side of the island"], ["hide", "Caché", "Hidden"]],
    sex: [["exact", "Gardé", "Kept"], ["hide", "Caché", "Hidden"]],
    age: [["exact", "Exact", "Exact"], ["b3", "Par tranches de 3 ans", "3-year bands"], ["b5", "Par tranches de 5 ans", "5-year bands"], ["hide", "Caché", "Hidden"]],
    birth_month: [["exact", "Exact", "Exact"], ["season", "Saison", "Season"], ["hide", "Caché", "Hidden"]],
    coat: [["exact", "Exact", "Exact"], ["shade", "Clair ou foncé", "Light or dark"], ["hide", "Caché", "Hidden"]],
    mark: [["exact", "Exact", "Exact"], ["yesno", "Oui ou non", "Yes or no"], ["hide", "Caché", "Hidden"]],
  };
  const RAW = { zone: "exact", sex: "exact", age: "exact", birth_month: "exact", coat: "exact", mark: "exact", k: 1 };
  const OCTO = { zone: "exact", sex: "exact", age: "b5", birth_month: "season", coat: "shade", mark: "hide", k: 2 };
  const A3 = { ...RAW, showRecipe: false };
  const darkCoats = () => new Set(["fonce", "brun"].map((k) => codeOf("coat", k)));
  const noMark = () => codeOf("mark", "aucun");

  function gen(col, mode, i) {
    const v = C[col][i];
    switch (mode) {
      case "exact": return v;
      case "hide": return "*";
      case "side": return D.sides[D.dict.zone[v].key];
      case "b3": return Math.floor(v / 3);
      case "b5": return Math.floor(v / 5);
      case "season": return SEASON[v];
      case "shade": return darkCoats().has(v) ? 1 : 0;
      case "yesno": return v === noMark() ? 0 : 1;
      default: return v;
    }
  }

  function scramble() {
    const cols = D.attack_columns;
    const keys = new Array(N), sizes = new Map();
    for (let i = 0; i < N; i++) { keys[i] = cols.map((c) => gen(c, A3[c], i)).join("|"); sizes.set(keys[i], (sizes.get(keys[i]) || 0) + 1); }
    const pub = [];
    for (let i = 0; i < N; i++) if (sizes.get(keys[i]) >= A3.k) pub.push(i);
    let uniq = 0;
    for (const i of pub) if (sizes.get(keys[i]) === 1) uniq++;
    const secretsBy = new Map();
    for (const i of pub) { if (!secretsBy.has(keys[i])) secretsBy.set(keys[i], new Set()); secretsBy.get(keys[i]).add(C.secret[i]); }
    let inferred = 0;
    for (const i of pub) if (sizes.get(keys[i]) >= 2 && secretsBy.get(keys[i]).size === 1) inferred++;
    const prec = cols.map((c) => {
      if (A3[c] === "hide") return 0;
      const before = new Set(C[c]).size;
      return new Set(pub.map((i) => gen(c, A3[c], i))).size / before;
    });
    const tk = keys[target];
    const published = sizes.get(tk) >= A3.k;
    const sameSecret = published && sizes.get(tk) >= 2 && secretsBy.get(tk).size === 1;
    return {
      pub, uniq: pub.length ? uniq / pub.length : 0, kept: pub.length / N,
      precision: prec.reduce((a, b) => a + b, 0) / prec.length,
      inferred: pub.length ? inferred / pub.length : 0,
      gwen: { published, size: sizes.get(tk), sameSecret, safe: !published || (sizes.get(tk) >= 2 && !sameSecret) },
    };
  }

  // les 3 questions des scientifiques
  const ECO = [
    { fr: () => `Combien de phoques se reposent sur l'${lab("zone", codeOf("zone", "ilot"))} ?`, en: () => `How many seals rest on the ${lab("zone", codeOf("zone", "ilot"))}?`,
      needs: { zone: ["exact"] },
      calc: (idx, g) => { const z = codeOf("zone", "ilot"); return idx.filter((i) => g("zone", i) === z).length; },
      fmt: (v) => fmtInt(Math.round(v)) },
    { fr: () => "Quelle part des phoques est née en automne ?", en: () => "What share of seals was born in autumn?",
      needs: { birth_month: ["exact", "season"] },
      calc: (idx, g, m) => { const autumn = m("birth_month") === "season" ? (i) => g("birth_month", i) === 3 : (i) => [8, 9, 10].includes(g("birth_month", i)); return idx.filter(autumn).length / idx.length; },
      fmt: (v) => pct(v) },
    { fr: () => "Quelle part des mâles a un pelage foncé ?", en: () => "What share of males has a dark coat?",
      needs: { sex: ["exact"], coat: ["exact", "shade"] },
      calc: (idx, g, m) => { const male = codeOf("sex", "M"); const dark = m("coat") === "shade" ? (i) => g("coat", i) === 1 : (i) => darkCoats().has(g("coat", i)); const males = idx.filter((i) => g("sex", i) === male); return males.filter(dark).length / males.length; },
      fmt: (v) => pct(v) },
  ];
  function ecoAnswer(q, idx, modes) {
    for (const [c, ok] of Object.entries(q.needs)) if (!ok.includes(modes[c] || "exact")) return null;
    return q.calc(idx, (c, i) => gen(c, modes[c] || "exact", i), (c) => modes[c] || "exact");
  }
  const faithful = (truth, v) => v !== null && !Number.isNaN(v) && Math.abs(v - truth) / Math.max(Math.abs(truth), 1e-9) < 0.05;

  function renderKnobs() {
    const box = $("#knobs"); box.replaceChildren();
    for (const [col, opts] of Object.entries(KNOBS)) {
      box.append(h("fieldset", { class: "knob" }, h("legend", {}, qLabel(col)),
        h("div", { class: "seg" }, opts.map(([mode, fr, en]) => h("button", {
          type: "button", "aria-pressed": A3[col] === mode ? "true" : "false",
          onclick: () => { A3[col] = mode; renderA3(); },
        }, L(fr, en))))));
    }
    box.append(h("div", { class: "knob" },
      h("label", { for: "k-range" }, L("Retirer les phoques trop seuls", "Remove seals that are too lonely")),
      h("div", { class: "slider" },
        h("input", { type: "range", id: "k-range", min: "1", max: "8", step: "1", value: String(A3.k),
          oninput: (e) => { A3.k = Number(e.target.value); renderA3(); } }),
        h("output", { for: "k-range", class: "mono", style: "font-weight:700" }, `k = ${A3.k}`)),
      h("span", { class: "hint" }, A3.k === 1
        ? L("k = 1 : personne n'est retiré.", "k = 1: nobody is removed.")
        : L(`k = ${A3.k} : un phoque n'est publié que s'il a au moins ${A3.k - 1} sosie${A3.k > 2 ? "s" : ""} avec exactement les mêmes attributs.`,
            `k = ${A3.k}: a seal is published only if it has at least ${A3.k - 1} look-alike${A3.k > 2 ? "s" : ""} with exactly the same attributes.`))),
      h("div", { class: "row" }, h("button", { type: "button", class: "btn", onclick: () => { Object.assign(A3, RAW); renderA3(); } }, L("Tout remettre à zéro", "Reset everything"))));
  }

  const meter = (name, value, frac, cls = "") => h("div", { class: `meter ${cls}` },
    h("div", { class: "top" }, h("span", { class: "name" }, name), h("span", { class: "v" }, value)),
    h("div", { class: "bar-t" }, h("div", { class: "bar-f", style: `width:${Math.max(0, Math.min(1, frac)) * 100}%` })));

  function renderA3() {
    renderKnobs();
    const r = scramble();
    const truthIdx = all();
    const answers = ECO.map((q) => { const t = ecoAnswer(q, truthIdx, {}); const p = ecoAnswer(q, r.pub, A3); return { q, t, p, ok: faithful(t, p) }; });
    const okCount = answers.filter((a) => a.ok).length;
    const g = r.gwen;
    const goals = [
      { done: r.uniq === 0, t: L("Plus aucun phoque unique", "No unique seal left"),
        s: r.uniq === 0 ? L("Personne ne peut être reconnu à coup sûr.", "Nobody can be recognised for sure.") : L(`Encore ${pct(r.uniq, 1)} de phoques reconnaissables à coup sûr.`, `${pct(r.uniq, 1)} of seals can still be recognised for sure.`) },
      { done: g.safe, t: L("Le secret de Gwen est à l'abri", "Gwen's secret is safe"),
        s: !g.published ? L("Gwen n'est plus dans le registre publié.", "Gwen is no longer in the published register.")
          : g.size === 1 ? L("On peut encore retrouver Gwen avec ses 4 indices.", "Gwen can still be found with her 4 clues.")
          : g.sameSecret ? L(`Gwen se cache parmi ${g.size} phoques… qui ont tous le même secret. On le devine quand même !`, `Gwen hides among ${g.size} seals… who all share the same secret. It can still be guessed!`)
          : L(`Gwen se cache parmi ${g.size} phoques identiques.`, `Gwen hides among ${g.size} identical seals.`) },
      { done: okCount >= 2, t: L("Les scientifiques gardent 2 questions sur 3", "Scientists keep 2 questions out of 3"),
        s: L(`Pour l'instant : ${okCount} sur 3 (voir le tableau plus bas).`, `Right now: ${okCount} out of 3 (see the table below).`) },
    ];
    $("#mission").replaceChildren(...goals.map((m, k) => h("li", { class: m.done ? "done" : null },
      h("span", { class: "box", "aria-hidden": "true" }, m.done ? "✓" : String(k + 1)),
      h("span", {}, h("span", { class: "t" }, m.t, h("span", { class: "sr-only" }, m.done ? L(" (rempli)", " (met)") : "")), h("br"), h("span", { class: "s" }, m.s)))));

    $("#meters").replaceChildren(
      meter(L("Phoques reconnaissables à coup sûr", "Seals recognisable for sure"), pct(r.uniq, 1), r.uniq, "risk"),
      meter(L("Secrets devinables sans retrouver le phoque", "Secrets guessable without finding the seal"), pct(r.inferred, 1), r.inferred, "risk"),
      meter(L("Phoques gardés dans le registre", "Seals kept in the register"), pct(r.kept), r.kept),
      meter(L("Détail gardé (précision)", "Detail kept (precision)"), pct(r.precision), r.precision),
      h("p", { class: "gwen-line" }, goals[1].s));

    $("#eco").replaceChildren(
      h("thead", {}, h("tr", {},
        h("th", { scope: "col" }, L("Question des scientifiques", "Scientists' question")),
        h("th", { scope: "col", class: "num" }, L("Vrai registre", "True register")),
        h("th", { scope: "col", class: "num" }, L("Ton registre publié", "Your published register")))),
      h("tbody", {}, answers.map(({ q, t, p, ok }) => h("tr", {},
        h("td", {}, q[lang]()),
        h("td", { class: "num" }, q.fmt(t)),
        h("td", { class: "num" }, p === null ? "— " : `${q.fmt(p)} `,
          p === null ? h("span", { class: "pill bad" }, L("impossible", "impossible"))
            : ok ? h("span", { class: "pill ok" }, L("✓ juste", "✓ right"))
            : h("span", { class: "pill mid" }, L("faussé", "skewed")))))));

    const done = goals.every((m) => m.done);
    if (done) R.a3 = { uniq: r.uniq, inferred: r.inferred, kept: r.kept, ok: okCount };
    const win = $("#win");
    if (!done) {
      win.replaceChildren();
    } else {
      win.replaceChildren(h("div", { class: "result" },
        h("h4", {}, L("Mission réussie !", "Mission accomplished!")),
        h("p", {}, L(`Ton registre ne laisse personne unique, Gwen est à l'abri et les scientifiques gardent ${okCount} questions sur 3. Tu as gardé ${pct(r.kept)} des phoques. Tu as trouvé un compromis entre risque et utilité.`,
          `Your register leaves nobody unique, Gwen is safe and scientists keep ${okCount} questions out of 3. You kept ${pct(r.kept)} of the seals. You found a trade-off between risk and utility.`)),
        A3.showRecipe
          ? h("p", { class: "recipe" }, L("La recette du poulpe : lieu exact, sexe gardé, âge par 5 ans, saison de naissance, pelage clair ou foncé, signe particulier caché, et k = 2. Résultat : les 3 questions restent justes. ",
              "Octo's recipe: exact spot, sex kept, age in 5-year bands, birth season, light or dark coat, mark hidden, and k = 2. Result: all 3 questions stay right. "),
              h("button", { type: "button", class: "btn", onclick: () => { Object.assign(A3, OCTO); renderA3(); } }, L("Essayer sa recette", "Try the recipe")))
          : h("button", { type: "button", class: "btn", onclick: () => { A3.showRecipe = true; renderA3(); } }, L("Comparer avec la recette du poulpe", "Compare with Octo's recipe"))));
    }
    renderReport();
  }

  // ---------- bonus : fausse colonie ----------
  let SYN = null;
  function mulberry32(a) {
    return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  const SYN_COLS = ["zone", "age", "birth_month", "coat", "mark", "temper", "weight_kg", "length_cm"];
  function synthesize(seed) {
    const rnd = mulberry32(seed);
    const bySex = new Map();
    for (let i = 0; i < N; i++) { const s = C.sex[i]; if (!bySex.has(s)) bySex.set(s, []); bySex.get(s).push(i); }
    const cols = { sex: new Array(N) };
    for (const c of SYN_COLS) cols[c] = new Array(N);
    for (let j = 0; j < N; j++) {
      const s = C.sex[Math.floor(rnd() * N)];
      cols.sex[j] = s;
      const pool = bySex.get(s);
      for (const c of SYN_COLS) cols[c][j] = C[c][pool[Math.floor(rnd() * pool.length)]];
    }
    return cols;
  }
  function meanCorr(src) {
    const by = new Map();
    for (let i = 0; i < N; i++) { const s = src.sex[i]; if (!by.has(s)) by.set(s, []); by.get(s).push(i); }
    const rs = [];
    for (const idx of by.values()) {
      const xs = idx.map((i) => src.age[i]), ys = idx.map((i) => src.weight_kg[i]);
      const mx = xs.reduce((a, b) => a + b, 0) / xs.length, my = ys.reduce((a, b) => a + b, 0) / ys.length;
      let sxy = 0, sxx = 0, syy = 0;
      for (let k = 0; k < xs.length; k++) { const dx = xs[k] - mx, dy = ys[k] - my; sxy += dx * dy; sxx += dx * dx; syy += dy * dy; }
      if (sxx && syy) rs.push(sxy / Math.sqrt(sxx * syy));
    }
    return rs.reduce((a, b) => a + b, 0) / rs.length;
  }
  function renderSynth() {
    const box = $("#synth");
    if (!SYN) { box.replaceChildren(); return; }
    const cols = D.attack_columns;
    const real = new Map();
    for (let i = 0; i < N; i++) { const k = cols.map((c) => C[c][i]).join("|"); real.set(k, (real.get(k) || 0) + 1); }
    let copies = 0;
    for (let j = 0; j < N; j++) if (real.get(cols.map((c) => SYN[c][j]).join("|")) === 1) copies++;
    const share = copies / N, ctrl = D.control_match;
    let gwenLike = 0;
    for (let j = 0; j < N; j++) if (["zone", "coat", "mark", "age"].every((c) => SYN[c][j] === known[c])) gwenLike++;
    const rReal = meanCorr(C), rSyn = meanCorr(SYN);
    box.replaceChildren(
      h("div", { class: "box" }, h("h4", {}, L("Recopie-t-elle des phoques ?", "Does it copy seals?")),
        h("div", { class: "big" }, pct(share, 1)),
        h("p", {}, L(`des faux phoques ont, par hasard, le même profil qu'un vrai phoque unique. Une colonie tirée complètement au hasard en a autant (${pct(ctrl, 1)}) : ce sont des coïncidences, pas des copies.`,
          `of fake seals happen to share the profile of a real unique seal. A colony drawn completely at random has as many (${pct(ctrl, 1)}): these are coincidences, not copies.`))),
      h("div", { class: "box" }, h("h4", {}, L("Et Gwen ?", "What about Gwen?")),
        h("div", { class: "big" }, fmtInt(gwenLike)),
        h("p", {}, L("faux phoques collent à ses 4 indices. Ce ne sont pas elle : son secret n'est pas dans cette colonie.", "fake seals match her 4 clues. None of them is her: her secret isn't in this colony."))),
      h("div", { class: "box" }, h("h4", {}, L("Ce qu'on perd", "What we lose")),
        h("div", { class: "big" }, `r = ${fmtNum(rSyn, 2)}`),
        h("p", {}, L(`Dans la vraie colonie, plus un phoque est jeune, plus il est léger (lien âge ↔ poids : r = ${fmtNum(rReal, 2)}). Notre générateur simple a oublié ce lien. Un bon générateur doit le garder sans recopier personne, et ça se mesure.`,
          `In the real colony, the younger the seal, the lighter it is (age ↔ weight link: r = ${fmtNum(rReal, 2)}). Our simple generator forgot this link. A good generator keeps it without copying anyone, and that can be measured.`))));
  }

  // ======================================================================
  // RAPPORT
  // ======================================================================
  function renderReport() {
    const four = D.curve[3].unique;
    const proof = (num, name, question, evidence, yours) => h("li", { class: "proof" },
      h("div", { class: "crit" }, h("span", { class: "num" }, num), h("span", { class: "name" }, name), h("span", { class: "qq" }, question)),
      h("div", { class: "evidence" }, evidence.map((p) => h("p", {}, p)), h("p", { class: "yours" }, yours)));
    $("#proofs").replaceChildren(
      proof(L("Question 1 · acte I", "Question 1 · act I"), L("Individualisation", "Singling out"), L("Peut-on isoler un phoque parmi les autres ?", "Can you isolate one seal from the others?"),
        [L(`Oui. Avec 4 informations banales, ${pct(four)} des phoques de la colonie sont uniques.`, `Yes. With 4 ordinary pieces of information, ${pct(four)} of the colony's seals are unique.`)],
        R.a1 ? L(`Ta preuve : tu as reconnu ${R.a1.name} avec ${R.a1.n} question${R.a1.n > 1 ? "s" : ""}.`, `Your evidence: you recognised ${R.a1.name} with ${R.a1.n} question${R.a1.n > 1 ? "s" : ""}.`)
          : L("Joue l'acte I pour ajouter ta propre preuve.", "Play act I to add your own evidence.")),
      proof(L("Question 2 · acte II", "Question 2 · act II"), L("Corrélation", "Linkability"), L("Peut-on relier le registre à une autre source ?", "Can you link the register to another source?"),
        [L("Oui. Des informations publiques venues d'une autre source (des photos sur les réseaux sociaux) suffisent à retrouver une ligne du registre.", "Yes. Public information from another source (photos on social media) is enough to find a row in the register.")],
        R.a2 ? L(`Ta preuve : ${R.a2.clues} informations trouvées sur les réseaux sociaux t'ont mené à la ligne ${R.a2.pseudo}, celle de Gwen, et à son secret.`, `Your evidence: ${R.a2.clues} pieces of information found on social media led you to row ${R.a2.pseudo}, Gwen's, and to her secret.`)
          : L("Fais le test de l'acte II pour ajouter ta propre preuve.", "Run the act II test to add your own evidence.")),
      proof(L("Question 3 · acte III", "Question 3 · act III"), L("Inférence", "Inference"), L("Peut-on deviner une information sans retrouver le phoque ?", "Can you guess something without finding the seal?"),
        [L("Parfois. Si tous les phoques d'un groupe ont le même secret, inutile de savoir lequel est Gwen pour l'apprendre.", "Sometimes. If all the seals in a group share the same secret, no need to know which one is Gwen to learn it.")],
        R.a3 ? L(`Ton réglage : ${pct(R.a3.uniq, 1)} de phoques uniques et ${pct(R.a3.inferred, 1)} de secrets devinables, en gardant ${pct(R.a3.kept)} de la colonie.`,
              `Your setting: ${pct(R.a3.uniq, 1)} unique seals and ${pct(R.a3.inferred, 1)} guessable secrets, keeping ${pct(R.a3.kept)} of the colony.`)
          : L("Réussis la mission de l'acte III pour ajouter ta propre preuve.", "Complete the act III mission to add your own evidence.")));
  }

  // ======================================================================
  // langue + démarrage
  // ======================================================================
  function fills() { $$('[data-fill="n"]').forEach((el) => { el.textContent = fmtInt(N); }); }

  function setLang(next) {
    lang = next;
    root.dataset.lang = lang; root.lang = lang;
    $$("[data-set-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.setLang === lang)));
    try { localStorage.setItem("kerdata-lang", lang); } catch { /* rien */ }
    if (D) { fills(); renderA1(); renderCurve(); renderA2(); renderA3(); renderSynth(); renderReport(); }
  }

  function start(data) {
    D = data; C = D.columns; N = D.meta.n;
    target = D.target.row;
    known = {};
    for (const [c, v] of Object.entries(D.target.known)) known[c] = typeof v === "string" ? codeOf(c, v) : v;
    $$("[data-set-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.setLang)));
    $("#reset-attack").addEventListener("click", () => { A2.used = []; renderA2(); });
    $("#make-synth").addEventListener("click", () => {
      SYN = synthesize(Math.floor(Math.random() * 2 ** 31));
      renderSynth();
      $("#make-synth").innerHTML = '<span class="fr">Fabriquer une autre fausse colonie</span><span class="en">Build another fake colony</span>';
    });
    A1.board = []; newBoard();
    setLang(lang);
  }

  root.dataset.lang = lang;
  if (window.KERDATA) start(window.KERDATA);
  else fetch("data/kerdata.json").then((r) => r.json()).then(start).catch(() => {
    $("#board").replaceChildren(h("p", {}, L("Impossible de charger la colonie (data/kerdata.json). Lance `just serve`.", "Could not load the colony (data/kerdata.json). Run `just serve`.")));
  });
})();
