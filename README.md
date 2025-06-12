
---


# GBN-Sim: Go-Back-N ARQ Protocol Simulator

This project simulates the **Go-Back-N (GBN)** reliable data transfer protocol using UDP sockets in Python. It demonstrates core networking concepts such as packet loss, corruption, retransmissions, window-based flow control, and fast retransmit behavior.

## 🚀 Features

- Implements **Go-Back-N ARQ** for reliable data transmission
- Simulates:
  - Packet corruption
  - Packet loss
  - Duplicate ACKs
  - Fast retransmission
  - Sliding window mechanism
- Checksum-based error detection using MD5
- Window sliding & timeout retransmission
- Real-time packet logs


## 🗂️ Folder Structure

```

📁 GBN-Sim/
├── sender.py          # Client-side: Sends packets with Go Back N logic
├── receiver.py        # Server-side: Receives packets and replies with ACKs
├── README.md          # Project documentation

````

## ⚙️ How It Works

- **Sender (`sender.py`)**:
  - Sends a fixed set of 8 packets (`pk1` to `pk8`)
  - Maintains a sliding window (size = 4)
  - Tracks timeouts and duplicate ACKs
  - Retransmits on timeout or 2 duplicate ACKs (Fast Retransmit)

- **Receiver (`receiver.py`)**:
  - Receives packets, validates checksum
  - Sends ACK if correct, or last ACK on corruption/loss
  - Simulates packet loss (for seq 1) and corruption (for seq 7)

## ▶️ How to Run

1. Open two terminal windows.
2. Start the receiver in one terminal:
   ```bash
   python Server.py
3. Start the sender in the other terminal:

   ```bash
   python Client.py
   ```

> ⚠️ Make sure both files are in the same directory and Python 3 is installed.

## 📚 Concepts Demonstrated

* Reliable data transfer using **Go-Back-N**
* Sliding window protocol for efficiency
* Timeout-based and duplicate ACK-based retransmissions
* Packet loss & corruption handling with checksum
* UDP socket programming in Python

## 🧠 Learning Objective

This simulation helps students understand how reliability is achieved over UDP, how window-based protocols work, and how retransmissions are handled in real-world scenarios.

---

Developed as part of a **Computer Networks** course project to demonstrate core protocol logic without external libraries.

