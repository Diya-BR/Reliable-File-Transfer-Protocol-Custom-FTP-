import socket, ssl, struct, os, time

def send_file():
    FILENAME = input("Enter Filename(With extension):") # Or "Kurose-7.pdf"
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.create_connection(('127.0.0.1', 5000)) as sock:
        with context.wrap_socket(sock, server_hostname='127.0.0.1') as ssock:
            ssock.send(FILENAME.encode())
            resume_offset = int(ssock.recv(1024).decode())
            print(f"[*] Starting from byte: {resume_offset}")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(2.0)
    
    with open(FILENAME, 'rb') as f:
        f.seek(resume_offset)
        seq = resume_offset // 1024
        while True:
            chunk = f.read(1024)
            if not chunk: break
            packet = struct.pack('!IHH', seq, sum(chunk) & 0xFFFF, len(chunk)) + chunk
            
            acked = False
            while not acked:
                udp_sock.sendto(packet, ('127.0.0.1', 5001))
                try:
                    ack_data, _ = udp_sock.recvfrom(4)
                    if struct.unpack('!I', ack_data)[0] == seq:
                        print(f"[ACK] Packet {seq} confirmed. Pausing 5s...")
                        acked = True
                        seq += 1
                        time.sleep(5) # Observable pause
                except socket.timeout:
                    print(f"[!] Retrying packet {seq}...")
        
        udp_sock.sendto(struct.pack('!IHH', 999999, 0, 0), ('127.0.0.1', 5001))
        print("[+] Success!")

if __name__ == "__main__":
    send_file()