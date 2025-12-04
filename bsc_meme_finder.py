from web3 import Web3
import json
import requests
from requests.exceptions import HTTPError

# --- 설정 정보 ---
BNB_RPC_URL = "https://bsc-dataseed.binance.org/"
PANCAKESWAP_FACTORY_ADDRESS = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
# WBNB 주소: BNB Chain에서 유동성 풀의 기준이 되는 토큰입니다.
WBNB_ADDRESS = "0xbb4cdb9cbd36b01bd1cbaebf2de08a174a87c142" 
DATA_FILE_PATH = "bsc_meme_data.json"

# --- Factory 계약 ABI (주요 함수만 포함) ---
# Factory 계약에서 'allPairs' 함수를 사용하려면 해당 함수의 ABI가 필요합니다.
FACTORY_ABI = json.loads('''
[
    {"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},
    {"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}
]
''')

# --- Utility 함수 ---
def fetch_token_info(w3, token_address):
    """토큰의 이름과 심볼을 가져오는 함수"""
    # ERC-20 토큰의 name 및 symbol ABI (표준)
    TOKEN_ABI = json.loads('''
    [
        {"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},
        {"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}
    ]
    ''')
    try:
        token_contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=TOKEN_ABI)
        name = token_contract.functions.name().call()
        symbol = token_contract.functions.symbol().call()
        return name, symbol
    except Exception as e:
        # 정보가 없는 경우 (예: 잘못된 주소 또는 API 오류)
        return "Unknown Token", "UNK"

def find_bsc_pools():
    """BNB Chain의 유동성 풀 목록을 쿼리하는 함수"""
    print(f"-> BNB RPC {BNB_RPC_URL}에 연결 중...")
    w3 = Web3(Web3.HTTPProvider(BNB_RPC_URL))
    
    if not w3.is_connected():
        print("❌ RPC 연결 실패. URL을 확인하거나 잠시 후 다시 시도하세요.")
        return []
    
    factory_contract = w3.eth.contract(address=w3.to_checksum_address(PANCAKESWAP_FACTORY_ADDRESS), abi=FACTORY_ABI)
    
    try:
        # Factory 계약에서 총 풀 개수를 가져옵니다.
        total_pools = factory_contract.functions.allPairsLength().call()
        print(f"-> PancakeSwap에서 발견된 총 유동성 풀 개수: {total_pools}")
        
        # ⚠️ 테스트를 위해 상위 5개의 풀만 조회합니다. (전체 조회는 매우 느리고 RPC 제한에 걸릴 수 있음)
        pools_to_check = 5 
        
        meme_candidates = []

        # 각 풀 주소를 조회합니다.
        for i in range(pools_to_check):
            pair_address = factory_contract.functions.allPairs(i).call()
            # (이후 Pool 계약을 조회하여 어떤 토큰들이 거래되는지 확인하는 복잡한 과정이 생략됨)
            
            # **임의의 밈 코인 후보 데이터 생성 (실제 데이터 쿼리 아님)**
            # 이 단계에서는 실제 블록체인 쿼리가 복잡하므로, 임의의 데이터를 생성하여 UI 테스트에 사용합니다.
            if i == 0:
                 name, symbol = fetch_token_info(w3, WBNB_ADDRESS) # WBNB 정보 가져오기
            else:
                 name, symbol = f"MemeCoin {i}", f"MM{i}"
                 
            meme_candidates.append({
                "name": name,
                "symbol": symbol,
                "chain": "BNB Chain",
                "liquidity_pool_address": pair_address,
                # 거래량은 실제 Pool 데이터를 쿼리해야 하므로 임의 값 사용
                "estimated_24h_volume": total_pools * 1000 + i * 500
            })
            
        return meme_candidates

    except Exception as e:
        print(f"❌ 데이터 쿼리 중 오류 발생: {e}")
        return []

def save_data(data):
    """가져온 데이터를 JSON 파일로 저장"""
    with open(DATA_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"데이터가 성공적으로 {DATA_FILE_PATH}에 저장되었습니다. (총 {len(data)}개)")


if __name__ == "__main__":
    collected_data = find_bsc_pools()
    save_data(collected_data)