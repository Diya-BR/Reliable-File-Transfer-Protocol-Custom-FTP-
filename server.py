import socket
import ssl
import threading
import os
import struct

TCP_PORT = 5000
UDP_PORT = 5001

def handle_client(secure_conn):
    udp_sock = None
    try:
        # 1. SSL Handshake
        data = secure_conn.recv(1024).decode()
        if not data: return
        filename = "received_" + data.strip()
        
        # Resume Logic
        resume_offset = os.path.getsize(filename) if os.path.exists(filename) else 0
        secure_conn.send(str(resume_offset).encode(), )
        secure_conn.close()
        print(f"[*] SSL Handshake complete. Target: {filename}", flush=True)
        print(f"[*] Server starting from byte: {resume_offset}", flush=True)

        # 2. UDP Setup
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(('0.0.0.0', UDP_PORT))
        udp_sock.settimeout(15.0) 

        expected_seq = resume_offset // 1024
        
        with open(filename, "ab" if resume_offset > 0 else "wb") as f:
            while True:
                try:
                    packet, addr = udp_sock.recvfrom(1032)
                    header = packet[:8]
                    payload = packet[8:]
                    seq, chk, d_len = struct.unpack('!IHH', header)

                    if seq == 999999: # EOF Signal
                        print(f"\n[+] SUCCESS: {filename} fully received!", flush=True)
                        break
                    
                    # Reliability check
                    if seq == expected_seq:
                        if (sum(payload) & 0xFFFF) == chk:
                            f.write(payload)
                            f.flush() # Ensure it's on the disk
                            
                            # Send ACK
                            udp_sock.sendto(struct.pack('!I', seq), addr)
                            print(f"[OK] Received Packet {seq}", flush=True)
                            expected_seq += 1
                        else:
                            print(f"[!] Checksum error on packet {seq}", flush=True)
                    else:
                        # If we get an old packet, we still ACK it so the client moves on
                        if seq < expected_seq:
                            udp_sock.sendto(struct.pack('!I', seq), addr)

                except socket.timeout:
                    print("\n[!] UDP Timeout: No data received for 15s.", flush=True)
                    break
    except Exception as e:
        print(f"[!] Server error: {e}", flush=True)
    finally:
        if udp_sock:
            udp_sock.close()

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', TCP_PORT))
    server_socket.listen(5)
    print(f"--- SERVER LIVE ON PORT {TCP_PORT} ---", flush=True)

    while True:
        client_sock, _ = server_socket.accept()
        secure_conn = context.wrap_socket(client_sock, server_side=True)
        threading.Thread(target=handle_client, args=(secure_conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()