import socket
import time
import random

class Process:
    def __init__(self, host, port, process_id, r, k):
        self.host = host
        self.port = port
        self.process_id = process_id
        self.r = r
        self.k = k

    def start(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        for _ in range(self.r):
            # Atraso aleatório usando k
            time.sleep(random.uniform(0, self.k))

            req_msg = f"REQUEST|{self.process_id}|{int(time.time()*1000)}"
            try:
                client_socket.send(req_msg.encode())
                client_socket.settimeout(200)
            except:
                pass
            
            try:
                resp = client_socket.recv(1024).decode()
                if resp.startswith("GRANT"):
                    with open("resultado.txt", "a") as f:
                        now_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        ms = int(time.time()*1000) % 1000
                        f.write(f"Process {self.process_id}: {now_str}.{ms}\n")

                    time.sleep(self.k)

                    release_msg = f"RELEASE|{self.process_id}|{int(time.time()*1000)}"
                    client_socket.send(release_msg.encode())
                elif resp.startswith("SHUTDOWN"):
                    print(f"Process {self.process_id}: Encerrando cliente ao receber SHUTDOWN.")
                    break
                else:
                    print(f"{self.process_id} recebeu resposta inesperada: {resp}")
            except socket.timeout:
                print(f"{self.process_id} - Timeout esperando GRANT")
            except Exception as e:
                if e.errno == 10038:  # Ignorar se o erro for relacionado a socket inválido
                    pass
                elif e.errno == 10053:  # Ignorar se o erro for relacionado a socket inválido
                   pass
                else:
                    print(f"{self.process_id} - Erro: {e}")
            
        client_socket.close()