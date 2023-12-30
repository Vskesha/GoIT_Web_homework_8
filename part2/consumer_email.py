import sys
import os
import json

import pika

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
email_queue = "email_queue"

channel.queue_declare(queue=email_queue, durable=True)


def email_callback(ch, method, properties, body) -> None:
    contact_data = json.loads(body)
    contact_id = contact_data.get("contact_id")
    contact = Contact.objects(id=contact_id).first()

    if contact:
        contact.send = True
        contact.save()
        print(f"Sending email to {contact.email}...send.status: {contact.send}")


def main():
    channel.basic_consume(queue="email_queue", on_message_callback=email_callback)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
