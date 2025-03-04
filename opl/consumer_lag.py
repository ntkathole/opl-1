#!/usr/bin/env python3

import logging
import time
from kafka import KafkaConsumer
from kafka.consumer import group
from kafka import TopicPartition


class ConsumerLag:
    """
    ConsumerLag gets the lag info for a particular topic of all the partitions by providing
    bootstrap_server and kafka group as input.
    """
    def __init__(self, topic, bootstrap_servers, group) -> None:
        self.topic = topic
        self.group = group
        self.bootstrap_servers = bootstrap_servers
        self.logger = logging.getLogger('consumer_lag')
        self.offset_records = {}
    

    def _getconsumer(self):
        consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset="latest",
            enable_auto_commit=False,
            max_poll_records=50,
            max_poll_interval_ms=300000,
            group_id=self.group,
            session_timeout_ms=50000,
            heartbeat_interval_ms=10000,
            consumer_timeout_ms=100000)
        
        return consumer


    def store_offset_records(self):
        consumer = self._getconsumer()
        partition_set = consumer.partitions_for_topic(self.topic)
        counter = 0
        while counter < 5:
            counter += 1
            partition_set = consumer.partitions_for_topic(self.topic)
            if partition_set:
                break
            else:
                time.sleep(10)

        partitions = []
        for partition_id in partition_set:
            partitions.append(TopicPartition(self.topic, partition_id))

        curr_offsets = {}
        for partition in partitions:
            committed = consumer.committed(partition)
            curr_offsets[partition.partition] = committed

        end_offsets = consumer.end_offsets(partitions)
    
        for partition_id, value in curr_offsets.items():
            record = {'curr_offset': value, 'end_offset': end_offsets[TopicPartition(topic=self.topic, partition=partition_id)]}
            self.offset_records[partition_id] = record


    def get_lag(self):
        self.store_offset_records()
        response = True
        for _ , record in self.offset_records.items():
            diff = record['end_offset'] - record['curr_offset']
            if diff == 0:
                response *= True
            else:
                response *= False
        
        return response
