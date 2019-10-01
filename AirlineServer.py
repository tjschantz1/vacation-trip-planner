#from xmlrpc.server import SimpleXMLRPCServer # Python 3
#from xmlrpc.server import SimpleXMLRPCRequestHandler # Python 3
from SimpleXMLRPCServer import SimpleXMLRPCServer # Python 2
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler # Python 2
import pandas as pd
import sys
from pymongo import MongoClient

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/airline',)

# Create airline server
server = SimpleXMLRPCServer(('192.168.1.24', 55501), allow_none=True)
server.register_introspection_functions()

class AirlineFunctions:
        
    def __init__(self): #, client, db, collection, res_count
        try: # to connect to the MongoDB server
            self.client = MongoClient('192.168.1.28', 27017, 
                                      username='root', 
                                      password='B6YTUOng2ScO')
            self.db = self.client.Vacation # get database from client
            self.collection = self.db.Airlines # get collection from db
            self.reservations = self.db.Reservations # get reservations from db
            self.res_count = self.reservations.estimated_document_count() # reservations in db
            self.res_tbl_cols = ['ResID','Airline_ID','Name','FromDate','ToDate']
        except:
            print('COULD NOT CONNECT TO MONGODB')
            sys.exit()
    
    # Format db retrieval
    def FormatDB(self, db_type, cols):
        df = pd.DataFrame(list(db_type))
        df = df[cols+['_id']] # reorder columns; _id used for deletion
        df.dropna(subset=[self.res_tbl_cols[1]], inplace=True) # remove NaNs
        return df
    
    # Get list of airlines
    def GetList(self):
        print(' In the GetList function')  
        airlines = self.FormatDB(self.collection.find(),
                                 ['Airline_ID','AirlineName','FromCity',
                                  'ToCity','BookedYN'])
        print(' ========================')
        return airlines.drop(['_id'], axis=1).to_string(index=False)
        
    # Get list of reservations
    def GetReservationList(self):
        print(' In the GetReservationList function')
        res_tbl = self.FormatDB(self.reservations.find(),
                                 self.res_tbl_cols)
        print(' ========================')
        return res_tbl.drop(['_id'], axis=1).to_string(index=False)

	# Create a reservation
    def AddReservation(self, airlineID, Name, FromDate, ToDate):
        
       print(' In the AddReservation function')
       self.res_count = self.res_count + 1
       try: # to update the airline record
           self.collection.update_one({'Airline_ID':airlineID}, 
                                  {'$set':{'BookedYN':'Y'}})   
           new_res = {'ResID':self.res_count, 'Airline_ID':airlineID, 'Name':Name,
                      'FromDate':FromDate, 'ToDate':ToDate}
           self.reservations.insert(new_res) # add to db

           print('\nNew reservation added to Airlines\n')
           print(' ========================')
           return True
       except:
           print('ERROR IN ADDING RESERVATION')
           sys.exit()

    # Function to remove a reservation
    def RemoveReservation(self, ResID):
        
        # Server partition handler (user did not input ResID for deletion)
        if ResID == False: ResID = self.res_count

        print(' In the RemoveReservation function')  
        
        try: # to update the airline record
            res_tbl = self.FormatDB(self.reservations.find(),
                                     self.res_tbl_cols)
            airlineID = res_tbl.loc[(res_tbl.ResID == ResID) & 
                                    (res_tbl.Airline_ID.isnull() == False), 
                                   'Airline_ID'].iloc[0]
            
            # Update Y/N in Airlines
            if res_tbl.Airline_ID[res_tbl.Airline_ID==airlineID].count() == 1:
                self.collection.update({'Airline_ID':airlineID}, 
                                       {'$set':{'BookedYN':'N'}})
                
            # Remove reservation
            removed = res_tbl[(res_tbl.ResID == ResID) & 
                              (res_tbl.Airline_ID.isnull() == False)]
            self.reservations.delete_one({'_id':removed['_id'].iloc[0]})
        
            print('\nReservation deleted from Airlines\n')
            print(' ========================')
            return removed.drop(['_id'], axis=1).to_string(index=False)
        except:
            print('ERROR IN DELETING RESERVATION')
            sys.exit()            

server.register_instance(AirlineFunctions()) # instanciate

print('AirlineServer is ready to accept calls....')

# Run the server's main loop
server.serve_forever()