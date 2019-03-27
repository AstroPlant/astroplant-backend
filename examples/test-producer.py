from confluent_kafka import Producer
import json


producer = Producer({
    "bootstrap.servers": "lb.cluster-astroplant-dev.aws.surfsaralabs.nl:9999",
    #"debug": "security",
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": "",
    "sasl.password": ""
    })


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


# Trigger any available delivery report callbacks from previous produce() call
producer.poll(0)

# Asynchronously produce a message, the delivery report callback
# will be triggered from poll() above, or flush() below, when the message has
# been successfully delivered or failed permanently.
producer.produce('test', value="42", callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
producer.flush()
