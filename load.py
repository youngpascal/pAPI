import pypeerassets as pa
from binascii import hexlify, unhexlify
from flask import session
from dbsetup import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

engine = create_engine('sqlite:///test.db', echo=False)
node = pa.RpcNode(testnet=True)


def loadData():

    # Bind session to engine
    Session = sessionmaker(bind=engine)
    s = Session()

    # Load DeckSpawns

    txids = [txid for txid in pa.find_deck_spawns(node)]
    deck_spawns = [node.getrawtransaction(txid, 1) for txid in txids]

    for txid, raw_tx in zip(txids, deck_spawns):
        try:
            # Validate Deck creation transaction paid to P2TH address
            pa.validate_deckspawn_p2th(node, raw_tx)
        except:
            continue
        try:
            # Read OP_RETURN data in valid transaction
            protobuf = pa.read_tx_opreturn(raw_tx)
        except KeyError:
            continue

        try:
            # Parse OP_RETURN protobuf data
            d = pa.parse_deckspawn_metainfo(protobuf)
        except AssertionError:
            continue

        try:
            # Find Issuer
            issuer = pa.find_tx_sender(node, raw_tx)
            # Load database object from dbsetup
            D = Decks( txid, d["name"], issuer, raw_tx["blockhash"], d["issue_mode"][0], d["number_of_decimals"] )
            # Load values then pass into Protobuf Deck Object
            d["production"] = True
            d["issuer"] = issuer
            d["asset_id"] = txid
            d["time"] = raw_tx["blocktime"]
            d["network"] = node.network
            Deck = pa.protocol.Deck(**d)
            print("Deck: " + Deck.name + " sucessfully loaded")        

        except Exception as e:
            print(e)
            continue

        try:
            # Load Deck P2TH WIF into daemon "accounts" using deck txid as label. 
            pa.load_deck_p2th_into_local_node(node, Deck)
        except Exception as e:
            print(e)
        
        loadCards(s, Deck)
        print("--Cards:" + Deck.name + " cards sucessfully loaded.")

        try:
            # Add Data to engine session and commit to database
            s.add(D)
            s.commit()
        except IntegrityError:
            s.rollback()
            continue

def loadCards(s, Deck):
    # Create a list containing rawtx's of each card event
    cards = [node.getrawtransaction(c["txid"],1) for c in  node.listtransactions(Deck.asset_id)]
    _cards = []
    # Iterate through and validate each card event
    for c in cards:
        try:
            pa.validate_card_transfer_p2th(Deck, c)
        except:
            continue
        protobuf = pa.read_tx_opreturn(c)
        vouts = c["vout"]
        sender = pa.find_tx_sender(node,c)
        blockseq = pa.tx_serialization_order(node, c["blockhash"], c["txid"])
        blocknum = node.getblock(c["blockhash"])["height"]
        
        try:
            pcard = pa.postprocess_card( protobuf, c, sender, vouts, blockseq, blocknum, Deck )
        except:
            continue
        try:
            for pc in pcard:
                id = c["txid"] + str(pc["cardseq"])
                C = Cards(id, pc["txid"], pc["cardseq"], pc["receiver"][0], sender, pc["amount"][0], blocknum, blockseq, Deck.asset_id )
                try:
                    CardObject = pa.protocol.CardTransfer(Deck, pc["receiver"], pc["amount"],txid =pc["txid"], blocknum=blocknum, cardseq=pc["cardseq"], blockseq=blockseq)
                    _cards.append(CardObject)
                except Exception as e:
                    print(e)
                s.add(C)
                s.commit()
        except Exception as e:
            s.rollback()

loadData()