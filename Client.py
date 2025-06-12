import socket
import hashlib
import time
from collections import deque

first_transmission = set()

def calculate_checksum(seq, data):
    return hashlib.md5((str(seq) + data).encode()).hexdigest()

def make_packet(seq, data):
    key = seq
    CFlag = False
    ACKFlag = False
    checksum = calculate_checksum(seq, data)
    if seq == 7 and key not in first_transmission:
        first_transmission.add(key)
        checksum = "corrupted_checksum"
    return f"{checksum}:{seq}:{ACKFlag}:{CFlag}:{data}"

def is_ack(pkt):
    try:
        seq, ackFlag, cFlag = pkt.split(':')
        return int(seq), ackFlag == 'True', cFlag == 'False'
    except:
        return -1, False, False


def rdt_send_gbn():
    host = 'localhost'
    port = 7336
    window_size = 4
    base = 0
    next_seq = 0
    timeout = 5
    max_seq = 8
    packet_buffer = deque()
    start_time = None
    # Add these variables at the start of rdt_send_gbn()
    last_ack = -1
    dup_ack_count = {}


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setblocking(False)

    while True:
        if next_seq < base + window_size:
            messages = ['pk1', 'pk2', 'pk3', 'pk4', 'pk5', 'pk6', 'pk7', 'pk8']
            remaining = (base + window_size) - next_seq
            print(f"\nWindow: {base % max_seq} to {(base + window_size - 1)%max_seq}, Next seq: {next_seq%max_seq}, Remaining: {remaining}")
            num_messages = len(messages)
            for _ in range(remaining):
                msg_index = next_seq % num_messages
                msg = messages[msg_index]
                seq = next_seq % max_seq
                pkt = make_packet(seq, msg)
                packet_buffer.append((seq, msg))
                client_socket.sendto(pkt.encode(), (host, port))
                print(f"Sent packet seq {seq}: {msg}")
                next_seq += 1


            if messages and start_time is None:
                start_time = time.time()
            
            time.sleep(2)

        try:
            response, _ = client_socket.recvfrom(1024)
            response = response.decode()
            print(f"\nReceived: {response}")

            ack_seq, ackFlag, cFlag = is_ack(response)
            if ackFlag:
                print(f"Valid ACK for seq {ack_seq}")
                
                # Duplicate ACK handling
                if ack_seq == last_ack:
                    dup_ack_count[ack_seq] = dup_ack_count.get(ack_seq, 0) + 1
                    print(f"Duplicate ACK count for {ack_seq}: {dup_ack_count[ack_seq]}")

                    if dup_ack_count[ack_seq] == 2:
                        print(f"\nFast retransmit triggered for seq {(ack_seq + 1) % max_seq}")
                        start_index = 0
                        for i, (seq, _) in enumerate(packet_buffer):
                            if seq == (ack_seq + 1) % max_seq:
                                start_index = i
                                break
                        # Resend packets from seq ack_seq + 1 to next_seq
                        for seq, msg in list(packet_buffer)[start_index:]:
                            pkt = make_packet(seq, msg)
                            client_socket.sendto(pkt.encode(), (host, port))
                            print(f"Fast retransmit packet seq {seq}: {msg}")
                        start_time = time.time()
                        dup_ack_count = {} 
                else:
                    last_ack = ack_seq
                    dup_ack_count = {}  # reset on new ACK

                # Slide the window
                while packet_buffer and (
                    packet_buffer[0][0] <= ack_seq or
                    (packet_buffer[0][0] > (max_seq // 2) and ack_seq < (max_seq // 2))
                ):
                    packet_buffer.popleft()
                    base += 1
                    

                if base == next_seq:
                    start_time = None
                else:
                    start_time = time.time()
            elif cFlag and ackFlag:
                print(f"Corrupted ACK for seq {ack_seq}")
                # Handle corrupted ACK
                if ack_seq in dup_ack_count:
                    dup_ack_count[ack_seq] += 1
                    if dup_ack_count[ack_seq] == 2:
                        print(f"\nFast retransmit triggered for seq {(ack_seq + 1) % max_seq}")
                        start_index = 0
                        for i, (seq, _) in enumerate(packet_buffer):
                            if seq == (ack_seq + 1) % max_seq:
                                start_index = i
                                break
                        # Resend packets from seq ack_seq + 1 to next_seq
                        for seq, msg in list(packet_buffer)[start_index:]:
                            pkt = make_packet(seq, msg)
                            client_socket.sendto(pkt.encode(), (host, port))
                            print(f"Fast retransmit packet seq {seq}: {msg}")
                        start_time = time.time()
                        dup_ack_count = {}
            else:
                print("Invalid ACK")
        except BlockingIOError:
            pass

        if start_time is not None and (time.time() - start_time > timeout):
            print(f"\nTimeout! Resending unacknowledged packets from seq {base % max_seq}")
            for seq, msg in packet_buffer:
                pkt = make_packet(seq, msg)
                client_socket.sendto(pkt.encode(), (host, port))
                print(f"Resent packet seq {seq}: {pkt}")
            start_time = time.time()

if __name__ == "__main__":
    rdt_send_gbn()
