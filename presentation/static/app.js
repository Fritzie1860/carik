/**
 * Carik Editorial Studio - Frontend Application Controller
 */

// Sample Drafts
const SAMPLE_DRAFTS = {
  tech_ai: `Kecerdasan buatan (AI) berkembang dengan sangat cepat dan mempengaruhi seluruh lanskap teknologi saat ini. Banyak perusahaan teknologi berlomba-lomba untuk mengadopsi AI guna membuka potensi baru dan meningkatkan efisiensi kerja.

Selanjutnya, AI memberikan banyak kemudahan dalam otomatisasi tugas-tugas rutin yang membosankan. Hal ini menjadi bukti nyata bagaimana transformasi digital merombak alur kerja tim rekayasa perangkat lunak secara mulus dan menyeluruh.

Kesimpulannya, kita harus memanfaatkan teknologi ini dengan bijak agar tidak tertinggal dalam persaingan global.`,
  business: `Strategi pertumbuhan berbasis produk atau product-led growth semakin diminati oleh startup modern.

Dengan fokus pada pengalaman pengguna yang intuitif, perusahaan dapat mengakselerasi adopsi tanpa bergantung penuh pada tim sales tradisional. Namun, metrik retensi tetap menjadi fondasi utama keberlanjutan bisnis.`,
  editorial: `Jurnalisme modern menghadapi tantangan berat di era banjir informasi. Kecepatan sering kali mengorbankan akurasi dan kedalaman investigasi.

Untuk menjaga kepercayaan publik, ruang redaksi harus memperkuat verifikasi fakta dan menyajikan perspektif yang tajam serta berimbang.`
};

// Application State
const state = {
  sourceText: "",
  activeTab: 0,
  viewMode: "clean", // 'clean' | 'highlights'
  isProcessing: false,
  isSidebarCollapsed: false,
  drafts: [], // { iteration: 0, title: "Original (Bahasa)", text: "..." }
  latestReport: null,
  bannedCliches: {},
  apiKey: localStorage.getItem("carik_gemini_api_key") || "",
  ws: null,
};

