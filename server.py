import socket
import threading

HOST = "127.0.0.1"
PORT = 65432

exit_event = threading.Event()  # Event to signal threads to exit

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()

connections = []
usernames = []
lock = threading.Lock()

def check_connections():
    while not exit_event.is_set():
        try:
            conn, addr = s.accept()
            print(f"Connected by {addr}")

            username = conn.recv(1024).decode('utf-8')
            print(f"{username} joined the chat")

            with lock:
                connections.append(conn)
                usernames.append(username)

            for connection in connections:
                try:
                    connection.send(f"{username} joined the chat".encode('utf-8'))
                except OSError as e:
                    print(f"Error broadcasting message to {addr}: {e}")
                    handle_disconnect(connection, addr)

            threading.Thread(target=check_chatting, args=(conn, addr, username)).start()
        except OSError as e:
            # Handle errors during accept, e.g., if the socket is closed
            print(f"Error accepting connection: {e}")

def check_chatting(conn, addr, username):
    while not exit_event.is_set():
        try:
            data = conn.recv(1024)
            if not data:
                break  # Connection closed by the client

            print(f"{username}: {data.decode('utf-8')}")

            if data == b'!bye':
                break  # Close the connection for this client

            with lock:
                broadcast_message(username, data, addr)
        except OSError as e:
            # Handle errors during recv, e.g., if the connection is closed
            print(f"Error in thread for {username}: {e}")
            break

    with lock:
        handle_disconnect(conn, addr)

def broadcast_message(sender, message, addr):
    for connection in connections:
        try:
            connection.send(f"{sender}: {message.decode('utf-8')}".encode('utf-8'))
        except OSError as e:
            print(f"Error broadcasting message to {addr}: {e}")
            index = connections.index(connection)
            with lock:
                connection.send(f"{username} disconnected".encode('utf-8'))
                connections.pop(index)
                username = usernames.pop(index)
                print(f"Connection with {addr} closed for {username}")
                connection.close()

def handle_disconnect(connection, addr):
    index = connections.index(connection)
    with lock:
        try:
            username = usernames.pop(index)
            print(f"Connection with {addr} closed for {username}")
            connection.send(f"{username} disconnected".encode('utf-8'))
            connection.close()
            connections.pop(index)
        except IndexError:
            pass

if __name__ == "__main__":
    threading.Thread(target=check_connections).start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Server shutting down...")
        exit_event.set()  # Set the exit event to signal threads to exit
