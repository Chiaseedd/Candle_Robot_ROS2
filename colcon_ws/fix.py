import sys

def fix_crlf(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n')
    with open(file_path, 'wb') as f:
        f.write(content)

if __name__ == '__main__':
    fix_crlf(sys.argv[1])
