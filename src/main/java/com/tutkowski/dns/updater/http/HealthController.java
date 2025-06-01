package com.tutkowski.dns.updater.http;

import com.sun.net.httpserver.HttpHandler;

import java.io.OutputStream;

public class HealthController implements IController {
    public String getPath() {
        return "/health";
    }

    public HttpHandler getHandler() {
        return (httpExchange) -> {
            String response = "{\"status\":\"UP\"}";
            httpExchange.sendResponseHeaders(200, response.length());
            try (OutputStream os = httpExchange.getResponseBody()) {
                os.write(response.getBytes());
            }
        };
    }
}
