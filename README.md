# pAPI
A PeerAssets API that provides data pertaining to Decks and their respective Card and Vote transactions.
pAPI uses pypeerassets coupled with flask to provide an API that minimally indexes the blockchain while gathering application specific transactions.

### Supported Database Types
Due to the use of SQLAlchemy DBAPI the following database types are supported:
  * PostgreSQL
  * MYSQL 
  * sqlite  
  * Oracle 
  * Miscrosoft SQL Server

## Before running api.py (Python 3.x)
Currently there is no process to continually sync the database with the subscribed decks. This is being worked on
so while testing please load the database with data by running "load.py" in the data directory. 
### Load Data
> python load.py
### Run server
> python api.py

Defaults to run on port 5000

### Examples
#### Lists all production decks
> 127.0.0.1:5000/api/v1/decks
#### Lists all decks issued by issuer
> 127.0.0.1:5000/api/v1/decks/<**issuer**>
#### Lists all cards for a given deck
> 127.0.0.1:5000/api/v1/cards/<**deck_id**>
