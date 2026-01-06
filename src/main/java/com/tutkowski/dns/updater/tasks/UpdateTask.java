package com.tutkowski.dns.updater.tasks;

import com.google.inject.Inject;
import com.tutkowski.dns.updater.Config;
import com.tutkowski.dns.updater.clients.ipcheck.IpCheck;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.services.route53.Route53Client;
import software.amazon.awssdk.services.route53.model.*;

import java.util.Collections;
import java.util.concurrent.TimeUnit;

public class UpdateTask implements ITask {
    private static final Logger logger = LoggerFactory.getLogger(UpdateTask.class);
    private final Config config;
    private final IpCheck ipCheck;

    @Inject
    public UpdateTask(Config config, IpCheck ipCheck) {
        this.config = config;
        this.ipCheck = ipCheck;
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.MINUTES;
    }

    @Override
    public long getPeriod() {
        return 5;
    }

    @Override
    public long getInitialDelay() {
        return 0;
    }

    @Override
    public void run() {
        try {
            logger.info("Fetching current public IP");
            String ipAddress = this.ipCheck.getCurrentIp();
            logger.info("Current public IP is {}", ipAddress);

            ResourceRecord record = ResourceRecord.builder().value(ipAddress).build();

            ResourceRecordSet recordSet = ResourceRecordSet.builder()
                    .name(config.RECORD_NAME)
                    .type(RRType.A)
                    .ttl(900L)
                    .resourceRecords(Collections.singletonList(record))
                    .build();

            Change change = Change.builder()
                    .action(ChangeAction.UPSERT)
                    .resourceRecordSet(recordSet)
                    .build();

            ChangeBatch changeBatch = ChangeBatch.builder().changes(change).build();

            ChangeResourceRecordSetsRequest request = ChangeResourceRecordSetsRequest.builder()
                    .hostedZoneId(config.HOSTED_ZONE_ID)
                    .changeBatch(changeBatch)
                    .build();

            try (Route53Client client = Route53Client.create()) {
                logger.info("Updating Route53 record {} in zone {}", config.RECORD_NAME, config.HOSTED_ZONE_ID);
                ChangeResourceRecordSetsResponse response = client.changeResourceRecordSets(request);
                logger.info("Route53 change submitted: {}", response.changeInfo());
                logger.info("Successfully updated DNS entry");
            } catch (Exception e) {
                logger.error("Failed to update DNS entry", e);
                throw e;
            }
        } catch (Exception e) {
            logger.error("Update task failed", e);
        }
    }
}
