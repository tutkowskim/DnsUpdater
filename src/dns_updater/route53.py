"""Route 53 DNS record operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_route53 import Route53Client
    from mypy_boto3_route53.type_defs import ChangeResourceRecordSetsResponseTypeDef


class Route53RecordUpdater:
    """UPSERT an IPv4 address into a Route 53 A record."""

    def __init__(
        self,
        hosted_zone_id: str,
        record_name: str,
        ttl_seconds: int,
        client: Route53Client | None = None,
    ):
        self._hosted_zone_id = hosted_zone_id
        self._record_name = record_name
        self._ttl_seconds = ttl_seconds
        self._client = client

    def upsert_a_record(self, ip_address: str) -> ChangeResourceRecordSetsResponseTypeDef:
        """Submit an A-record UPSERT and return the AWS response."""

        if self._client is None:
            self._client = boto3.client("route53")

        return self._client.change_resource_record_sets(
            HostedZoneId=self._hosted_zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": self._record_name,
                            "Type": "A",
                            "TTL": self._ttl_seconds,
                            "ResourceRecords": [{"Value": ip_address}],
                        },
                    }
                ]
            },
        )
