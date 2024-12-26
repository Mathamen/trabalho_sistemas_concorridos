import socket
import threading
import time
import queue

class Coordinator:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.connections = {}  # process_id -> socket
        self.request_queue = queue.Queue()
        self.current_process = None
        self.lock = threading.Lock()

        self.log_file = open("coordinator_log.txt", "a")
        self.process_count = {}

    def start(self):
        print("Coordinator: running...")
        threading.Thread(target=self.accept_connections, daemon=True).start()
        threading.Thread(target=self.interface_thread, daemon=True).start()
        self.process_requests()

    def accept_connections(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except:
                break

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                parts = data.split("|")
                msg_type = parts[0]
                process_id = parts[1]
                if msg_type == "REQUEST":
                    with self.lock:
                        self.connections[process_id] = client_socket
                        self.request_queue.put(process_id)
                    self.log_msg("RECEIVED", data, client_socket.getpeername())
                elif msg_type == "RELEASE":
                    with self.lock:
                        self.log_msg("RECEIVED", data, client_socket.getpeername())
                        if self.current_process == process_id:
                            self.current_process = None
                else:
                    self.log_msg("UNKNOWN", data, client_socket.getpeername())
            except:
                break
        client_socket.close()

    def process_requests(self):
        while True:
            with self.lock:
                if not self.current_process and not self.request_queue.empty():
                    proc_id = self.request_queue.get()
                    sock = self.connections.get(proc_id)
                    if sock:
                        try:
                            grant_msg = f"GRANT|{proc_id}|{int(time.time()*1000)}"
                            sock.send(grant_msg.encode())
                            self.log_msg("SENT", grant_msg, sock.getpeername())
                            self.current_process = proc_id
                            self.process_count[proc_id] = self.process_count.get(proc_id, 0) + 1
                        except:
                            pass
            time.sleep(0.05)

    def interface_thread(self):
        while True:
            cmd = input("Comando (1=exibir fila, 2=contagem processos, 3=sair): ")
            if cmd == "1":
                with self.lock:
                    print(list(self.request_queue.queue))
            elif cmd == "2":
                print(self.process_count)
            elif cmd == "3":
                self.log_file.close()
                self.server_socket.close()
                break

    def log_msg(self, msg_type, message, addr):
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_str = f"{t} | {msg_type} | {message} | {addr}\n"
        self.log_file.write(log_str)
        self.log_file.flush()