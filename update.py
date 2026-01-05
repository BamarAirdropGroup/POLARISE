import json
import requests
import time
import uuid
import secrets
import os
import random
import re
from datetime import datetime
import pytz
import asyncio
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from aiohttp import ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector, ProxyType
from fake_useragent import FakeUserAgent
from colorama import Fore, Style, init
init(autoreset=True)
wib = pytz.timezone('Asia/Singapore')


def load_referral_code(default="rUcOC9"):
    try:
        with open('ref.txt', 'r', encoding='utf-8') as f:
            code = f.read().strip()
            if code:
                return code
    except FileNotFoundError:
        print(f"{Fore.YELLOW}ref.txt not found, using default referral code.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Error reading ref.txt: {e}, using default.{Style.RESET_ALL}")
    return default

REF_CODE = load_referral_code()


def generate_random_email():
    """Generate random email for mailsac.com domain"""
    username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
    return f"{username}@mailsac.com"


def load_topics_from_json():
    """Load topics from topic.json file"""
    try:
        with open('topic.json', 'r', encoding='utf-8') as f:
            topics_data = json.load(f)
        return topics_data
    except FileNotFoundError:
        raise FileNotFoundError(f"{Fore.RED}topic.json not found. Please create topic.json file.{Style.RESET_ALL}")
    except Exception as e:
        raise Exception(f"{Fore.RED}Error loading topic.json: {e}{Style.RESET_ALL}")


def load_topic_contents_from_json():
    """Load topic contents from topic_contents.json file"""
    try:
        with open('topic_contents.json', 'r', encoding='utf-8') as f:
            contents_data = json.load(f)
        return contents_data
    except FileNotFoundError:
        raise FileNotFoundError(f"{Fore.RED}topic_contents.json not found. Please create topic_contents.json file.{Style.RESET_ALL}")
    except Exception as e:
        raise Exception(f"{Fore.RED}Error loading topic_contents.json: {e}{Style.RESET_ALL}")


def load_comments_from_json():
    """Load comments from comment.json file"""
    try:
        with open('comment.json', 'r', encoding='utf-8') as f:
            comments_data = json.load(f)
        
        
        if isinstance(comments_data, dict) and "comments" in comments_data:
            return comments_data.get("comments", [])
        elif isinstance(comments_data, list):
            return comments_data
        else:
            raise ValueError(f"{Fore.RED}comment.json format not recognized. It should be an array or object with 'comments' key.{Style.RESET_ALL}")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"{Fore.RED}comment.json not found. Please create comment.json file.{Style.RESET_ALL}")
    except Exception as e:
        raise Exception(f"{Fore.RED}Error loading comment.json: {e}{Style.RESET_ALL}")