// DOM Elements
const el = {
  sourceTextarea: document.getElementById("source-textarea"),
  sampleSelect: document.getElementById("sample-select"),
  charCount: document.getElementById("char-count"),
  wordCount: document.getElementById("word-count"),
  maxRetriesSelect: document.getElementById("max-retries-select"),
  btnStart: document.getElementById("btn-start-process"),
  btnAuditOnly: document.getElementById("btn-audit-only"),
  
  draftVersionTabs: document.getElementById("draft-version-tabs"),
  btnModeClean: document.getElementById("btn-mode-clean"),
  btnModeHighlights: document.getElementById("btn-mode-highlights"),
  btnCopyDraft: document.getElementById("btn-copy-draft"),
  btnExportMd: document.getElementById("btn-export-md"),
  
  paneSource: document.getElementById("pane-source"),
  draftContainer: document.getElementById("draft-container"),
  draftEmptyState: document.getElementById("draft-empty-state"),
  proseContent: document.getElementById("prose-content"),
  draftWordCount: document.getElementById("draft-word-count"),
  draftReadTime: document.getElementById("draft-read-time"),
  draftSentenceCount: document.getElementById("draft-sentence-count"),
  draftStatusIndicator: document.getElementById("draft-status-indicator"),
  
  hudStatusBanner: document.getElementById("hud-status-banner"),
  bannerIcon: document.getElementById("banner-icon"),
  bannerTitle: document.getElementById("banner-title"),
  bannerDesc: document.getElementById("banner-desc"),
  
  cardBurstiness: document.getElementById("card-burstiness"),
  valBurstiness: document.getElementById("val-burstiness"),
  badgeBurstiness: document.getElementById("badge-burstiness"),
  burstinessHistogram: document.getElementById("burstiness-histogram"),
  
  cardCliches: document.getElementById("card-cliches"),
  valCliches: document.getElementById("val-cliches"),
  badgeCliches: document.getElementById("badge-cliches"),
  clichesChips: document.getElementById("cliches-chips"),
  
  cardGrammar: document.getElementById("card-grammar"),
  valGrammar: document.getElementById("val-grammar"),
  badgeGrammar: document.getElementById("badge-grammar"),
  subtextGrammar: document.getElementById("subtext-grammar"),
  
  cardPlagiarism: document.getElementById("card-plagiarism"),
  valPlagiarism: document.getElementById("val-plagiarism"),
  badgePlagiarism: document.getElementById("badge-plagiarism"),
  fillPlagiarism: document.getElementById("fill-plagiarism"),
  
  cardEmDash: document.getElementById("card-em-dash"),
  valEmDash: document.getElementById("val-em-dash"),
  badgeEmDash: document.getElementById("badge-em-dash"),
  
  feedbackContent: document.getElementById("feedback-content"),
  btnInspectDetails: document.getElementById("btn-inspect-details"),
  
  activityDrawer: document.getElementById("activity-drawer"),
  drawerToggleBtn: document.getElementById("drawer-toggle-btn"),
  drawerLogsContainer: document.getElementById("drawer-logs-container"),
  logCount: document.getElementById("log-count"),
  
  engineModeLabel: document.getElementById("engine-mode-label"),
  btnOpenSettings: document.getElementById("btn-open-settings"),
  settingsDialog: document.getElementById("settings-dialog"),
  btnCloseSettings: document.getElementById("btn-close-settings"),
  inputGeminiKey: document.getElementById("input-gemini-key"),
  btnSaveKey: document.getElementById("btn-save-key"),
  btnClearKey: document.getElementById("btn-clear-key"),
  
  rulesDialog: document.getElementById("rules-dialog"),
  btnOpenRules: document.getElementById("btn-open-rules"),
  btnCloseRules: document.getElementById("btn-close-rules"),
  bannedTokensCloud: document.getElementById("banned-tokens-cloud"),
  
  detailsDialog: document.getElementById("details-dialog"),
  detailsDialogTitle: document.getElementById("details-dialog-title"),
  detailsDialogSubtitle: document.getElementById("details-dialog-subtitle"),
  detailsDialogBody: document.getElementById("details-dialog-body"),
  btnCloseDetails: document.getElementById("btn-close-details"),
  
  step1Tag: document.getElementById("step-1-tag"),
  step2Tag: document.getElementById("step-2-tag"),
  step3Tag: document.getElementById("step-3-tag"),
  stepReadyTag: document.getElementById("step-ready-tag"),
};

