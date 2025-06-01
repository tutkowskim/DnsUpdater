package com.tutkowski.dns.updater;

import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Key;
import com.google.inject.TypeLiteral;
import com.tutkowski.dns.updater.http.Server;
import com.tutkowski.dns.updater.tasks.ITask;

import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

public class Main {
    public static void main(String[] args) {
        try {
            Injector injector = Guice.createInjector(new AppModule());
            Server server = injector.getInstance(Server.class);
            server.start();

            Set<ITask> tasks = injector.getInstance(Key.get(new TypeLiteral<>() {}));
            ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
            for (ITask task : tasks) {
                scheduler.scheduleAtFixedRate(task, task.getInitialDelay(), task.getPeriod(), task.getTimeUnit());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}