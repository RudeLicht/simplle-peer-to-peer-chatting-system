# echo-client.py

import socket
import threading

def main_menu():
    print("\nWelcome to pyChat\n")
    print("""
[1] Start Chatting
[2] Quit
    """)
    choice = input(">:")
    while choice not in ['1', '2']:
        choice = input(">:")
    
    match choice:
        case '1':
            start_chatting()
        case '2':
            print("Goodbye!")
            quit()

def start_chatting(): 
    def receive_messages(sock, username):
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break

                # Check if the message contains the expected delimiter
                if ": " in data.decode('utf-8'):
                    # Split the message into sender and content
                    sender, message = data.decode('utf-8').split(": ", 1)

                    # Determine the color based on the sender
                    color = '\033[94m' if sender == username else '\033[92m'

                    # Print the formatted message with color, excluding sender's own messages
                    if sender != username:
                        print(f"\n{color}{sender}: {message}\033[0m\n")
                else:
                    print(f"\n\033[94mServer: {data.decode('utf-8')}\n")  # Handle messages from the server

            except OSError as e:
                if "Bad file descriptor" in str(e):
                    break
                else:
                    raise

    HOST = "127.0.0.1"
    PORT = 65432

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    name = input("Enter your username: ")
    name_byte = bytes(name, encoding="utf-8")
    s.send(name_byte)

    # Start a separate thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(s, name)).start()

    print("Chat started. Type your messages. Type '!bye' to exit.\n")

    while True:
        msg = input()
        print("^ Sent")
        msg_byte = bytes(msg, encoding="utf-8")
        s.send(msg_byte)

        if msg == "!bye":
            break

    s.close()

if __name__ == "__main__":
    main_menu()