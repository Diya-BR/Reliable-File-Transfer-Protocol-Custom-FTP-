# Secure & Reliable Hybrid File Transfer Protocol

A custom file transfer implementation that utilizes a **Hybrid Architecture** (TCP/SSL + UDP) to balance security and custom reliability.

## 🚀 Key Features
- **SSL/TLS Handshake:** Secure metadata exchange (filename/offset) using an encrypted Control Channel.
- **Reliable UDP (RDT):** Custom implementation of the **Stop-and-Wait ARQ** protocol.
- **Data Integrity:** 16-bit summation checksums to prevent file corruption.
- **Resume Support:** Automatically detects existing partial files and resumes from the last confirmed byte.
- **Progress Tracking:** Real-time visual progress bar for monitoring transfers.

## 🛠️ System Architecture
The system operates in two distinct phases:
1. **Control Phase (TCP Port 5000):** Establish an SSL connection to negotiate the filename and determine the starting byte offset.
2. **Data Phase (UDP Port 5001):** Transfer file data in 1KB chunks with sequence-based acknowledgments (ACKs).

## 🚦 Setup & Execution

### Prerequisites
- Python 3.x
- SSL Certificates (`cert.pem`, `key.pem`) in the root directory.

### Running the System
1. **Start the Server:**
   ```bash
   python server.py
2. **Start the Server:**
   ```bash
   python client.py
