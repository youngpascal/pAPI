from flask import jsonify, Flask, request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from load import *

# Setup database engine and connect
engine = create_engine('sqlite:///data/papi.db')
conn = engine.connect()
# Setup Flask application
app = Flask(__name__)
# Setup Session
Session = sessionmaker(bind=engine)
s = Session()
# Setup CORS extension to allow the content-type header
CORS(app, resources = r'/api/*')

@app.route('/api/')
# Show PeerAssets version information
def versionInfo():
    return jsonify({'name': "PeerAssets", "Version": 1.0})

@app.route('/api/v1/decks')
# List all production decks
def productionAssets():
    condition = "select * from decks"
    decks = []
    result = conn.execute(condition).fetchall()
    for a in result:
        decks.append( dict(a) )
    return jsonify(decks)

@app.route('/api/v1/decks/cards')
# List all production cards
def _productionCards():
    condition = ("select d.name AS [Deck Name],d.id as [Deck ID], c.blocknum AS [Card Blockheight], c.blockseq AS [Card Blocksequence], "
                "c.cardseq AS [Card Sequence], c.sender AS [Sender], c.Receiver AS [Receiver], c.amount AS [Card Amount], " 
                "c.id AS [Card TxiD], c.ctype AS [Card Type]"
                "from decks d inner join cards c on c.decks_id = d.txid "
                "order by blockheight ASC, blockseq ASC, cardseq ASC")
    cards = []
    result = conn.execute(condition).fetchall()
    for a in result:
        cards.append( dict(a) )
    return jsonify(cards)

@app.route('/api/v1/cards/<string:deck_id>', methods=['GET'])
# List all production cards
def productionCards(deck_id):
    condition = ("select blocknum, blockseq, cardseq, sender, " +
                "receiver, amount, id, ctype from cards " +
                "where decks_id = '{}' ".format(deck_id) + 
                "order by blocknum ASC, blockseq ASC, cardseq ASC")
    cards = []
    res = conn.execute(condition).fetchall()
    for a in res:
        cards.append( dict(a) )

    condition = ("select name, issuer, txid, issue_mode," +
                "decimals from decks where txid = '{}' ".format(deck_id))

    res = dict(conn.execute(condition).fetchone())
    res["cards"] = cards
    return jsonify(res)

@app.route('/api/v1/decks/issuer/<string:issuer>', methods=['GET'])
# List all assets by issuer
def issuerAssets(issuer):
    condition = "select * from decks where issuer = '{}' ".format(issuer)
    decks = []
    result = conn.execute(condition).fetchall()
    for a in result:
        decks.append( dict(a) )
    return jsonify(decks)

@app.route('/api/v1/decks/name/<string:name>', methods=['GET'])
# List decks with specific name
def nameAssets(name):
    #condition = "select * from decks where name = '{}' ".format(name)
    condition = ("select d.name AS [Deck Name], c.blockheight AS [Card Blockheight], c.blockseq AS [Card Blocksequence], "
                "c.cardseq AS [Card Sequence], c.sender AS [Sender], c.Receiver AS [Receiver], c.amount AS [Card Amount], " 
                "c.id AS [Card TxiD], c.blockhash AS [Card Blockhash] "
                "from decks d inner join cards c on c.decks_id = d.txid WHERE d.name = '{}' "
                "order by blocknum ASC, blockseq ASC, cardseq ASC").format(name)
    decks = []
    result = conn.execute(condition).fetchall()
    for a in result:
        decks.append( dict(a) )
    return jsonify(decks)

if __name__ == "__main__":
    app.run( host="0.0.0.0", port=5000)
