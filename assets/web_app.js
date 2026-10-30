// Application State
const state = {
  resumeData: null,
  resumeFormatted: "",
  applications: [],
  config: {
    model_list: ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
    default_temperature: 0.2
  }
};

// Sample Job Profile for quick testing
const SAMPLE_JOB_PROFILE = `Senior Software Engineer / Machine Learning
Location: Remote / Calgary, AB
Experience: 3+ years

Responsibilities:
• Architect, build, and deploy high-throughput microservices in Python, Go, and Docker/Kubernetes.
• Train, fine-tune, and evaluate deep learning and reinforcement learning models using PyTorch and TensorFlow.
• Implement scalable data pipelines using SQL, PostgreSQL, and Kafka.
• Design CI/CD workflows and automated testing suites using GitHub Actions and Pytest.
• Collaborate with cross-functional product teams to deliver client-facing features in an Agile environment.

Requirements & Qualifications:
• B.S. or M.S. in Computer Science, Software Engineering, or related quantitative field.
• Proven expertise with Python, PyTorch, Scikit-learn, and cloud platforms (AWS / GCP).
• Familiarity with modern containerization, Kubernetes, and distributed streaming architectures.
• Strong communication, leadership, and analytical problem-solving skills.`;

// DOM Elements
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSettings();
  loadConfig();
  loadResume();
  loadApplications();
  bindActions();
});

// Tab Switcher
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
      });
      document.getElementById(targetId).classList.add("active");
    });
  });
}

// Settings initialization
function initSettings() {
  const tempSlider = document.getElementById("tempSlider");
  const tempVal = document.getElementById("tempVal");
  tempSlider.addEventListener("input", (e) => {
    tempVal.textContent = parseFloat(e.target.value).toFixed(1);
  });

  const apiKeyInput = document.getElementById("apiKeyInput");
  const savedKey = localStorage.getItem("gemini_api_key");
  if (savedKey) {
    apiKeyInput.value = savedKey;
  }
  apiKeyInput.addEventListener("change", (e) => {
    localStorage.setItem("gemini_api_key", e.target.value.trim());
  });
}

// Bind Button Actions
function bindActions() {
  // Load Sample JD
  document.getElementById("btnLoadSample").addEventListener("click", () => {
    document.getElementById("jobProfileInput").value = SAMPLE_JOB_PROFILE;
    showToast("Sample Job Profile loaded!");
  });

  // Clear JD
  document.getElementById("btnClearJob").addEventListener("click", () => {
    document.getElementById("jobProfileInput").value = "";
  });

  // Apply Settings / Analyze Match Button
  document.getElementById("btnApply").addEventListener("click", handleAnalyze);

  // Job Tracker Actions
  document.getElementById("btnAddApp").addEventListener("click", addApplicationRow);
  document.getElementById("btnSaveApps").addEventListener("click", saveApplications);
  document.getElementById("btnExportCsv").addEventListener("click", exportApplicationsCsv);
}

// Load Config
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    if (res.ok) {
      const data = await res.json();
      state.config = data;
    }
  } catch (e) {
    console.log("Using static config fallback");
  }

  // Populate model selector
  const modelSelect = document.getElementById("modelSelect");
  modelSelect.innerHTML = "";
  state.config.model_list.forEach(model => {
    const opt = document.createElement("option");
    opt.value = model;
    opt.textContent = model;
    modelSelect.appendChild(opt);
  });
}

// Load Resume
async function loadResume() {
  const resumeBox = document.getElementById("resumeBox");
  try {
    const res = await fetch("/api/resume");
    if (res.ok) {
      const data = await res.json();
      state.resumeData = data.raw;
      state.resumeFormatted = data.formatted;
      resumeBox.value = data.formatted;
      return;
    }
  } catch (e) {
    console.log("Direct API unavailable, attempting static file fetch...");
  }

  // Static fetch fallback for data/resume_info.json
  try {
    const staticRes = await fetch("data/resume_info.json");
    if (staticRes.ok) {
      const jsonData = await staticRes.json();
      state.resumeData = jsonData;
      state.resumeFormatted = formatResumeClient(jsonData);
      resumeBox.value = state.resumeFormatted;
    }
  } catch (err) {
    resumeBox.value = "Failed to load resume. Please check data/resume_info.json.";
  }
}

