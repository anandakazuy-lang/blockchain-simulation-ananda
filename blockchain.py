import hashlib
import json
import time


class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }

        encoded_data = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(encoded_data).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 3
        self.mining_reward = 50

        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(
            0,
            [
                {"sender": "System", "receiver": "Alice", "amount": 500}
            ],
            "0"
        )

        self.chain.append(genesis)

    def get_latest_block(self):
        return self.chain[-1]

    def get_balances(self, include_pending=False):
        balances = {}

        for block in self.chain:
            for transaction in block.transactions:
                sender = transaction["sender"]
                receiver = transaction["receiver"]
                amount = transaction["amount"]

                if sender != "System":
                    balances[sender] = balances.get(sender, 0) - amount

                balances[receiver] = balances.get(receiver, 0) + amount

        if include_pending:
            for transaction in self.pending_transactions:
                sender = transaction["sender"]
                receiver = transaction["receiver"]
                amount = transaction["amount"]

                balances[sender] = balances.get(sender, 0) - amount
                balances[receiver] = balances.get(receiver, 0) + amount

        return balances

    def create_transaction(self, sender, receiver, amount):
        if sender == receiver:
            raise ValueError("Pengirim dan penerima tidak boleh sama.")

        if amount <= 0:
            raise ValueError("Jumlah coin harus lebih besar dari 0.")

        balances = self.get_balances(include_pending=True)
        sender_balance = balances.get(sender, 0)

        if amount > sender_balance:
            raise ValueError(
                f"Saldo {sender} tidak cukup. Saldo tersedia: {sender_balance} coin."
            )

        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        }

        self.pending_transactions.append(transaction)

        return transaction

    def mine_pending_transactions(self, miner):
        if not self.pending_transactions:
            raise ValueError("Tidak ada transaksi untuk ditambang.")

        reward_transaction = {
            "sender": "System",
            "receiver": miner,
            "amount": self.mining_reward
        }

        transactions = self.pending_transactions.copy()
        transactions.append(reward_transaction)

        new_block = Block(
            len(self.chain),
            transactions,
            self.get_latest_block().hash
        )

        new_block.mine_block(self.difficulty)

        self.chain.append(new_block)
        self.pending_transactions = []

        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                return False

        return True