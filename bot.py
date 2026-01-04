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

POLARISE_TOPICS = {
    "core_protocol": [
        "ERC-1000: The Game-Changer NFT Standard",
        "NFT Liquidity Crisis: The Problem We're Solving",
        "Flash Trade Explained: Instant NFT Swaps",
        "P-Tokens: Your NFT's Liquid Twin"
    ],
    "defi_tools": [
        "100% LTV Loans: Too Good to Be True?",
        "Leverage in NFT Trading Without Getting Rekt",
        "Consignment: Get Paid Now, Sell Later",
        "Multi-Chain Strategy: Why It Matters"
    ],
    "nft_ecosystem": [
        "Beyond JPEGs: Real NFT Utility",
        "Non-Standard Assets (NSA) Market Explained",
        "NFT Gaming & Metaverse Integration",
        "Digital Art vs Financial Assets: The Debate"
    ],
    "platform": [
        "Polarise Testnet: Your First Steps",
        "From PawnFi to Polarise: The Rebrand Story",
        "Security First: How We Protect Your Assets",
        "User Experience Revolution in NFT DeFi"
    ],
    "insights": [
        "The NFT Market: Dead or Just Getting Started?",
        "DeFi + NFTs: Why It Took So Long",
        "Institutional Money & NFT Liquidity",
        "Web3's Biggest Lie: You Own Your Assets"
    ],
    "market_analysis": [
        "NFT Floor Price Dynamics Explained",
        "Volatility: Friend or Foe in NFT Markets?",
        "The Liquidity Premium: Why It Matters",
        "Market Cycles & Timing Your NFT Strategy"
    ],
    "educational": [
        "NFT Liquidity 101: A Beginner's Guide",
        "Smart Contracts Demystified for Normies",
        "Tokenomics: The $PFT Guide",
        "Risk Management for NFT Holders"
    ],
    "future_vision": [
        "The Next Evolution of NFTs",
        "Building the Future of Digital Ownership"
    ],
    "hot_takes": [
        "OpenSea is Dead (And That's Good)",
        "Why Most NFT Projects Deserve to Fail",
        "The Truth About NFT Communities",
        "Royalties Are Killing NFTs",
        "DAOs Don't Work (Yet)",
        "The Metaverse Hype Was a Lie",
        "Why I'm Bullish on NFTs But Bearish on Your Project",
        "The Real Reason You Can't Sell Your NFT",
        "Crypto Twitter Is Ruining Crypto",
        "If You Don't Understand Liquidity, You Don't Understand NFTs"
    ]
}

COMMENT_LIST = [
    "Good", "Great", "Nice", "Awesome", "Cool", "Well done", "Good job", "Solid", "Perfect", "Amazing",
    "GM", "GM Mate", "Good Morning", "Morning Mate", "Morning all", "GM everyone", "Rise and shine", "Morning vibes", "Fresh start", "New day",
    "GN", "GN Mate", "Good Night", "Night Mate", "Sleep well", "Sweet dreams", "Rest well", "Night vibes", "Time to rest", "See you tomorrow",
    "Hello", "Hello Mate", "Hi", "Hi Mate", "Hey", "Hey Mate", "Yo", "Yo Mate", "What's up", "Sup Mate",
    "Agree", "Totally agree", "Absolutely", "Indeed", "Exactly", "True", "Well said", "Makes sense", "Facts", "100% agree",
    "LFG", "Let's go", "Keep going", "On fire", "Bullish", "WAGMI", "To the moon", "Big vibes", "Strong move", "Nice play",
    "Follow me", "Follow back", "Let's connect", "Support each other", "Stay connected", "See you around", "Much respect", "Cheers", "Salute", "Respect"
]