// Format Resume on Client (mirrors src/utils.py format_resume)
function formatResumeClient(data) {
  const lines = [];
  if (data.education) {
    lines.push("Education:\n----------");
    lines.push(`- *Degree*: ${data.education.degree || ""}`);
    lines.push(`- *fieldOfStudy*: ${data.education.fieldOfStudy || ""}`);
    lines.push(`- *School*: ${data.education.school || ""}`);
    if (data.education.courses) {
      lines.push(`- *Courses*: ${data.education.courses.join(", ")}`);
    }
    lines.push("");
  }

  if (data.work) {
    lines.push("Work Experience:\n-----------------");
    let i = 1;
    for (const [k, comp] of Object.entries(data.work)) {
      lines.push(`${i}. **${comp.name}**`);
      lines.push(`   *Position*: ${comp.position}`);
      lines.push(`   *Duration*: ${comp.startDate} - ${comp.endDate}`);
      lines.push("   *Highlights*:");
      if (comp.highlights) {
        comp.highlights.forEach(h => lines.push(`   - ${h}`));
      }
      lines.push("");
      i++;
    }
  }

  if (data.skills) {
    lines.push("Skills:\n-------");
    for (const [cat, sk] of Object.entries(data.skills)) {
      lines.push(`- **${cat}**: ${Array.isArray(sk) ? sk.join(", ") : sk}`);
    }
  }

  return lines.join("\n");
}

