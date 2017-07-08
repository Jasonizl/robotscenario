import qrtools

def decodeImage(imgpath):
    """
    call ALPhotoCaptureProxy::takePicture(), remember fileName and pass it here

    :param imgpath:
    :return: data of qr-code if valid or "NULL"
    """

    qr = qrtools.QR()
    qr.decode(imgpath)

    #if qr.data == "NULL":
    #    return "error"

    return qr.data  # either data or NULL

