import socket
import threading
import secrets
import base64

def handle_client(client_socket: socket.socket, client_address):
    """Handle individual client connections with challenge-response protocol"""
    try:
        print(f"Connection from {client_address}")
        
        # Step 1: Generate and send a random message
        random_message = secrets.token_hex(16)  # 32 character hex string
        print(f"Sending challenge to {client_address}: {random_message}")
        
        challenge = f"{random_message}\n"
        client_socket.send(challenge.encode('utf-8'))
        
        # Step 2: Wait for client's base64url encoded response
        client_socket.settimeout(30)  # 30 second timeout
        response = client_socket.recv(1024).decode('utf-8').strip()
        print(f"Received response from {client_address}: {response}")
        
        # Step 3: Verify the response
        try:
            # Encode our original message in base64url for comparison
            expected_encoded = base64.urlsafe_b64encode(random_message.encode('utf-8')).decode('utf-8')
            
            # Remove any padding for comparison (base64url standard)
            expected_encoded = expected_encoded.rstrip('=')
            response_cleaned = response.rstrip('=')
            
            print(f"Expected: {expected_encoded}")
            print(f"Received: {response_cleaned}")
            
            # Step 4: Send verification result
            if expected_encoded == response_cleaned:
                result_message = "SUCCESS: Correct base64url encoding!\n"
                print(f"✓ Client {client_address} provided correct encoding")
            else:
                result_message = "FAILURE: Incorrect base64url encoding!\n"
                print(f"✗ Client {client_address} provided incorrect encoding")
                
        except Exception as decode_error:
            result_message = f"ERROR: Invalid base64url format - {decode_error}\n"
            print(f"✗ Client {client_address} sent invalid format: {decode_error}")
        
        # Send the final result to client
        client_socket.send(result_message.encode('utf-8'))
        
    except socket.timeout:
        print(f"✗ Client {client_address} timed out")
        try:
            timeout_message = "ERROR: Response timeout\n"
            client_socket.send(timeout_message.encode('utf-8'))
        except:
            pass
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        # Close the client connection
        client_socket.close()
        print(f"Connection to {client_address} closed")

def start_tcp_server(host='0.0.0.0', port=8080):
    """Start the TCP server"""
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow socket reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind the socket to host and port
        server_socket.bind((host, port))
        
        # Listen for incoming connections (max 5 in queue)
        server_socket.listen(5)
        
        print("Protocol: Challenge-Response with base64url encoding")
        print("Waiting for connections...")
        
        while True:
            # Accept incoming connection
            client_socket, client_address = server_socket.accept()
            
            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_tcp_server()
