from flask import jsonify, Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup database engine and connect
engine = create_engine('sqlite:///data/papi.db')
conn = engine.connect()
# Setup Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# Setup Session
Session = sessionmaker(bind=engine)
s = Session()


@app.route('/papi')
# Show PeerAssets version information
def versionInfo():
    return jsonify({'name': "PeerAssets", "Version": 1.0})

@app.route('/papi/assets')
# List all production decks
def productionAssets():
    condition = "select * from decks"
    decks = []
    result = conn.execute(condition).fetchall()
    for a in result:
        decks.append( dict(a) )
    return jsonify(decks)

@app.route('/papi/assets/cards')
# List all production cards
def _productionCards():
    condition = ("select d.name AS [Deck Name],d.txid as [Deck ID], c.blocknum AS [Card Blockheight], c.blockseq AS [Card Blocksequence], "
                "c.cardseq AS [Card Sequence], c.sender AS [Sender], c.Receiver AS [Receiver], c.amount AS [Card Amount], " 
                "c.id AS [Card TxiD], c.ctype AS [Card Type]"
                "from decks d inner join cards c on c.decks_id = d.txid "
                "order by blockheight ASC, blockseq ASC, cardseq ASC")
    cards = []
    result = conn.execute(condition).fetchall()
    for a in result:
        cards.append( dict(a) )
    return jsonify(cards)

@app.route('/papi/cards/<string:deck_id>')
# List all production cards
def productionCards(deck_id):
    condition = ("select d.name AS [Deck Name],d.txid as [Deck ID], c.blocknum AS [Card Blockheight], c.blockseq AS [Card Blocksequence]," + 
                "c.cardseq AS [Card Sequence], c.sender AS [Sender], c.Receiver AS [Receiver], c.amount AS [Card Amount]," + 
                "c.id AS [Card TxiD], c.ctype AS [Card Type] from decks d inner join cards c on c.decks_id = d.txid where c.decks_id = '{}' ".format(deck_id) + 
                "order by blocknum ASC, blockseq ASC, cardseq ASC")
    cards = []
    result = conn.execute(condition).fetchall()
    for a in result:
        cards.append( dict(a) )
    return jsonify(cards)

@app.route('/papi/assets/issuer/<string:issuer>', methods=['GET'])
# List all assets by issuer
def issuerAssets(issuer):
    condition = "select * from decks where issuer = '{}' ".format(issuer)
    decks = []
    result = conn.execute(condition).fetchall()
    for a in result:
        decks.append( dict(a) )
    return jsonify(decks)

@app.route('/papi/assets/name/<string:name>', methods=['GET'])
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