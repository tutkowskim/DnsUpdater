package com.tutkowski.dns.updater.tasks;

import com.google.inject.Inject;
import com.tutkowski.dns.updater.Config;
import com.tutkowski.dns.updater.clients.ipcheck.IpCheck;
import software.amazon.awssdk.services.route53.Route53Client;
import software.amazon.awssdk.services.route53.model.*;

import java.util.Collections;
import java.util.concurrent.TimeUnit;

public class UpdateTask implements ITask {
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
            System.out.println("Fetching current ip");
            String ipAddress = this.ipCheck.getCurrentIp();
            System.out.println("Found current ip to be " + ipAddress);

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
                System.out.println("Updating DNS entry to current IP");
                ChangeResourceRecordSetsResponse response = client.changeResourceRecordSets(request);
                System.out.println(response.changeInfo().toString());
                System.out.println("Successfully updated DNS entry");
            } catch (Exception e) {
                System.out.println("Failed to update DNS entry");
                throw e;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
