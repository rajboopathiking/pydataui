package com.pydataui.app;

import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebViewClient;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(PyDataUIBridgePlugin.class);
        super.onCreate(savedInstanceState);

        // Attach in-process JNI interceptor to the Capacitor WebView
        WebView webView = getBridge().getWebView();
        if (webView != null) {
            webView.setWebViewClient(new BridgeWebViewClient(getBridge()) {
                @Override
                public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                    WebResourceResponse intercepted = PyDataUIWebViewInterceptor.interceptRequest(MainActivity.this, request);
                    if (intercepted != null) {
                        return intercepted;
                    }
                    return super.shouldInterceptRequest(view, request);
                }
            });
        }
    }
}
