#Parse blockchain for relevant blocks
#and gather decks and their associated cards.
#Perform validity checks then sort into
#SQLite table for quick indexing.

#TODO: Check for rerun so it doesnt re-populate tables 

import pypeerassets as pa
from binascii import hexlify, unhexlify
from flask import session
from dbsetup import *
from sqlalchemy.orm import sessionmaker
from pprint import pprint

engine = create_engine('sqlite:///test.db', echo=False)
node = pa.provider.rpcnode.RpcNode(testnet=True)

#Main sorting and table insertion
def findDecksAndCards():
    Session = sessionmaker(bind=engine)
    s = Session()
    txs = [tx for tx in pa.find_deck_spawns(node)]
    for tx in txs:
            raw_tx = node.getrawtransaction(tx,1)
            try:
                pa.validate_deckspawn_p2th(node, raw_tx)
            except AssertionError:
                continue

            blockhash = raw_tx['blockhash']
            issuer = pa.find_tx_sender(node, raw_tx)
            proto = pa.read_tx_opreturn(raw_tx)

            try:
                data = pa.parse_deckspawn_metainfo(proto)
            except AssertionError:
                continue

            deck_list = Decks(tx , data['name'], issuer, blockhash, hexlify(proto).decode())

            #TODO: Find the source of the Truncated Message
            #      Protobuf error
            try:
                deck_object = pa.find_deck(node, tx)[0]
                for cards in findCards(s, tx, deck_object):
                    s.add(cards)   
            except Exception as e:
                print(e)
            s.add(deck_list)

            s.commit()

#Helper functions#
def deckParser(raw_tx):
    try:
        pa.validate_deckspawn_p2th(node, raw_tx, prod=True)
        data = pa.parse_deckspawn_metainfo(pa.read_tx_opreturn(raw_tx))
        if data:

            d = data
            d["asset_id"] = raw_tx["txid"]
            try:
                d["time"] = raw_tx["blocktime"]
            except KeyError:
                d["time"] = 0
            d["issuer"] = pa.find_tx_sender(node, raw_tx)
            d["network"] = node.network
            d["production"] = True
            return pa.protocol.Deck(**d)

    except (AssertionError, TypeError) as err:
        pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as th:
        for result in th.map(deck_parser, deck_spawns):
            if result:
                yield result


def getInfo():
    return node.getinfo()

def getProto(assets):
    import json
    assets = [ pa.parse_deckspawn_metainfo(unhexlify(asset['proto'].encode())) for asset in assets]
    n_assets = []
    for asset in assets:
        asset['asset_specific_data'] = hexlify(asset['asset_specific_data']).decode()
        n_assets.append(json.dumps(asset,indent=4,sort_keys=True))
    return n_assets

def findCards(session, deck_id, deck):
    try:
        pa.load_deck_p2th_into_local_node(node, deck)
    except:
        pass
    cards = [card.__dict__ for card in pa.find_card_transfers(node, deck)]
    cards_list = []
    for c in cards:  
        txid = c["txid"]
        cardseq = c["cardseq"]
        id = txid + str(c["cardseq"])
        receiver = c["receiver"][0]
        sender = c["sender"]
        amount = c["amount"][0]
        blockhash = c["blockhash"]
        blockheight = c["blocknum"]
        blockseq = c["blockseq"]
        raw_tx = node.getrawtransaction(txid,1)
        proto = pa.read_tx_opreturn(raw_tx) 
        cards = Cards(id, txid, cardseq, receiver, sender, amount, blockhash, blockheight, blockseq, hexlify(proto).decode(), deck_id)
        cards_list.append(cards)
        
    return cards_list

#End of source#
findDecksAndCards()

 