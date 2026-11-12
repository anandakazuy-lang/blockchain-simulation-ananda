from flask import Flask, render_template, request, redirect, url_for, flash
from blockchain import Blockchain

app = Flask(__name__)
app.secret_key = "blockchain-secret-key"

blockchain = Blockchain()

users = ["Alice", "Bob", "Charlie", "David", "Eve"]
miners = ["Miner1", "Miner2", "Miner3"]


@app.route("/")
def index():
    return render_template(
        "index.html",
        users=users,
        miners=miners,
        chain=blockchain.chain,
        pending=blockchain.pending_transactions,
        valid=blockchain.is_chain_valid()
    )


@app.route("/transaction", methods=["POST"])
def transaction():
    sender = request.form.get("sender")
    receiver = request.form.get("receiver")
    amount = request.form.get("amount", type=float)

    if sender not in users or receiver not in users:
        flash("Nama pengguna tidak valid.", "error")
        return redirect(url_for("index"))

    if amount is None:
        flash("Masukkan jumlah coin yang valid.", "error")
        return redirect(url_for("index"))

    try:
        blockchain.create_transaction(sender, receiver, amount)
        flash("Transaksi berhasil ditambahkan!", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


@app.route("/mine", methods=["POST"])
def mine():
    miner = request.form.get("miner")

    if miner not in miners:
        flash("Miner tidak valid.", "error")
        return redirect(url_for("index"))

    try:
        block = blockchain.mine_pending_transactions(miner)
        flash(
            f"Block {block.index} berhasil ditambang! "
            f"{miner} menerima reward 50 coin.",
            "success"
        )
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    global blockchain
    blockchain = Blockchain()
    flash("Blockchain berhasil direset.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)