class Polarise:
    def __init__(self) -> None:
        self.BASE_API = "https://apia.polarise.org/api/app/v1"
        self.RPC_URL = "https://chainrpc.polarise.org/"
        self.EXPLORER = "https://explorer.polarise.org/tx/"
        self.REF_CODE = REF_CODE  
        self.CONFIG = {
            "transfer": {
                "amount": 0.001,
                "gas_fee": 0.0021,
                "recepient": "0x9c4324156bA59a70FFbc67b98eE2EF45AEE4e19F"
            },
            "donate": {
                "amount": 1,
                "recepient": "0x115E97549E02eB1134F32E92208da1D7c6306Eca",
                "token_address": "0x351EF49f811776a3eE26f3A1fBc202915B8f2945",
                "contract_address": "0x639A8A05DAD556256046709317c76927b053a85D",
            },
            "discussion": {
                "contract_address": "0x58477a0e15ae82E9839f209b13EFF25eC06c252B",
            },
            "faucet": {
                "task_id": 1
            }
        }
        self.CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "address", "name": "account", "type": "address" }
                ],
                "name": "balanceOf",
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    { "internalType": "address", "name": "owner", "type": "address" },
                    { "internalType": "address", "name": "spender", "type": "address" }
                ],
                "name": "allowance",
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    { "internalType": "address", "name": "spender", "type": "address" },
                    { "internalType": "uint256", "name": "value", "type": "uint256" }
                ],
                "name": "approve",
                "outputs": [
                    { "internalType": "bool", "name": "", "type": "bool" }
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    { "name": "receiver", "type": "address", "internalType": "address"},
                    { "name": "amount", "type": "uint256", "internalType": "uint256"}
                ],
                "name": "donate",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "type": "function",
                "name": "createDiscussionEvent",
                "inputs": [
                    { "name": "questionId", "type": "bytes32", "internalType": "bytes32" },
                    { "name": "nftMint", "type": "bool", "internalType": "bool" },
                    { "name": "communityRecipient", "type": "address", "internalType": "address" },
                    { "name": "collateralToken", "type": "address", "internalType": "address" },
                    { "name": "endTime", "type": "uint64", "internalType": "uint64" },
                    { "name": "outcomeSlots", "type": "bytes32[]", "internalType": "bytes32[]" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            }
        ]
        self.HEADERS = {}
        self.api_key = None
        self.all_topics = []
        self.comment_list = []
        self.topic_contents = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.auth_tokens = {}
        self.nonce = {}
        self.sub_id = {}
        self.faucet_tx_hashes = {}  
    
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def log(self, message):
        timestamp = datetime.now().astimezone(wib).strftime('%x %X %Z')
        print(
            f"{Fore.CYAN}[ {timestamp} ]{Style.RESET_ALL}"
            f"{Fore.WHITE} | {Style.RESET_ALL}{message}",
            flush=True
        )
    
    def welcome(self):
        print(f"""
{Fore.GREEN}Polarise{Fore.BLUE} Daily Auto BOT
{Fore.YELLOW}
        """)
    
    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
   
    def print_question(self):
        """Print proxy selection question"""
        while True:
            try:
                print(f"{Fore.WHITE}1. Run With Proxy")
                print(f"{Fore.WHITE}2. Run Without Proxy")
                proxy_choice = int(input(f"{Fore.BLUE}Choose [1/2] -> ").strip())
                if proxy_choice in [1, 2]:
                    proxy_type = "With" if proxy_choice == 1 else "Without"
                    print(f"{Fore.GREEN}Run {proxy_type} Proxy Selected.")
                    break
                else:
                    print(f"{Fore.RED}Please enter either 1 or 2.")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Enter a number (1 or 2).")
        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE}Rotate Invalid Proxy? [y/n] -> ").strip().lower()
                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED}Invalid input. Enter 'y' or 'n'.")
        return proxy_choice, rotate_proxy
    
    def load_all_topics(self):
        try:
            
            topics_data = load_topics_from_json()
            all_topics = []
            for category, topics in topics_data.items():
                if isinstance(topics, list):
                    all_topics.extend(topics)
            return all_topics
        except Exception as e:
            self.log(f"{Fore.RED}Failed to load topics: {str(e)}{Style.RESET_ALL}")
            raise e
       
    def load_accounts(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return []
    
    def load_accounts_with_email(self):
        """Load accounts from mail.txt in format email:privatekey"""
        try:
            accounts = []
            with open('mail.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        if ':' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                email, private_key = parts[0].strip(), parts[1].strip()
                                accounts.append((email, private_key))
            return accounts
        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'mail.txt' Not Found.{Style.RESET_ALL}")
            return []
       
    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
           
            if not self.proxies:
                self.log(f"{Fore.RED}No Proxies Found.{Style.RESET_ALL}")
                return
            self.log(f"{Fore.GREEN}Proxies Total: {len(self.proxies)}{Style.RESET_ALL}")
       
        except Exception as e:
            self.log(f"{Fore.RED}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []
    
    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"
    
    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]
    
    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
   
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None
        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None
        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None
        raise Exception("Unsupported Proxy Type.")
   
    def generate_address(self, account: str):
        try:
            account_obj = Account.from_key(account)
            address = account_obj.address
            return address
        except Exception as e:
            self.log(f"{Fore.RED}Failed to generate address: {e}{Style.RESET_ALL}")
            return None
       
    def mask_account(self, account):
        try:
            if len(account) > 12:
                return account[:6] + '*' * 6 + account[-6:]
            return account
        except Exception as e:
            return "Unknown"
       
    def generate_signature(self, account: str, address: str):
        try:
            from eth_account.messages import encode_defunct
            from eth_utils import to_hex
           
            message = f"Nonce to confirm: {self.nonce[address]}"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)
            return message, signature
        except Exception as e:
            raise Exception(f"Generate Signature Failed: {str(e)}")
        
    def generate_login_payload(self, account: str, address: str):
        try:
            message, signature = self.generate_signature(account, address)
            payload = {
                "signature": signature,
                "chain_name": "polarise",
                "name": address[:6],
                "nonce": self.nonce[address],
                "wallet": address,
                "sid": self.access_tokens[address],
                "sub_id": self.sub_id[address],
                "inviter_code": self.REF_CODE  
            }
            return payload
        except Exception as e:
            raise Exception(f"Generate Login Payload Failed: {str(e)}")

    def generate_swap_payload(self, account: str, address: str, user_id: int, username: str, used_points: int):
        try:
            message, signature = self.generate_signature(account, address)
            payload = {
                "user_id": user_id,
                "user_name": username,
                "user_wallet": address,
                "used_points": used_points,
                "token_symbol": "GRISE",
                "chain_name": "polarise",
                "signature": signature,
                "sign_msg": message
            }
            return payload
        except Exception as e:
            raise Exception(f"Generate Swap Points Payload Failed: {str(e)}")
       
    def generate_save_post_payload(self, user_id: str, content: dict):
        try:
            payload = {
                "user_id": user_id,
                "chain_name": "polarise",
                "community_id": 0,
                "community_name": "",
                "title": content["title"],
                "tags": [],
                "description": content["description"],
                "published_time": int(time.time()) * 1000,
                "media_links": "[]",
                "is_subscribe_enable": False
            }
            return payload
        except Exception as e:
            raise Exception(f"Generate Save Post Payload Failed: {str(e)}")
       
    def generate_discuss_options(self):
        options = [
            {"index":0,"title":"Agree","price":0,"total_buy_share":0,"total_sell_share":0,"total_held_share":0},
            {"index":1,"title":"Not Agree","price":0,"total_buy_share":0,"total_sell_share":0,"total_held_share":0}
        ]
        return options
   
    def build_outcome_slots(self, options: list):
        from eth_utils import keccak, to_bytes
        outcome_slots = []
        for opt in options:
            if not isinstance(opt, dict):
                raise ValueError("each option must be dict")
            title = opt.get("title")
            if not title or not isinstance(title, str):
                raise ValueError("option.title must be string")
            hashed = keccak(to_bytes(text=title))
            outcome_slots.append("0x" + hashed.hex())
        return outcome_slots
    
    def generate_save_discussion_payload(self, user_id: str, discuss_data: dict):
        try:
            payload = {
                "user_id": user_id,
                "community_id": 0,
                "community_name": "",
                "title": discuss_data['title'],
                "options": json.dumps(discuss_data['options']),
                "tags": [],
                "description": discuss_data["description"],
                "published_time": discuss_data['published_time'],
                "tx_hash": discuss_data['tx_hash'],
                "chain_name": "polarise",
                "media_links": "[]",
                "question_id": discuss_data['question_id'],
                "end_time": discuss_data['end_time']
            }
            return payload
        except Exception as e:
            raise Exception(f"Generate Save Discussion Payload Failed: {str(e)}")
    
    def generate_faucet_task_extra_info(self, address: str, tx_hash: str):
        """Generate extra info for faucet task completion"""
        extra_dict = {
            "tx_hash": tx_hash,
            "from": address,
            "to": address,  
            "value": "1000000"  
        }
        return json.dumps(extra_dict)
    
    async def bind_email_task(self, address: str, email: str, use_proxy: bool):
        """Complete email binding task (task_id: 3)"""
        try:
            extra_info = json.dumps({"email": email})
            complete = await self.complete_task(address, 3, "Bind Email", use_proxy, extra_info)
            
            if complete:
                if complete.get("code") == "200":
                    if complete.get("data", {}).get("finish_status") == 1:
                        self.log(f"{Fore.GREEN}✓ Email bound successfully: {email}{Style.RESET_ALL}")
                        return True
                    else:
                        self.log(f"{Fore.YELLOW}⚠ Email already bound{Style.RESET_ALL}")
                        return True
                else:
                    err_msg = complete.get("msg", "Unknown Error")
                    self.log(f"{Fore.RED}✗ Bind email failed: {err_msg}{Style.RESET_ALL}")
            return False
        except Exception as e:
            self.log(f"{Fore.RED}✗ Bind email error: {str(e)}{Style.RESET_ALL}")
            return False
    
    async def complete_faucet_task(self, address: str, tx_hash: str, use_proxy: bool):
        """Complete faucet task after claiming"""
        try:
            extra_info = self.generate_faucet_task_extra_info(address, tx_hash)
            complete = await self.complete_task(address, 1, "Faucet Claim", use_proxy, extra_info)
            
            if complete:
                if complete.get("code") == "200":
                    if complete.get("data", {}).get("finish_status") == 1:
                        self.log(f"{Fore.GREEN}✓ Faucet task completed successfully{Style.RESET_ALL}")
                        return True
                    else:
                        self.log(f"{Fore.YELLOW}⚠ Faucet task already completed{Style.RESET_ALL}")
                        return True
                else:
                    err_msg = complete.get("msg", "Unknown Error")
                    self.log(f"{Fore.RED}✗ Faucet task completion failed: {err_msg}{Style.RESET_ALL}")
            return False
        except Exception as e:
            self.log(f"{Fore.RED}✗ Faucet task completion error: {str(e)}{Style.RESET_ALL}")
            return False
    
    async def complete_task(self, address: str, task_id: int, title: str, use_proxy: bool, extra=None, retries=5):
        url = f"{self.BASE_API}/points/completetask"
        payload = {
            "user_wallet": address,
            "task_id": task_id,
            "chain_name": "polarise"
        }
       
        if extra is not None:
            payload["extra_info"] = extra
        
        data = json.dumps(payload)
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Complete task '{title}' failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}
        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
       
    async def get_token_balance(self, address: str, use_proxy: bool, token_address=None):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if token_address is None:
                balance = web3.eth.get_balance(address)
            else:
                asset_address = web3.to_checksum_address(token_address)
                token_contract = web3.eth.contract(address=asset_address, abi=self.CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()
            token_balance = web3.from_wei(balance, "ether")
            return token_balance
        except Exception as e:
            self.log(f"{Fore.RED}Balance check failed: {str(e)}{Style.RESET_ALL}")
            return None
    
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        from web3.exceptions import TransactionNotFound
       
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(f"{Fore.YELLOW}[Attempt {attempt + 1}] Send TX Error: {str(e)}{Style.RESET_ALL}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")
    
    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        from web3.exceptions import TransactionNotFound
       
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(f"{Fore.YELLOW}[Attempt {attempt + 1}] Wait for Receipt Error: {str(e)}{Style.RESET_ALL}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
    
    async def perform_transfer(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            amount_to_wei = web3.to_wei(self.CONFIG['transfer']['amount'], "ether")
            max_priority_fee = web3.to_wei(100, "gwei")
            max_fee = max_priority_fee
            transfer_tx = {
                "from": web3.to_checksum_address(address),
                "to": web3.to_checksum_address(self.CONFIG['transfer']['recepient']),
                "value": amount_to_wei,
                "gas": 21000,
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            }
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, transfer_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            return amount_to_wei, tx_hash, block_number
        except Exception as e:
            self.log(f"{Fore.RED}Transfer failed: {str(e)}{Style.RESET_ALL}")
            return None, None, None
    
    async def approving_token(self, account: str, address: str, spender: str, asset_address: str, amount: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
           
            token_contract = web3.eth.contract(address=asset_address, abi=self.CONTRACT_ABI)
            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})
                max_priority_fee = web3.to_wei(100, "gwei")
                max_fee = max_priority_fee
                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })
                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
                block_number = receipt.blockNumber
                self.log(f"{Fore.GREEN}✓ Approval successful{Style.RESET_ALL}")
                self.log(f"{Fore.CYAN}Block: {block_number}{Style.RESET_ALL}")
                self.log(f"{Fore.CYAN}Tx: {self.EXPLORER}{tx_hash}{Style.RESET_ALL}")
                await asyncio.sleep(3)
            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
    
    async def perform_donate(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            amount_to_wei = web3.to_wei(self.CONFIG['donate']['amount'], "ether")
            receiver_address = web3.to_checksum_address(self.CONFIG['donate']['recepient'])
            token_address = web3.to_checksum_address(self.CONFIG['donate']['token_address'])
            contract_address = web3.to_checksum_address(self.CONFIG['donate']['contract_address'])
            await self.approving_token(account, address, contract_address, token_address, amount_to_wei, use_proxy)
            token_contract = web3.eth.contract(address=contract_address, abi=self.CONTRACT_ABI)
            donate_data = token_contract.functions.donate(receiver_address, amount_to_wei)
            estimated_gas = donate_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(100, "gwei")
            max_fee = max_priority_fee
            donate_tx = donate_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, donate_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            return tx_hash, block_number
        except Exception as e:
            self.log(f"{Fore.RED}Donate failed: {str(e)}{Style.RESET_ALL}")
            return None, None
    
    async def perform_create_discuss(self, account: str, address: str, discuss_data: dict, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            community_recipient = "0x0000000000000000000000000000000000000000"
            collateral_token = web3.to_checksum_address(self.CONFIG['donate']['token_address'])
            contract_address = web3.to_checksum_address(self.CONFIG['discussion']['contract_address'])
            question_id = "0x" + discuss_data['question_id']
            end_time = discuss_data['end_time']
            outcome_slots = self.build_outcome_slots(discuss_data['options'])
            token_contract = web3.eth.contract(address=contract_address, abi=self.CONTRACT_ABI)
            discuss_data_func = token_contract.functions.createDiscussionEvent(
                question_id, False, community_recipient, collateral_token, end_time, outcome_slots
            )
            estimated_gas = discuss_data_func.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(100, "gwei")
            max_fee = max_priority_fee
            discuss_tx = discuss_data_func.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, discuss_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            return tx_hash, block_number
        except Exception as e:
            self.log(f"{Fore.RED}Create discussion failed: {str(e)}{Style.RESET_ALL}")
            return None, None
    
    async def generate_extra_info(self, account: str, address: str, use_proxy: bool):
        amount, tx_hash, block_number = await self.perform_transfer(account, address, use_proxy)
        if amount and tx_hash and block_number:
            self.log(f"{Fore.GREEN}✓ Transfer successful{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN}Block: {block_number}{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN}Tx: {self.EXPLORER}{tx_hash}{Style.RESET_ALL}")
           
            extra_dict = {
                "tx_hash": tx_hash,
                "from": address,
                "to": self.CONFIG['transfer']["recepient"],
                "value": str(amount)
            }
            extra = json.dumps(extra_dict)
           
            await asyncio.sleep(3)
            return extra
        else:
            self.log(f"{Fore.RED}✗ Transfer failed{Style.RESET_ALL}")
            return False
    
    async def process_perfrom_donate(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_donate(account, address, use_proxy)
        if tx_hash and block_number:
            self.log(f"{Fore.GREEN}✓ Donate successful{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN}Block: {block_number}{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN}Tx: {self.EXPLORER}{tx_hash}{Style.RESET_ALL}")
            await asyncio.sleep(3)
            return True
        else:
            self.log(f"{Fore.RED}✗ Donate failed{Style.RESET_ALL}")
            return False
    
    async def process_perfrom_create_discuss(self, account: str, address: str, discuss_data: dict, use_proxy: bool):
        tx_hash, block_number = await self.perform_create_discuss(account, address, discuss_data, use_proxy)
        if tx_hash and block_number:
            self.log(f"{Fore.GREEN}✓ Discussion created{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN}Block: {block_number}{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN}Tx: {self.EXPLORER}{tx_hash}{Style.RESET_ALL}")
            await asyncio.sleep(3)
            return tx_hash
        else:
            self.log(f"{Fore.RED}✗ Discussion creation failed{Style.RESET_ALL}")
            return False
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            self.log(f"{Fore.RED}✗ Connection failed: {str(e)}{Style.RESET_ALL}")
            return None
    
    async def get_nonce(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/profile/getnonce"
        data = json.dumps({"wallet": address, "chain_name": "polarise"})
        headers = {
            **self.HEADERS[address],
            "Authorization": "Bearer",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Get nonce failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def gen_biz_id(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/discussion/generatebizid"
        data = json.dumps({
            "biz_input": address,
            "biz_type": "subscription_question",
            "chain_name": "polarise"
        })
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": "Bearer",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Generate biz id failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def wallet_login(self, account: str, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/profile/login"
        data = json.dumps(self.generate_login_payload(account, address))
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": "Bearer",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Login failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def profile_info(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/profile/profileinfo"
        data = json.dumps({"chain_name": "polarise"})
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Fetch profile failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def swap_points(self, account: str, address: str, user_id: int, username: str, used_points: int, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/profile/swappoints"
        data = json.dumps(self.generate_swap_payload(account, address, user_id, username, used_points))
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Swap points failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def task_list(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/points/tasklist"
        data = json.dumps({"user_wallet": address, "chain_name": "polarise"})
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Fetch task list failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def generate_content(self, topic: str):
        """Generate content from topic_contents.json file"""
        try:
            
            if not self.topic_contents:
                self.topic_contents = load_topic_contents_from_json()
            
            
            if topic in self.topic_contents:
                return self.topic_contents[topic]
            else:
                
                self.log(f"{Fore.YELLOW}⚠ Content for topic '{topic}' not found in topic_contents.json{Style.RESET_ALL}")
                title = f"Discussion: {topic}"
                description = f"""Let's talk about {topic}!
This is an important topic for anyone interested in NFT liquidity and DeFi. Polarise Protocol is at the forefront of solving the NFT liquidity crisis.
What are your thoughts on this? Do you agree or disagree with the current approaches?
Share your insights below! 🚀
#NFT #DeFi #Liquidity #PolariseProtocol"""
               
                return {
                    "title": title,
                    "description": description,
                    "topic": topic
                }
           
        except Exception as e:
            self.log(f"{Fore.RED}✗ Create content failed: {str(e)}{Style.RESET_ALL}")
            return None
    
    async def gen_question_id(self, address: str, biz_input: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/discussion/generatebizid"
        data = json.dumps({
            "biz_input": biz_input,
            "biz_type": "discussion_question",
            "chain_name": "polarise"
        })
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": "Bearer",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Generate question id failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def save_discussion(self, address: str, user_id: int, discuss_data: dict, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/discussion/savediscussion"
        data = json.dumps(self.generate_save_discussion_payload(user_id, discuss_data))
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Save discussion failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def save_post(self, address: str, user_id: int, content: dict, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/posts/savepost"
        data = json.dumps(self.generate_save_post_payload(user_id, content))
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Save post failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def home_list(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/aggregation/homelist"
        data = json.dumps({"user_id": 0, "cursor": 0, "limit": 20, "chain_name": "polarise"})
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Fetch home list failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def save_comment(self, address: str, user_id: int, post_id: int, content: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/posts/savecomment"
        data = json.dumps({
            "user_id": user_id,
            "post_id": post_id,
            "content": content,
            "tags" : [],
            "published_time": int(time.time()) * 1000,
            "chain_name": "polarise"
        })
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Save comment failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def save_suborder(self, address: str, sub_address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/subscription/savesuborder"
        data = json.dumps({
            "subed_addr": sub_address,
            "sub_id": self.sub_id[address],
            "order_time": int(time.time()),
            "chain_name": "polarise"
        })
        headers = {
            **self.HEADERS[address],
            "Accesstoken": self.access_tokens[address],
            "Authorization": f"Bearer {self.auth_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"{Fore.RED}✗ Save suborder failed: {str(e)}{Style.RESET_ALL}")
                return None
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(f"{Fore.CYAN}Using proxy: {proxy}{Style.RESET_ALL}")
            is_valid = await self.check_connection(proxy)
            if is_valid:
                self.log(f"{Fore.GREEN}✓ Connection successful{Style.RESET_ALL}")
                return True
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
                self.log(f"{Fore.YELLOW}Rotating proxy to: {proxy}{Style.RESET_ALL}")
                await asyncio.sleep(1)
                continue
            self.log(f"{Fore.RED}✗ Connection failed and rotation disabled{Style.RESET_ALL}")
            return False
    
    async def process_wallet_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
           
            get_nonce = await self.get_nonce(address, use_proxy)
            if not get_nonce:
                return False
            if get_nonce.get("code") != "200":
                err_msg = get_nonce.get("msg", "Unknown Error")
                self.log(f"{Fore.RED}✗ Get nonce failed: {err_msg}{Style.RESET_ALL}")
                return False
           
            self.nonce[address] = get_nonce.get("signed_nonce")
            self.log(f"{Fore.GREEN}✓ Got nonce{Style.RESET_ALL}")
           
            biz_id = await self.gen_biz_id(address, use_proxy)
            if not biz_id:
                return False
            if biz_id.get("code") != "200":
                err_msg = biz_id.get("msg", "Unknown Error")
                self.log(f"{Fore.RED}✗ Generate biz id failed: {err_msg}{Style.RESET_ALL}")
                return False
           
            self.sub_id[address] = biz_id.get("data", {}).get("Biz_Id")
            self.log(f"{Fore.GREEN}✓ Generated biz id{Style.RESET_ALL}")
            login = await self.wallet_login(account, address, use_proxy)
            if not login:
                return False
            if login.get("code") != "200":
                err_msg = login.get("msg", "Unknown Error")
                self.log(f"{Fore.RED}✗ Login failed: {err_msg}{Style.RESET_ALL}")
                return False
            auth_token = login.get("data", {}).get("auth_token_info", {}).get("auth_token")
            self.auth_tokens[address] = f"{auth_token} {self.access_tokens[address]} {address} polarise"
            self.log(f"{Fore.GREEN}✓ Login successful{Style.RESET_ALL}")
            return True
        return False

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        """Original process_accounts method for daily tasks"""
        self.log(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        self.log(f"{Fore.CYAN}Processing: {self.mask_account(address)}{Style.RESET_ALL}")
       
        logined = await self.process_wallet_login(account, address, use_proxy, rotate_proxy)
        if logined:
           
            profile = await self.profile_info(address, use_proxy)
            if profile:
                if profile.get("code") == "200":
                    user_id = profile.get("data", {}).get("id")
                    username = profile.get("data", {}).get("user_name")
                    exchange_points = profile.get("data", {}).get("exchange_total_points")
                    cumulative_revenue = profile.get("data", {}).get("cumulative_revenue")
                    self.log(f"{Fore.CYAN}Points: {exchange_points}{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN}Balance: {cumulative_revenue} GRISE{Style.RESET_ALL}")
                    if exchange_points >= 100:
                        used_points = (exchange_points // 100) * 100
                        swap = await self.swap_points(account, address, user_id, username, used_points, use_proxy)
                        if swap:
                            if swap.get("code") == "200":
                                self.log(f"{Fore.CYAN}Swapping points...{Style.RESET_ALL}")
                                received_amount = swap.get("data", {}).get("received_amount")
                                tx_hash = swap.get("data", {}).get("tx_hash")
                               
                                self.log(f"{Fore.GREEN}✓ Swap successful{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Received: {received_amount} GRISE{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Tx: {self.EXPLORER}{tx_hash}{Style.RESET_ALL}")
                            else:
                                err_msg = swap.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Swap failed: {err_msg}{Style.RESET_ALL}")
                    else:
                        self.log(f"{Fore.YELLOW}⚠ Insufficient points for swap (need 100){Style.RESET_ALL}")
                else:
                    err_msg = profile.get("msg", "Unknown Error")
                    self.log(f"{Fore.RED}✗ Fetch profile failed: {err_msg}{Style.RESET_ALL}")
            task_list = await self.task_list(address, use_proxy)
            if task_list:
                if task_list.get("code") == "200":
                    self.log(f"{Fore.CYAN}Fetching tasks...{Style.RESET_ALL}")
                    tasks = task_list.get("data", {}).get("list")
                    for task in tasks:
                        task_id = task.get("id")
                        title = task.get("name")
                        reward = task.get("points")
                        state = task.get("state")
                        if state == 1:
                            self.log(f"{Fore.YELLOW}✓ {title}: Already completed{Style.RESET_ALL}")
                            continue
                        if task_id == 3:
                            self.log(f"{Fore.YELLOW}⏭ {title}: Skipped{Style.RESET_ALL}")
                            continue
                        elif task_id in [1, 2]:
                            self.log(f"{Fore.CYAN}▶ {title}{Style.RESET_ALL}")
                            self.log(f"{Fore.CYAN}Amount: {self.CONFIG['transfer']['amount']} POLAR{Style.RESET_ALL}")
                            self.log(f"{Fore.CYAN}Gas Fee: {self.CONFIG['transfer']['gas_fee']} POLAR{Style.RESET_ALL}")
                            balance = await self.get_token_balance(address, use_proxy)
                            self.log(f"{Fore.CYAN}Balance: {balance} POLAR{Style.RESET_ALL}")
                            if balance is None:
                                self.log(f"{Fore.RED}✗ Failed to fetch POLAR balance{Style.RESET_ALL}")
                                continue
                            if balance < self.CONFIG['transfer']['amount'] + self.CONFIG['transfer']['gas_fee']:
                                self.log(f"{Fore.RED}✗ Insufficient POLAR balance{Style.RESET_ALL}")
                                continue
                            extra = await self.generate_extra_info(account, address, use_proxy)
                            if not extra:
                                continue
                            complete = await self.complete_task(address, task_id, title, use_proxy, extra)
                            if not complete:
                                continue
                            if complete.get("code") != "200":
                                err_msg = complete.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Task not completed: {err_msg}{Style.RESET_ALL}")
                                continue
                            if complete.get("data", {}).get("finish_status") == 1:
                                self.log(f"{Fore.GREEN}✓ Task completed{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Reward: {reward} points{Style.RESET_ALL}")
                            elif complete.get("data", {}).get("finish_status") == 0:
                                self.log(f"{Fore.RED}✗ Task not completed{Style.RESET_ALL}")
                            else:
                                self.log(f"{Fore.YELLOW}⚠ Task already completed{Style.RESET_ALL}")
                        elif task_id in [7, 8]:
                            self.log(f"{Fore.CYAN}▶ {title}{Style.RESET_ALL}")
                            topic = random.choice(self.all_topics)
                            if not topic:
                                self.log(f"{Fore.RED}✗ No topic found{Style.RESET_ALL}")
                                continue
                            self.log(f"{Fore.CYAN}Topic: {topic}{Style.RESET_ALL}")
                            content = await self.generate_content(topic)
                            if not content:
                                continue
                            title_text = content['title']
                            description = content['description']
                            self.log(f"{Fore.CYAN}Title: {title_text}{Style.RESET_ALL}")
                            if task_id == 7:
                                timestamp = int(time.time()) * 1000
                                biz_input = f"{title_text.lower()}{timestamp}-agree-not agree"
                                biz_id = await self.gen_question_id(address, biz_input, use_proxy)
                                if not biz_id:
                                    continue
                       
                                if biz_id.get("code") != "200":
                                    err_msg = biz_id.get("msg", "Unknown Error")
                                    self.log(f"{Fore.RED}✗ Generate question id failed: {err_msg}{Style.RESET_ALL}")
                                    continue
                                question_id = biz_id.get("data", {}).get("Biz_Id")
                                options = self.generate_discuss_options()
                                now_time = int(time.time())
                                published_time = now_time * 1000
                                end_time = now_time + 1209600
                                discuss_data = {
                                    "title": title_text,
                                    "description": description,
                                    "question_id": question_id,
                                    "options": options,
                                    "published_time": published_time,
                                    "end_time": end_time,
                                }
                                tx_hash = await self.process_perfrom_create_discuss(account, address, discuss_data, use_proxy)
                                if not tx_hash:
                                    continue
                                discuss_data["tx_hash"] = tx_hash
                                save_discuss = await self.save_discussion(address, user_id, discuss_data, use_proxy)
                                if not save_discuss:
                                    continue
                                if save_discuss.get("code") != "200":
                                    err_msg = save_discuss.get("msg", "Unknown Error")
                                    self.log(f"{Fore.RED}✗ Save discussion failed: {err_msg}{Style.RESET_ALL}")
                                    continue
                                self.log(f"{Fore.GREEN}✓ Discussion posted{Style.RESET_ALL}")
                            elif task_id == 8:
                                save_post = await self.save_post(address, user_id, content, use_proxy)
                                if not save_post:
                                    continue
                                if save_post.get("code") != "200":
                                    err_msg = save_post.get("msg", "Unknown Error")
                                    self.log(f"{Fore.RED}✗ Save post failed: {err_msg}{Style.RESET_ALL}")
                                    continue
                                self.log(f"{Fore.GREEN}✓ Post created{Style.RESET_ALL}")
                            complete = await self.complete_task(address, task_id, title, use_proxy)
                            if not complete:
                                continue
                            if complete.get("code") != "200":
                                err_msg = complete.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Task not completed: {err_msg}{Style.RESET_ALL}")
                                continue
                            if complete.get("data", {}).get("finish_status") == 1:
                                self.log(f"{Fore.GREEN}✓ Task completed{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Reward: {reward} points{Style.RESET_ALL}")
                            elif complete.get("data", {}).get("finish_status") == 0:
                                self.log(f"{Fore.RED}✗ Task not completed{Style.RESET_ALL}")
                            else:
                                self.log(f"{Fore.YELLOW}⚠ Task already completed{Style.RESET_ALL}")
                        elif task_id == 9:
                            self.log(f"{Fore.CYAN}▶ {title}{Style.RESET_ALL}")
                            self.log(f"{Fore.CYAN}Amount: {self.CONFIG['donate']['amount']} GRISE{Style.RESET_ALL}")
                            balance = await self.get_token_balance(address, use_proxy, self.CONFIG['donate']['token_address'])
                            self.log(f"{Fore.CYAN}Balance: {balance} GRISE{Style.RESET_ALL}")
                            if balance is None:
                                self.log(f"{Fore.RED}✗ Failed to fetch GRISE balance{Style.RESET_ALL}")
                                continue
                            if balance < self.CONFIG['donate']['amount']:
                                self.log(f"{Fore.RED}✗ Insufficient GRISE balance{Style.RESET_ALL}")
                                continue
                            donate = await self.process_perfrom_donate(account, address, use_proxy)
                            if not donate:
                                continue
                            complete = await self.complete_task(address, task_id, title, use_proxy)
                            if not complete:
                                continue
                            if complete.get("code") != "200":
                                err_msg = complete.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Task not completed: {err_msg}{Style.RESET_ALL}")
                                continue
                            if complete.get("data", {}).get("finish_status") == 1:
                                self.log(f"{Fore.GREEN}✓ Task completed{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Reward: {reward} points{Style.RESET_ALL}")
                            elif complete.get("data", {}).get("finish_status") == 0:
                                self.log(f"{Fore.RED}✗ Task not completed{Style.RESET_ALL}")
                            else:
                                self.log(f"{Fore.YELLOW}⚠ Task already completed{Style.RESET_ALL}")
                        elif task_id in [10, 11]:
                            self.log(f"{Fore.CYAN}▶ {title}{Style.RESET_ALL}")
                            home_list = await self.home_list(address, use_proxy)
                            if not home_list:
                                continue
                            if home_list.get("code") != "200":
                                err_msg = home_list.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Fetch post list failed: {err_msg}{Style.RESET_ALL}")
                                continue
                            post = home_list.get("data", {}).get("list", [])
                            square = random.choice(post)
                            post_id = square.get("id")
                            sub_address = square.get("user_wallet")
                            if task_id == 10:
                                
                                if not self.comment_list:
                                    self.comment_list = load_comments_from_json()
                                content = random.choice(self.comment_list)
                                self.log(f"{Fore.CYAN}Post ID: {post_id}{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Comment: {content}{Style.RESET_ALL}")
                                save_comment = await self.save_comment(address, user_id, post_id, content, use_proxy)
                                if not save_comment:
                                    continue
                                if save_comment.get("code") != "200":
                                    err_msg = save_comment.get("msg", "Unknown Error")
                                    self.log(f"{Fore.RED}✗ Save comment failed: {err_msg}{Style.RESET_ALL}")
                                    continue
                                self.log(f"{Fore.GREEN}✓ Comment posted{Style.RESET_ALL}")
                               
                            elif task_id == 11:
                                self.log(f"{Fore.CYAN}Subscribing to: {sub_address}{Style.RESET_ALL}")
                                save_suborder = await self.save_suborder(address, sub_address, use_proxy)
                                if not save_suborder:
                                    continue
                                if save_suborder.get("code") != "200":
                                    err_msg = save_suborder.get("msg", "Unknown Error")
                                    self.log(f"{Fore.RED}✗ Subscribe failed: {err_msg}{Style.RESET_ALL}")
                                    continue
                                self.log(f"{Fore.GREEN}✓ Subscribed{Style.RESET_ALL}")
                            complete = await self.complete_task(address, task_id, title, use_proxy)
                            if not complete:
                                continue
                            if complete.get("code") != "200":
                                err_msg = complete.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Task not completed: {err_msg}{Style.RESET_ALL}")
                                continue
                            if complete.get("data", {}).get("finish_status") == 1:
                                self.log(f"{Fore.GREEN}✓ Task completed{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Reward: {reward} points{Style.RESET_ALL}")
                            elif complete.get("data", {}).get("finish_status") == 0:
                                self.log(f"{Fore.RED}✗ Task not completed{Style.RESET_ALL}")
                            else:
                                self.log(f"{Fore.YELLOW}⚠ Task already completed{Style.RESET_ALL}")
                        else:
                            complete = await self.complete_task(address, task_id, title, use_proxy)
                            if not complete:
                                continue
                            if complete.get("code") != "200":
                                err_msg = complete.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Task '{title}' not completed: {err_msg}{Style.RESET_ALL}")
                                continue
                            if complete.get("data", {}).get("finish_status") == 1:
                                self.log(f"{Fore.GREEN}✓ {title}: Completed{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Reward: {reward} points{Style.RESET_ALL}")
                            elif complete.get("data", {}).get("finish_status") == 0:
                                self.log(f"{Fore.RED}✗ {title}: Not completed{Style.RESET_ALL}")
                            else:
                                self.log(f"{Fore.YELLOW}⚠ {title}: Already completed{Style.RESET_ALL}")
                else:
                    err_msg = task_list.get("msg", "Unknown Error")
                    self.log(f"{Fore.RED}✗ Fetch task list failed: {err_msg}{Style.RESET_ALL}")
           
            
            await asyncio.sleep(5)

    async def process_accounts_with_email(self, email: str, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        """Process account with email binding"""
        self.log(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        self.log(f"{Fore.CYAN}Processing: {self.mask_account(address)} | Email: {email}{Style.RESET_ALL}")
       
        logined = await self.process_wallet_login(account, address, use_proxy, rotate_proxy)
        if logined:
           
            profile = await self.profile_info(address, use_proxy)
            if profile:
                if profile.get("code") == "200":
                    user_id = profile.get("data", {}).get("id")
                    username = profile.get("data", {}).get("user_name")
                    exchange_points = profile.get("data", {}).get("exchange_total_points")
                    cumulative_revenue = profile.get("data", {}).get("cumulative_revenue")
                    self.log(f"{Fore.CYAN}Points: {exchange_points}{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN}Balance: {cumulative_revenue} GRISE{Style.RESET_ALL}")
                    
                    
                    self.log(f"{Fore.CYAN}▶ Binding email: {email}{Style.RESET_ALL}")
                    await self.bind_email_task(address, email, use_proxy)
                    
                    
                    if exchange_points >= 100:
                        used_points = (exchange_points // 100) * 100
                        swap = await self.swap_points(account, address, user_id, username, used_points, use_proxy)
                        if swap:
                            if swap.get("code") == "200":
                                self.log(f"{Fore.CYAN}Swapping points...{Style.RESET_ALL}")
                                received_amount = swap.get("data", {}).get("received_amount")
                                tx_hash = swap.get("data", {}).get("tx_hash")
                               
                                self.log(f"{Fore.GREEN}✓ Swap successful{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Received: {received_amount} GRISE{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN}Tx: {self.EXPLORER}{tx_hash}{Style.RESET_ALL}")
                            else:
                                err_msg = swap.get("msg", "Unknown Error")
                                self.log(f"{Fore.RED}✗ Swap failed: {err_msg}{Style.RESET_ALL}")
                    else:
                        self.log(f"{Fore.YELLOW}⚠ Insufficient points for swap (need 100){Style.RESET_ALL}")
                else:
                    err_msg = profile.get("msg", "Unknown Error")
                    self.log(f"{Fore.RED}✗ Fetch profile failed: {err_msg}{Style.RESET_ALL}")
            
            
            task_list = await self.task_list(address, use_proxy)
            if task_list:
                if task_list.get("code") == "200":
                    self.log(f"{Fore.CYAN}Fetching tasks...{Style.RESET_ALL}")
                    tasks = task_list.get("data", {}).get("list")
                    for task in tasks:
                        task_id = task.get("id")
                        title = task.get("name")
                        reward = task.get("points")
                        state = task.get("state")
                        
                        
                        if task_id == 3:
                            self.log(f"{Fore.YELLOW}✓ {title}: Already completed{Style.RESET_ALL}")
                            continue
                        
                        if state == 1:
                            self.log(f"{Fore.YELLOW}✓ {title}: Already completed{Style.RESET_ALL}")
                            continue
                        
                        
                        if task_id == 1:  
                            self.log(f"{Fore.CYAN}▶ {title}{Style.RESET_ALL}")
                            
                            if address in self.faucet_tx_hashes:
                                tx_hash = self.faucet_tx_hashes[address]
                                self.log(f"{Fore.CYAN}Completing faucet task with tx: {tx_hash}{Style.RESET_ALL}")
                                await self.complete_faucet_task(address, tx_hash, use_proxy)
                            else:
                                self.log(f"{Fore.YELLOW}⚠ No faucet tx hash found for this account{Style.RESET_ALL}")
                            continue
                        
                        
            
            
            await asyncio.sleep(3)
    
    async def main_with_email_binding(self):
        """Main function for running with email binding from mail.txt"""
        try:
            accounts = self.load_accounts_with_email()
            if not accounts:
                self.log(f"{Fore.RED}No accounts loaded from mail.txt. Create mail.txt file with email:privatekey format.{Style.RESET_ALL}")
                return
            
            
            self.all_topics = self.load_all_topics()
            self.comment_list = load_comments_from_json()
            self.topic_contents = load_topic_contents_from_json()
           
            proxy_choice, rotate_proxy = self.print_question()
            
            while True:
                self.clear_terminal()
                self.welcome()
                self.log(f"{Fore.GREEN}Total accounts: {len(accounts)}{Style.RESET_ALL}")
                use_proxy = True if proxy_choice == 1 else False
                if use_proxy:
                    self.load_proxies()
               
                for idx, (email, account) in enumerate(accounts, start=1):
                    if account:
                        address = self.generate_address(account)
                        if not address:
                            self.log(f"{Fore.RED}[{idx}] Invalid private key{Style.RESET_ALL}")
                            continue
                        self.access_tokens[address] = str(uuid.uuid4())
                        self.HEADERS[address] = {
                            "Accept": "*/*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://app.polarise.org",
                            "Referer": "https://app.polarise.org/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": FakeUserAgent().random
                        }
                        await self.process_accounts_with_email(email, account, address, use_proxy, rotate_proxy)
                
                self.log(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                self.log(f"{Fore.GREEN}All accounts processed!{Style.RESET_ALL}")
               
                
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN}[ Waiting {formatted_time} for next run... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1
                print() 
       
        except Exception as e:
            self.log(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            raise e

    async def main(self):
        """Main function for running without email binding"""
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No accounts loaded. Create accounts.txt file.{Style.RESET_ALL}")
                return
            
            
            self.all_topics = self.load_all_topics()
            self.comment_list = load_comments_from_json()
            self.topic_contents = load_topic_contents_from_json()
           
            proxy_choice, rotate_proxy = self.print_question()
            while True:
                self.clear_terminal()
                self.welcome()
                self.log(f"{Fore.GREEN}Total accounts: {len(accounts)}{Style.RESET_ALL}")
                use_proxy = True if proxy_choice == 1 else False
                if use_proxy:
                    self.load_proxies()
               
                for idx, account in enumerate(accounts, start=1):
                    if account:
                        address = self.generate_address(account)
                        if not address:
                            self.log(f"{Fore.RED}[{idx}] Invalid private key{Style.RESET_ALL}")
                            continue
                        self.access_tokens[address] = str(uuid.uuid4())
                        self.HEADERS[address] = {
                            "Accept": "*/*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://app.polarise.org",
                            "Referer": "https://app.polarise.org/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": FakeUserAgent().random
                        }
                        
                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                self.log(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                self.log(f"{Fore.GREEN}All accounts processed!{Style.RESET_ALL}")
               
                
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN}[ Waiting {formatted_time} for next run... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1
                print() 
       
        except Exception as e:
            self.log(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            raise e
        
class PolariseRegisterBot:
    def __init__(self):
        self.base_url = "https://apia.polarise.org/api/app/v1"
        self.faucet_url = "https://apifaucet-t.polarise.org"
        self.rpc_url = "https://chainrpc.polarise.org"
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://app.polarise.org',
            'referer': 'https://app.polarise.org/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }

        try:
            with open("capmonster_key.txt", "r") as f:
                self.capmonster_key = f.read().strip()
        except:
            self.capmonster_key = None
            print(f"{Fore.YELLOW}CapMonster key not found - captcha will not work{Style.RESET_ALL}")

        
        self.inviter_code = load_referral_code(default="rUcOC9")

        self.proxies = []
        if os.path.exists("proxy.txt"):
            with open("proxy.txt", "r") as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}Loaded {len(self.proxies)} proxies from proxy.txt{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}proxy.txt not found - running without proxies{Style.RESET_ALL}")
    
    def get_proxy_connector(self):
        if self.proxies:
            proxy = random.choice(self.proxies)
            
            if proxy.startswith("http://") or proxy.startswith("https://"):
                return ProxyConnector(proxy_type=ProxyType.HTTP, host=proxy.split("://")[1].split(":")[0], port=int(proxy.split(":")[-1].split("@")[-1] if "@" in proxy else proxy.split(":")[-1]))
            elif proxy.startswith("socks5://"):
                return ProxyConnector(proxy_type=ProxyType.SOCKS5, host=proxy.split("://")[1].split(":")[0], port=int(proxy.split(":")[1]))
            
        return None
    
    def create_new_wallet(self):
        private_key = "0x" + secrets.token_hex(32)
        account = Account.from_key(private_key)
        address = account.address
        return private_key, address
    
    def get_nonce(self, wallet_address):
        url = f"{self.base_url}/profile/getnonce"
        data = {"wallet": wallet_address.lower(), "chain_name": "polarise"}
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    return result.get("signed_nonce")
        except Exception as e:
            print(f"{Fore.RED}Nonce error: {e}{Style.RESET_ALL}")
        return None
    
    def login(self, private_key, wallet_address):
        nonce = self.get_nonce(wallet_address)
        if not nonce:
            print(f"{Fore.RED}Failed to get nonce{Style.RESET_ALL}")
            return None, None
        
        account = Account.from_key(private_key)
        message = f"Nonce to confirm: {nonce}"
        message_hash = encode_defunct(text=message)
        signed_message = account.sign_message(message_hash)
        signature = '0x' + signed_message.signature.hex()
        
        SID = str(uuid.uuid4())
        url = f"{self.base_url}/profile/login"
        data = {
            "signature": signature,
            "chain_name": "polarise",
            "name": wallet_address[:6],
            "nonce": nonce,
            "wallet": wallet_address.lower(),
            "sid": SID,
            "inviter_code": self.inviter_code
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    print(f"{Fore.GREEN}Login successful{Style.RESET_ALL}")
                    return result.get("data", {}).get("auth_token_info", {}).get("auth_token"), SID
        except Exception as e:
            print(f"{Fore.RED}Login error: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}Login failed{Style.RESET_ALL}")
        return None, None
    
    def solve_captcha(self):
        if not self.capmonster_key:
            print(f"{Fore.YELLOW}No CapMonster key{Style.RESET_ALL}")
            return None
        
        print(f"{Fore.CYAN}Solving captcha...{Style.RESET_ALL}")
        create_task = {
            "clientKey": self.capmonster_key,
            "task": {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": "https://faucet.polarise.org",
                "websiteKey": "6Le97hIsAAAAAFsmmcgy66F9YbLnwgnWBILrMuqn"
            }
        }
        
        try:
            resp = requests.post("https://api.capmonster.cloud/createTask", json=create_task, timeout=30)
            task_id = resp.json().get("taskId")
            if not task_id:
                return None
            
            for _ in range(40):
                time.sleep(3)
                result = requests.post("https://api.capmonster.cloud/getTaskResult",
                                       json={"clientKey": self.capmonster_key, "taskId": task_id}, timeout=30).json()
                if result.get("status") == "ready":
                    print(f"{Fore.GREEN}Captcha solved{Style.RESET_ALL}")
                    return result.get("solution", {}).get("gRecaptchaResponse")
        except Exception as e:
            print(f"{Fore.RED}Captcha error: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}Captcha solve failed{Style.RESET_ALL}")
        return None
    
    def claim_faucet(self, wallet_address, recaptcha_response):
        url = f"{self.faucet_url}/claim"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'origin': 'https://faucet.polarise.org',
            'referer': 'https://faucet.polarise.org/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        data = {
            "address": wallet_address.lower(),
            "denom": "uluna",
            "amount": "1",
            "response": recaptcha_response
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                txhash = result.get("txhash")
                if txhash:
                    print(f"{Fore.GREEN}Faucet claimed successfully! Amount: 0.1 POLAR | Tx: {txhash}{Style.RESET_ALL}")
                    return txhash
        except Exception as e:
            print(f"{Fore.RED}Claim error: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}Faucet claim failed{Style.RESET_ALL}")
        return None
    
    def complete_faucet_task(self, wallet_address, auth_token, sid, tx_hash):
        """Complete faucet task after claiming"""
        try:
            url = f"{self.base_url}/points/completetask"
            headers = {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://app.polarise.org',
                'referer': 'https://app.polarise.org/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
                'accesstoken': sid,
                'authorization': f'Bearer {auth_token} {sid} {wallet_address} polarise'
            }
            
            # Generate extra info for faucet task
            extra_info = json.dumps({
                "tx_hash": tx_hash,
                "from": wallet_address,
                "to": wallet_address,
                "value": "1000000"
            })
            
            data = {
                "user_wallet": wallet_address.lower(),
                "task_id": 1,  
                "extra_info": extra_info,
                "chain_name": "polarise"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    if result.get("data", {}).get("finish_status") == 1:
                        print(f"{Fore.GREEN}Faucet task completed successfully{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.YELLOW}Faucet task already completed{Style.RESET_ALL}")
                        return True
                else:
                    print(f"{Fore.RED}Faucet task completion failed: {result.get('msg')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Faucet task completion error: {e}{Style.RESET_ALL}")
        
        return False
    
    def bind_email(self, wallet_address, auth_token, sid):
        """Bind email to account (task_id: 3)"""
        try:
            url = f"{self.base_url}/points/completetask"
            headers = {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://app.polarise.org',
                'referer': 'https://app.polarise.org/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
                'accesstoken': sid,
                'authorization': f'Bearer {auth_token} {sid} {wallet_address} polarise'
            }
            
            
            email = generate_random_email()
            
            data = {
                "user_wallet": wallet_address.lower(),
                "task_id": 3,
                "extra_info": json.dumps({"email": email}),
                "chain_name": "polarise"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    print(f"{Fore.GREEN}Email bound successfully: {email}{Style.RESET_ALL}")
                    return email
                else:
                    print(f"{Fore.YELLOW}Email binding response: {result.get('msg')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Email binding error: {e}{Style.RESET_ALL}")
        
        return None
    
    def save_account_info(self, email, private_key, tx_hash=None):
        """Save account info to both wallet.txt and mail.txt"""
        
        with open("wallet.txt", "a") as f:
            f.write(private_key + "\n")
        
        
        if tx_hash:
            with open("mail.txt", "a") as f:
                f.write(f"{email}:{private_key}:{tx_hash}\n")
        else:
            with open("mail.txt", "a") as f:
                f.write(f"{email}:{private_key}\n")
        
        print(f"{Fore.GREEN}Account saved:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Email: {email}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Private Key: {private_key[:10]}...{Style.RESET_ALL}")
        if tx_hash:
            print(f"{Fore.CYAN}  Faucet Tx: {tx_hash[:20]}...{Style.RESET_ALL}")
    
    def register_and_faucet_with_email(self, num_accounts):
        """Register accounts with email binding and faucet claim"""
        for i in range(num_accounts):
            print(f"\n{Fore.CYAN}[{i+1}/{num_accounts}] Creating new wallet...{Style.RESET_ALL}")
            
            
            pk, addr = self.create_new_wallet()
            print(f"{Fore.CYAN}Address: {addr}{Style.RESET_ALL}")
            
            
            auth = None
            sid = None
            for attempt in range(1, 11):
                print(f"{Fore.CYAN}Logging in... (attempt {attempt}/10){Style.RESET_ALL}")
                auth, sid = self.login(pk, addr)
                if auth:
                    break
                time.sleep(5)
            
            if not auth:
                print(f"{Fore.RED}Login failed after 10 attempts - skipping this wallet{Style.RESET_ALL}")
                continue
            
            
            captcha = None
            for attempt in range(1, 5):
                captcha = self.solve_captcha()
                if captcha:
                    break
                time.sleep(10)
            
            tx_hash = None
            if captcha:
                
                print(f"{Fore.CYAN}Claiming 0.1 from faucet...{Style.RESET_ALL}")
                tx_hash = self.claim_faucet(addr, captcha)
                
                if tx_hash:
                    
                    print(f"{Fore.CYAN}Completing faucet task...{Style.RESET_ALL}")
                    self.complete_faucet_task(addr, auth, sid, tx_hash)
                    
                    
                    print(f"{Fore.CYAN}Binding email...{Style.RESET_ALL}")
                    email = self.bind_email(addr, auth, sid)
                    
                    if not email:
                        print(f"{Fore.YELLOW}Email binding failed, using random email{Style.RESET_ALL}")
                        email = generate_random_email()
                else:
                    print(f"{Fore.RED}Faucet claim failed - skipping email binding{Style.RESET_ALL}")
                    email = generate_random_email()
            else:
                print(f"{Fore.RED}Captcha failed - skipping faucet and email binding{Style.RESET_ALL}")
                email = generate_random_email()
            
            
            self.save_account_info(email, pk, tx_hash)
            
            
            if i < num_accounts - 1:
                print(f"{Fore.YELLOW}Waiting 3 seconds before next account...{Style.RESET_ALL}")
                time.sleep(3)
        
        print(f"\n{Fore.GREEN}Registration completed!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Accounts saved to:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  - wallet.txt (private keys only){Style.RESET_ALL}")
        print(f"{Fore.CYAN}  - mail.txt (email:privatekey:tx_hash format){Style.RESET_ALL}")

class PolariseFaucetBot:
    def __init__(self):
        self.base_url = "https://apia.polarise.org/api/app/v1"
        self.faucet_url = "https://apifaucet-t.polarise.org"
        self.rpc_url = "https://chainrpc.polarise.org"
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://app.polarise.org',
            'referer': 'https://app.polarise.org/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }
        
        try:
            with open("capmonster_key.txt", "r") as f:
                self.capmonster_key = f.read().strip()
        except:
            self.capmonster_key = None
            print(f"{Fore.YELLOW}CapMonster key not found - captcha will not work{Style.RESET_ALL}")
    
    def load_accounts(self):
        """Load accounts from accounts.txt"""
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except FileNotFoundError:
            print(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return []
    
    def get_address_from_private_key(self, private_key):
        """Get address from private key"""
        try:
            account = Account.from_key(private_key)
            return account.address
        except:
            return None
    
    def get_nonce(self, wallet_address):
        url = f"{self.base_url}/profile/getnonce"
        data = {"wallet": wallet_address.lower(), "chain_name": "polarise"}
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    return result.get("signed_nonce")
        except Exception as e:
            print(f"{Fore.RED}Nonce error: {e}{Style.RESET_ALL}")
        return None
    
    def login(self, private_key, wallet_address):
        nonce = self.get_nonce(wallet_address)
        if not nonce:
            print(f"{Fore.RED}Failed to get nonce{Style.RESET_ALL}")
            return None, None
        
        account = Account.from_key(private_key)
        message = f"Nonce to confirm: {nonce}"
        message_hash = encode_defunct(text=message)
        signed_message = account.sign_message(message_hash)
        signature = '0x' + signed_message.signature.hex()
        
        SID = str(uuid.uuid4())
        url = f"{self.base_url}/profile/login"
        data = {
            "signature": signature,
            "chain_name": "polarise",
            "name": wallet_address[:6],
            "nonce": nonce,
            "wallet": wallet_address.lower(),
            "sid": SID,
            "inviter_code": "rUcOC9"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    print(f"{Fore.GREEN}Login successful{Style.RESET_ALL}")
                    return result.get("data", {}).get("auth_token_info", {}).get("auth_token"), SID
        except Exception as e:
            print(f"{Fore.RED}Login error: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}Login failed{Style.RESET_ALL}")
        return None, None
    
    def solve_captcha(self):
        """Solve captcha using CapMonster"""
        if not self.capmonster_key:
            print(f"{Fore.YELLOW}No CapMonster key{Style.RESET_ALL}")
            return None
        
        print(f"{Fore.CYAN}Solving captcha...{Style.RESET_ALL}")
        create_task = {
            "clientKey": self.capmonster_key,
            "task": {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": "https://faucet.polarise.org",
                "websiteKey": "6Le97hIsAAAAAFsmmcgy66F9YbLnwgnWBILrMuqn"
            }
        }
        
        try:
            resp = requests.post("https://api.capmonster.cloud/createTask", json=create_task, timeout=30)
            task_id = resp.json().get("taskId")
            if not task_id:
                return None
            
            for _ in range(40):
                time.sleep(3)
                result = requests.post("https://api.capmonster.cloud/getTaskResult",
                                       json={"clientKey": self.capmonster_key, "taskId": task_id}, timeout=30).json()
                if result.get("status") == "ready":
                    print(f"{Fore.GREEN}Captcha solved{Style.RESET_ALL}")
                    return result.get("solution", {}).get("gRecaptchaResponse")
        except Exception as e:
            print(f"{Fore.RED}Captcha error: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}Captcha solve failed{Style.RESET_ALL}")
        return None
    
    def claim_faucet(self, wallet_address, recaptcha_response):
        """Claim faucet for wallet address"""
        url = f"{self.faucet_url}/claim"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'origin': 'https://faucet.polarise.org',
            'referer': 'https://faucet.polarise.org/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        data = {
            "address": wallet_address.lower(),
            "denom": "uluna",
            "amount": "1",
            "response": recaptcha_response
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                txhash = result.get("txhash")
                if txhash:
                    print(f"{Fore.GREEN}Faucet claimed successfully! Amount: 1 | Tx: {txhash}{Style.RESET_ALL}")
                    return txhash
        except Exception as e:
            print(f"{Fore.RED}Claim error: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.RED}Faucet claim failed{Style.RESET_ALL}")
        return None
    
    def complete_faucet_task(self, wallet_address, auth_token, sid, tx_hash):
        """Complete faucet task after claiming"""
        try:
            url = f"{self.base_url}/points/completetask"
            headers = {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://app.polarise.org',
                'referer': 'https://app.polarise.org/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
                'accesstoken': sid,
                'authorization': f'Bearer {auth_token} {sid} {wallet_address} polarise'
            }
            
            
            extra_info = json.dumps({
                "tx_hash": tx_hash,
                "from": wallet_address,
                "to": wallet_address,
                "value": "1000000"
            })
            
            data = {
                "user_wallet": wallet_address.lower(),
                "task_id": 1,  
                "extra_info": extra_info,
                "chain_name": "polarise"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "200":
                    if result.get("data", {}).get("finish_status") == 1:
                        print(f"{Fore.GREEN}Faucet task completed successfully{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.YELLOW}Faucet task already completed{Style.RESET_ALL}")
                        return True
                else:
                    print(f"{Fore.RED}Faucet task completion failed: {result.get('msg')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Faucet task completion error: {e}{Style.RESET_ALL}")
        
        return False
    
    def claim_faucet_for_all_accounts(self):
        """Claim faucet for all accounts in accounts.txt"""
        accounts = self.load_accounts()
        if not accounts:
            print(f"{Fore.RED}No accounts found in accounts.txt{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}Found {len(accounts)} accounts{Style.RESET_ALL}")
        
        for idx, private_key in enumerate(accounts, start=1):
            print(f"\n{Fore.CYAN}[{idx}/{len(accounts)}] Processing account...{Style.RESET_ALL}")
            
            address = self.get_address_from_private_key(private_key)
            if not address:
                print(f"{Fore.RED}Invalid private key{Style.RESET_ALL}")
                continue
            
            print(f"{Fore.CYAN}Address: {address}{Style.RESET_ALL}")
            
            
            print(f"{Fore.CYAN}Logging in...{Style.RESET_ALL}")
            auth_token, sid = self.login(private_key, address)
            
            if not auth_token:
                print(f"{Fore.RED}Login failed - skipping{Style.RESET_ALL}")
                continue
            
            
            captcha = None
            for attempt in range(1, 4):
                captcha = self.solve_captcha()
                if captcha:
                    break
                time.sleep(5)
            
            if not captcha:
                print(f"{Fore.RED}Captcha failed - skipping{Style.RESET_ALL}")
                continue
            
            
            tx_hash = self.claim_faucet(address, captcha)
            
            if tx_hash:
                
                print(f"{Fore.CYAN}Completing faucet task...{Style.RESET_ALL}")
                self.complete_faucet_task(address, auth_token, sid, tx_hash)
                print(f"{Fore.GREEN}Faucet process completed for {address}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Faucet failed for {address}{Style.RESET_ALL}")
            
            
            if idx < len(accounts):
                print(f"{Fore.YELLOW}Waiting 3 seconds before next account...{Style.RESET_ALL}")
                time.sleep(3)
        
        print(f"\n{Fore.GREEN}Faucet claim process completed!{Style.RESET_ALL}")

class PolariseEmailBinder:
    def __init__(self):
        self.base_url = "https://apia.polarise.org/api/app/v1"
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://app.polarise.org',
            'referer': 'https://app.polarise.org/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }
    
    def load_accounts(self):
        """Load accounts from accounts.txt"""
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except FileNotFoundError:
            print(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return []
    
    def get_address_from_private_key(self, private_key):
        """Get address from private key"""
        try:
            account = Account.from_key(private_key)
            return account.address
        except:
            return None
    
    def get_nonce(self, wallet_address, retry_count=3):
        """Get nonce with retry"""
        url = f"{self.base_url}/profile/getnonce"
        data = {"wallet": wallet_address.lower(), "chain_name": "polarise"}
        
        for attempt in range(1, retry_count + 1):
            try:
                print(f"{Fore.CYAN}Getting nonce... (attempt {attempt}/{retry_count}){Style.RESET_ALL}")
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == "200":
                        nonce = result.get("signed_nonce")
                        if nonce:
                            print(f"{Fore.GREEN}Got nonce successfully{Style.RESET_ALL}")
                            return nonce
                
                print(f"{Fore.YELLOW}Nonce attempt {attempt} failed: {response.status_code}{Style.RESET_ALL}")
                
            except requests.exceptions.Timeout:
                print(f"{Fore.YELLOW}Nonce request timeout (attempt {attempt}){Style.RESET_ALL}")
            except requests.exceptions.ConnectionError:
                print(f"{Fore.YELLOW}Connection error (attempt {attempt}){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}Nonce error (attempt {attempt}): {e}{Style.RESET_ALL}")
            
            if attempt < retry_count:
                print(f"{Fore.YELLOW}Waiting 5 seconds before retry...{Style.RESET_ALL}")
                time.sleep(5)
        
        print(f"{Fore.RED}Failed to get nonce after {retry_count} attempts{Style.RESET_ALL}")
        return None
    
    def login(self, private_key, wallet_address, max_retries=5):
        """Login with retry mechanism"""
        for attempt in range(1, max_retries + 1):
            print(f"{Fore.CYAN}Logging in... (attempt {attempt}/{max_retries}){Style.RESET_ALL}")
            
            nonce = self.get_nonce(wallet_address, retry_count=3)
            if not nonce:
                print(f"{Fore.YELLOW}Login attempt {attempt}: Failed to get nonce{Style.RESET_ALL}")
                if attempt < max_retries:
                    print(f"{Fore.YELLOW}Waiting 5 seconds before retry...{Style.RESET_ALL}")
                    time.sleep(5)
                continue
            
            try:
                account = Account.from_key(private_key)
                message = f"Nonce to confirm: {nonce}"
                message_hash = encode_defunct(text=message)
                signed_message = account.sign_message(message_hash)
                signature = '0x' + signed_message.signature.hex()
                
                SID = str(uuid.uuid4())
                url = f"{self.base_url}/profile/login"
                data = {
                    "signature": signature,
                    "chain_name": "polarise",
                    "name": wallet_address[:6],
                    "nonce": nonce,
                    "wallet": wallet_address.lower(),
                    "sid": SID,
                    "inviter_code": "rUcOC9"
                }
                
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == "200":
                        auth_token = result.get("data", {}).get("auth_token_info", {}).get("auth_token")
                        if auth_token:
                            print(f"{Fore.GREEN}✓ Login successful on attempt {attempt}{Style.RESET_ALL}")
                            return auth_token, SID
                
                print(f"{Fore.YELLOW}Login attempt {attempt} failed: {response.status_code}{Style.RESET_ALL}")
                
            except requests.exceptions.Timeout:
                print(f"{Fore.YELLOW}Login request timeout (attempt {attempt}){Style.RESET_ALL}")
            except requests.exceptions.ConnectionError:
                print(f"{Fore.YELLOW}Connection error (attempt {attempt}){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}Login error (attempt {attempt}): {e}{Style.RESET_ALL}")
            
            if attempt < max_retries:
                print(f"{Fore.YELLOW}Waiting 10 seconds before next login attempt...{Style.RESET_ALL}")
                time.sleep(10)
        
        print(f"{Fore.RED}Login failed after {max_retries} attempts{Style.RESET_ALL}")
        return None, None
    
    def bind_email_to_account(self, wallet_address, auth_token, sid, email=None, max_retries=3):
        """Bind email to account (task_id: 3) with retry"""
        if not email:
            email = generate_random_email()
        
        for attempt in range(1, max_retries + 1):
            print(f"{Fore.CYAN}Binding email... (attempt {attempt}/{max_retries}){Style.RESET_ALL}")
            
            try:
                url = f"{self.base_url}/points/completetask"
                headers = {
                    'accept': '*/*',
                    'content-type': 'application/json',
                    'origin': 'https://app.polarise.org',
                    'referer': 'https://app.polarise.org/',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
                    'accesstoken': sid,
                    'authorization': f'Bearer {auth_token} {sid} {wallet_address} polarise'
                }
                
                data = {
                    "user_wallet": wallet_address.lower(),
                    "task_id": 3,
                    "extra_info": json.dumps({"email": email}),
                    "chain_name": "polarise"
                }
                
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == "200":
                        if result.get("data", {}).get("finish_status") == 1:
                            print(f"{Fore.GREEN}✓ Email bound successfully: {email}{Style.RESET_ALL}")
                            return email
                        else:
                            print(f"{Fore.YELLOW}Email already bound or not completed{Style.RESET_ALL}")
                            return email
                
                print(f"{Fore.YELLOW}Email binding attempt {attempt} failed: {response.status_code}{Style.RESET_ALL}")
                
            except requests.exceptions.Timeout:
                print(f"{Fore.YELLOW}Email binding request timeout (attempt {attempt}){Style.RESET_ALL}")
            except requests.exceptions.ConnectionError:
                print(f"{Fore.YELLOW}Connection error (attempt {attempt}){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}Email binding error (attempt {attempt}): {e}{Style.RESET_ALL}")
            
            if attempt < max_retries:
                print(f"{Fore.YELLOW}Waiting 5 seconds before retry...{Style.RESET_ALL}")
                time.sleep(5)
        
        print(f"{Fore.RED}Email binding failed after {max_retries} attempts{Style.RESET_ALL}")
        return None
    
    def save_to_main_mail(self, email, private_key):
        """Save email:privatekey to main_mail.txt"""
        try:
            with open("main_mail.txt", "a") as f:
                f.write(f"{email}:{private_key}\n")
            print(f"{Fore.GREEN}✓ Saved to main_mail.txt: {email}:{private_key[:10]}...{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Error saving to main_mail.txt: {e}{Style.RESET_ALL}")
            return False
    
    def bind_emails_for_all_accounts(self):
        """Bind emails for all accounts in accounts.txt"""
        accounts = self.load_accounts()
        if not accounts:
            print(f"{Fore.RED}No accounts found in accounts.txt{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}Found {len(accounts)} accounts{Style.RESET_ALL}")
        
        successful_binds = 0
        failed_binds = 0
        
        for idx, private_key in enumerate(accounts, start=1):
            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[{idx}/{len(accounts)}] Processing account...{Style.RESET_ALL}")
            
            address = self.get_address_from_private_key(private_key)
            if not address:
                print(f"{Fore.RED}Invalid private key{Style.RESET_ALL}")
                failed_binds += 1
                continue
            
            print(f"{Fore.CYAN}Address: {address}{Style.RESET_ALL}")
            
            
            print(f"{Fore.CYAN}Attempting to login with retries...{Style.RESET_ALL}")
            auth_token, sid = self.login(private_key, address, max_retries=5)
            
            if not auth_token:
                print(f"{Fore.RED}Login failed after all retries - skipping{Style.RESET_ALL}")
                failed_binds += 1
                continue
            
            
            print(f"{Fore.CYAN}Attempting to bind email with retries...{Style.RESET_ALL}")
            email = self.bind_email_to_account(address, auth_token, sid, max_retries=3)
            
            if email:
                
                if self.save_to_main_mail(email, private_key):
                    successful_binds += 1
                    print(f"{Fore.GREEN}✓ Account {idx} processed successfully{Style.RESET_ALL}")
                else:
                    failed_binds += 1
                    print(f"{Fore.RED}✗ Failed to save account {idx}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Email binding failed for account {idx}{Style.RESET_ALL}")
                failed_binds += 1
            
            
            if idx < len(accounts):
                print(f"{Fore.YELLOW}Waiting 5 seconds before next account...{Style.RESET_ALL}")
                time.sleep(5)
        
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}EMAIL BINDING PROCESS COMPLETED!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Total accounts processed: {len(accounts)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Successful binds: {successful_binds}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed binds: {failed_binds}{Style.RESET_ALL}")
        if successful_binds > 0:
            print(f"{Fore.CYAN}Accounts saved to main_mail.txt{Style.RESET_ALL}")
            
if __name__ == "__main__":
    while True:
        print("\n" + "="*60)
        print(f"{Fore.GREEN} POLARISE BOT - Main Menu{Style.RESET_ALL}")
        print("="*60)
        print(f"{Fore.WHITE}1. Register accounts (Faucet → Task → Email){Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. Daily run with email binding (from mail.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Daily run without email binding (from accounts.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. Faucet claim + Task completion only (from accounts.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}5. Bind emails from accounts.txt to main_mail.txt{Style.RESET_ALL}")
        print(f"{Fore.WHITE}0. Exit{Style.RESET_ALL}")
        print("="*60)
        
        choice = input(f"{Fore.BLUE}Select option (1/2/3/4/5/0): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            bot = PolariseRegisterBot()
            try:
                num = int(input(f"{Fore.BLUE}How many accounts to create: {Style.RESET_ALL}"))
                if num <= 0:
                    print(f"{Fore.RED}Number must be positive{Style.RESET_ALL}")
                    continue
                bot.register_and_faucet_with_email(num)
            except ValueError:
                print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
        
        elif choice == "2":
            bot = Polarise()
            asyncio.run(bot.main_with_email_binding())
        
        elif choice == "3":
            bot = Polarise()
            asyncio.run(bot.main())
        
        elif choice == "4":
            bot = PolariseFaucetBot()
            bot.claim_faucet_for_all_accounts()
        
        elif choice == "5":
            bot = PolariseEmailBinder()
            bot.bind_emails_for_all_accounts()
        
        elif choice == "0":
            print(f"{Fore.YELLOW}Exiting{Style.RESET_ALL}")
            break
        
        else:
            print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
