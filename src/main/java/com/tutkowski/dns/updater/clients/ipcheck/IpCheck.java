package com.tutkowski.dns.updater.clients.ipcheck;

import com.google.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

@Singleton
public class IpCheck {
    private static final Logger logger = LoggerFactory.getLogger(IpCheck.class);
    private static final HttpClient client = HttpClient.newHttpClient();

    public String getCurrentIp() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://checkip.amazonaws.com/"))
                .GET()
                .build();

        logger.debug("Requesting public IP from checkip.amazonaws.com");
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        String body = response.body();
        if (body == null || body.isBlank()) {
            logger.warn("Received empty response when fetching public IP");
            return "";
        }
        return body.trim();
    }
}
