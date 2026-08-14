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

  /* ---------- tabs ---------- */
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.add("hidden"));
      tab.classList.add("active");
      document.querySelector(`.tab-panel[data-panel="${tab.dataset.tab}"]`).classList.remove("hidden");
    });
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

  /* ---------- submit ---------- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.classList.add("hidden");
    results.classList.add("hidden");
    setLoading(true);

    try {
      const res = await fetch("/api/tailor", { method: "POST", body: new FormData(form) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      renderResults(data);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });

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

  function renderResults(data) {
    const { match, rewritten } = data;

    animateScore(match.score);
    pillList(document.getElementById("must-found"), match.must_have_found);
    pillList(document.getElementById("must-missing"), match.must_have_missing);
    pillList(document.getElementById("nice-found"), match.nice_to_have_found);
    pillList(document.getElementById("nice-missing"), match.nice_to_have_missing);

    const bulletsEl = document.getElementById("bullets");
    bulletsEl.innerHTML = "";
    rewritten.forEach((b) => {
      const div = document.createElement("div");
      div.className = "bullet-pair";
      const orig = document.createElement("p");
      orig.className = "original";
      orig.textContent = b.original;
      const rew = document.createElement("p");
      rew.className = "rewritten";
      rew.textContent = b.rewritten;
      div.appendChild(orig);
      div.appendChild(rew);
      bulletsEl.appendChild(div);
    });

    results.classList.remove("hidden");
    results.scrollIntoView({ behavior: "smooth", block: "start" });
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
})();
