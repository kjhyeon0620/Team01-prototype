import base64
import numpy as np



# TinyDB, wav array 저장 도구 
def numpy_to_base64(arr: np.ndarray) -> str:
    """ Numpy array를 base64 문자열로 변환 """
    arr_bytes = arr.tobytes()
    b64_bytes = base64.b64encode(arr_bytes)
    b64_str = b64_bytes.decode('utf-8')
    return b64_str

def base64_to_numpy(b64_str: str, dtype, shape) -> np.ndarray:
    """ base64 문자열을 numpy array로 복원 """
    b64_bytes = b64_str.encode('utf-8')
    arr_bytes = base64.b64decode(b64_bytes)
    arr = np.frombuffer(arr_bytes, dtype=dtype)
    arr = arr.reshape(shape)
    return arr