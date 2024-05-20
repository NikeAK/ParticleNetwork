class Network:
    def __init__(
            self,
            name            : str,
            rpc             : list,
            chain_id        : int,
            eip1559_support : bool,
            token           : str,
            explorer        : str,
            decimals        : int = 18,
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_support = eip1559_support
        self.token = token
        self.explorer = explorer
        self.decimals = decimals

    def __repr__(self):
        return f'{self.name}'

class AllNetwork:
    EthereumRPC = Network(
        name='Ethereum Sepolia',
        rpc=[
            'https://ethereum-sepolia-rpc.publicnode.com',
        ],
        chain_id=11155111,
        eip1559_support=True,
        token='ETH',
        explorer='https://sepolia.etherscan.io'
    )

    ArbitrumRPC = Network(
        name='Arbitrum Sepolia',
        rpc=[
            'https://endpoints.omniatech.io/v1/arbitrum/sepolia/public',
        ],
        chain_id=421614,
        eip1559_support=True,
        token='ETH',
        explorer='https://sepolia.arbiscan.io'
    )

    OptimismRPC = Network(
        name='Optimism Sepolia',
        rpc=[
            'https://endpoints.omniatech.io/v1/op/sepolia/public',
        ],
        chain_id=11155420,
        eip1559_support=True,
        token='ETH',
        explorer='https://sepolia-optimism.etherscan.io'
    )

    BaseRPC = Network(
        name='Base Sepolia',
        rpc=[
            'https://base-sepolia.blockpi.network/v1/rpc/public',
        ],
        chain_id=84532,
        eip1559_support=True,
        token='ETH',
        explorer='https://sepolia.basescan.org'
    )

    LineaRPC = Network(
        name='Linea Sepolia',
        rpc=[
            'https://linea-sepolia.blockpi.network/v1/rpc/public',
        ],
        chain_id=59141,
        eip1559_support=True,
        token='ETH',
        explorer='https://sepolia.lineascan.build'
    )

    BlastRPC = Network(
        name='Blast Sepolia',
        rpc=[
            'https://sepolia.blast.io',
        ],
        chain_id=168587773,
        eip1559_support=True,
        token='ETH',
        explorer='https://sepolia.blastscan.io'
    )

    PolygonRPC = Network(
        name='Polygon Amoy',
        rpc=[
            'https://polygon-amoy-bor-rpc.publicnode.com',
        ],
        chain_id=80002,
        eip1559_support=True,
        token='Matic',
        explorer='https://www.oklink.com/ru/amoy'
    )

    BSC_RPC = Network(
        name='BNB Chain Testnet',
        rpc=[
            'https://bsc-testnet.public.blastapi.io',
        ],
        chain_id=97,
        eip1559_support=False,
        token='BNB',
        explorer='https://testnet.bscscan.com'
    )

    AvalancheRPC = Network(
        name='Avalanche Testnet',
        rpc=[
            'https://rpc.ankr.com/avalanche_fuji',
        ],
        chain_id=43113,
        eip1559_support=True,
        token='AVAX',
        explorer='https://testnet.snowtrace.io'
    )

    B2networkRPC = Network(
        name='B2Network Testnet',
        rpc=[
            'https://b2-testnet.alt.technology',
        ],
        chain_id=1123,
        eip1559_support=True,
        token='BTC',
        explorer='https://testnet-explorer.bsquared.network'
    )

NETWORK_BYKEY = {
    1: AllNetwork.EthereumRPC,
    2: AllNetwork.ArbitrumRPC,
    3: AllNetwork.OptimismRPC,
    4: AllNetwork.BaseRPC,
    5: AllNetwork.LineaRPC,
    6: AllNetwork.BlastRPC,
    7: AllNetwork.PolygonRPC,
    8: AllNetwork.BSC_RPC,
    9: AllNetwork.AvalancheRPC,
    10: AllNetwork.B2networkRPC
}

