import json
import threading
import time


class Queue:
    limit = 10

    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        if self.size() >= self.limit:
            raise OverflowError("enqueue to full queue")
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        raise IndexError("dequeue from empty queue")

    def size(self):
        return len(self.items)

class Consumer:
    phone_number_map = {
        "2": ["A", "B", "C"],
        "3": ["D", "E", "F"],
        "4": ["G", "H", "I"],
        "5": ["J", "K", "L"],
        "6": ["M", "N", "O"],
        "7": ["P", "Q", "R", "S"],
        "8": ["T", "U", "V"],
        "9": ["W", "X", "Y", "Z"]
    }

    def validate(self, phone_number):
        if len(phone_number) > 11:
            phone_number = phone_number[-11:]
        if len(phone_number) < 11:
            phone_number = phone_number.ljust(11, '0')
        return phone_number

    def decode(self, phone_number):
        result = ""
        for char in phone_number.upper():
            for number, letters in self.phone_number_map.items():
                if char in letters:
                    result += number
                    break
            else:
                result += char
        return result

    def consume(self, queue, producer_done):
        while True:
            if not queue.is_empty():
                phone_number = queue.dequeue()
                validated_number = self.validate(phone_number)
                decoded_number = self.decode(validated_number)
                print(f"[Consumer] {phone_number} -> {decoded_number}")
            elif producer_done.is_set():
                print("[Consumer] No more phone numbers")
                break
            else:
                time.sleep(0.5)

class Producer:
    def __init__(self, phone_numbers):
        self.phone_numbers = phone_numbers

    def produce(self, queue, producer_done):
        # queue phone numbers
        for number in self.phone_numbers:
            try:
                queue.enqueue(number)
                print(f"[Producer] Enqueued: {number}")
                time.sleep(1)
            except OverflowError:
                print("[Producer] Queue full, waiting...")
                time.sleep(1)

        print("[Producer] Producción terminada.")
        producer_done.set() # Producer has finished

def main():

    #create queue 
    q = Queue()

    # load from JSON file   
    with open("phone_numbers.json", "r") as file:
        data = json.load(file)
        phone_numbers = data["phone_numbers"]

    producer = Producer(phone_numbers)
    consumer = Consumer()

    # Notify the consumer when the producer is done
    producer_done = threading.Event()

    producer_thread = threading.Thread(target=producer.produce, args=(q, producer_done))
    consumer_thread = threading.Thread(target=consumer.consume, args=(q, producer_done))

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

if __name__ == "__main__":
    main()
