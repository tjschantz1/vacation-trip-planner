#from xmlrpc.server import SimpleXMLRPCServer # Python 3
#from xmlrpc.server import SimpleXMLRPCRequestHandler # Python 3
from SimpleXMLRPCServer import SimpleXMLRPCServer # Python 2
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler # Python 2
import pandas as pd
import sys
from pymongo import MongoClient

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/hotel',)

# Create hotel server
server = SimpleXMLRPCServer(('192.168.1.25', 55502), allow_none=True)
server.register_introspection_functions()

class HotelFunctions:
        
    def __init__(self): #, client, db, collection, res_count
        try: # to connect to the MongoDB server
            self.client = MongoClient('192.168.1.28', 27017, 
                                      username='root', 
                                      password='B6YTUOng2ScO')
            self.db = self.client.Vacation # get database from client
            self.collection = self.db.Hotels # get collection from db
            self.reservations = self.db.Reservations # get reservations from db
            self.res_count = self.reservations.estimated_document_count() # reservations in db
            self.res_tbl_cols = ['ResID','Hotel_ID','Name','FromDate','ToDate']
        except:
            print('COULD NOT CONNECT TO MONGODB')
            sys.exit()
            
    # Format db retrieval
    def FormatDB(self, db_type, cols):
        df = pd.DataFrame(list(db_type))
        df = df[cols+['_id']] # reorder columns; _id used for deletion
        df.dropna(subset=[self.res_tbl_cols[1]], inplace=True) # remove NaNs
        return df
    
    # Get list of hotels
    def GetList(self):
        print(' In the GetList function')  
        hotels = self.FormatDB(self.collection.find(),
                         ['Hotel_ID','Hotel_Name','City',
                          'From','To','BookedYN'])
        print(' ========================')
        return hotels.drop(['_id'], axis=1).to_string(index=False)
        
    # Get list of reservations
    def GetReservationList(self):
        print(' In the GetReservationList function')
        res_tbl = self.FormatDB(self.reservations.find(),
                                self.res_tbl_cols)
        print(' ========================')
        return res_tbl.drop(['_id'], axis=1).to_string(index=False)

	# Create a reservation
    def AddReservation(self, hotelID, Name, FromDate, ToDate):
        
       print(' In the AddReservation function')
       self.res_count = self.res_count + 1
       try: # to update the hotel record
           self.collection.update_one({'Hotel_ID':hotelID}, 
                                  {'$set':{'BookedYN':'Y'}})   
           new_res = {'ResID':self.res_count, 'Hotel_ID':hotelID, 'Name':Name,
                      'FromDate':FromDate, 'ToDate':ToDate}
           self.reservations.insert(new_res) # add to db

           print('\nNew reservation added to Hotels\n')
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
        
        try: # to update the hotel record
            res_tbl = self.FormatDB(self.reservations.find(),
                                     self.res_tbl_cols)
            hotelID = res_tbl.loc[(res_tbl.ResID == ResID) & 
                                  (res_tbl.Hotel_ID.isnull() == False), 
                                  'Hotel_ID'].iloc[0]
            
            # Update Y/N in Hotels
            if res_tbl.Hotel_ID[res_tbl.Hotel_ID==hotelID].count() == 1:
                self.collection.update({'Hotel_ID':hotelID}, 
                                       {'$set':{'BookedYN':'N'}})
                
            # Remove reservation
            removed = res_tbl[(res_tbl.ResID == ResID) & 
                              (res_tbl.Hotel_ID.isnull() == False)]
            self.reservations.delete_one({'_id':removed['_id'].iloc[0]})
        
            print('\nReservation deleted from Hotels\n')
            print(' ========================')
            return removed.drop(['_id'], axis=1).to_string(index=False)
        except:
            print('ERROR IN DELETING RESERVATION')
            sys.exit()            

server.register_instance(HotelFunctions()) # instanciate

print('HotelServer is ready to accept calls....')

# Run the server's main loop
server.serve_forever()

#%% Removed

#def dtConvert(df, colList):
#    for c in colList:
#        df[c] = pd.to_datetime(df[c], errors='coerce')
#dtConvert(hotels, ['From', 'To'])

## Create initial list of hotel availability
#hotels = pd.DataFrame([
#    ['1','AA','Chicago','LA', 'N'], 
#    ['2','AA','Chicago','San Francisco', 'N'], 
#    ['3','UA','Chicago','New York', 'N'], 
#    ['4','UA','Chicago','Newark', 'N'],
#    ['5','Delta','Chicago','Salt Lake City', 'N']],
#    columns = ['Hotel_ID','HotelName','FromCity','ToCity','Booked?'])
#
#cols = ['ResID','hotelID','Name', 'FromDate', 'ToDate']
#Reservations = pd.DataFrame(columns=cols)
#res_count = 0

#    # Upate hotel booking Y/N
#    def UpdateHotelBooking(self, hotelID, add_res):
#        global hotels
#        if add_res == True:
#            hotels['Booked?'] = np.where(hotels.Hotel_ID == hotelID, 'Y', 
#                  hotels['Booked?'])
#        else:
#            hotels['Booked?'] = np.where(hotels.Hotel_ID == hotelID, 'N', 
#                  hotels['Booked?'])
#        return True

#        # Update Y/N in hotels
#        if Reservations.hotelID[Reservations.hotelID==hotelID].count() == 1:
#            self.UpdateHotelBooking(hotelID, False)
#            
#        # Remove reservation
#        Removed = Reservations[Reservations.ResID == ResID]
#        Reservations = Reservations[Reservations.ResID != ResID]

#        hotels = pd.DataFrame(list(self.collection.find()))
#        hotels = hotels.drop(['_id'], axis=1)
#        cols = ['Hotel_ID','Hotel_Name','City','From','To','BookedYN']
#        hotels = hotels[cols] # reorder columns