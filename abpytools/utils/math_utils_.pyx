from libc.math cimport pow as pow_C
from abpytools.cython_extensions.convert_py_2_C cimport get_C_double_array_pointers, release_C_pointer, get_array_from_ptr
import itertools
from cython.operator cimport dereference, postincrement



class Matrix2D(Matrix2D_backend):

    def __init__(self, values):
        """
        Lightweight numpy-like class for fast numerical calculations with Cython
        Args:
            values:
        """
        super().__init__(values)

    @property
    def values(self):
        """
        Returns data as a list of lists
        """
        return self._get_values()

    @property
    def shape(self):
        return self.n_rows, self.n_cols

    def __str__(self):

        final_string = "[{}]"
        intermediate_string = ""
        for i in range(self.n_rows):
            intermediate_string += "[{}]".format(', '.join([str(x) for x in self._get_row(i)]))

        return final_string.format(intermediate_string)

    def __repr__(self):

        repr_string = "array"
        first=True
        for x in self.__str__().split('\n'):
            if first:
                repr_string += "{}\n".format(x)
                first=False
            else:
                repr_string+="     {}\n".format(x)
        return repr_string


cdef class Matrix2D_backend:
    """
    Cython class to manipulate double precision 2D matrix
    """

    def __init__(self, values_, ptrs=None, shape=None):
        # if ptr and shape are defined, values will be ignored and the data will be read from ptrs
        # check all rows have the same size
        self.values_ = values_
        self.n_rows = len(self.values_)
        self.n_cols = len(self.values_[0])
        self.size = self.n_cols * self.n_rows

        cdef int i

        for i in range(1, self.n_rows):
           if len(self.values_[i]) != self.n_cols:
               raise ValueError("All rows must have the same number of elements")

        # copy data to a contiguous C array
        self.data_C = get_C_double_array_pointers(list(itertools.chain(*self.values_)), self.n_rows * self.n_cols)

    def _check_index(self, int row, int column):
        if row * self.n_cols + column < self.size:
            raise IndexError("Requested element is outside array bounds")

    cdef double* _get_value_pointer(self, int row, int col):
        cdef double* ptr = &self.data_C[self.n_cols * row + col]

    cdef double* _get_row_pointer(self, int row):
        """
        Get pointer of first element of this row
        Args:
            row:

        Returns:

        """
        # pointer to first element of C array row
        cdef double* ptr = &self.data_C[self.n_cols * row]
        return ptr

    def _get_row(self, int row):
        result = []
        cdef int i
        ptr = self._get_row_pointer(row)
        for i in range(self.n_cols):
            result.append(dereference(ptr))
            postincrement(ptr)

        return result

    def __dealloc__(self):
        # releases C memory allocation
        release_C_pointer(self.data_C)

    def __getitem__(self, int row):
        # create vector using data_ references
        return Vector.create(self._get_row_pointer(row), self.n_cols)

    def _get_values(self):
        """
        Returns all values of C array
        Returns:

        """
        cdef list result = []
        cdef int i
        cdef int j
        cdef double* ptr
        cdef list row_result

        for i in range(self.n_rows):
            row_result = []
            ptr = self._get_row_pointer(i)  # this is more of a sanity check than anything else
            for j in range(self.n_cols):
                row_result.append(dereference(ptr))  # same as *ptr in C
                postincrement(ptr) # same as ptr++ in C
            result.append(row_result)

        return result


# class Vector(Vector_backend):
#
#     def __init__(self, values=None):
#         super().__init__(values)
#
#
#     def __getitem__(self, idx):
#         return self._get_element(idx)
#
#     def __setitem__(self, idx, value):
#         return
#
#     @property
#     def size(self):
#         return self.size_
#
#
cdef class Vector:

    """
    Lightweight Cython vector class implementation that stores data as C arrays and uses these to perform calculations
    """

    def __init__(self, values_=None):
        if values_ is not None:
            self.size_ = len(values_)
            self.data_C = get_C_double_array_pointers(values_, self.size_)

    @staticmethod
    cdef Vector create(double* ptr, int size):
        cdef Vector vec = Vector()
        vec.size_ = size
        vec.data_C = get_array_from_ptr(ptr, size)
        return vec

    cpdef double dot_product(self, Vector other):

        """
        Vector dot product
        Args:
            other: 

        Returns:

        """

        if self.size_ != other.size:
            raise ValueError("Vector size mismatch")

        return internal_vector_dot_product_(self.data_C, other.data_C, self.size_)

    cdef double _get_element(self, int idx):
        return self.data_C[idx]

    cdef void _set_array_value(self, int idx, double value):
        cdef double* ptr = &self.data_C[idx]
        ptr = &value
        # self.data_C[idx] = value

    @property
    def values(self):
        """
        Returns:
        """
        return [self._get_element(i) for i in range(self.size_)]

    def __dealloc__(self):
        release_C_pointer(self.data_C)

    @property
    def size(self):
        return self.size_

    def __getitem__(self, int idx):
        return self._get_element(idx)

    def __setitem__(self, idx, value):
        self._set_array_value(idx, value)

cdef double internal_vector_dot_product_(double *u, double *v, int size):
    """
    "Pure" C definition of dot product for Cython compiler (to be only used in the backend).
    
    Args:
        u: 
        v: 
        size: 

    Returns:

    """

    cdef int i
    cdef double result = 0.0

    for i in range(size):
        result += u[i] * v[i]

    return result


cdef double internal_vector_norm_(double *u, int norm, int size):
    """
    "Pure" C definition of vector norm for Cython compiler (to be only used in the backend).
    
    Args:
        u: 
        norm: 
        size: 

    Returns:

    """

    cdef int i
    cdef double result = 0.0
    cdef double inverse_norm = 1.0 / norm

    for i in range(size):
        result += pow_C(u[i], norm)

    result = pow_C(result, inverse_norm)

    return result


cpdef double dot_product_(list u, list v):
    """
    Python API to use Cython dot_product implementation.
    
    Args:
        u list: Python list representing vector u  
        v list: Python list representing vector v

    Returns: Dot product of u and v

    """

    cdef int size
    if len(u) == len(v):
        size = len(u)
    else:
        raise ValueError("Vector size mismatch")

    cdef double *u_ = get_C_double_array_pointers(u, size)
    cdef double *v_ = get_C_double_array_pointers(v, size)

    cdef double result = internal_vector_dot_product_(u_, v_, size)

    release_C_pointer(u_)
    release_C_pointer(v_)

    return result