# Pre-generated content for each topic
TOPIC_CONTENTS = {
    "ERC-1000: The Game-Changer NFT Standard": {
        "title": "ERC-1000: This Changes Everything for NFTs",
        "description": "Remember when ERC-20 changed DeFi forever? ERC-1000 is about to do the same for NFTs.\n\nForget about illiquid JPEGs collecting digital dust. ERC-1000 introduces native liquidity pools, instant swaps, and fractional ownership baked right into the standard.\n\nThis isn't just another token standard—it's a complete rethinking of what NFTs can BE.\n\nWhat's your take? Will this finally solve NFT liquidity?"
    },
    "NFT Liquidity Crisis: The Problem We're Solving": {
        "title": "The Dirty Secret No One Talks About: NFT Liquidity",
        "description": "Here's a hard truth: 95% of NFTs are basically worthless because they CAN'T BE SOLD.\n\nFloor prices? Meaningless when there's zero volume.\n\nYou're not investing—you're speculating on greater fools.\n\nPolarise isn't just another platform. We're solving the fundamental flaw in the NFT market.\n\nThoughts? Have you ever been stuck with an NFT you couldn't sell?"
    },
    "Flash Trade Explained: Instant NFT Swaps": {
        "title": "NFT Trading at Light Speed: Flash Trades Explained",
        "description": "Ever tried to sell an NFT and waited days for a buyer? Those days are OVER.\n\nFlash trades = instant NFT swaps with zero slippage.\n\nIt's like Uniswap for NFTs, but faster and smarter.\n\nNo more praying for buyers. No more race to the bottom on price.\n\nGame-changing or overhyped? Let's discuss!"
    },
    "P-Tokens: Your NFT's Liquid Twin": {
        "title": "Unlock Your NFT's Value Instantly with P-Tokens",
        "description": "Your NFT is stuck in your wallet? Not anymore.\n\nP-Tokens = instant liquidity for ANY NFT.\n\n1️⃣ Wrap your NFT\n2️⃣ Get P-Tokens\n3️⃣ Trade, lend, or leverage immediately\n\nIt's like having your cake and eating it too.\n\nAnyone tried this yet? Thoughts on the risks?"
    },
    "100% LTV Loans: Too Good to Be True?": {
        "title": "100% LTV on NFTs: Revolutionary or Reckless?",
        "description": "100% loan-to-value on NFTs sounds impossible... until now.\n\nTraditional finance would call this crazy. We call it innovation.\n\nRisk? Managed by real-time price oracles and dynamic collateral ratios.\n\nThis could unlock BILLIONS in trapped NFT value.\n\nToo good to be true? Or the future of NFT finance?"
    },
    "Leverage in NFT Trading Without Getting Rekt": {
        "title": "NFT Leverage: Your Fast Track to Gains (or Losses)",
        "description": "Leverage trading NFTs = 10x your gains or 100x your losses.\n\nPolarise gives you the tools but YOU need the strategy.\n\nKey rules:\n1. Never go all-in\n2. Set stop losses\n3. Understand the asset\n\nUsed leverage before? Share your best/worst experiences!"
    },
    "Consignment: Get Paid Now, Sell Later": {
        "title": "Consignment: The Smart NFT Seller's Secret Weapon",
        "description": "Why wait months to sell your NFT when you can get paid NOW?\n\nConsignment = instant liquidity + future upside.\n\nIt's like getting a loan AND keeping ownership benefits.\n\nPerfect for:\n- Projects with long-term potential\n- Undervalued gems\n- Strategic holdings\n\nUnderrated feature or too complex for most users?"
    },
    "Multi-Chain Strategy: Why It Matters": {
        "title": "Stuck on One Chain? You're Missing the Big Picture",
        "description": "Ethereum maxis vs Solana degens vs Polygon enthusiasts...\n\nWhy choose when you can have ALL of them?\n\nMulti-chain isn't just a feature—it's a survival strategy.\n\nDifferent chains = different communities = different opportunities.\n\nAre you multi-chain yet? Which chain has surprised you most?"
    },
    "Beyond JPEGs: Real NFT Utility": {
        "title": "NFTs Are More Than JPEGs (Despite What Critics Say)",
        "description": "JPEGs were just the beginning.\n\nReal NFT utility:\n- Access tokens\n- Identity verification\n- Royalty streams\n- Governance rights\n- Real-world asset ownership\n\nThe JPEG phase was necessary... but we're moving BEYOND.\n\nWhat's the most innovative NFT use case you've seen?"
    },
    "Non-Standard Assets (NSA) Market Explained": {
        "title": "NSA: The Hidden Gem of NFT Markets",
        "description": "Forget boring standards. NSA = Non-Standard Assets.\n\nThese are the weird, unique, complex digital assets that don't fit in boxes.\n\nThink:\n- Fractionalized real estate\n- Complex financial instruments\n- Multi-asset bundles\n\nNSA market could be 10x larger than 'regular' NFTs.\n\nDiscover any cool NSAs lately?"
    },
    "NFT Gaming & Metaverse Integration": {
        "title": "NFT Gaming: The Next Billion-Dollar Industry",
        "description": "Gaming + NFTs = perfect match.\n\nFinally, TRUE digital ownership in games.\n\nCross-game assets, player-driven economies, actual value creation.\n\nForget play-to-earn. This is OWN-to-earn.\n\nWhich NFT game has impressed you most?"
    },
    "Digital Art vs Financial Assets: The Debate": {
        "title": "Are NFTs Art or Financial Assets? (Answer: BOTH)",
        "description": "The eternal debate: Art vs Finance.\n\nWhy can't they be both?\n\nGreat art has ALWAYS been a financial asset.\n\nDigital art NFTs just make it accessible and liquid.\n\nStop arguing about definitions. Start creating value.\n\nWhere do you stand on this debate?"
    },
    "Polarise Testnet: Your First Steps": {
        "title": "Polarise Testnet: Play with Real Money (But Not Really)",
        "description": "Testnets are boring... until you're playing with real concepts.\n\nPolarise testnet = risk-free experimentation with REAL features.\n\nTry everything:\n- Flash trades\n- 100% LTV loans\n- Consignment\n\nZero risk, maximum learning.\n\nAlready tested? Share your experience!"
    },
    "From PawnFi to Polarise: The Rebrand Story": {
        "title": "PawnFi to Polarise: More Than Just a Name Change",
        "description": "PawnFi was good... but Polarise is GREAT.\n\nWhy rebrand?\n1. Broader vision\n2. Beyond just 'pawn' services\n3. Complete NFT finance ecosystem\n\nSometimes you outgrow your name. We definitely did.\n\nWhat do you think of the new name/brand?"
    },
    "Security First: How We Protect Your Assets": {
        "title": "NFT Security: Our #1 Priority (And It Should Be Yours Too)",
        "description": "Lose your NFTs = lose everything.\n\nOur security approach:\n- Multi-sig everything\n- Regular audits\n- Insurance funds\n- Bug bounties\n\nBut remember: NOT YOUR KEYS, NOT YOUR NFTS.\n\nWhat security practices do you follow?"
    },
    "User Experience Revolution in NFT DeFi": {
        "title": "NFT DeFi Doesn't Have to Be Complicated (Seriously)",
        "description": "Most DeFi platforms look like airplane dashboards.\n\nOurs? Simple, intuitive, HUMAN.\n\nGood UX isn't a luxury—it's a requirement for mass adoption.\n\nIf your grandma can't use it, you're doing it wrong.\n\nBest UX you've seen in DeFi?"
    },
    "The NFT Market: Dead or Just Getting Started?": {
        "title": "NFT Market Report: Far From Dead, Just Getting Interesting",
        "description": "Headlines say NFTs are dead. Data says otherwise.\n\nWhat's changing:\n- Less speculation, more utility\n- Institutional interest growing\n- Real-world use cases emerging\n\nThe 'easy money' phase is over. The REAL phase is just beginning.\n\nBullish or bearish on NFTs?"
    },
    "DeFi + NFTs: Why It Took So Long": {
        "title": "DeFi + NFTs: The Marriage That Should Have Happened Years Ago",
        "description": "Why did it take so long to combine DeFi and NFTs?\n\nTechnical challenges:\n- Non-fungible vs fungible\n- Valuation problems\n- Liquidity issues\n\nBut the wait was worth it. The synergy is incredible.\n\nWhy do you think it took this long?"
    },
    "Institutional Money & NFT Liquidity": {
        "title": "Institutional Money Is Coming to NFTs (And It Changes Everything)",
        "description": "When institutions enter NFTs, liquidity problems disappear.\n\nBut there's a catch: They need infrastructure.\n\nThat's where we come in.\n\nInstitutional-grade tools for institutional money.\n\nGood or bad for the space?"
    },
    "Web3's Biggest Lie: You Own Your Assets": {
        "title": "The Hard Truth: You Don't Really 'Own' Your Web3 Assets",
        "description": "Here's an unpopular truth: Full ownership in Web3 is a myth.\n\nReality:\n- Protocol risk\n- Smart contract risk\n- Centralized exchange risk\n- Regulatory risk\n\nTrue ownership = understanding AND managing these risks.\n\nControversial take or hard truth?"
    },
    "NFT Floor Price Dynamics Explained": {
        "title": "Floor Prices Are Mostly Meaningless (Here's Why)",
        "description": "Obsessing over floor prices? You're missing the point.\n\nFloor price ≠ liquidity\nFloor price ≠ demand\nFloor price ≠ value\n\nIt's just ONE metric, and often the least important one.\n\nWhat metrics do YOU actually watch?"
    },
    "Volatility: Friend or Foe in NFT Markets?": {
        "title": "NFT Volatility: Your Best Friend or Worst Enemy?",
        "description": "Volatility = risk = opportunity.\n\nThe key isn't avoiding volatility—it's USING it.\n\nBuy when there's blood in the streets. Sell when there's hype.\n\nEasier said than done, obviously.\n\nHow do you handle NFT volatility?"
    },
    "The Liquidity Premium: Why It Matters": {
        "title": "Liquidity Premium: The Most Important Concept in NFT Investing",
        "description": "Liquid assets trade at a PREMIUM.\n\nIlliquid assets = discount.\n\nThe liquidity premium can be 50%+ for NFTs.\n\nTranslation: Your NFT is worth LESS if you can't sell it easily.\n\nAre you factoring liquidity into your NFT buys?"
    },
    "Market Cycles & Timing Your NFT Strategy": {
        "title": "NFT Market Cycles: When to Buy, When to Sell, When to HODL",
        "description": "Market cycles exist. Ignore them at your peril.\n\nGeneral rule:\n- Buy in bear markets\n- Sell in bull markets\n- Build in between\n\nSimple in theory. Hard in practice.\n\nWhat phase do you think we're in now?"
    },
    "NFT Liquidity 101: A Beginner's Guide": {
        "title": "NFT Liquidity for Beginners (No Jargon, I Promise)",
        "description": "New to NFTs? Confused by 'liquidity' talk?\n\nSimple analogy:\nLiquidity = how easily you can buy/sell something.\n\nHigh liquidity = easy to trade\nLow liquidity = hard to trade\n\nThat's it. Start there.\n\nWhat confused you most when starting with NFTs?"
    },
    "Smart Contracts Demystified for Normies": {
        "title": "Smart Contracts Aren't That Smart (And That's Okay)",
        "description": "Smart contracts = digital vending machines.\n\nPut something in → Get something out.\n\nNo magic. No AI. Just code doing what it's told.\n\nThe 'smart' part is they execute automatically.\n\nStill confused? Ask me anything!"
    },
    "Tokenomics: The $PFT Guide": {
        "title": "$PFT Tokenomics: More Than Just Another Governance Token",
        "description": "$PFT isn't just for voting (though you can do that too).\n\nReal utility:\n- Fee discounts\n- Staking rewards\n- Protocol incentives\n- Governance rights\n\nTokenomics matter. Ours are designed for LONG-TERM growth.\n\nWhat makes good tokenomics in your view?"
    },
    "Risk Management for NFT Holders": {
        "title": "NFT Risk Management: Don't Learn This the Hard Way",
        "description": "NFT losses hurt more than crypto losses. Here's how to avoid them:\n\n1. Diversify (yes, even with NFTs)\n2. Never invest more than you can lose\n3. Have an exit strategy\n4. Understand what you're buying\n\nWhat's your #1 risk management rule?"
    },
    "The Next Evolution of NFTs": {
        "title": "The Next NFT Evolution: What Comes After JPEGs?",
        "description": "We're at NFT 2.0. What does 3.0 look like?\n\nMy predictions:\n- Dynamic NFTs\n- AI-generated assets\n- Cross-chain composability\n- Real-world integration\n\nToo optimistic? What's YOUR prediction?"
    },
    "Building the Future of Digital Ownership": {
        "title": "Digital Ownership: The Future We're Building Together",
        "description": "Digital ownership isn't just about NFTs.\n\nIt's about control, rights, and value in the digital world.\n\nWe're building tools for THAT future.\n\nNot just trading cards. Not just art.\n\nThe foundation of digital property rights.\n\nWhat does digital ownership mean to YOU?"
    },
    "OpenSea is Dead (And That's Good)": {
        "title": "OpenSea's Decline: Natural Evolution or Failure?",
        "description": "OpenSea dominated... until it didn't.\n\nWhat happened?\n1. Complacency\n2. High fees\n3. Stagnant innovation\n4. Competition\n\nTheir decline creates SPACE for innovation.\n\nGood for the ecosystem overall.\n\nRIP OpenSea or too early to call?"
    },
    "Why Most NFT Projects Deserve to Fail": {
        "title": "Hard Truth: 99% of NFT Projects SHOULD Fail",
        "description": "Not every project deserves to succeed.\n\nMany are:\n- Cash grabs\n- Copycats\n- No utility\n- Bad teams\n\nFailure isn't bad—it's NECESSARY for a healthy ecosystem.\n\nSurvival of the fittest applies to NFTs too.\n\nAgree or too harsh?"
    },
    "The Truth About NFT Communities": {
        "title": "NFT 'Communities': Real Connection or Illusion?",
        "description": "NFT communities promise connection... but often deliver hype.\n\nReal community = shared values + mutual support\nFake community = price talk + empty promises\n\nWhich ones have you found? The real deal or just noise?"
    },
    "Royalties Are Killing NFTs": {
        "title": "Royalty Debate: Necessary Incentive or Growth Killer?",
        "description": "Royalties sounded great... until they didn't.\n\nProblem: They discourage trading.\nSolution: Find better incentives.\n\nCreators deserve rewards. But not at the cost of LIQUIDITY.\n\nThere's a middle ground. We need to find it.\n\nWhere do you stand on royalties?"
    },
    "DAOs Don't Work (Yet)": {
        "title": "DAO Reality Check: Great in Theory, Messy in Practice",
        "description": "DAOs promise decentralized governance... but often deliver gridlock.\n\nCurrent problems:\n- Voter apathy\n- Whale dominance\n- Slow decisions\n- Legal uncertainty\n\nThe concept is revolutionary. The execution needs work.\n\nBeen in a DAO? Share your experience!"
    },
    "The Metaverse Hype Was a Lie": {
        "title": "Metaverse Reality Check: We're Not Ready (And That's Okay)",
        "description": "The metaverse hype peaked... then crashed.\n\nWhy?\n- Terrible UX\n- No real utility\n- Corporate takeover\n- Tech not ready\n\nThe vision is still valid. But we're years away from execution.\n\nToo pessimistic or realistic assessment?"
    },
    "Why I'm Bullish on NFTs But Bearish on Your Project": {
        "title": "NFTs Are Amazing... But Your Project Probably Isn't",
        "description": "NFT technology = revolutionary\nYour monkey JPEG project = probably not\n\nBeing bullish on NFTs doesn't mean being bullish on EVERY NFT.\n\nDiscrimination is GOOD. Be picky.\n\nWhat makes an NFT project ACTUALLY good?"
    },
    "The Real Reason You Can't Sell Your NFT": {
        "title": "Can't Sell Your NFT? Here's the Real Reason",
        "description": "It's not the market. It's not bad luck.\n\nThe reason: NOBODY WANTS IT.\n\nHarsh but true. Value = what someone will pay.\n\nIf no one's buying, your NFT isn't worth what you think.\n\nBeen there? What did you learn?"
    },
    "Crypto Twitter Is Ruining Crypto": {
        "title": "CT Is Broken: How Crypto Twitter Hurts More Than Helps",
        "description": "Crypto Twitter used to be about ideas. Now it's about:\n- Clout chasing\n- Fake alpha\n- Tribal warfare\n- Signal boosting\n\nThe noise is drowning out the signal.\n\nTime for a reset. Or am I just getting old?"
    },
    "If You Don't Understand Liquidity, You Don't Understand NFTs": {
        "title": "NFT Mastery Starts with Understanding Liquidity",
        "description": "You can know everything about art, tech, and trends...\n\nBut if you don't understand liquidity, you don't understand NFT VALUE.\n\nLiquidity = exit options = REAL value\n\nMaster this first. Everything else comes after.\n\nHow long did it take you to understand liquidity?"
    }
}

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
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.auth_tokens = {}
        self.nonce = {}
        self.sub_id = {}
        self.faucet_tx_hashes = {}  # Store faucet tx hashes
    
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
            all_topics = []
            for category, topics in POLARISE_TOPICS.items():
                all_topics.extend(topics)
            return all_topics
        except Exception as e:
            self.log(f"{Fore.RED}Failed to load topics: {e}{Style.RESET_ALL}")
            return []
       
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
            "to": address,  # Faucet sends to same address
            "value": "1000000"  # 1 token in wei
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
        """Generate content without using external APIs"""
        try:
            # Check if we have pre-generated content for this topic
            if topic in TOPIC_CONTENTS:
                return TOPIC_CONTENTS[topic]
           
            # Fallback: generate simple content if topic not in pre-generated list
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
                                content = random.choice(COMMENT_LIST)
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
           
            # Add delay between accounts
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
                    
                    # Bind email first (task_id: 3)
                    self.log(f"{Fore.CYAN}▶ Binding email: {email}{Style.RESET_ALL}")
                    await self.bind_email_task(address, email, use_proxy)
                    
                    # Continue with other tasks...
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
            
            # Continue with other tasks as before...
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
                        
                        # Skip email binding task since we already did it
                        if task_id == 3:
                            self.log(f"{Fore.YELLOW}✓ {title}: Already completed{Style.RESET_ALL}")
                            continue
                        
                        if state == 1:
                            self.log(f"{Fore.YELLOW}✓ {title}: Already completed{Style.RESET_ALL}")
                            continue
                        
                        # Process other tasks...
                        if task_id == 1:  # Faucet task
                            self.log(f"{Fore.CYAN}▶ {title}{Style.RESET_ALL}")
                            # Check if we have a faucet tx hash for this account
                            if address in self.faucet_tx_hashes:
                                tx_hash = self.faucet_tx_hashes[address]
                                self.log(f"{Fore.CYAN}Completing faucet task with tx: {tx_hash}{Style.RESET_ALL}")
                                await self.complete_faucet_task(address, tx_hash, use_proxy)
                            else:
                                self.log(f"{Fore.YELLOW}⚠ No faucet tx hash found for this account{Style.RESET_ALL}")
                            continue
                        
                        # ... (other task processing continues)
            
            # Add delay between accounts
            await asyncio.sleep(5)
    
    async def main_with_email_binding(self):
        """Main function for running with email binding from mail.txt"""
        try:
            accounts = self.load_accounts_with_email()
            if not accounts:
                self.log(f"{Fore.RED}No accounts loaded from mail.txt. Create mail.txt file with email:privatekey format.{Style.RESET_ALL}")
                return
            
            self.all_topics = self.load_all_topics()
           
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
               
                # Wait 24 hours before next run
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN}[ Waiting {formatted_time} for next run... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1
                print() # New line after countdown
       
        except Exception as e:
            self.log(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            raise e

    async def main(self):
        """Main function for running without email binding"""
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No accounts loaded. Create accounts.txt file.{Style.RESET_ALL}")
                return
            self.all_topics = self.load_all_topics()
           
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
                        # Call the original process_accounts method
                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                self.log(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                self.log(f"{Fore.GREEN}All accounts processed!{Style.RESET_ALL}")
               
                # Wait 24 hours before next run
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN}[ Waiting {formatted_time} for next run... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1
                print() # New line after countdown
       
        except Exception as e:
            self.log(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
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
            # Support http, https, socks5
            if proxy.startswith("http://") or proxy.startswith("https://"):
                return ProxyConnector(proxy_type=ProxyType.HTTP, host=proxy.split("://")[1].split(":")[0], port=int(proxy.split(":")[-1].split("@")[-1] if "@" in proxy else proxy.split(":")[-1]))
            elif proxy.startswith("socks5://"):
                return ProxyConnector(proxy_type=ProxyType.SOCKS5, host=proxy.split("://")[1].split(":")[0], port=int(proxy.split(":")[1]))
            # Add basic auth if needed (format user:pass@ip:port)
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
                "task_id": 1,  # Faucet task ID
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
            
            # Generate random email
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
        # Save to wallet.txt (private key only)
        with open("wallet.txt", "a") as f:
            f.write(private_key + "\n")
        
        # Save to mail.txt (email:privatekey:tx_hash)
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
            
            # Create wallet
            pk, addr = self.create_new_wallet()
            print(f"{Fore.CYAN}Address: {addr}{Style.RESET_ALL}")
            
            # Login
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
            
            # Solve captcha for faucet
            captcha = None
            for attempt in range(1, 5):
                captcha = self.solve_captcha()
                if captcha:
                    break
                time.sleep(10)
            
            tx_hash = None
            if captcha:
                # Claim faucet FIRST
                print(f"{Fore.CYAN}Claiming 0.1 from faucet...{Style.RESET_ALL}")
                tx_hash = self.claim_faucet(addr, captcha)
                
                if tx_hash:
                    # Complete faucet task SECOND
                    print(f"{Fore.CYAN}Completing faucet task...{Style.RESET_ALL}")
                    self.complete_faucet_task(addr, auth, sid, tx_hash)
                    
                    # Bind email THIRD (after faucet)
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
            
            # Save account info
            self.save_account_info(email, pk, tx_hash)
            
            # Delay between accounts
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
            "inviter_code": "2BHlBH"
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
            
            # Generate extra info for faucet task
            extra_info = json.dumps({
                "tx_hash": tx_hash,
                "from": wallet_address,
                "to": wallet_address,
                "value": "1000000"
            })
            
            data = {
                "user_wallet": wallet_address.lower(),
                "task_id": 1,  # Faucet task ID
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
            
            # Login first to get auth token
            print(f"{Fore.CYAN}Logging in...{Style.RESET_ALL}")
            auth_token, sid = self.login(private_key, address)
            
            if not auth_token:
                print(f"{Fore.RED}Login failed - skipping{Style.RESET_ALL}")
                continue
            
            # Solve captcha
            captcha = None
            for attempt in range(1, 4):
                captcha = self.solve_captcha()
                if captcha:
                    break
                time.sleep(5)
            
            if not captcha:
                print(f"{Fore.RED}Captcha failed - skipping{Style.RESET_ALL}")
                continue
            
            # Claim faucet
            tx_hash = self.claim_faucet(address, captcha)
            
            if tx_hash:
                # Complete faucet task
                print(f"{Fore.CYAN}Completing faucet task...{Style.RESET_ALL}")
                self.complete_faucet_task(address, auth_token, sid, tx_hash)
                print(f"{Fore.GREEN}Faucet process completed for {address}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Faucet failed for {address}{Style.RESET_ALL}")
            
            # Delay between accounts
            if idx < len(accounts):
                print(f"{Fore.YELLOW}Waiting 10 seconds before next account...{Style.RESET_ALL}")
                time.sleep(10)
        
        print(f"\n{Fore.GREEN}Faucet claim process completed!{Style.RESET_ALL}")

if __name__ == "__main__":
    while True:
        print("\n" + "="*60)
        print(f"{Fore.GREEN} POLARISE BOT - Main Menu{Style.RESET_ALL}")
        print("="*60)
        print(f"{Fore.WHITE}1. Register accounts (Faucet → Task → Email){Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. Daily run with email binding (from mail.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Daily run without email binding (from accounts.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. Faucet claim + Task completion only (from accounts.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}0. Exit{Style.RESET_ALL}")
        print("="*60)
        
        choice = input(f"{Fore.BLUE}Select option (1/2/3/4/0): {Style.RESET_ALL}").strip()
        
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
        
        elif choice == "0":
            print(f"{Fore.YELLOW}Exiting{Style.RESET_ALL}")
            break
        
        else:
            print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
