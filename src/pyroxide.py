from threading import Thread
import requests
import math
import socket
import logging
from struct import pack


class Pyroxide:
    def __init__(self, timeout=3, logger=None):
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        self.good_list = []

    @staticmethod
    def is_socks4(host, port, soc):
        ipaddr = socket.inet_aton(host)
        packet4 = f"\x04\x01{pack('>H', port)}{ipaddr}\x00"
        soc.sendall(packet4.encode("utf-8"))
        data = soc.recv(8)
        if len(data) < 2:
            # Null response
            return False
        if data[0] != "\x00":
            # Bad data
            return False
        if data[1] != "\x5A":
            # Server Error
            return False
        return True

    @staticmethod
    def is_socks5(soc):
        soc.sendall(b"\x05\x01\x00")
        data = soc.recv(2)
        if len(data) < 2:
            # Null response
            return False
        if data[0] != "\x05":
            # Not SOCKS5
            return False
        if data[1] != "\x00":
            # Requires Auth
            return False
        return True

    def test_socks(self, proxy_list, thread_number):
        working_list = []
        for item in proxy_list:
            ip = item.split(":")[0]
            port = int(item.split(":")[1])
            try:
                if port < 0 or port > 65536:
                    self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                    self.logger.info(f"[Thread: {thread_number}] Invalid Port: {port}")
                    return 0
            except Exception as e:
                self.logger.info(f"[Thread: {thread_number}] Proxy Failed: {ip}")
                self.logger.info(f"[Thread: {thread_number}] Proxy Failed: {e}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            try:
                s.connect((ip, port))
                if self.is_socks4(ip, port, s):
                    s.close()
                    self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                    self.logger.info(f"[Thread: {thread_number}] Proxy Works: True")
                    working_list.append(item)
                elif self.is_socks5(s):
                    s.close()
                    self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                    self.logger.info(f"[Thread: {thread_number}] Proxy Works: True")
                    working_list.append(item)
                else:
                    s.close()
                    self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                    self.logger.info(f"[Thread: {thread_number}] Proxy Works: False")
            except socket.timeout:
                s.close()
                self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                self.logger.info(f"[Thread: {thread_number}] Connection Refused")
            except socket.error as e:
                s.close()
                self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                self.logger.info(f"[Thread: {thread_number}] Error: {e}")
        self.good_list.extend(working_list)

    def verify_proxy(self, proxy_list, thread_number):
        working_list = []
        for item in proxy_list:
            try:
                proxy_dict = {"http": item, "https": item}
                r = requests.get(
                    "http://ipinfo.io/json", proxies=proxy_dict, timeout=self.timeout
                )
                response = r.json()
                ip = response["ip"]
                self.logger.info(f"[Thread: {thread_number}] Current IP: {ip}")
                self.logger.info(f"[Thread: {thread_number}] Proxy Active: {item}")
                self.logger.info(
                    f'[Thread: {thread_number}] Proxy Works: {"True" if ip == item.split(":")[0] else "False"}'
                )
                working_list.append(item)
            except Exception as e:
                self.logger.info(f"[Thread: {thread_number}] Proxy Failed: {item}")
                self.logger.info(f"[Thread: {thread_number}] Proxy Failed: {e}")

        self.logger.info(
            f"[Thread: {thread_number}] Working Proxies: {len(working_list)}"
        )
        self.good_list.extend(working_list)

    @staticmethod
    def get_proxies(file):
        proxy_list = []
        with open(file, "r+") as f:
            for item in f.readlines():
                proxy_list.append(item.strip())
        return proxy_list

    def setup(self, number_threads, proxy_file):
        thread_count = float(number_threads)
        proxy_list = self.get_proxies(proxy_file)
        amount = int(math.ceil(len(proxy_list) / thread_count))
        proxy_lists = [
            proxy_list[x : x + amount] for x in range(0, len(proxy_list), amount)
        ]
        if len(proxy_list) % thread_count > 0.0:
            proxy_lists[len(proxy_lists) - 1].append(proxy_list[len(proxy_list) - 1])
        return proxy_lists

    def main(self, threads, proxy_file, target):
        lists = self.setup(threads, proxy_file)
        thread_list = []
        count = 0
        for item in lists:
            thread_list.append(Thread(target=target, args=(item, count)))
            thread_list[len(thread_list) - 1].start()
            count += 1

        for x in thread_list:
            x.join()

        self.logger.info(f"Working Proxies: {len(self.good_list)}")
        return self.good_list

    def check_proxy(self, proxy_file, threads):
        self.main(threads, proxy_file, self.verify_proxy)

    def check_socks(self, proxy_file, threads):
        self.main(threads, proxy_file, self.test_socks)
