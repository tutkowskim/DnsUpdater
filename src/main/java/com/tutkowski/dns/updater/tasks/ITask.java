package com.tutkowski.dns.updater.tasks;

import java.util.concurrent.TimeUnit;

public interface ITask extends Runnable {
    TimeUnit getTimeUnit();

    long getPeriod();

    long getInitialDelay();
}
