import qrtools


def main():
    """
    tests image recognition of qrtools with a given set of images
    :return:
    """
    img = ["test1.jpg", "test2.png", "test3.jpg", "test4.jpeg"]

    for i in range(0, len(img)):
        qr = qrtools.QR()
        qr.decode(img[i])
        print "Data for", img[i], ":"
        print qr.data, "\n"


if __name__ == '__main__':
    main()
