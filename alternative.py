# airdrop_alternative.py
import socket
import threading
import os

# Define constants
SERVER_HOST = "0.0.0.0"  # Use all available interfaces
SERVER_PORT = 5001  # Port to listen on for connections
BUFFER_SIZE = 4096  # Size of data packets for transfer

# Define function to handle incoming file requests
def handle_client(client_socket, client_address):
    print(f"[+] Connection from {client_address} established.")
    
    # Receive filename and file size
    file_info = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = file_info.split("|")
    filename = os.path.basename(filename)
    filesize = int(filesize)
    
    # Prepare to receive the file
    with open(filename, "wb") as f:
        print(f"[+] Receiving {filename}...")
        bytes_received = 0
        while bytes_received < filesize:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            bytes_received += len(bytes_read)
        print(f"[+] File received: {filename}")
    
    client_socket.close()

# Server to listen for incoming file transfer requests
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Server listening on {SERVER_HOST}:{SERVER_PORT}...")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

# Client to send files to the server
def send_file(server_ip, filepath):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, SERVER_PORT))
    
    # Send filename and file size
    filesize = os.path.getsize(filepath)
    file_info = f"{os.path.basename(filepath)}|{filesize}"
    client_socket.send(file_info.encode())
    
    # Send file data
    with open(filepath, "rb") as f:
        print(f"[*] Sending {filepath} to {server_ip}...")
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)
    print(f"[+] File {filepath} sent successfully.")
    
    client_socket.close()

# To start as server or client
if __name__ == "__main__":
    import sys
    mode = input("Start as (server/client): ").strip().lower()
    if mode == "server":
        start_server()
    elif mode == "client":
        server_ip = input("Enter server IP: ").strip()
        filepath = input("Enter file path to send: ").strip()
        if os.path.exists(filepath):
            send_file(server_ip, filepath)
        else:
            print("File does not exist.")
    else:
        print("Invalid mode. Please choose 'server' or 'client'.")
