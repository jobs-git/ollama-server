# MIT License

# Copyright (c) 2025 James Guana

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import subprocess
import sysconfig
import os
import urllib.parse
import ipaddress
import requests
import tarfile
import time

# from ollama-python
def _parse_host (host=None):
    port = 11434
    host = host or ''
    scheme, _, hostport = host.partition('://')

    if not hostport:
        scheme, hostport = 'http', host
    elif scheme == 'http':
        port = 80
    elif scheme == 'https':
        port = 443

    split = urllib.parse.urlsplit('://'.join([scheme, hostport]))
    host = split.hostname or '127.0.0.1'
    port = split.port or port

    try:
        if isinstance(ipaddress.ip_address(host), ipaddress.IPv6Address):
            host = f'[{host}]'
    except ValueError:
        pass

    if path := split.path.strip('/'):
        return f'{scheme}://{host}:{port}/{path}'

    return f'{scheme}://{host}:{port}'

def _check_server (url):

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass

    print(f"No server detected at {url}")
    return False

def start():

    bin_dir = sysconfig.get_paths()["scripts"]
    ollama_binary = os.path.join(bin_dir, "ollama")

    if not (os.path.isfile(ollama_binary) and os.access(ollama_binary, os.X_OK)):
        print("Ollama binary not found in the Python environment. Downloading and installing...")
        _download_and_install_ollama()

    url = _parse_host()

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        if _check_server(url):
            print (f"Server running and accessible")
            return True
        else:
            print (f"Attempt {attempt}: Starting the server...")
            subprocess.Popen("ollama serve", shell = True) #.wait ()
            time.sleep(1)

    print("Exceeded maximum retries. The server could not be started.")

    return False

def stop():

    # there is no official way of stopping ollama server outside systemd
    # see: https://github.com/ollama/ollama/issues/9169

    return False

def _download_and_install_ollama():
    url = "https://ollama.com/download/ollama-linux-amd64.tgz"
    download_path = "/tmp/ollama-linux-amd64.tgz"

    urllib.request.urlretrieve(url, download_path)
    print(f"Downloaded file to {download_path}")

    bin_dir = sysconfig.get_paths()["scripts"]
    parent_dir = os.getenv("OLLAMA_INSTALL_DIR") or os.path.dirname(bin_dir)

    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(path=parent_dir)

    print(f"Extracted and unpacked files to {parent_dir}")
    print("Installation complete.")

    os.remove(download_path)
    print(f"Temporary file {download_path} deleted.")