// Logging Helper
let logCounter = 0;
function addLog(tag, message, type = "normal") {
  logCounter++;
  const timeStr = new Date().toTimeString().split(" ")[0];
  const div = document.createElement("div");
  div.className = `log-entry log-${type}`;
  div.innerHTML = `
    <span class="log-time">${timeStr}</span>
    <span class="log-tag">${tag}</span>
    <span class="log-msg">${escapeHtml(message)}</span>
  `;
  el.drawerLogsContainer.appendChild(div);
  el.drawerLogsContainer.scrollTop = el.drawerLogsContainer.scrollHeight;
  el.logCount.textContent = `${logCounter} events`;
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function updateStepper(stage) {
  [el.step1Tag, el.step2Tag, el.step3Tag, el.stepReadyTag].forEach(s => s.className = "step-item");
  if (stage === "TRANSLATE") {
    el.step1Tag.className = "step-item active";
  } else if (stage === "AUDIT") {
    el.step1Tag.className = "step-item passed";
    el.step2Tag.className = "step-item active";
  } else if (stage === "PARAPHRASE") {
    el.step1Tag.className = "step-item passed";
    el.step2Tag.className = "step-item passed";
    el.step3Tag.className = "step-item active";
  } else if (stage === "READY") {
    el.step1Tag.className = "step-item passed";
    el.step2Tag.className = "step-item passed";
    el.step3Tag.className = "step-item passed";
    el.stepReadyTag.className = "step-item active passed";
  }
}

// Check Backend Health & Cliches
async function initBackendInfo() {
  if (state.apiKey) {
    el.engineModeLabel.textContent = "Gemini AI Active";
  } else {
    el.engineModeLabel.textContent = "Google Engine (Free)";
  }

  try {
    const res = await fetch("/api/v1/cliches");
    const data = await res.json();
    state.bannedCliches = data.cliches || {};
    renderBannedTokensCloud(state.bannedCliches);
  } catch (err) {
    console.warn("Could not fetch cliches", err);
  }
}

function renderBannedTokensCloud(cliches) {
  el.bannedTokensCloud.innerHTML = "";
  Object.keys(cliches).forEach(word => {
    const span = document.createElement("span");
    span.className = "banned-token-badge";
    span.textContent = word;
    span.title = `Suggested: ${cliches[word]}`;
    el.bannedTokensCloud.appendChild(span);
  });
}

// Settings Dialog
el.btnOpenSettings.addEventListener("click", () => {
  el.inputGeminiKey.value = state.apiKey;
  el.settingsDialog.showModal();
});
el.btnCloseSettings.addEventListener("click", () => el.settingsDialog.close());

el.btnSaveKey.addEventListener("click", () => {
  state.apiKey = el.inputGeminiKey.value.trim();
  if (state.apiKey) {
    localStorage.setItem("carik_gemini_api_key", state.apiKey);
    el.engineModeLabel.textContent = "Gemini AI Active";
    addLog("SETTINGS", "Saved Gemini API Key", "system");
  } else {
    localStorage.removeItem("carik_gemini_api_key");
    el.engineModeLabel.textContent = "Google Engine (Free)";
    addLog("SETTINGS", "Switched to Free Engine", "system");
  }
  el.settingsDialog.close();
});

el.btnClearKey.addEventListener("click", () => {
  state.apiKey = "";
  localStorage.removeItem("carik_gemini_api_key");
  el.inputGeminiKey.value = "";
  el.engineModeLabel.textContent = "Google Engine (Free)";
  addLog("SETTINGS", "Cleared Gemini API Key", "system");
  el.settingsDialog.close();
});

// WebSocket Connection
function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/pipeline-progress`;
  
  state.ws = new WebSocket(wsUrl);

  state.ws.onopen = () => {
    addLog("WS", "Connected to pipeline stream", "system");
  };

  state.ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleWsMessage(msg);
    } catch (err) {
      console.error("WS Parse error", err);
    }
  };

  state.ws.onclose = () => {
    setTimeout(connectWebSocket, 3000);
  };
}

function handleWsMessage(msg) {
  const { event, data } = msg;
  addLog(event, data.status || event);

  if (event.includes("TRANSLATING")) {
    updateStepper("TRANSLATE");
  } else if (event.includes("AUDITING")) {
    updateStepper("AUDIT");
  } else if (event.includes("STAGE_3")) {
    updateStepper("PARAPHRASE");
  } else if (event.includes("PASSED") || event.includes("READY")) {
    updateStepper("READY");
  }

  if (data.status) {
    updatePipelineStatusBadge(data.status);
  }

  if (data.latest_report) {
    state.latestReport = data.latest_report;
    updateHUD(data.latest_report);
  }
}

// Text Input Events
el.sourceTextarea.addEventListener("input", () => {
  state.sourceText = el.sourceTextarea.value;
  const chars = state.sourceText.length;
  const words = state.sourceText.trim() ? state.sourceText.trim().split(/\s+/).length : 0;
  el.charCount.textContent = `${chars} chars`;
  el.wordCount.textContent = `${words} words`;
});

el.sampleSelect.addEventListener("change", (e) => {
  const key = e.target.value;
  if (key && SAMPLE_DRAFTS[key]) {
    el.sourceTextarea.value = SAMPLE_DRAFTS[key];
    el.sourceTextarea.dispatchEvent(new Event("input"));
    addLog("SAMPLE", `Loaded sample: ${key}`);
  }
});

// Start Process
el.btnStart.addEventListener("click", async () => {
  const text = el.sourceTextarea.value.trim();
  if (!text) {
    alert("Silakan masukkan teks draft artikel terlebih dahulu.");
    return;
  }

  setProcessing(true);
  updateStepper("TRANSLATE");
  state.drafts = [{ iteration: 0, title: "Original (Bahasa)", text }];
  renderDraftTabs();
  selectTab(0);
  addLog("PROCESS", "Executing Stage 1: Translation (conorbronsdon style)...");

  try {
    const res = await fetch("/api/v1/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        max_retries: parseInt(el.maxRetriesSelect.value, 10),
        target_tone: "editorial",
        api_key: state.apiKey || null
      })
    });

    const data = await res.json();
    if (data.success || data.final_draft) {
      handleProcessComplete(data);
    }
  } catch (err) {
    addLog("ERROR", err.message, "error");
    alert("Terjadi kesalahan: " + err.message);
  } finally {
    setProcessing(false);
  }
});

// Audit English Only Button
el.btnAuditOnly.addEventListener("click", async () => {
  const text = el.sourceTextarea.value.trim();
  if (!text) {
    alert("Masukkan teks bahasa Inggris untuk diaudit.");
    return;
  }

  setProcessing(true);
  updateStepper("AUDIT");
  addLog("AUDIT", "Running Stage 2: Deterministic Audit...");

  try {
    const res = await fetch("/api/v1/audit-only", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const report = await res.json();
    state.latestReport = report;
    state.drafts = [{ iteration: 1, title: "English Draft", text }];
    renderDraftTabs();
    selectTab(0);
    updateHUD(report);
    if (report.metrics.is_passing) {
      updateStepper("READY");
    }
    addLog("AUDIT_DONE", `Audit finished. Passed: ${report.metrics.is_passing}`);
  } catch (err) {
    addLog("ERROR", err.message, "error");
    alert("Audit error: " + err.message);
  } finally {
    setProcessing(false);
  }
});

function setProcessing(loading) {
  state.isProcessing = loading;
  el.btnStart.disabled = loading;
  el.btnAuditOnly.disabled = loading;
  if (loading) {
    el.draftContainer.classList.add("is-processing");
  } else {
    el.draftContainer.classList.remove("is-processing");
  }
}

function handleProcessComplete(data) {
  const { final_draft, processing_time_sec } = data;
  addLog("COMPLETE", `Flow finished in ${processing_time_sec}s with status: ${final_draft.status}`, "system");

  state.drafts = [
    { iteration: 0, title: "Original (Bahasa)", text: final_draft.original_bahasa }
  ];

  // Stage 1 Translation
  if (final_draft.iteration_history.length > 0 && final_draft.iteration_history[0].draft_snapshot) {
    state.drafts.push({
      iteration: 1,
      title: "Stage 1: Translated",
      text: final_draft.iteration_history[0].draft_snapshot,
      report: final_draft.iteration_history[0]
    });
  }

  // Stage 3 Sub-Passes
  if (final_draft.sub_pass_history && final_draft.sub_pass_history.length > 0) {
    final_draft.sub_pass_history.forEach((sub, sIdx) => {
      state.drafts.push({
        iteration: sIdx + 2,
        title: sub.pass_name.split(":")[0],
        text: sub.revised_text,
        subPass: sub
      });
    });
  }

  // Ready Article
  state.drafts.push({
    iteration: state.drafts.length,
    title: final_draft.status === "PASSED" ? "✨ Ready Article" : "Final Draft",
    text: final_draft.current_english_draft,
    report: final_draft.iteration_history[final_draft.iteration_history.length - 1]
  });

  renderDraftTabs();
  selectTab(state.drafts.length - 1);

  if (final_draft.iteration_history.length > 0) {
    const lastReport = final_draft.iteration_history[final_draft.iteration_history.length - 1];
    state.latestReport = lastReport;
    updateHUD(lastReport);
  }

  updatePipelineStatusBadge(final_draft.status);
  updateStepper(final_draft.status === "PASSED" ? "READY" : "AUDIT");
}

function renderDraftTabs() {
  el.draftVersionTabs.innerHTML = "";
  state.drafts.forEach((d, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `tab-btn ${state.activeTab === idx ? "active" : ""}`;
    btn.textContent = d.title;
    btn.onclick = () => selectTab(idx);
    el.draftVersionTabs.appendChild(btn);
  });
}

function selectTab(idx) {
  state.activeTab = idx;
  const draft = state.drafts[idx];
  if (!draft) return;

  renderDraftTabs();
  renderDraftContent(draft.text, draft.report || state.latestReport);
}

// Clean Paragraph and Markdown Formatter
function formatEditorialProse(text, cliches = []) {
  if (!text) return "";
  
  const paragraphs = text.split(/\n\n+/);
  const htmlBlocks = [];

  paragraphs.forEach(rawPara => {
    const para = rawPara.trim();
    if (!para) return;

    // Headers
    if (para.startsWith("### ")) {
      htmlBlocks.push(`<h4 class="prose-heading-3">${escapeHtml(para.substring(4))}</h4>`);
      return;
    }
    if (para.startsWith("## ")) {
      htmlBlocks.push(`<h3 class="prose-heading-2">${escapeHtml(para.substring(3))}</h3>`);
      return;
    }
    if (para.startsWith("# ")) {
      htmlBlocks.push(`<h2 class="prose-heading-1">${escapeHtml(para.substring(2))}</h2>`);
      return;
    }

    // Blockquote
    if (para.startsWith("> ")) {
      htmlBlocks.push(`<blockquote class="prose-quote">${escapeHtml(para.substring(2))}</blockquote>`);
      return;
    }

    // List item
    if (para.startsWith("- ") || para.startsWith("* ")) {
      const items = para.split(/\n[-*]\s+/).filter(i => i.trim());
      const listHtml = items.map(it => `<li>${escapeHtml(it.replace(/^[-*]\s+/, ""))}</li>`).join("");
      htmlBlocks.push(`<ul class="prose-list">${listHtml}</ul>`);
      return;
    }

    // Regular Paragraph
    let pText = escapeHtml(para);
    if (state.viewMode === "highlights" && cliches.length > 0) {
      cliches.forEach(word => {
        const reg = new RegExp(`\\b(${word})\\b`, "gi");
        const replacement = state.bannedCliches[word.toLowerCase()] || "simplify";
        pText = pText.replace(reg, `<mark class="pill-cliche" title="Suggested: ${replacement}">$1</mark>`);
      });
    }

    htmlBlocks.push(`<p class="prose-p">${pText}</p>`);
  });

  return htmlBlocks.join("");
}

function renderDraftContent(text, report) {
  if (!text) {
    el.draftEmptyState.classList.remove("hidden");
    el.proseContent.classList.add("hidden");
    return;
  }

  el.draftEmptyState.classList.add("hidden");
  el.proseContent.classList.remove("hidden");

  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
  const readTime = Math.max(1, Math.ceil(words / 200));

  el.draftWordCount.textContent = `${words} words`;
  el.draftReadTime.textContent = `${readTime} min read`;
  el.draftSentenceCount.textContent = `${sentences} sentences`;

  const cliches = (report && report.metrics) ? report.metrics.cliche_matches : [];
  el.proseContent.innerHTML = formatEditorialProse(text, cliches);
}

// View Mode Toggles
el.btnModeClean.addEventListener("click", () => {
  state.viewMode = "clean";
  el.btnModeClean.classList.add("active");
  el.btnModeHighlights.classList.remove("active");
  const draft = state.drafts[state.activeTab];
  if (draft) renderDraftContent(draft.text, draft.report || state.latestReport);
});

el.btnModeHighlights.addEventListener("click", () => {
  state.viewMode = "highlights";
  el.btnModeHighlights.classList.add("active");
  el.btnModeClean.classList.remove("active");
  const draft = state.drafts[state.activeTab];
  if (draft) renderDraftContent(draft.text, draft.report || state.latestReport);
});

// Copy & Export
el.btnCopyDraft.addEventListener("click", () => {
  const draft = state.drafts[state.activeTab];
  if (draft && draft.text) {
    navigator.clipboard.writeText(draft.text);
    addLog("CLIPBOARD", "Draft copied to clipboard");
  }
});

el.btnExportMd.addEventListener("click", () => {
  const draft = state.drafts[state.activeTab];
  if (!draft || !draft.text) return;

  const blob = new Blob([draft.text], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `carik-draft.md`;
  a.click();
  URL.revokeObjectURL(url);
  addLog("EXPORT", "Downloaded markdown file");
});

// Update HUD & Quality Gauges
function updateHUD(report) {
  if (!report || !report.metrics) return;
  const m = report.metrics;

  if (m.is_passing) {
    el.hudStatusBanner.className = "hud-status-banner banner-pass";
    el.bannerIcon.textContent = "✅";
    el.bannerTitle.textContent = `All Checks Passed (Ready Article)`;
    el.bannerDesc.textContent = "All editorial standards met. Ready for publication.";
  } else {
    el.hudStatusBanner.className = "hud-status-banner banner-fail";
    el.bannerIcon.textContent = "⚠️";
    el.bannerTitle.textContent = `Stage 2: Issues Detected (Loop #${report.iteration})`;
    el.bannerDesc.textContent = "Draft routed to Stage 3: Multi-Pass Paraphrase.";
  }

  // 1. Burstiness
  el.valBurstiness.textContent = m.burstiness_score.toFixed(1);
  const burstPass = m.burstiness_score >= 8.5;
  el.cardBurstiness.setAttribute("data-status", burstPass ? "pass" : "fail");
  el.badgeBurstiness.className = `metric-badge ${burstPass ? "badge-pass" : "badge-fail"}`;
  el.badgeBurstiness.textContent = burstPass ? "OPTIMAL" : "MONOTONOUS";
  renderHistogram(m.sentence_lengths, burstPass);

  // 2. Cliches
  const clicheCount = m.cliche_matches.length;
  el.valCliches.textContent = clicheCount;
  const clichePass = clicheCount === 0;
  el.cardCliches.setAttribute("data-status", clichePass ? "pass" : "fail");
  el.badgeCliches.className = `metric-badge ${clichePass ? "badge-pass" : "badge-fail"}`;
  el.badgeCliches.textContent = clichePass ? "CLEAN" : `${clicheCount} FLAGGED`;
  renderClicheChips(m.cliche_matches);

  // 3. Grammar
  el.valGrammar.textContent = m.critical_grammar_errors;
  const gramPass = m.critical_grammar_errors === 0;
  el.cardGrammar.setAttribute("data-status", gramPass ? "pass" : "fail");
  el.badgeGrammar.className = `metric-badge ${gramPass ? "badge-pass" : "badge-fail"}`;
  el.badgeGrammar.textContent = gramPass ? "ZERO ERRORS" : `${m.critical_grammar_errors} ISSUES`;

  // 4. Plagiarism
  const plagPct = (m.plagiarism_ratio * 100).toFixed(1);
  el.valPlagiarism.textContent = `${plagPct}%`;
  const plagPass = m.plagiarism_ratio < 0.08;
  el.cardPlagiarism.setAttribute("data-status", plagPass ? "pass" : "fail");
  el.badgePlagiarism.className = `metric-badge ${plagPass ? "badge-pass" : "badge-fail"}`;
  el.badgePlagiarism.textContent = plagPass ? "ORIGINAL" : "SIMILAR";
  el.fillPlagiarism.style.width = `${Math.min(100, m.plagiarism_ratio * 100 * 2)}%`;
  el.fillPlagiarism.className = `progress-bar-fill ${plagPass ? "" : "fail"}`;

  // 5. Em-dash
  el.valEmDash.textContent = m.em_dash_count;
  const emPass = m.em_dash_count <= 2;
  el.cardEmDash.setAttribute("data-status", emPass ? "pass" : "fail");
  el.badgeEmDash.className = `metric-badge ${emPass ? "badge-pass" : "badge-fail"}`;
  el.badgeEmDash.textContent = emPass ? "LEAN" : "OVERUSED";

  // Feedback Content
  el.feedbackContent.textContent = report.feedback_summary || "No specific feedback.";
}

