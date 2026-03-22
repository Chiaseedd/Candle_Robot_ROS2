import socket
import time
t = time.time()
try:
    socket.getaddrinfo(socket.gethostname(), 0, socket.AF_UNSPEC, socket.SOCK_STREAM)
except Exception as e:
    print(f"Error: {e}")
print(f"Time: {time.time() - t}")
