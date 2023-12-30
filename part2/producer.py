import pika
import json
import time
from bson import json_util
import random
from faker import Faker
from model import Contact

credentials = pika.PlainCredentials("xtgzllnt", "4GDSnhfWem5lTuqARnDM9AfLYhrm7AhQ")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="cow-01.rmq2.cloudamqp.com",
        port=5672,
        credentials=credentials,
        virtual_host="xtgzllnt",
    )
)
channel = connection.channel()
exchange = "web16 hw8"
email_queue = "email_queue"
sms_queue = "sms_queue"

channel.exchange_declare(exchange=exchange, exchange_type="direct")
channel.queue_declare(queue=email_queue, durable=True)
channel.queue_declare(queue=sms_queue, durable=True)
channel.queue_bind(exchange=exchange, queue=email_queue)
channel.queue_bind(exchange=exchange, queue=sms_queue)

fake = Faker()


def main() -> None:
    Contact.objects().delete()
    inform = ["SMS", "email"]
    for i in range(10):
        contact = Contact(
            name=fake.name(),
            email=fake.email(),
            send=False,
            phone_number=fake.phone_number(),
            preferred_notifications=random.choice(inform),
        )
        contact.save()

        contact_data = {
            "contact_id": str(contact.id),
            "name": contact.name,
            "email": contact.email,
            "send": contact.send,
            "phone_number": contact.phone_number,
            "preferred_notifications": contact.preferred_notifications,
        }

        message = json.dumps(contact_data, default=json_util.default).encode()

        if contact.preferred_notifications == "SMS":
            contact.send = True
            contact.save()
            channel.basic_publish(
                exchange=exchange,
                routing_key=sms_queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )
            print(f" [x] Sent SMS to {contact.name}")

        elif contact.preferred_notifications == "email":
            contact.send = True
            contact.save()
            channel.basic_publish(
                exchange=exchange,
                routing_key=email_queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )
            print(f" [x] Sent email to {contact.name}")
            print("All messages sent. Waiting for consumers to finish...")
            time.sleep(3)


if __name__ == "__main__":
    main()
