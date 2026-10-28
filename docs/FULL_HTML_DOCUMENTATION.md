# 🌐 Interactive Full HTML Documentation Suite

PyDataUI provides a suite of **standalone, interactive HTML documentation portals** designed for offline usage, direct browser inspection, and rich interactive exploration.

---

## 📚 Standalone HTML Portals

| Portal | Description | Actions |
| :--- | :--- | :--- |
| **📘 Full Developer Manual** | Comprehensive 14-chapter architectural &amp; framework manual. | [Open Fullscreen (HTML)](full-documentation.html){ .md-button .md-button--primary } |
| **📱 Mobile &amp; Desktop Guide** | Native Android APK, iOS IPA, Sideloadly, AltStore, &amp; Tauri guide. | [Open Mobile Guide (HTML)](mobile-desktop-guide.html){ .md-button } |
| **🧩 Interactive API Explorer** | Live searchable component catalog with parameters &amp; code copy. | [Open API Explorer (HTML)](api-reference.html){ .md-button } |
| **📊 Template Gallery** | Interactive showcase of ML, KPI, EDA, and Pipeline templates. | [Open Gallery (HTML)](examples/data-team-gallery.html){ .md-button } |

---

## ⚡ Live Embedded Full Documentation Manual

Below is the live embedded version of **`full-documentation.html`**. You can search, copy code snippets, switch sections, and toggle dark/light mode directly:

<div style="margin: 1.5rem 0;">
  <p style="margin-bottom: 0.75rem;">
    <a href="full-documentation.html" target="_blank" rel="noopener" class="md-button md-button--primary">
      ⤢ Open Full Documentation in New Tab
    </a>
  </p>

  <iframe
    src="full-documentation.html"
    title="PyDataUI Full Developer Documentation Manual"
    style="width: 100%; height: 85vh; min-height: 720px; border: 1px solid #334155; border-radius: 12px; background: #090d16;"
    loading="lazy"
  ></iframe>
</div>

---

## 📦 Offline Access &amp; Portability

All HTML documentation files in `docs/` are **completely standalone** and self-contained:
- Open them directly from disk (`file:///path/to/docs/full-documentation.html`) without starting an HTTP or Python server.
- Share with teammates via email, Slack, or host behind corporate firewalls / AWS S3 buckets.
- Zero external build toolchains or npm scripts required.
