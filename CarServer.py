#from xmlrpc.server import SimpleXMLRPCServer # Python 3
#from xmlrpc.server import SimpleXMLRPCRequestHandler # Python 3
from SimpleXMLRPCServer import SimpleXMLRPCServer # Python 2
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler # Python 2
import pandas as pd
import sys
from pymongo import MongoClient

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/car',)

# Create car server
server = SimpleXMLRPCServer(('192.168.1.26', 55503), allow_none=True)
server.register_introspection_functions()

class CarFunctions:
        
    def __init__(self): #, client, db, collection, res_count
        try: # to connect to the MongoDB server
            self.client = MongoClient('192.168.1.28', 27017, 
                                      username='root', 
                                      password='B6YTUOng2ScO')
            self.db = self.client.Vacation # get database from client
            self.collection = self.db.Cars # get collection from db
            self.reservations = self.db.Reservations # get reservations from db
            self.res_count = self.reservations.estimated_document_count() # reservations in db
            self.res_tbl_cols = ['ResID','Car_ID','Name','FromDate','ToDate']
        except:
            print('COULD NOT CONNECT TO MONGODB')
            sys.exit()
            
    # Format db retrieval
    def FormatDB(self, db_type, cols):
        df = pd.DataFrame(list(db_type))
        df = df[cols+['_id']] # reorder columns; _id used for deletion
        df.dropna(subset=[self.res_tbl_cols[1]], inplace=True) # remove NaNs
        return df
    
    # Get list of cars
    def GetList(self):
        print(' In the GetList function')
        cars = self.FormatDB(self.collection.find(),
                         ['Car_ID','Company','Location',
                          'Rate','BookedYN'])
        print(' ========================')
        return cars.drop(['_id'], axis=1).to_string(index=False)
        
    # Get list of reservations
    def GetReservationList(self):
        print(' In the GetReservationList function')
        res_tbl = self.FormatDB(self.reservations.find(),
                                 self.res_tbl_cols)
        print(' ========================')
        return res_tbl.drop(['_id'], axis=1).to_string(index=False)

	# Create a reservation
    def AddReservation(self, carID, Name, FromDate, ToDate):
        
       print(' In the AddReservation function')
       self.res_count = self.res_count + 1
       try: # to update the car record
           self.collection.update_one({'Car_ID':carID}, 
                                  {'$set':{'BookedYN':'Y'}})   
           new_res = {'ResID':self.res_count, 'Car_ID':carID, 'Name':Name,
                      'FromDate':FromDate, 'ToDate':ToDate}
           self.reservations.insert(new_res) # add to db

           print('\nNew reservation added to Cars\n')
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
        
        try: # to update the car record
            res_tbl = self.FormatDB(self.reservations.find(),
                                     self.res_tbl_cols)
            carID = res_tbl.loc[(res_tbl.ResID == ResID) & 
                                (res_tbl.Car_ID.isnull() == False), 
                                'Car_ID'].iloc[0]
            
            # Update Y/N in Cars
            if res_tbl.Car_ID[res_tbl.Car_ID==carID].count() == 1:
                self.collection.update({'Car_ID':carID}, 
                                       {'$set':{'BookedYN':'N'}})
                
            # Remove reservation
            removed = res_tbl[(res_tbl.ResID == ResID) & 
                              (res_tbl.Car_ID.isnull() == False)]
            self.reservations.delete_one({'_id':removed['_id'].iloc[0]})
        
            print('\nReservation deleted from Cars\n')
            print(' ========================')
            return removed.drop(['_id'], axis=1).to_string(index=False)
        except:
            print('ERROR IN DELETING RESERVATION')
            sys.exit()            

server.register_instance(CarFunctions()) # instanciate

print('CarServer is ready to accept calls....')

# Run the server's main loop
server.serve_forever()

#%% Removed

#def dtConvert(df, colList):
#    for c in colList:
#        df[c] = pd.to_datetime(df[c], errors='coerce')
#dtConvert(cars, ['From', 'To'])

## Create initial list of car availability
#cars = pd.DataFrame([
#    ['1','AA','Chicago','LA', 'N'], 
#    ['2','AA','Chicago','San Francisco', 'N'], 
#    ['3','UA','Chicago','New York', 'N'], 
#    ['4','UA','Chicago','Newark', 'N'],
#    ['5','Delta','Chicago','Salt Lake City', 'N']],
#    columns = ['Car_ID','CarName','FromCity','ToCity','Booked?'])
#
#cols = ['ResID','carID','Name', 'FromDate', 'ToDate']
#Reservations = pd.DataFrame(columns=cols)
#res_count = 0

#    # Upate car booking Y/N
#    def UpdateCarBooking(self, carID, add_res):
#        global cars
#        if add_res == True:
#            cars['Booked?'] = np.where(cars.Car_ID == carID, 'Y', 
#                  cars['Booked?'])
#        else:
#            cars['Booked?'] = np.where(cars.Car_ID == carID, 'N', 
#                  cars['Booked?'])
#        return True

#        # Update Y/N in cars
#        if Reservations.carID[Reservations.carID==carID].count() == 1:
#            self.UpdateCarBooking(carID, False)
#            
#        # Remove reservation
#        Removed = Reservations[Reservations.ResID == ResID]
#        Reservations = Reservations[Reservations.ResID != ResID]

#        cars = pd.DataFrame(list(self.collection.find()))
#        cars = cars.drop(['_id'], axis=1)
#        cols = ['Car_ID','Company','Location','Rate','BookedYN']
#        cars = cars[cols] # reorder columns