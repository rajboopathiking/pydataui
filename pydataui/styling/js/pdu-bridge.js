/**
 * PyDataUI Mobile Bridge (v1.1.0)
 * Native Offline Parity, In-Process JNI Bridge & Micro-Latency Interactions.
 */
(function () {
    'use strict';

    // 1. Capacitor JNI Bridge Registration
    var hasCapacitor = typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins;
    window.PyDataUIBridge = {
        isAvailable: function () {
            return !!(hasCapacitor && window.Capacitor.Plugins.PyDataUIBridge);
        },
        dispatch: async function (method, path, headers, body) {
            if (!this.isAvailable()) {
                throw new Error("PyDataUIBridge is only available in native Android/iOS mobile shells.");
            }
            return await window.Capacitor.Plugins.PyDataUIBridge.dispatch({
                method: method || 'GET',
                path: path || '/',
                headers: headers || {},
                body: typeof body === 'object' ? JSON.stringify(body) : (body || '')
            });
        }
    };

    if (window.PyDataUIBridge.isAvailable()) {
        console.log("⚡ [PyDataUI] In-Process JNI Bridge detected (Zero-Socket / Direct Memory Mode)");
    }

    function ready(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    ready(function () {
        window.__pduActiveTab = window.__pduActiveTab || 'dashboard';

        // 2. Generic Instant client-side tab switcher (works 100% offline with zero latency).
        window.switchTabMobile = function (tabId) {
            window.__pduActiveTab = tabId;
            try { localStorage.setItem('pdu_active_tab', tabId); } catch (e) {}

            var panels = document.querySelectorAll('.tab-panel');
            for (var i = 0; i < panels.length; i++) {
                panels[i].classList.add('hidden');
                panels[i].classList.remove('block');
            }

            var target = document.getElementById('tab-' + tabId);
            if (target) {
                target.classList.remove('hidden');
                target.classList.add('block');
            }

            // Update tab button highlights if tab buttons exist
            var buttons = document.querySelectorAll('[id^="btn-tab-"]');
            for (var j = 0; j < buttons.length; j++) {
                var btn = buttons[j];
                var t = btn.id.replace('btn-tab-', '');
                var dot = document.getElementById('dot-tab-' + t);
                if (t === tabId) {
                    btn.classList.add('text-primary', 'font-bold');
                    btn.classList.remove('text-muted-foreground');
                    if (dot) dot.classList.add('bg-primary');
                } else {
                    btn.classList.remove('text-primary', 'font-bold');
                    btn.classList.add('text-muted-foreground');
                    if (dot) dot.classList.remove('bg-primary');
                }
            }
        };

        // Restore selected tab from local storage on load.
        try {
            var savedTab = localStorage.getItem('pdu_active_tab');
            if (savedTab) window.switchTabMobile(savedTab);
        } catch (e) {}

        // 3. Strip redundant blanket includes to guarantee minimal action payloads.
        function stripRedundantIncludes() {
            var els = document.querySelectorAll('[hx-include="#pdu-root"]');
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                var post = el.getAttribute('hx-post') || '';
                // Keep include on specific complex forms if designated, otherwise strip
                if (el.hasAttribute('data-preserve-include')) continue;
                el.removeAttribute('hx-include');
            }
        }
        window.stripPduIncludes = stripRedundantIncludes;
        stripRedundantIncludes();

        // 4. Per-action latency telemetry.
        document.body.addEventListener('htmx:beforeRequest', function () {
            window.__pduActionT0 = performance.now();
        });
        document.body.addEventListener('htmx:afterSettle', function () {
            if (window.__pduActionT0) {
                console.log('⚡ [PyDataUI] Action round-trip: ' + Math.round(performance.now() - window.__pduActionT0) + 'ms');
                window.__pduActionT0 = 0;
            }
            stripRedundantIncludes();
        });

        // 5. Retain active tab and UI state across any SSR swaps.
        document.body.addEventListener('htmx:afterSwap', function () {
            if (window.__pduActiveTab) window.switchTabMobile(window.__pduActiveTab);
            stripRedundantIncludes();
        });

        // 6. Graceful offline error handling (toast notification instead of blank screen).
        document.body.addEventListener('htmx:responseError', function (evt) {
            console.warn('[PyDataUI] Action returned response error:', evt.detail);
        });
        document.body.addEventListener('htmx:sendError', function (evt) {
            console.warn('[PyDataUI] Network send error (offline):', evt.detail);
            showOfflineToast();
        });

        function showOfflineToast() {
            var toast = document.getElementById('pdu-offline-toast');
            if (!toast) {
                toast = document.createElement('div');
                toast.id = 'pdu-offline-toast';
                toast.className = 'fixed bottom-20 left-1/2 -translate-x-1/2 px-4 py-2 bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs rounded-full shadow-lg z-50 transition-opacity duration-300';
                toast.innerText = '⚡ Offline Mode — Local Cache Active';
                document.body.appendChild(toast);
            }
            toast.style.opacity = '1';
            setTimeout(function () {
                toast.style.opacity = '0';
            }, 3000);
        }

        // 7. Dynamic Backend Host Switcher & Health Watcher
        function defaultBackend() {
            try {
                if (window.location && /^https?:$/.test(window.location.protocol) && window.location.origin !== 'null') {
                    return window.location.origin;
                }
            } catch (e) {}
            return 'http://127.0.0.1:8000';
        }

        window.promptBackendConfig = function () {
            var current = localStorage.getItem('pdu_backend_url') || defaultBackend();
            var nextUrl = prompt('Enter Python Backend Server URL:\n(e.g. http://192.168.x.x:8000 or tunnel URL)', current);
            if (nextUrl !== null && nextUrl.trim() !== '') {
                localStorage.setItem('pdu_backend_url', nextUrl.trim().replace(/\/$/, ''));
                alert('Saved backend target: ' + nextUrl.trim());
                window.checkBackendHealth && window.checkBackendHealth();
            }
        };

        // Rewrite HTMX paths when a custom remote backend is configured
        document.body.addEventListener('htmx:configRequest', function (evt) {
            var backend = localStorage.getItem('pdu_backend_url');
            if (backend && evt.detail.path && evt.detail.path.indexOf('/') === 0) {
                evt.detail.path = backend.replace(/\/$/, '') + evt.detail.path;
            }
        });

        window.checkBackendHealth = function () {
            var backend = localStorage.getItem('pdu_backend_url') || defaultBackend();
            var dot = document.getElementById('conn-dot');
            var txt = document.getElementById('conn-text');
            if (!dot || !txt) return;
            fetch(backend.replace(/\/$/, '') + '/_pdu/health', { mode: 'cors' })
                .then(function (r) { return r.json(); })
                .then(function () {
                    dot.className = 'w-2 h-2 rounded-full bg-emerald-400';
                    txt.innerText = 'Backend Live: ' + backend.replace(/^https?:\/\//, '');
                })
                .catch(function () {
                    dot.className = 'w-2 h-2 rounded-full bg-amber-400';
                    txt.innerText = 'Standalone Mode (Tap to sync)';
                });
        };
        setTimeout(window.checkBackendHealth, 1000);

        // 8. Modern shadcn Sidebar & Drawer Controller (Zero-JS Full Keyboard & Mobile Support)
        function initSidebarController() {
            function toggleSidebar() {
                var provider = document.querySelector('[data-sidebar-provider="true"]');
                var sidebar = document.querySelector('aside.pdu-sidebar');
                var backdrop = document.querySelector('[data-pdu-sidebar-backdrop="true"]');
                if (!sidebar) return;

                var isMobile = window.innerWidth < 768;
                if (isMobile) {
                    var mobileOpen = sidebar.getAttribute('data-mobile-open') === 'true';
                    if (mobileOpen) {
                        sidebar.removeAttribute('data-mobile-open');
                        if (backdrop) backdrop.classList.add('hidden');
                    } else {
                        sidebar.setAttribute('data-mobile-open', 'true');
                        if (backdrop) backdrop.classList.remove('hidden');
                    }
                } else {
                    var currState = (provider ? provider.getAttribute('data-state') : sidebar.getAttribute('data-state')) || 'expanded';
                    var nextState = currState === 'expanded' ? 'collapsed' : 'expanded';
                    if (provider) provider.setAttribute('data-state', nextState);
                    sidebar.setAttribute('data-state', nextState);
                    try { localStorage.setItem('pdu-sidebar-state', nextState); } catch (e) {}
                }
            }

            // Restore saved desktop sidebar state
            try {
                var savedSidebar = localStorage.getItem('pdu-sidebar-state');
                if (savedSidebar && window.innerWidth >= 768) {
                    var provider = document.querySelector('[data-sidebar-provider="true"]');
                    var sidebar = document.querySelector('aside.pdu-sidebar');
                    if (provider) provider.setAttribute('data-state', savedSidebar);
                    if (sidebar) sidebar.setAttribute('data-state', savedSidebar);
                }
            } catch (e) {}

            // Delegate sidebar trigger clicks
            document.addEventListener('click', function (e) {
                if (e.target.closest('[data-pdu-sidebar-trigger="true"]') || e.target.closest('[data-pdu-sidebar-rail="true"]')) {
                    e.preventDefault();
                    toggleSidebar();
                } else if (e.target.closest('[data-pdu-sidebar-backdrop="true"]')) {
                    toggleSidebar();
                }
            });

            // Keyboard shortcut: Cmd+B / Ctrl+B
            document.addEventListener('keydown', function (e) {
                if ((e.metaKey || e.ctrlKey) && (e.key === 'b' || e.key === 'B')) {
                    e.preventDefault();
                    toggleSidebar();
                }
            });
        }
        initSidebarController();

        // 9. Dropdown & Popover Dismiss Controller
        document.addEventListener('click', function (e) {
            // Dropdown trigger
            var dropTrig = e.target.closest('[data-pdu-dropdown-trigger="true"]');
            if (dropTrig) {
                e.preventDefault();
                var dropContainer = dropTrig.closest('[data-pdu-dropdown="true"]');
                var content = dropContainer ? dropContainer.querySelector('.pdu-dropdown-content') : null;
                if (content) {
                    var isOpen = content.getAttribute('data-open') === 'true';
                    closeAllOverlays();
                    if (!isOpen) {
                        content.classList.remove('hidden');
                        content.setAttribute('data-open', 'true');
                    }
                }
                return;
            }

            // Popover trigger
            var popTrig = e.target.closest('[data-pdu-popover-trigger="true"]');
            if (popTrig) {
                e.preventDefault();
                var popContainer = popTrig.closest('[data-pdu-popover="true"]');
                var popContent = popContainer ? popContainer.querySelector('.pdu-popover-content') : null;
                if (popContent) {
                    var isPopOpen = popContent.getAttribute('data-open') === 'true';
                    closeAllOverlays();
                    if (!isPopOpen) {
                        popContent.classList.remove('hidden');
                        popContent.setAttribute('data-open', 'true');
                    }
                }
                return;
            }

            // Click outside closes open dropdowns/popovers
            if (!e.target.closest('.pdu-dropdown-content') && !e.target.closest('.pdu-popover-content')) {
                closeAllOverlays();
            }
        });

        function closeAllOverlays() {
            var drops = document.querySelectorAll('.pdu-dropdown-content');
            for (var i = 0; i < drops.length; i++) {
                drops[i].classList.add('hidden');
                drops[i].removeAttribute('data-open');
            }
            var pops = document.querySelectorAll('.pdu-popover-content');
            for (var j = 0; j < pops.length; j++) {
                pops[j].classList.add('hidden');
                pops[j].removeAttribute('data-open');
            }
        }

        // 10. Command Palette (Cmd+K / Ctrl+K Spotlight Search)
        function initCommandPalette() {
            function openCommand() {
                var dialog = document.querySelector('[data-pdu-command-dialog="true"]');
                if (dialog) {
                    dialog.classList.remove('hidden');
                    var input = dialog.querySelector('[data-pdu-command-input="true"]');
                    if (input) {
                        input.value = '';
                        input.focus();
                        filterCommandItems('');
                    }
                }
            }

            function closeCommand() {
                var dialog = document.querySelector('[data-pdu-command-dialog="true"]');
                if (dialog) dialog.classList.add('hidden');
            }

            function filterCommandItems(query) {
                var q = (query || '').toLowerCase().trim();
                var items = document.querySelectorAll('.pdu-command-item');
                for (var i = 0; i < items.length; i++) {
                    var it = items[i];
                    var val = it.getAttribute('data-value') || it.innerText.toLowerCase();
                    if (!q || val.indexOf(q) !== -1) {
                        it.style.display = 'flex';
                    } else {
                        it.style.display = 'none';
                    }
                }
            }

            document.addEventListener('keydown', function (e) {
                if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
                    e.preventDefault();
                    var dialog = document.querySelector('[data-pdu-command-dialog="true"]');
                    if (dialog && !dialog.classList.contains('hidden')) {
                        closeCommand();
                    } else {
                        openCommand();
                    }
                } else if (e.key === 'Escape') {
                    closeCommand();
                    closeAllOverlays();
                }
            });

            document.addEventListener('click', function (e) {
                if (e.target.closest('[data-pdu-command-trigger="true"]')) {
                    e.preventDefault();
                    openCommand();
                } else if (e.target.closest('[data-pdu-command-close="true"]')) {
                    e.preventDefault();
                    closeCommand();
                }
            });

            document.addEventListener('input', function (e) {
                if (e.target.matches('[data-pdu-command-input="true"]')) {
                    filterCommandItems(e.target.value);
                }
            });
        }
        initCommandPalette();

        // 11. Hyperparameter Slider Bubble Sync
        document.addEventListener('input', function (e) {
            if (e.target.matches('[data-pdu-slider="true"]')) {
                var parent = e.target.closest('.w-full');
                if (parent) {
                    var bubble = parent.querySelector('.pdu-slider-value');
                    if (bubble) bubble.innerText = e.target.value;
                }
            }
        });
    });
})();
