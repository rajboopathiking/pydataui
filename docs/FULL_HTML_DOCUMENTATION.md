# 🌐 Interactive Full HTML Documentation Suite

PyDataUI provides a suite of **standalone, interactive HTML documentation portals** designed for offline usage, direct browser inspection, and rich interactive exploration.

---

## 📚 Standalone HTML Portals

<div class="md-typeset__table">
<table style="width: 100%;">
  <thead>
    <tr>
      <th style="width: 30%;">Portal</th>
      <th style="width: 45%;">Description</th>
      <th style="width: 25%;">Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>📘 Full Developer Manual</strong></td>
      <td>Comprehensive 13-chapter architectural &amp; framework manual.</td>
      <td><a href="../full-documentation.html" target="_blank" rel="noopener" class="md-button md-button--primary">Open Fullscreen</a></td>
    </tr>
    <tr>
      <td><strong>📱 Mobile &amp; Desktop Guide</strong></td>
      <td>Native Android APK, iOS IPA, Sideloadly, AltStore, &amp; Tauri guide.</td>
      <td><a href="../mobile-desktop-guide.html" target="_blank" rel="noopener" class="md-button">Open Mobile Guide</a></td>
    </tr>
    <tr>
      <td><strong>🧩 Interactive API Explorer</strong></td>
      <td>Live searchable component catalog with parameters &amp; code copy.</td>
      <td><a href="../api-reference.html" target="_blank" rel="noopener" class="md-button">Open API Explorer</a></td>
    </tr>
    <tr>
      <td><strong>📊 Template Gallery</strong></td>
      <td>Interactive showcase of ML, KPI, EDA, and Pipeline templates.</td>
      <td><a href="../examples/data-team-gallery.html" target="_blank" rel="noopener" class="md-button">Open Gallery</a></td>
    </tr>
  </tbody>
</table>
</div>

---

## ⚡ Live Embedded Full Documentation Manual

Below is the live embedded version of **`full-documentation.html`**. You can search, copy code snippets, switch sections, and toggle dark/light mode directly:

<div style="margin: 1.5rem 0;">
  <p style="margin-bottom: 0.75rem;">
    <a href="../full-documentation.html" target="_blank" rel="noopener" class="md-button md-button--primary">
      ⤢ Open Full Documentation in New Tab
    </a>
  </p>

  <iframe
    id="pdu-docs-iframe"
    src="../full-documentation.html"
    title="PyDataUI Full Developer Documentation Manual"
    style="width: 100%; height: 85vh; min-height: 750px; border: 1px solid #334155; border-radius: 12px; background: #090d16;"
    loading="lazy"
  ></iframe>
</div>

<script>
  (function() {
    var iframe = document.getElementById('pdu-docs-iframe');
    if (!iframe) return;
    // Auto-detect whether ../full-documentation.html or full-documentation.html is required
    var loc = window.location.pathname;
    if (loc.indexOf('FULL_HTML_DOCUMENTATION') !== -1) {
      iframe.src = '../full-documentation.html';
    } else {
      iframe.src = 'full-documentation.html';
    }
  })();
</script>

---

## 📦 Offline Access &amp; Portability

All HTML documentation files in `docs/` are **completely standalone** and self-contained:
- Open them directly from disk (`file:///path/to/docs/full-documentation.html`) without starting an HTTP or Python server.
- Share with teammates via email, Slack, or host behind corporate firewalls / AWS S3 buckets.
- Zero external build toolchains or npm scripts required.