function renderHistogram(lengths, isPass) {
  el.burstinessHistogram.innerHTML = "";
  if (!lengths || lengths.length === 0) return;

  const maxLen = Math.max(...lengths, 20);
  lengths.slice(0, 24).forEach(len => {
    const bar = document.createElement("div");
    bar.className = `hist-bar ${isPass ? "pass" : "fail"}`;
    const pct = Math.max(10, Math.min(100, (len / maxLen) * 100));
    bar.style.height = `${pct}%`;
    bar.title = `${len} words`;
    el.burstinessHistogram.appendChild(bar);
  });
}

function renderClicheChips(cliches) {
  el.clichesChips.innerHTML = "";
  if (!cliches || cliches.length === 0) {
    el.clichesChips.innerHTML = '<span class="empty-chip">No clichés detected</span>';
    return;
  }
  cliches.forEach(word => {
    const chip = document.createElement("span");
    chip.className = "cliche-chip";
    chip.textContent = word;
    chip.title = `Suggested: ${state.bannedCliches[word.toLowerCase()] || "cut/replace"}`;
    el.clichesChips.appendChild(chip);
  });
}

function updatePipelineStatusBadge(status) {
  el.draftStatusIndicator.innerHTML = "";
  const pill = document.createElement("span");
  pill.className = `status-pill ${status === "PASSED" ? "status-success" : "status-active"}`;
  pill.textContent = status;
  el.draftStatusIndicator.appendChild(pill);
}

