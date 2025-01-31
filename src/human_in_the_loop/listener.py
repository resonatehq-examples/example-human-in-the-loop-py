import socket
from ._constants import HOST, PORT


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                buffer = ""
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    buffer += data.decode()
                    # Split received data into lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        print(line)
                # Print any remaining data after connection closes
                if buffer:
                    print(buffer)
