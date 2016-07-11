import numpy as np
from scipy.sparse import csc_matrix

# doubleMatrixSize doubles the size of a sparse matrix in a extremely efficient way by
# maintaining the data and indices arrays untouched, without copying any data, except only the indptr
# array and filling it with trailing values
def doubleMatrixSize(matrixOrder, u16_adjacencyMatrix):
    # Add the required trailing values to the new pointer (which is the last value repeated)
    new_indptr = np.hstack((u16_adjacencyMatrix.indptr, np.repeat(u16_adjacencyMatrix.indptr[-1], matrixOrder) ) )
    
    # Double the matrix order
    matrixOrder += matrixOrder
    matrixShape = (matrixOrder, matrixOrder)
    
    # Keep data and indices, and only update the indptr and the matrixShape
    u16_adjacencyMatrix=csc_matrix((u16_adjacencyMatrix.data, \
                        u16_adjacencyMatrix.indices, new_indptr), matrixShape)
                        
    return (matrixOrder, u16_adjacencyMatrix)