// Handle Match Analysis
async function handleAnalyze() {
  const jobProfile = document.getElementById("jobProfileInput").value.trim();
  if (!jobProfile) {
    alert("Please enter a job profile description first.");
    return;
  }

  const modelName = document.getElementById("modelSelect").value;
  const temperature = parseFloat(document.getElementById("tempSlider").value);
  const apiKey = document.getElementById("apiKeyInput").value.trim();

  const needShort = document.getElementById("toggleShorten").checked;
  const needScore = document.getElementById("toggleScore").checked;
  const needMissing = document.getElementById("toggleMissing").checked;
  const needDivide = document.getElementById("toggleDivide").checked;

  const btn = document.getElementById("btnApply");
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner">⏳</span> Analyzing...`;

  try {
    const payload = {
      job_profile: jobProfile,
      resume_text: state.resumeFormatted,
      model_name: modelName,
      temperature: temperature,
      need_short_JB: needShort,
      need_match_score: needScore,
      need_missing_skills: needMissing,
      need_divide_missing_skills: needDivide,
      api_key: apiKey
    };

    let resultData = null;

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const json = await res.json();
        resultData = json.data;
        if (json.message) {
          showToast(json.message);
        }
      }
    } catch (e) {
      console.log("Server API not reachable, running client preview...");
    }

    // Client fallback if no server response
    if (!resultData) {
      resultData = generateClientPreview(jobProfile, state.resumeFormatted);
      showToast("Displayed analysis in preview mode");
    }

    renderResults(resultData, { needShort, needScore, needMissing, needDivide });

  } catch (err) {
    console.error(err);
    alert("Error performing analysis: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
}

// Client Preview Generator (Fallback)
function generateClientPreview(jobProfile, resumeText) {
  return {
    short_job_profile: "• Core Qualifications: Strong foundation in software architecture, cloud engineering, and data systems\n• Key Requirements: Expertise in Python/Distributed Systems, container orchestration, and CI/CD pipelines\n• Target Domain: High-throughput engineering, ML integration, and real-time data processing",
    match_score: 82,
    missing_skills: {
      "Programming Languages": ["Go", "TypeScript"],
      "Tools": ["Kubernetes", "AWS", "Jira"],
      "Libraries": ["FastAPI"],
      "Soft Skills": ["Cross-functional Leadership", "Agile Project Ownership"],
      "Miscellaneous": ["Distributed Microservices", "Kafka Streaming"]
    },
    divide_missing_skills: {
      "Software Developer": ["Go", "TypeScript", "Microservices", "Kafka Streaming"],
      "ML Engineer/Data Scientist": ["Kubernetes", "AWS"],
      "Data Analyst": ["Jira"]
    }
  };
}

// Render Results onto the UI
function renderResults(data, toggles) {
  const container = document.getElementById("resultsContainer");
  container.innerHTML = "";

  // 1. Short Job Profile
  if (toggles.needShort && data.short_job_profile) {
    const card = document.createElement("div");
    card.className = "result-card";
    card.innerHTML = `
      <div class="result-header">Short Job Profile</div>
      <div class="rainbow-divider"></div>
      <div style="white-space: pre-line; line-height: 1.6; color: #334155; font-size: 14px;">${escapeHtml(data.short_job_profile)}</div>
    `;
    container.appendChild(card);
  }

  // 2. Match Score
  if (toggles.needScore && typeof data.match_score !== "undefined") {
    const score = parseInt(data.match_score) || 0;
    const barColor = score >= 70 ? "#22c55e" : score >= 40 ? "#f97316" : "#ef4444";
    const message = score >= 70 ? "Good match!" : score >= 40 ? "Fair match!" : "Poor match!";

    const card = document.createElement("div");
    card.className = "result-card";
    card.innerHTML = `
      <div class="result-header">Job Match Score:</div>
      <div class="rainbow-divider"></div>
      <div class="progress-bar-container">
        <div class="progress-bar" style="width: ${score}%; background-color: ${barColor};">
          ${score}%
        </div>
      </div>
      <div class="score-message">${message}</div>
    `;
    container.appendChild(card);
  }

  // 3. Missing Skills
  if (toggles.needMissing && data.missing_skills) {
    const ms = data.missing_skills;
    const card = document.createElement("div");
    card.className = "result-card";

    const renderList = (items) => {
      if (!items || items.length === 0) return '<div style="font-size: 13px; color: #94a3b8;">None identified</div>';
      return `<ul class="skill-list">${items.map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>`;
    };

    card.innerHTML = `
      <div class="result-header">Missing Skills</div>
      <div class="rainbow-divider"></div>
      <div class="skills-grid-3">
        <div class="skill-category-box">
          <div class="skill-category-title">Programming Languages</div>
          ${renderList(ms["Programming Languages"])}
        </div>
        <div class="skill-category-box">
          <div class="skill-category-title">Tools</div>
          ${renderList(ms["Tools"])}
        </div>
        <div class="skill-category-box">
          <div class="skill-category-title">Libraries</div>
          ${renderList(ms["Libraries"])}
        </div>
      </div>
      <div class="skills-grid-2">
        <div class="skill-category-box">
          <div class="skill-category-title">Soft Skills</div>
          ${renderList(ms["Soft Skills"])}
        </div>
        <div class="skill-category-box">
          <div class="skill-category-title">Miscellaneous</div>
          ${renderList(ms["Miscellaneous"])}
        </div>
      </div>
    `;
    container.appendChild(card);
  }

  // 4. Divided Missing Skills
  if (toggles.needDivide && data.divide_missing_skills) {
    const dms = data.divide_missing_skills;
    const card = document.createElement("div");
    card.className = "result-card";

    const renderBadges = (items) => {
      if (!items || items.length === 0) return '<div style="font-size: 13px; color: #94a3b8;">None</div>';
      return items.map(s => `<span class="skill-badge">${escapeHtml(s)}</span>`).join(" ");
    };

    card.innerHTML = `
      <div class="result-header">Divided Missing Skills</div>
      <div class="rainbow-divider"></div>
      <div class="skills-grid-3">
        <div class="skill-category-box">
          <div class="skill-category-title">Software Developer</div>
          ${renderBadges(dms["Software Developer"])}
        </div>
        <div class="skill-category-box">
          <div class="skill-category-title">ML Engineer/Data Scientist</div>
          ${renderBadges(dms["ML Engineer/Data Scientist"])}
        </div>
        <div class="skill-category-box">
          <div class="skill-category-title">Data Analyst</div>
          ${renderBadges(dms["Data Analyst"])}
        </div>
      </div>
    `;
    container.appendChild(card);
  }

  // Scroll smoothly to results
  container.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------------- JOB TRACKER ----------------
async function loadApplications() {
  try {
    const res = await fetch("/api/applications");
    if (res.ok) {
      const data = await res.json();
      state.applications = data.applications || [];
      renderApplicationsTable();
      return;
    }
  } catch (e) {
    console.log("Server API not available for applications, fetching static CSV...");
  }

  // Static CSV fallback
  try {
    const csvRes = await fetch("data/job_tracker/job_applications.csv");
    if (csvRes.ok) {
      const csvText = await csvRes.text();
      state.applications = parseCsv(csvText);
      renderApplicationsTable();
    }
  } catch (e) {
    console.log("No CSV found, starting empty");
    state.applications = [];
    renderApplicationsTable();
  }
}

function parseCsv(text) {
  const lines = text.trim().split("\n");
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map(h => h.trim());
  const rows = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const parts = line.split(",").map(p => p.trim());
    const obj = {};
    headers.forEach((h, idx) => {
      const val = parts[idx] || "";
      if (["Applied", "Optimized", "LinkedIn Reach", "Cold Email", "Selected"].includes(h)) {
        obj[h] = val.toLowerCase() === "true" || val === "1";
      } else {
        obj[h] = val;
      }
    });
    rows.push(obj);
  }
  return rows;
}

function renderApplicationsTable() {
  const tbody = document.getElementById("trackerTableBody");
  tbody.innerHTML = "";

  if (state.applications.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: #94a3b8; padding: 24px;">No applications tracked yet. Click "+ Add Application" above.</td></tr>`;
    return;
  }

  state.applications.forEach((row, index) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td><input type="date" class="tracker-input" value="${row.Date || ''}" onchange="updateRowField(${index}, 'Date', this.value)"></td>
      <td><input type="text" class="tracker-input" placeholder="Company" value="${escapeHtml(row.Company || '')}" onchange="updateRowField(${index}, 'Company', this.value)"></td>
      <td><input type="text" class="tracker-input" placeholder="Position" value="${escapeHtml(row.Position || '')}" onchange="updateRowField(${index}, 'Position', this.value)"></td>
      <td><input type="text" class="tracker-input" placeholder="https://..." value="${escapeHtml(row.Link || '')}" onchange="updateRowField(${index}, 'Link', this.value)"></td>
      <td style="text-align:center;"><input type="checkbox" class="table-checkbox" ${row.Applied ? 'checked' : ''} onchange="updateRowField(${index}, 'Applied', this.checked)"></td>
      <td style="text-align:center;"><input type="checkbox" class="table-checkbox" ${row.Optimized ? 'checked' : ''} onchange="updateRowField(${index}, 'Optimized', this.checked)"></td>
      <td style="text-align:center;"><input type="checkbox" class="table-checkbox" ${row['LinkedIn Reach'] ? 'checked' : ''} onchange="updateRowField(${index}, 'LinkedIn Reach', this.checked)"></td>
      <td style="text-align:center;"><input type="checkbox" class="table-checkbox" ${row['Cold Email'] ? 'checked' : ''} onchange="updateRowField(${index}, 'Cold Email', this.checked)"></td>
      <td style="text-align:center;"><input type="checkbox" class="table-checkbox" ${row.Selected ? 'checked' : ''} onchange="updateRowField(${index}, 'Selected', this.checked)"></td>
      <td>
        <select class="tracker-select stage-${row.Stage || 'Applied'}" onchange="updateRowField(${index}, 'Stage', this.value); this.className = 'tracker-select stage-' + this.value;">
          <option value="Applied" ${row.Stage === 'Applied' ? 'selected' : ''}>Applied</option>
          <option value="Interview" ${row.Stage === 'Interview' ? 'selected' : ''}>Interview</option>
          <option value="Offer" ${row.Stage === 'Offer' ? 'selected' : ''}>Offer</option>
          <option value="Rejected" ${row.Stage === 'Rejected' ? 'selected' : ''}>Rejected</option>
        </select>
      </td>
      <td style="text-align:center;">
        <button class="btn-delete-row" title="Delete Row" onclick="deleteRow(${index})">✕</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.updateRowField = function(index, field, value) {
  if (state.applications[index]) {
    state.applications[index][field] = value;
  }
};

window.deleteRow = function(index) {
  state.applications.splice(index, 1);
  renderApplicationsTable();
};

function addApplicationRow() {
  const today = new Date().toISOString().split("T")[0];
  state.applications.unshift({
    Date: today,
    Company: "",
    Position: "",
    Link: "",
    Applied: true,
    Optimized: false,
    "LinkedIn Reach": false,
    "Cold Email": false,
    Selected: false,
    Stage: "Applied"
  });
  renderApplicationsTable();
}

async function saveApplications() {
  try {
    const res = await fetch("/api/applications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ applications: state.applications })
    });
    if (res.ok) {
      showToast("Changes saved successfully to job_applications.csv!");
      return;
    }
  } catch (e) {
    console.log("Local API unavailable for saving, falling back to download");
  }

  exportApplicationsCsv();
  showToast("Saved applications (CSV downloaded)!");
}

function exportApplicationsCsv() {
  const headers = ["Date", "Company", "Position", "Link", "Applied", "Optimized", "LinkedIn Reach", "Cold Email", "Selected", "Stage"];
  const rows = [headers.join(",")];

  state.applications.forEach(app => {
    const r = headers.map(h => {
      const v = app[h];
      return typeof v === "boolean" ? (v ? "True" : "False") : `"${(v || '').toString().replace(/"/g, '""')}"`;
    });
    rows.push(r.join(","));
  });

  const blob = new Blob([rows.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "job_applications.csv";
  a.click();
  URL.revokeObjectURL(url);
}

// Utilities
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showToast(msg) {
  let toast = document.getElementById("toastMsg");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toastMsg";
    toast.className = "toast-msg";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 3500);
}

