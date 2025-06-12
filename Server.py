import socket
import hashlib

def calculate_checksum(seq, data):
    return hashlib.md5((str(seq) + data).encode()).hexdigest()

def is_corrupted(packet):
    try:
        checksum, seq, ACKFlag , CFlag , data = packet.split(':')
        return checksum != calculate_checksum(int(seq), data)
    except:
        return True

def make_ack(seq, cFlag=False, ackFlag=True):
    return f"{seq}:{ackFlag}:{cFlag}"

def rdt_receive_gbn():
    host = 'localhost'
    port = 7336
    max_seq = 8
    expected_seq = 0
    count = 0

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server listening on port: {port}...")

    while True:
        data, addr = server_socket.recvfrom(1024)
        packet = data.decode()
        print(f"\nReceived: {packet}")

        if is_corrupted(packet):
            print(f"Corrupted packet. Sending ACK {((expected_seq - 1) % max_seq)}")
            server_socket.sendto(make_ack((expected_seq - 1) % max_seq,cFlag=True,ackFlag=True).encode(), addr)
            continue

        try:
            _, seq,cFLag,ackFlag, msg = packet.split(':', 4)
            seq = int(seq)
        except:
            print("Malformed packet.")
            continue

        
        if seq == expected_seq:
            # Simulate packet loss for packet 1
            if seq == 1 and count == 0:
                count += 1
                print("Simulating packet loss for seq 1")
                continue

            # # Simulate ACK loss for packet 2
            # if seq == 2 and count == 1:
            #     count += 1
            #     expected_seq = (expected_seq + 1) % max_seq
            #     print("Simulating ACK loss for seq 2")
            #     continue

            # Normal packet processing
            print(f"Delivered: {msg}")
            print("----------------------")
            server_socket.sendto(make_ack(seq,cFlag=False,ackFlag=True).encode(), addr)
            expected_seq = (expected_seq + 1) % max_seq
        else:
            print(f"Out-of-order packet. Expected {expected_seq}, got {seq}")
            print("----------------------")
            server_socket.sendto(make_ack((expected_seq - 1) % max_seq,cFlag=False,ackFlag=True).encode(), addr)

if __name__ == "__main__":
    rdt_receive_gbn()
