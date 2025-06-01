package com.tutkowski.dns.updater.http;

import com.sun.net.httpserver.HttpHandler;

public interface IController {
    String getPath();
    HttpHandler getHandler();
}
