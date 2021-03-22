import numpy as np
cimport numpy as np
np.import_array()

def correct_24bit_signed(np.ndarray[np.int32_t, ndim=1] A):
    """
    This function is for np.int32 data that contains 24-bit
    signed integer data. To transform, one must:

      1. Mask off int32 most significant byte (MSB)
            This could contain unwanted data from overlapping
            memory addresses
      2. Transform to negative
            Transform involves setting int32 MSB by evaluating
            the value of the 24-bit MSB
    """
    cdef Py_ssize_t i
    cdef np.int32_t third_bit, negative
    cdef np.int32_t neg_mask=0xff000000
    cdef np.int32_t bit_mask=0x00ffffff
    cdef np.int32_t eval_mask=0x00ff0000
    cdef np.int32_t thresh = 0x80
    cdef np.ndarray[np.int32_t, ndim=1] B = np.empty(A.shape[0], dtype=np.int32)
    for i in np.arange(A.shape[0]):
        third_bit = A[i] & eval_mask
        is_neg = third_bit >= thresh
        if is_neg:
            B[i] = (A[i] & bit_mask) | neg_mask
        else:
            B[i] = A[i] & bit_mask
    return B