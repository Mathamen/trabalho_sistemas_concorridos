import threading
import random
from coordinator import Coordinator
from process import Process

if __name__ == "__main__":
    coord = Coordinator("localhost", 12345)
    coord_thread = threading.Thread(target=coord.start)
    coord_thread.start()

    process_threads = []
    for i in range(5):
        # Maior variação de k
        k = random.randint(10, 200)
        k = k/100
        p = Process("localhost", 12345, f"P{i}", r=20,k=k)
        t = threading.Thread(target=p.start)
        t.start()
        process_threads.append(t)

    for t in process_threads:
        t.join()

    coord_thread.join()