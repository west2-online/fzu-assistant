import base64

def simple_encrypt(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def simple_decrypt(code):
    return base64.b64decode(code).decode('utf-8')

def encrypt_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        encoded = simple_encrypt(f.read())
    with open(output_path, 'w') as f:
        f.write(encoded)

def decrypt_file(input_path, output_path):
    with open(input_path, 'r') as f:
        decoded = simple_decrypt(f.read())
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decoded)

if __name__ == "__main__":
    encrypt_file("./filter/s.txt", "./filter/sensitive_terms.txt")