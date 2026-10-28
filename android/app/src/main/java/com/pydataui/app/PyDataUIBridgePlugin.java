package com.pydataui.app;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.JSObject;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * Capacitor Plugin that bridges WebView JavaScript directly to the in-process Python runtime
 * via Chaquopy JNI, skipping Uvicorn and local TCP loopback sockets.
 */
@CapacitorPlugin(name = "PyDataUIBridge")
public class PyDataUIBridgePlugin extends Plugin {

    private static boolean pythonStarted = false;

    /**
     * Ensure the embedded Python engine is initialized.
     */
    public synchronized void ensurePython() {
        if (!pythonStarted) {
            try {
                Class<?> pyClass = Class.forName("com.chaquo.python.Python");
                java.lang.reflect.Method isStarted = pyClass.getMethod("isStarted");
                boolean started = (Boolean) isStarted.invoke(null);
                if (!started) {
                    Class<?> platformClass = Class.forName("com.chaquo.python.android.AndroidPlatform");
                    Object platform = platformClass.getConstructor(android.content.Context.class)
                            .newInstance(getContext());
                    java.lang.reflect.Method start = pyClass.getMethod("start", Class.forName("com.chaquo.python.PythonPlatform"));
                    start.invoke(null, platform);
                }
                pythonStarted = true;
            } catch (ClassNotFoundException e) {
                // Chaquopy not bundled in this build variant; fallback gracefully
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Dispatch an ASGI request directly to the in-process Python runtime.
     * 
     * JavaScript Call:
     * const resp = await Capacitor.Plugins.PyDataUIBridge.dispatch({
     *     method: "POST",
     *     path: "/_pdu/event/CounterState/increment",
     *     headers: { "Content-Type": "application/json" },
     *     body: JSON.stringify({ count: 1 })
     * });
     */
    @PluginMethod
    public void dispatch(PluginCall call) {
        ensurePython();
        String method = call.getString("method", "GET");
        String path = call.getString("path", "/");
        JSObject headersObj = call.getObject("headers", new JSObject());
        String body = call.getString("body", "");

        try {
            Class<?> pyClass = Class.forName("com.chaquo.python.Python");
            java.lang.reflect.Method getInstance = pyClass.getMethod("getInstance");
            Object py = getInstance.invoke(null);

            java.lang.reflect.Method getModule = pyClass.getMethod("getModule", String.class);
            Object bridgeModule = getModule.invoke(py, "pydataui.shell.bridge");

            Class<?> pyObjClass = Class.forName("com.chaquo.python.PyObject");
            java.lang.reflect.Method callAttr = pyObjClass.getMethod("callAttr", String.class, Object[].class);

            Object[] args = new Object[]{method, path, headersObj.toString(), body};
            Object pyResult = callAttr.invoke(bridgeModule, "dispatch_in_process", args);

            java.lang.reflect.Method getAttr = pyObjClass.getMethod("get", String.class);
            Object statusObj = getAttr.invoke(pyResult, "status_code");
            Object bodyTextObj = getAttr.invoke(pyResult, "body_text");
            Object headersJsonObj = getAttr.invoke(pyResult, "headers_json");

            int status = ((Number) statusObj.getClass().getMethod("toInt").invoke(statusObj)).intValue();
            String bodyText = (String) bodyTextObj.getClass().getMethod("toString").invoke(bodyTextObj);
            String headersJson = (String) headersJsonObj.getClass().getMethod("toString").invoke(headersJsonObj);

            JSObject ret = new JSObject();
            ret.put("status", status);
            ret.put("body", bodyText);
            ret.put("headers", headersJson);
            call.resolve(ret);

        } catch (ClassNotFoundException e) {
            call.reject("Chaquopy is not installed in this APK build. Use Wi-Fi backend mode or enable Chaquopy in build.gradle.");
        } catch (Exception e) {
            call.reject("JNI Bridge Error: " + e.getMessage(), e);
        }
    }
}
