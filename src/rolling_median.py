from datetime import datetime, timedelta
import json
import numpy as np
import sys
from scipy.sparse import csc_matrix
from sparseMatrix import doubleMatrixSize

# dt (datetime)
# bo (bool)
# u16 (uint16)

_60sec = timedelta(seconds = 60)
dt_highestTime = datetime.min   # Keeps track of the most recent transaction
userCount = 0                   # Works as id for each user
users = {}              # Dictionary storing the users' names and ids (used to index the sparse matrix)
medianVal = 0           # Initialize median value

# The sparse matrix stores the elapsed time of the corresponding node since
# the highestTime payment. Only payments within the 60 second frame are
# stored.
# A uint16 is used hoping that there is a delay no longer than 65535
# seconds between the payments
# The adjancency matrix will be symmetric.
# Seconds elapsed starts in 1 not 0 because otherwise the node will not be
# counted in the median
matrixOrder = 50        # Guess for the number of users
matrixShape = (matrixOrder, matrixOrder)
u16_adjacencyMatrix = csc_matrix(matrixShape, dtype=np.uint16)

# sys.argv[1] contains the payment sequences and sys.argv[2] will store the output 
outputFile = open(sys.argv[2], 'w')

with open(sys.argv[1]) as f:
    for line in f:
        # Check for correct input
        try:
            currentPayment = json.loads(line)
            dt_currentPayment = datetime.strptime(currentPayment['created_time'], '%Y-%m-%dT%H:%M:%SZ')
        except:      # Either Json line or datetime incorrectly encoded
            continue

        # If they are both strings and neither one is emtpy, the entry is safe, otherwise ignore it
        if (not isinstance(currentPayment['target'], basestring)) or (not currentPayment['target']) \
            or (not isinstance(currentPayment['actor'], basestring)) or (not currentPayment['actor']):
            continue

        # If the transaction is more recent than the most recent one:
        if dt_currentPayment > dt_highestTime:
            # Check wether one of the users is a new user (or both) and register him/her
            if not currentPayment['target'] in users:
                users[currentPayment['target']] = userCount
                userCount += 1      # Increase the users count

            if not currentPayment['actor'] in users:
                users[currentPayment['actor']] = userCount
                userCount += 1      # Increase the users count

            secondsDelta = (dt_currentPayment - dt_highestTime).total_seconds()
            dt_highestTime = dt_currentPayment  # Update highest time
            u16_adjacencyMatrix += (u16_adjacencyMatrix > 0)*secondsDelta     # Update elapsed time in all transactions
    
            # Delete nodes that are outside of the 60sec gap
            u16_adjacencyMatrix[u16_adjacencyMatrix > 61] = 0
            u16_adjacencyMatrix.eliminate_zeros()
            # del users[]
            
            if userCount > matrixOrder:
                matrixOrder, u16_adjacencyMatrix = doubleMatrixSize(matrixOrder, u16_adjacencyMatrix)
    
            # Add the transaction to the sparse matrix, remember that the count starts in 1
            u16_adjacencyMatrix[ users[currentPayment['target']] , users[currentPayment['actor']] ] = 1
            u16_adjacencyMatrix[ users[currentPayment['actor']] , users[currentPayment['target']] ] = 1
    
            # Calculate the median
            connections = csc_matrix(u16_adjacencyMatrix > 0).sum(2)   # Sum over y axis
            medianVal = np.median(connections[connections>0], axis=1)
    
        # If it is not the most recent transaction, but falls within the 60sec gap:
        elif dt_currentPayment > (dt_highestTime - _60sec):
            # Check wether one of the users is a new user (or both) and register him/her
            if not currentPayment['target'] in users:
                users[currentPayment['target']] = userCount
                userCount += 1
    
            if not currentPayment['actor'] in users:
                users[currentPayment['actor']] = userCount
                userCount += 1
    
            if userCount > matrixOrder:
                matrixOrder, u16_adjacencyMatrix = doubleMatrixSize(matrixOrder, u16_adjacencyMatrix)

            secondsDelta = (dt_highestTime - dt_currentPayment).total_seconds()
            # Add the transaction to the sparse matrix, remember that the count starts in 1
            u16_adjacencyMatrix[ users[currentPayment['target']] , users[currentPayment['actor']] ] = secondsDelta + 1
            u16_adjacencyMatrix[ users[currentPayment['actor']] , users[currentPayment['target']] ] = secondsDelta + 1
    
            # Calculate the median
            connections = csc_matrix(u16_adjacencyMatrix > 0).sum(2)   # Sum over y axis
            medianVal = np.median(connections[connections>0], axis=1)
    
        # If currentPayment is not the most recent transaction and it's also outside of the 60sec gap
#       else:  
#          do_nothing()

        # Write output to file    
        print >> outputFile, '%.2f' % medianVal

# Close working file
outputFile.close()