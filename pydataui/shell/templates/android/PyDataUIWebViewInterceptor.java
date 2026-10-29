package com.pydataui.app;

import android.content.Context;
import android.net.Uri;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * Native Android WebView Client Interceptor that captures HTMX and AJAX requests
 * directed to /_pdu/* and dispatches them directly to the Python ASGI app via JNI.
 */
public class PyDataUIWebViewInterceptor {

    public static WebResourceResponse interceptRequest(Context context, WebResourceRequest request) {
        if (request == null || request.getUrl() == null) {
            return null;
        }

        Uri uri = request.getUrl();
        String path = uri.getPath();
        if (path == null) {
            return null;
        }

        // Intercept PyDataUI endpoints
        if (!path.startsWith("/_pdu/") && !path.startsWith("/api/")) {
            return null;
        }

        String fullUrl = uri.toString();
        String method = request.getMethod();
        Map<String, String> requestHeaders = request.getRequestHeaders();
        org.json.JSONObject headersJson = new org.json.JSONObject(requestHeaders != null ? requestHeaders : new HashMap<String, String>());

        try {
            Class<?> pyClass = Class.forName("com.chaquo.python.Python");
            java.lang.reflect.Method isStarted = pyClass.getMethod("isStarted");
            boolean started = (Boolean) isStarted.invoke(null);
            if (!started) {
                Class<?> platformClass = Class.forName("com.chaquo.python.android.AndroidPlatform");
                Object platform = platformClass.getConstructor(Context.class).newInstance(context);
                java.lang.reflect.Method start = pyClass.getMethod("start", Class.forName("com.chaquo.python.PythonPlatform"));
                start.invoke(null, platform);
            }

            java.lang.reflect.Method getInstance = pyClass.getMethod("getInstance");
            Object py = getInstance.invoke(null);

            java.lang.reflect.Method getModule = pyClass.getMethod("getModule", String.class);
            Object bridgeModule = getModule.invoke(py, "pydataui.shell.bridge");

            Class<?> pyObjClass = Class.forName("com.chaquo.python.PyObject");
            java.lang.reflect.Method callAttr = pyObjClass.getMethod("callAttr", String.class, Object[].class);

            Object[] args = new Object[]{method, fullUrl, headersJson.toString(), ""};
            Object pyResult = callAttr.invoke(bridgeModule, "dispatch_in_process", args);

            java.lang.reflect.Method getAttr = pyObjClass.getMethod("get", String.class);
            Object statusObj = getAttr.invoke(pyResult, "status_code");
            Object bodyBytesObj = getAttr.invoke(pyResult, "body");
            Object contentTypeObj = getAttr.invoke(pyResult, "content_type");

            int statusCode = ((Number) statusObj.getClass().getMethod("toInt").invoke(statusObj)).intValue();
            byte[] bodyBytes = (byte[]) bodyBytesObj.getClass().getMethod("toJava", Class.class).invoke(bodyBytesObj, byte[].class);
            String contentType = (String) contentTypeObj.getClass().getMethod("toString").invoke(contentTypeObj);

            String mimeType = "text/html";
            String encoding = "UTF-8";
            if (contentType != null) {
                String[] parts = contentType.split(";");
                mimeType = parts[0].trim();
                for (String p : parts) {
                    if (p.trim().toLowerCase().startsWith("charset=")) {
                        encoding = p.trim().substring(8);
                    }
                }
            }

            Map<String, String> responseHeaders = new HashMap<>();
            responseHeaders.put("Access-Control-Allow-Origin", "*");
            responseHeaders.put("Cache-Control", "no-store");

            InputStream dataStream = new ByteArrayInputStream(bodyBytes != null ? bodyBytes : new byte[0]);
            return new WebResourceResponse(
                mimeType,
                encoding,
                statusCode,
                statusCode == 200 ? "OK" : "Error",
                responseHeaders,
                dataStream
            );

        } catch (ClassNotFoundException e) {
            return null;
        } catch (Exception e) {
            e.printStackTrace();
            String errHtml = "<div class='pdu-jni-error'>⚠️ JNI In-Process Bridge Error: " + e.getMessage() + "</div>";
            return new WebResourceResponse(
                "text/html",
                "UTF-8",
                500,
                "Internal Error",
                new HashMap<String, String>(),
                new ByteArrayInputStream(errHtml.getBytes(StandardCharsets.UTF_8))
            );
        }
    }
}
