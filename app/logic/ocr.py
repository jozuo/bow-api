import boto3
import cv2
import numpy as np

client = boto3.client("textract", region_name="us-east-1")


def ocr(binary: bytes) -> dict:
    document = {"Bytes": _convert_image(binary=binary)}
    return client.detect_document_text(Document=document)


def _convert_image(binary: bytes) -> bytes:
    """
    以下サイトのロジックで画像の影を除去して二値化する
    https://qiita.com/fallaf/items/1c5387a79027b2ec64b0
    """
    arr = np.asarray(bytearray(binary), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    ksize = 51
    blur = cv2.blur(img, (ksize, ksize))
    rij = img / blur
    index_1 = np.where(rij >= 0.98)
    index_0 = np.where(rij < 0.98)
    rij[index_0] = 0
    rij[index_1] = 1

    rij = img / blur
    index_1 = np.where(rij >= 1.00)  # 1以上の値があると邪魔なため
    rij[index_1] = 1
    rij_int = np.array(rij * 255, np.uint8)  # 除算結果が実数値になるため整数に変換
    rij_HSV = cv2.cvtColor(rij_int, cv2.COLOR_BGR2HSV)
    ret, thresh = cv2.threshold(rij_HSV[:, :, 2], 0, 255, cv2.THRESH_OTSU)
    rij_HSV[:, :, 2] = thresh
    rij_ret = cv2.cvtColor(rij_HSV, cv2.COLOR_HSV2BGR)

    _, result = cv2.imencode(".png", rij_ret)

    return result.tobytes()
