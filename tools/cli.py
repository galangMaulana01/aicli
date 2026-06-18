import os
import re

class CLI:
    def __init__(self):
        self.tools = {
            'READ': self.read_file,
            'EDIT': self.edit_file,
            'SCAN': self.scan_directory
        }

    def read_file(self, path):
        try:
            with open(path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"File {path} tidak ditemukan."

    def edit_file(self, path, content):
        try:
            with open(path, 'w') as file:
                file.write(content)
            return f"File {path} telah diedit."
        except Exception as e:
            return f"Error: {str(e)}"

    def scan_directory(self, path):
        try:
            return os.listdir(path)
        except FileNotFoundError:
            return f"Directory {path} tidak ditemukan."

def main():
    cli = CLI()
    while True:
        command = input("Masukkan perintah: ")
        if command in cli.tools:
            if command == 'READ':
                path = input("Masukkan path file: ")
                print(cli.tools[command](path))
            elif command == 'EDIT':
                path = input("Masukkan path file: ")
                content = input("Masukkan isi file: ")
                print(cli.tools[command](path, content))
            elif command == 'SCAN':
                path = input("Masukkan path directory: ")
                print(cli.tools[command](path))
        else:
            print("Perintah tidak ditemukan.")

if __name__ == "__main__":
    main()