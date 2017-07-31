from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, UniqueConstraint
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///test.db', echo=True)
Base = declarative_base()

########################################################################

class Decks(Base):
    """"""
    __tablename__ = "decks"
    txid = Column(String, primary_key=True)
    name = Column(String)
    issuer = Column(String)
    issue_mode = Column(String)
    decimals = Column(Integer)

    blocks_hash = Column(String)
    
    #----------------------------------------------------------------------
    def __init__(self, txid, name, issuer, blockhash, issue_mode, decimals):
        """"""
        self.txid = txid
        self.name = name
        self.issuer = issuer
        self.blocks_hash = blockhash
        self.issue_mode = issue_mode
        self.decimals = decimals

class Cards(Base):
    """"""
    __tablename__ = "cards"
    id = Column(String, primary_key=True) #concatenate txid + blockseq 
    txid = Column(String)
    cardseq = Column(Integer)
    receiver = Column(String)
    sender = Column(String)
    amount = Column(Integer)
    blocknum = Column(Integer)
    blockseq = Column(String)

    #relationships
    decks_id = Column(String, ForeignKey('decks.txid'))
    assets = relationship("Decks", backref="cards")
    
    #----------------------------------------------------------------------
    def __init__(self, id, txid, cardseq, receiver, sender, amount, blocknum, blockseq, deck_id):
        """"""
        self.id = id
        self.txid = txid
        self.cardseq = cardseq
        self.receiver = receiver
        self.sender = sender
        self.amount = amount
        self.blocknum = blocknum
        self.blockseq = blockseq
        self.decks_id = deck_id
        
# create tables
Base.metadata.create_all(engine)
