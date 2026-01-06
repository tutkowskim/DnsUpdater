package com.tutkowski.dns.updater;

public class Config {
    // server settings
    public final String PORT;

    // aws settings
    public final String HOSTED_ZONE_ID;
    public final String RECORD_NAME;

    // observability settings
    public final String SENTRY_DSN;

    public Config() {
        this.PORT = System.getenv().getOrDefault("PORT", "8080");
        this.HOSTED_ZONE_ID = System.getenv().get("HOSTED_ZONE_ID");
        this.RECORD_NAME = System.getenv().get("RECORD_NAME");
        this.SENTRY_DSN = System.getenv().get("SENTRY_DSN");
    }
}
