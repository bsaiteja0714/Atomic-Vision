const html = document.documentElement;
const themeToggle = document.getElementById("themeToggle");

const dropArea = document.getElementById("dropArea");
const fileInput = document.getElementById("fileInput");
const statusText = document.getElementById("status");

const resultPanel = document.getElementById("resultPanel");
const ocrText = document.getElementById("ocrText");
const titleEl = document.getElementById("title");
const authorEl = document.getElementById("author");
const quoteEl = document.getElementById("quote");
const summaryEl = document.getElementById("summary");

/* THEME TOGGLE */
themeToggle.onclick = () => {
  html.dataset.theme = html.dataset.theme === "dark" ? "light" : "dark";
};

/* DRAG & DROP */
["dragenter", "dragover"].forEach(e =>
  dropArea.addEventListener(e, ev => {
    ev.preventDefault();
    dropArea.classList.add("dragover");
  })
);

["dragleave", "drop"].forEach(e =>
  dropArea.addEventListener(e, ev => {
    ev.preventDefault();
    dropArea.classList.remove("dragover");
  })
);

dropArea.onclick = () => fileInput.click();

dropArea.addEventListener("drop", e => {
  const file = e.dataTransfer.files[0];
  if (file) analyze(file);
});

fileInput.onchange = () => {
  if (fileInput.files[0]) analyze(fileInput.files[0]);
};

/* ANALYZE */
async function analyze(file) {
  statusText.textContent = "Analyzing…";
  resultPanel.classList.add("hidden");

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch("http://127.0.0.1:8000/analyze-page", {
      method: "POST",
      body: form
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => null);
      const detail = errData?.detail || `Server error (${res.status})`;
      statusText.textContent = `Error: ${detail}`;
      return;
    }

    const data = await res.json();

    ocrText.textContent = data.raw_ocr_text || "—";
    titleEl.textContent = data.title?.value || "Unknown";
    authorEl.textContent = data.author?.value || "Unknown";
    quoteEl.textContent = data.best_quote || "—";

    summaryEl.innerHTML = "";
    (data.summary || []).forEach(s => {
      const li = document.createElement("li");
      li.textContent = s;
      summaryEl.appendChild(li);
    });

    // Context explanation
    const contextEl = document.getElementById("context");
    if (contextEl) {
      contextEl.textContent = data.context_explanation || "—";
    }

    // Difficult words
    const wordsEl = document.getElementById("difficultWords");
    if (wordsEl) {
      wordsEl.innerHTML = "";
      (data.difficult_words || []).forEach(w => {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${w.word}</strong> — ${w.meaning}`;
        wordsEl.appendChild(li);
      });
      if (!data.difficult_words || data.difficult_words.length === 0) {
        wordsEl.innerHTML = "<li>—</li>";
      }
    }

    statusText.textContent = data.message;
    resultPanel.classList.remove("hidden");

  } catch (e) {
    statusText.textContent = `Connection error: ${e.message}`;
  }
}
