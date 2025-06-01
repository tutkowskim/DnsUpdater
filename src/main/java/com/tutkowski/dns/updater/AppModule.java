package com.tutkowski.dns.updater;

import com.google.inject.AbstractModule;
import com.google.inject.multibindings.Multibinder;
import com.tutkowski.dns.updater.clients.ipcheck.IpCheck;
import com.tutkowski.dns.updater.http.HealthController;
import com.tutkowski.dns.updater.http.IController;
import com.tutkowski.dns.updater.http.Server;
import com.tutkowski.dns.updater.tasks.ITask;
import com.tutkowski.dns.updater.tasks.UpdateTask;

public class AppModule extends AbstractModule {
    @Override
    protected void configure() {
        bind(Config.class);

        // Http
        bind(Server.class);
        Multibinder<IController> controllerBinder = Multibinder.newSetBinder(binder(), IController.class);
        controllerBinder.addBinding().to(HealthController.class);

        // Clients
        bind(IpCheck.class);

        // Tasks
        Multibinder<ITask> tasksBinder = Multibinder.newSetBinder(binder(), ITask.class);
        tasksBinder.addBinding().to(UpdateTask.class);
    }
}