// Drawer Toggle
el.drawerToggleBtn.addEventListener("click", () => {
  el.activityDrawer.classList.toggle("collapsed");
});

// Dialogs
el.btnOpenRules.addEventListener("click", () => el.rulesDialog.showModal());
el.btnCloseRules.addEventListener("click", () => el.rulesDialog.close());

el.btnInspectDetails.addEventListener("click", () => {
  if (!state.latestReport) {
    alert("Belum ada data audit.");
    return;
  }
  const rep = state.latestReport;
  el.detailsDialogTitle.textContent = `Audit Breakdown: Loop #${rep.iteration}`;
  el.detailsDialogSubtitle.textContent = `Timestamp: ${rep.timestamp || "N/A"}`;
  
  let html = `
    <div style="display:flex; flex-direction:column; gap:0.75rem;">
      <div class="feedback-card">
        <h4 style="font-size:0.85rem; font-weight:700;">Summary Guidance</h4>
        <p style="white-space:pre-line; color:var(--text-secondary);">${escapeHtml(rep.feedback_summary)}</p>
      </div>
  `;

  if (rep.flagged_sentences && rep.flagged_sentences.length > 0) {
    html += `
      <div class="feedback-card">
        <h4 style="font-size:0.85rem; font-weight:700;">Flagged Offsets & Recommendations</h4>
        <ul style="padding-left:1.2rem; color:var(--text-secondary); font-size:0.78rem;">
          ${rep.flagged_sentences.map(s => `<li>${escapeHtml(s)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  html += `</div>`;
  el.detailsDialogBody.innerHTML = html;
  el.detailsDialog.showModal();
});
el.btnCloseDetails.addEventListener("click", () => el.detailsDialog.close());

// Initialize
initBackendInfo();
connectWebSocket();
