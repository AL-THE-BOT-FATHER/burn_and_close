from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solders.keypair import Keypair #type: ignore
from solders.pubkey import Pubkey #type: ignore
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import burn, close_account, BurnParams, CloseAccountParams
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price #type: ignore

client = Client("")
signer = Keypair.from_base58_string("")
token_accounts = [""]

def burn_and_close_account(token_account: str):
    token_account_pubkey = Pubkey.from_string(token_account)
    print("Token Account:", token_account)
    
    try:
        token_balance = int(client.get_token_account_balance(token_account_pubkey).value.amount)
        print("Token Balance:", token_balance)
    except:
        token_balance = 0
        print("Token Balance:", token_balance)

    owner = signer.pubkey()
    recent_blockhash = client.get_latest_blockhash().value.blockhash
    transaction = Transaction(recent_blockhash=recent_blockhash, fee_payer=signer.pubkey())

    if token_balance > 0:
        mint_str = client.get_account_info_json_parsed(token_account_pubkey).value.data.parsed['info']['mint']
        print("Mint:", mint_str)
        mint = Pubkey.from_string(mint_str)
        burn_instruction = burn(
            BurnParams(
                program_id=TOKEN_PROGRAM_ID,
                account=token_account_pubkey,
                mint=mint,
                owner=owner,
                amount=token_balance
            )
        )
        
        transaction.add(burn_instruction)

    close_account_instruction = close_account(
        CloseAccountParams(
            program_id=TOKEN_PROGRAM_ID,
            account=token_account_pubkey,
            dest=owner,
            owner=owner
        )
    )
    transaction.add(set_compute_unit_price(100_000))
    transaction.add(set_compute_unit_limit(100_000))
    transaction.add(close_account_instruction)
    transaction.sign(signer)
    txn_sig = client.send_transaction(transaction, signer, opts=TxOpts(skip_preflight=True)).value
    print(txn_sig)

for token_account in token_accounts:
    try:
        burn_and_close_account(token_account)
    except Exception as e:
        print(e)
