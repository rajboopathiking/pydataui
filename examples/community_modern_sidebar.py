"""
Community Contribution: Modern Collapsible Sidebar (Hide & Expand)
==================================================================
Author: @rajboopathiking (First Community Component Contribution)
Built with: pdu.from_jsx() — Zero Node.js, Zero npm, 100% Pure Python + Tailwind/Shadcn tokens.

Features:
- Smooth 300ms Hide & Expand drawer animation
- Floating Expand button when sidebar is hidden (100% full-width canvas mode)
- Keyboard shortcut support: Cmd+B / Ctrl+B (VS Code / Shadcn style)
- Automatic theme & Dark/Light mode support via PyDataUI CSS tokens (bg-card, border-border, etc.)
- Works seamlessly in both Track 1 (Procedural) and Track 2 (Declarative) PyDataUI apps

Run:
    python examples/community_modern_sidebar.py
"""
import pydataui as pdu


# 1. Define the reusable ModernSidebarShell component via pdu.from_jsx()
ModernSidebarShell = pdu.from_jsx("""
<div className="flex min-h-screen w-full bg-background text-foreground">
  <aside
    id="pdu-modern-sidebar"
    data-hidden="false"
    className="group relative flex flex-col justify-between border-r border-border bg-card/95 backdrop-blur-md transition-all duration-300 ease-in-out w-64 shrink-0 overflow-hidden"
  >
    <div className="flex flex-col gap-4 p-4 w-64">
      <!-- Header: Brand + Hide Button -->
      <div className="flex items-center justify-between pb-3 border-b border-border/60">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm shadow-sm">
            {brand_icon}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-semibold tracking-tight truncate text-foreground">{brand}</span>
            <span className="text-[11px] text-muted-foreground truncate">{subtitle}</span>
          </div>
        </div>
        <button
          type="button"
          onclick="window.__pduToggleModernSidebar()"
          title="Hide sidebar (Ctrl+B / Cmd+B)"
          aria-label="Hide sidebar"
          className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2"/>
            <path d="M9 3v18"/>
            <path d="m16 15-3-3 3-3"/>
          </svg>
        </button>
      </div>

      <!-- Navigation Slot -->
      <nav className="flex flex-col gap-1">
        {nav_items}
      </nav>
    </div>

    <!-- Bottom Footer Slot -->
    <div className="p-4 border-t border-border/60 w-64">
      {footer}
    </div>
  </aside>

  <!-- Main Workspace -->
  <div className="relative flex-1 min-w-0 flex flex-col">
    <!-- Top Mini Bar with Expand Button (shown when sidebar is hidden) -->
    <div id="pdu-modern-expand-bar" className="hidden items-center gap-3 px-6 pt-4 pb-1">
      <button
        type="button"
        onclick="window.__pduToggleModernSidebar()"
        title="Expand sidebar (Ctrl+B / Cmd+B)"
        aria-label="Expand sidebar"
        className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground shadow-sm hover:bg-accent hover:text-accent-foreground transition-all cursor-pointer"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="18" height="18" x="3" y="3" rx="2"/>
          <path d="M9 3v18"/>
          <path d="m14 9 3 3-3 3"/>
        </svg>
        <span>Expand Sidebar</span>
        <kbd className="ml-1 rounded bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">⌘B</kbd>
      </button>
    </div>

    <!-- Main Page Content -->
    <main className="flex-1 p-6">
      {children}
    </main>
  </div>

  <script>
    (function () {
      window.__pduToggleModernSidebar = function () {
        var sidebar = document.getElementById('pdu-modern-sidebar');
        var expandBar = document.getElementById('pdu-modern-expand-bar');
        if (!sidebar || !expandBar) return;

        var isHidden = sidebar.getAttribute('data-hidden') === 'true';
        if (isHidden) {
          sidebar.setAttribute('data-hidden', 'false');
          sidebar.classList.remove('w-0', 'opacity-0', 'border-r-0');
          sidebar.classList.add('w-64', 'opacity-100');
          expandBar.classList.add('hidden');
          expandBar.classList.remove('flex');
        } else {
          sidebar.setAttribute('data-hidden', 'true');
          sidebar.classList.remove('w-64', 'opacity-100');
          sidebar.classList.add('w-0', 'opacity-0', 'border-r-0');
          expandBar.classList.remove('hidden');
          expandBar.classList.add('flex');
        }
      };

      if (!window.__pduSidebarShortcutBound) {
        window.__pduSidebarShortcutBound = true;
        document.addEventListener('keydown', function (e) {
          if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'b') {
            e.preventDefault();
            if (window.__pduToggleModernSidebar) {
              window.__pduToggleModernSidebar();
            }
          }
        });
      }
    })();
  </script>
</div>
""")


