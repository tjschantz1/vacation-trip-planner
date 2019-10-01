# =============================================================================
# CPSC-55500 Week  Assignment - Vacation Trip RPC Client
# =============================================================================

import xmlrpc.client  # Python 3
import sys

res_dict = {} # captures completed res types for roll-back following server partition

#%% Main call
def main():    
    
    #Determine Server
    server_dict = {1:['http://192.168.1.24:55501','Airline','Departure','Return'],
                   2:['http://192.168.1.25:55502', 'Hotel','Check-in','Check-out'], 
                   3:['http://192.168.1.26:55503','Car Rental','Pick-up', 'Drop-off']}
    print('\n===============================================================')
    print('Welcome! Please select which reservation you wish to make\n')
    print(' 1 = Airline\n', '2 = Hotel\n', '3 = Car Rental\n')
    try:
        iResType = int(input('Enter the number of the reservation type: '))
        calledServer = xmlrpc.client.ServerProxy(server_dict[iResType][0])
        print("You've chosen", server_dict[iResType][1], 'Reservation')
        print('\nPlease indicate the action you wish to take\n')
        print(' 1 = Make a new reservation\n', '2 = Delete an existing reservation\n')
        iDeleteBool = int(input('Enter the number of the desired action: '))
        if iDeleteBool == 2: # start delete reservation logic
            try:
                print('\n', calledServer.GetReservationList())
                iResID = int(input('\nReservation ID you wish to delete: '))
                print('\n', calledServer.RemoveReservation(iResID))
                print('\n...Reservation Deleted Successfully')
            except:
                print('*** NO RESERVATION(S) FOUND TO DELETE ***')
        else: # start add new reservation logic
            AddNew(calledServer, server_dict, iResType)
        print('\n===============================================================')
    except:
        print('*** INCORRECT ENTRY RECEIVED ***')
    
#%% Add new reservation logic
def AddNew(calledServer, server_dict, iResType):
    cont_check = True
    while cont_check == True: # start loop & start error handler for server call
        try:
            #%% Get list of hotels/airlines/cars
            print('\n===============================================================')
            print('>>> Calling GetList (', server_dict[iResType][1], ')...\n')
            options = calledServer.GetList()
            print(options) 
            print('===============================================================\n')
            
            #%% Reserve a room/flight/vehicle
            print('===============================================================')
            print('>>> Calling AddReservation (', server_dict[iResType][1], ')...\n')
            iID = int(input(server_dict[iResType][1] + ' ID under which to book the reservation: '))
            iName = input('First and last name of reservation holder: ')
            iFromDate = input(server_dict[iResType][2] + ' date (mm/dd/yy): ')
            iToDate = input(server_dict[iResType][3] + ' date (mm/dd/yy): ')
            calledServer.AddReservation(iID, iName, iFromDate, iToDate)
            print('Reservation Added Successfully')
            print('===============================================================\n')
            
            #%% Display a list of reservations
            def display_res():
                print('===============================================================')
                print('>>> Calling GetReservationList (', server_dict[iResType][1], ')...\n')
                reservations = calledServer.GetReservationList()
                print(reservations) 
                print('===============================================================\n')
                
            display_res()
            
            #%% Update reservation/server dicts & insert pause
            res_dict[iResType] = server_dict[iResType]
            print('*** ' + server_dict[iResType][1] + 
                  'Reservation completed successfully. Press any key to continue. ***')
            del server_dict[iResType]
            sys.stdin.readline() # wait for keyboard stroke
            
            #%% Continue with next reservation type
            if bool(server_dict): # returns TRUE if not the last one
                iContBool = input('Continue with next reservation type (Y/N)? ')
                if iContBool == 'Y':
                    print('\n===============================================================')
                    print('Please select the next reservation you wish to make\n')
                    remaining_options = [str(str(k)+' = '+x) for k,v in server_dict.items() 
                                        for i,x in enumerate(server_dict[k])
                                        if i % 4 == 1]
                    print('\n'.join(remaining_options)+'\n')
                    iResType = int(input('Enter the number of the reservation type: '))
                    calledServer = xmlrpc.client.ServerProxy(server_dict[iResType][0])
                    print("You've chosen", server_dict[iResType][1], 'Reservation')
                    print('\n===============================================================')
                else: cont_check = False # end reservation loop
            else: cont_check = False # end reservation loop
        except:
            cont_check = False # end reservation loop
            print('***', server_dict[iResType][1].upper(), 
                  'SERVER OFFLINE...PLEASE TRY AGAIN LATER ***\n')
            
            # Roll back previous reservations
            for k,v in res_dict.items():
                calledServer = xmlrpc.client.ServerProxy(v[0])
                print(v[1].upper(), 'RESERVATION REMOVED:')
                print(calledServer.RemoveReservation(False),'\n')

if __name__ == '__main__':
    main()       

#%% Removed
#from datetime import datetime
#import sys

#iFromDate = datetime.strptime(input('Check-in date (mm/dd/yy): '), '%m/%d/%y')
#iTomDate = datetime.strptime(input('Check-out date (mm/dd/yy): '), '%m/%d/%y')

#    print('===============================================================')
#    print('>>> Calling GetReservationList (Airlines)...\n')
#    listOfAirlineRes = airlineServer.GetReservationList()
#    print(listOfAirlineRes) 
#    print('===============================================================\n')
#    
#    print('===============================================================')
#    print('>>> Calling GetReservationList (Cars)...\n')
#    listOfCarRes = carServer.GetReservationList()
#    print(listOfCarRes) 
#    print('===============================================================\n')
#
#        %% Delete a reservation
#        print('===============================================================')
#        print('>>> Calling RemoveReservation (', server_dict[iResType][1], ')...\n')
#        iDeleteBool = input('Do you wish to delete a reservation (Y/N)? ')
#        if iDeleteBool == 'Y':
#            iResID = int(input('Reservation ID you wish to delete: '))
##            calledServer.RemoveReservation(iResID)
#            print('Reservation Removed Successfully')
#            print('...', calledServer.RemoveReservation(False))
#        print('===============================================================\n')
#        
#        #%% Display lists of reservations
#        if iDeleteBool == 'Y': display_res()
