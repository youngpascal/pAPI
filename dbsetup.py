from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, UniqueConstraint
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///test.db', echo=True)
Base = declarative_base()

########################################################################

class Blocks(Base):
    """"""
    __tablename__ = "blocks"
    id = Column(Integer, unique=True)
    blockhash = Column(String, primary_key=True)
    blockheight = Column(Integer)

    #----------------------------------------------------------------------
    def __init__(self, blockhash, blockheight):
        """"""
        self.blockhash = blockhash
        self.blockheight = blockheight

class Decks(Base):
    """"""
    __tablename__ = "decks"
    txid = Column(String, primary_key=True)
    name = Column(String)
    issuer = Column(String)
    proto = Column(String)

    #Relationships
    blocks_hash = Column(String, ForeignKey('blocks.blockhash'))
    assets = relationship("Blocks", backref="decks")
    
    #----------------------------------------------------------------------
    def __init__(self, txid, name, issuer, blockhash, proto):
        """"""
        self.txid = txid
        self.name = name
        self.issuer = issuer
        self.blocks_hash = blockhash
        self.proto = proto

class Cards(Base):
    """"""
    __tablename__ = "cards"
    id = Column(String, primary_key=True) #concatenate txid + blockseq 
    txid = Column(String)
    cardseq = Column(Integer)
    receiver = Column(String)
    sender = Column(String)
    amount = Column(Integer)
    blockhash = Column(String)
    blockheight = Column(Integer)
    blockseq = Column(String)
    proto = Column(String)

    #relationships
    decks_id = Column(String, ForeignKey('decks.txid'))
    assets = relationship("Decks", backref="cards")
    
    #----------------------------------------------------------------------
    def __init__(self, id, txid, cardseq, receiver, sender, amount, blockhash, blockheight, blockseq, proto, deck_id):
        """"""
        self.id = id
        self.txid = txid
        self.cardseq = cardseq
        self.receiver = receiver
        self.sender = sender
        self.amount = amount
        self.blockhash = blockhash
        self.blockheight = blockheight
        self.blockseq = blockseq
        self.proto = proto
        self.decks_id = deck_id

# create tables
Base.metadata.create_all(engine)