# 2. Reusable Nav Item helper built with pdu.from_jsx()
ModernNavItem = pdu.from_jsx("""
<a
  href="{href}"
  className="flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors {active_class}"
>
  <span className="flex items-center gap-2.5 truncate">
    <span className="text-base leading-none">{icon}</span>
    <span className="truncate">{label}</span>
  </span>
  {badge_html}
</a>
""")


def nav_link(label: str, icon: str = "•", href: str = "#", active: bool = False, badge: str = ""):
    """Helper to build a styled navigation item for ModernSidebarShell."""
    active_class = (
        "bg-primary/10 text-primary font-semibold"
        if active
        else "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
    )
    badge_html = (
        pdu.from_html(
            '<span class="rounded-full bg-primary/15 px-2 py-0.5 text-[10px] font-semibold text-primary">{text}</span>'
        )(text=badge)
        if badge
        else ""
    )
    return ModernNavItem(
        label=label,
        icon=icon,
        href=href,
        active_class=active_class,
        badge_html=badge_html,
    )


# 3. Demo Application (Track 2 Declarative Style)
app = pdu.App(title="Modern Collapsible Sidebar • PyDataUI", theme="zinc", dark_mode=True)


@app.page("/")
def home():
    nav = [
        nav_link("Overview", icon="📊", href="/", active=True),
        nav_link("AI Agents", icon="🤖", href="/agents", badge="3 Live"),
        nav_link("Data Pipelines", icon="⚡", href="/pipelines"),
        nav_link("Model Registry", icon="🧠", href="/models"),
        nav_link("Settings", icon="⚙️", href="/settings"),
    ]

    footer = pdu.from_jsx("""
    <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-2.5">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold">
        BR
      </div>
      <div className="flex flex-col min-w-0">
        <span className="text-xs font-semibold truncate text-foreground">Boopathi Raj</span>
        <span className="text-[11px] text-muted-foreground truncate">Maintainer • Pro</span>
      </div>
    </div>
    """)()

    main_content = pdu.Container(
        pdu.Row(
            pdu.Col(
                pdu.Heading("Modern Collapsible Sidebar", level=1),
                pdu.Text(
                    "Click the Hide icon inside the sidebar (or press Cmd+B / Ctrl+B) to collapse into full-width mode.",
                    class_name="text-sm text-muted-foreground mt-1",
                ),
            ),
            pdu.Badge("Community JSX", variant="secondary"),
            class_name="justify-between items-center pb-5 mb-6 border-b border-border/60",
        ),
        pdu.Grid(
            pdu.Card(
                pdu.Text("Active Agents", class_name="text-xs uppercase text-muted-foreground"),
                pdu.Heading("12 Online", level=2, class_name="text-3xl font-bold mt-1"),
                class_name="p-5",
            ),
            pdu.Card(
                pdu.Text("P99 Latency", class_name="text-xs uppercase text-muted-foreground"),
                pdu.Heading("1.2 ms", level=2, class_name="text-3xl font-bold mt-1 text-emerald-500"),
                class_name="p-5",
            ),
            pdu.Card(
                pdu.Text("Community Track", class_name="text-xs uppercase text-muted-foreground"),
                pdu.Heading("pdu.from_jsx", level=2, class_name="text-2xl font-bold mt-1 text-primary"),
                class_name="p-5",
            ),
            columns=3,
            class_name="gap-4",
        ),
    )

    return ModernSidebarShell(
        main_content,
        brand="PyDataUI Studio",
        brand_icon="⚡",
        subtitle="v1.7.0 • Community",
        nav_items=nav,
        footer=footer,
    )


if __name__ == "__main__":
    app.run(port=8000)
