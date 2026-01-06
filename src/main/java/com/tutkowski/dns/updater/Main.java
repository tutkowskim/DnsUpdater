package com.tutkowski.dns.updater;

import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Key;
import com.google.inject.TypeLiteral;
import com.tutkowski.dns.updater.http.Server;
import com.tutkowski.dns.updater.tasks.ITask;
import io.sentry.Sentry;
import io.sentry.SentryLevel;
import io.sentry.SentryOptions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

public class Main {
    private static final Logger logger = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {
        try {
            Injector injector = Guice.createInjector(new AppModule());
            
            Config config = injector.getInstance(Config.class);
            configureSentry(config);

            Server server = injector.getInstance(Server.class);
            server.start();
            logger.info("HTTP server started");

            Set<ITask> tasks = injector.getInstance(Key.get(new TypeLiteral<>() {}));
            ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
            for (ITask task : tasks) {
                scheduler.scheduleAtFixedRate(task, task.getInitialDelay(), task.getPeriod(), task.getTimeUnit());
                logger.info(
                        "Scheduled task {} with initialDelay={} {} period={} {}",
                        task.getClass().getSimpleName(),
                        task.getInitialDelay(),
                        task.getTimeUnit(),
                        task.getPeriod(),
                        task.getTimeUnit()
                );
            }
        } catch (Exception e) {
            logger.error("Fatal error during startup", e);
            Sentry.captureException(e);
        }
    }

    private static void configureSentry(Config config) {
        if (config.SENTRY_DSN == null || config.SENTRY_DSN.isBlank()) {
            logger.info("Sentry disabled (missing SENTRY_DSN)");
            return;
        }

        Sentry.init(options -> {
            options.setDsn(config.SENTRY_DSN);
            options.setTracesSampleRate(1.0);
            options.setDiagnosticLevel(SentryLevel.INFO);
        });
        logger.info("Sentry enabled");
    }
}
