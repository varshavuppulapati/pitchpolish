(function () {
  const form = document.getElementById("tailor-form");
  const submitBtn = document.getElementById("submit-btn");
  const btnLabel = submitBtn.querySelector(".btn-label");
  const spinner = submitBtn.querySelector(".spinner");
  const errorBox = document.getElementById("error");
  const results = document.getElementById("results");
  const dropzone = document.getElementById("dropzone");
  const dropzoneText = document.getElementById("dropzone-text");
  const fileInput = document.getElementById("resume_file");
  const roleHint = document.getElementById("role_hint");

  let lastRewritten = null;
  let lastJobDescription = "";

  /* ---------- tabs ---------- */
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.add("hidden"));
      tab.classList.add("active");
      document.querySelector(`.tab-panel[data-panel="${tab.dataset.tab}"]`).classList.remove("hidden");
    });
  });

  /* ---------- role chips ---------- */
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const already = chip.classList.contains("active");
      document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      if (already) {
        roleHint.value = "";
      } else {
        chip.classList.add("active");
        roleHint.value = chip.dataset.role;
      }
    });
  });

  /* ---------- compare toggle ---------- */
  const toggleCompare = document.getElementById("toggle-compare");
  const compareField = document.getElementById("compare-field");
  const compareBtn = document.getElementById("compare-btn");
  toggleCompare.addEventListener("click", () => {
    compareField.classList.toggle("hidden");
    compareBtn.classList.toggle("hidden");
    toggleCompare.textContent = compareField.classList.contains("hidden")
      ? "+ Compare against more jobs"
      : "− Hide comparison";
  });

  /* ---------- drag & drop ---------- */
  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    })
  );
  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      fileInput.files = e.dataTransfer.files;
      dropzoneText.textContent = file.name;
    }
  });
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) dropzoneText.textContent = fileInput.files[0].name;
  });

  /* ---------- steps ---------- */
  function setStep(n) {
    document.querySelectorAll(".step").forEach((s) => {
      const step = parseInt(s.dataset.step, 10);
      s.classList.toggle("active", step === n);
      s.classList.toggle("done", step < n);
    });
  }

  /* ---------- main submit ---------- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.classList.add("hidden");
    results.classList.add("hidden");
    document.getElementById("cover-letter-box").classList.add("hidden");
    setLoading(true);
    setStep(2);

    lastJobDescription = document.getElementById("job_description").value.trim();

    try {
      const res = await fetch("/api/tailor", { method: "POST", body: new FormData(form) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      lastRewritten = data.rewritten;
      renderResults(data);
      setStep(3);
      confettiBurst();
    } catch (err) {
      showError(err.message);
      setStep(1);
    } finally {
      setLoading(false);
    }
  });

  /* ---------- compare submit ---------- */
  compareBtn.addEventListener("click", async () => {
    const jobs = [
      document.getElementById("job_description").value.trim(),
      document.getElementById("compare_job_2").value.trim(),
      document.getElementById("compare_job_3").value.trim(),
    ].filter(Boolean);

    if (jobs.length < 2) {
      showError("Add at least one more job posting to compare.");
      return;
    }

    errorBox.classList.add("hidden");
    const fd = new FormData(form);
    fd.set("jobs", JSON.stringify(jobs));
    compareBtn.disabled = true;
    compareBtn.textContent = "Comparing...";

    try {
      const res = await fetch("/api/compare", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      renderCompare(data.results);
    } catch (err) {
      showError(err.message);
    } finally {
      compareBtn.disabled = false;
      compareBtn.textContent = "Compare scores";
    }
  });

  function renderCompare(results) {
    const chart = document.getElementById("compare-chart");
    chart.innerHTML = "";
    results.forEach((r) => {
      const row = document.createElement("div");
      row.className = "chart-row";
      row.innerHTML = `
        <span class="chart-label">${r.label}</span>
        <div class="chart-bar-track"><div class="chart-bar" style="width:${r.score}%"></div></div>
        <span class="chart-score">${r.score}%</span>
      `;
      chart.appendChild(row);
    });
    document.getElementById("compare-results").classList.remove("hidden");
  }

  /* ---------- cover letter ---------- */
  document.getElementById("cover-letter-btn").addEventListener("click", async () => {
    const btn = document.getElementById("cover-letter-btn");
    btn.disabled = true;
    btn.textContent = "Writing...";
    try {
      const fd = new FormData();
      fd.set("job_description", lastJobDescription);
      fd.set("bullets", JSON.stringify(lastRewritten || []));
      const res = await fetch("/api/cover-letter", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      document.getElementById("cover-letter-text").textContent = data.letter;
      document.getElementById("cover-letter-box").classList.remove("hidden");
    } catch (err) {
      showError(err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "✉️ Generate cover letter paragraph";
    }
  });

  document.getElementById("copy-letter-btn").addEventListener("click", () => {
    const text = document.getElementById("cover-letter-text").textContent;
    navigator.clipboard.writeText(text);
    const btn = document.getElementById("copy-letter-btn");
    const original = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => (btn.textContent = original), 1500);
  });

  /* ---------- export ---------- */
  document.getElementById("export-btn").addEventListener("click", async () => {
    const fd = new FormData();
    fd.set("rewritten", JSON.stringify(lastRewritten || []));
    const res = await fetch("/api/export", { method: "POST", body: fd });
    if (!res.ok) {
      const data = await res.json();
      showError(data.error || "Export failed.");
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "tailored-resume.docx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  /* ---------- helpers ---------- */
  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnLabel.classList.toggle("hidden", isLoading);
    spinner.classList.toggle("hidden", !isLoading);
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
  }

  function pillList(el, items) {
    el.innerHTML = "";
    items.forEach((k) => {
      const li = document.createElement("li");
      li.textContent = k;
      el.appendChild(li);
    });
  }

  function renderCloud(el, keywords, foundSet) {
    el.innerHTML = "";
    const must = keywords.must_have || [];
    const nice = keywords.nice_to_have || [];
    must.forEach((k) => el.appendChild(cloudTag(k, "lg", foundSet.has(k.toLowerCase()))));
    nice.forEach((k) => el.appendChild(cloudTag(k, "sm", foundSet.has(k.toLowerCase()))));
  }

  function cloudTag(text, size, found) {
    const span = document.createElement("span");
    span.className = `cloud-tag ${size} ${found ? "found" : "missing"}`;
    span.textContent = text;
    return span;
  }

  function renderResults(data) {
    const { match, rewritten, keywords, ats_issues } = data;

    animateScore(match.score);

    const foundSet = new Set(
      [...match.must_have_found, ...match.nice_to_have_found].map((k) => k.toLowerCase())
    );
    renderCloud(document.getElementById("keyword-cloud"), keywords, foundSet);

    pillList(document.getElementById("must-missing"), match.must_have_missing);
    pillList(document.getElementById("nice-missing"), match.nice_to_have_missing);

    const atsPanel = document.getElementById("ats-panel");
    const atsList = document.getElementById("ats-list");
    if (ats_issues && ats_issues.length) {
      atsList.innerHTML = "";
      ats_issues.forEach((issue) => {
        const li = document.createElement("li");
        li.textContent = issue;
        atsList.appendChild(li);
      });
      atsPanel.classList.remove("hidden");
    } else {
      atsPanel.classList.add("hidden");
    }

    const bulletsEl = document.getElementById("bullets");
    bulletsEl.innerHTML = "";
    rewritten.forEach((b) => {
      const div = document.createElement("div");
      div.className = "bullet-pair";
      div.appendChild(renderDiff(b.original, b.rewritten));
      bulletsEl.appendChild(div);
    });

    results.classList.remove("hidden");
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ---------- word-level diff ---------- */
  function wordDiff(a, b) {
    const aw = a.split(/\s+/).filter(Boolean);
    const bw = b.split(/\s+/).filter(Boolean);
    const m = aw.length, n = bw.length;
    const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
    for (let i = m - 1; i >= 0; i--) {
      for (let j = n - 1; j >= 0; j--) {
        dp[i][j] = aw[i] === bw[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
    let i = 0, j = 0;
    const parts = [];
    while (i < m && j < n) {
      if (aw[i] === bw[j]) {
        parts.push({ type: "same", text: aw[i] });
        i++; j++;
      } else if (dp[i + 1][j] >= dp[i][j + 1]) {
        parts.push({ type: "del", text: aw[i] });
        i++;
      } else {
        parts.push({ type: "add", text: bw[j] });
        j++;
      }
    }
    while (i < m) { parts.push({ type: "del", text: aw[i] }); i++; }
    while (j < n) { parts.push({ type: "add", text: bw[j] }); j++; }
    return parts;
  }

  function renderDiff(original, rewritten) {
    const p = document.createElement("p");
    p.className = "diff";
    const parts = wordDiff(original, rewritten);
    parts.forEach((part, idx) => {
      const node =
        part.type === "same"
          ? document.createTextNode(part.text)
          : document.createElement(part.type === "del" ? "del" : "ins");
      if (part.type !== "same") node.textContent = part.text;
      p.appendChild(node);
      if (idx < parts.length - 1) p.appendChild(document.createTextNode(" "));
    });
    return p;
  }

  function animateScore(target) {
    const fill = document.getElementById("meter-fill");
    const valueEl = document.getElementById("score-value");
    const circumference = 2 * Math.PI * 52;
    fill.style.strokeDasharray = `${circumference} ${circumference}`;

    let current = 0;
    const duration = 700;
    const start = performance.now();

    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      current = Math.round(progress * target);
      const offset = circumference - (current / 100) * circumference;
      fill.style.strokeDashoffset = offset;
      valueEl.textContent = `${current}%`;
      if (progress < 1) requestAnimationFrame(step);
    }
    fill.style.strokeDashoffset = circumference;
    requestAnimationFrame(step);
  }

  /* ---------- confetti ---------- */
  function confettiBurst() {
    const colors = ["#6366f1", "#22d3ee", "#f472b6", "#facc15"];
    for (let i = 0; i < 36; i++) {
      const el = document.createElement("div");
      el.className = "confetti-piece";
      el.style.left = Math.random() * 100 + "vw";
      el.style.background = colors[Math.floor(Math.random() * colors.length)];
      el.style.animationDuration = Math.random() * 1.2 + 1.4 + "s";
      el.style.animationDelay = Math.random() * 0.25 + "s";
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 3000);
    }
  }
})();
