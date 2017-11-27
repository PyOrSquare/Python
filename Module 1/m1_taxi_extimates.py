taxiOwned=100
taxiCapacity=4
print ('Enter estimated number of passengers today')
estPassengers=input()
result=int(estPassengers)/(taxiCapacity-1)
if ( int(estPassengers)%(taxiCapacity-1) > 0):
    result=result+1
print ('Number of Taxi rides based on estimated number of passengers is = %d' %(result) )
