/**
 * PyDataUI In-Process JNI Bridge Client.
 * Automatically detected when running inside Android Capacitor with Chaquopy.
 */
(function() {
    'use strict';

    const hasCapacitor = typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins;
    const bridgePlugin = hasCapacitor ? window.Capacitor.Plugins.PyDataUIBridge : null;

    window.PyDataUIBridge = {
        isAvailable: function() {
            return !!(hasCapacitor && window.Capacitor.Plugins.PyDataUIBridge);
        },

        dispatch: async function(method, path, headers, body) {
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
})();
