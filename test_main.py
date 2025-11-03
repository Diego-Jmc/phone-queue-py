import unittest
import threading
from main import Queue, Consumer, Producer

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.q = Queue()

    def test_enqueue_and_dequeue(self):
        self.q.enqueue("A")
        self.q.enqueue("B")
        self.assertEqual(self.q.size(), 2)
        self.assertEqual(self.q.dequeue(), "A")
        self.assertEqual(self.q.dequeue(), "B")
        self.assertTrue(self.q.is_empty())

    def test_overflow(self):
        for i in range(self.q.limit):
            self.q.enqueue(i)
        with self.assertRaises(OverflowError):
            self.q.enqueue(999)

    def test_dequeue_empty(self):
        with self.assertRaises(IndexError):
            self.q.dequeue()


class TestConsumer(unittest.TestCase):
    def setUp(self):
        self.consumer = Consumer()

    def test_validate_short(self):
        result = self.consumer.validate("123")
        self.assertEqual(len(result), 11)
        self.assertTrue(result.endswith("0"))

    def test_validate_long(self):
        result = self.consumer.validate("1234567890123")
        self.assertEqual(len(result), 11)

    def test_decode_word(self):
        # T=8, E=33, S=7777, T=8 -> 83377778
        self.assertEqual(self.consumer.decode("TEST"), "83377778")


class TestProducerConsumerIntegration(unittest.TestCase):
    def test_producer_consumer(self):
        q = Queue()
        producer_done = threading.Event()
        producer = Producer(["CALL-NOW", "HELLO"])
        consumer = Consumer()

        t1 = threading.Thread(target=producer.produce, args=(q, producer_done))
        t2 = threading.Thread(target=consumer.consume, args=(q, producer_done))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertTrue(producer_done.is_set())
        self.assertTrue(q.is_empty())


if __name__ == "__main__":
    unittest.main()
