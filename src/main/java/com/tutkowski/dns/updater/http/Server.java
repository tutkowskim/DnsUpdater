package com.tutkowski.dns.updater.http;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.sun.net.httpserver.HttpServer;
import com.tutkowski.dns.updater.Config;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.Set;

@Singleton
public class Server {
    private static final Logger logger = LoggerFactory.getLogger(Server.class);
    private final HttpServer httpServer;

    @Inject
    public Server(Config config, Set<IController> controllers) throws IOException {
        this.httpServer =  HttpServer.create(new InetSocketAddress(Integer.parseInt(config.PORT)), 0);
        for (IController controller : controllers) {
            this.httpServer.createContext(controller.getPath(), controller.getHandler());
            logger.info("Registered controller for path {}", controller.getPath());
        }
    }

    public void start() {
        this.httpServer.start();
        logger.info("Listening on port {}", httpServer.getAddress().getPort());
    }
}
