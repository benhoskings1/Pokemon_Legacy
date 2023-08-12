import os

import cv2
import numpy as np
import pygame as pg


class ImageEditor:
    def __init__(self, file: os.PathLike = None, pixelData=None):
        if file:
            if not os.path.exists(file):
                print("NO such file")
            head, self.fileName = os.path.split(file)
            self.image = cv2.imread(file, cv2.IMREAD_UNCHANGED)
            self.pixelData = self.image

        elif type(pixelData) is not None:
            self.image = pixelData
            self.pixelData = pixelData

        else:
            self.image = None
            self.pixelData = None

    def loadData(self, data):
        self.pixelData = data

    def addAlphaChannel(self, overwrite=False):
        newImage = cv2.cvtColor(self.image, cv2.COLOR_RGB2RGBA)
        if overwrite:
            self.pixelData = newImage

    def resetAlpha(self, overwrite=False):
        pixelDataCopy = self.pixelData.copy()
        for row in range(pixelDataCopy.shape[0]):
            for col in range(pixelDataCopy.shape[1]):
                pixelDataCopy[row, col, 3] = 255

        if overwrite:
            self.pixelData = pixelDataCopy

        return pixelDataCopy

    def replaceImage(self, path):
        self.image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        self.pixelData = np.array(self.image)

    def eraseColour(self, colour, overwrite=False):
        pixelDataCopy = self.pixelData.copy()

        for row in range(pixelDataCopy.shape[0]):
            for col in range(pixelDataCopy.shape[1]):
                pixel = pixelDataCopy[row, col, 0:3]
                if np.array_equal(pixel, np.array(colour)):
                    pixelDataCopy[row, col, 3] = 0

        if overwrite:
            self.pixelData = pixelDataCopy

        return pixelDataCopy

    def saveImage(self, directory: os.PathLike = None, name=None):
        if directory:
            if not os.path.exists(directory):
                print("Making directory")
                os.mkdir(directory)

        if name:
            if directory:
                cv2.imwrite(os.path.join(directory, name), self.pixelData)
            else:
                cv2.imwrite(name, self.pixelData)
        else:
            if directory:
                cv2.imwrite(self.fileName, self.pixelData)

        print("Image Saved")

    def checkLine(self, idx, axis):
        if axis == 0:
            # get the nth row
            pixels = self.pixelData[idx, :, :]
        else:
            pixels = self.pixelData[:, idx, :]

        for idx, pixel in enumerate(pixels):
            if pixel[3] != 0:
                return True

        return False

    def cropImage(self, overwrite=False):
        rowCrop = []

        for idx, row in enumerate(self.pixelData[:, 0, :]):
            crop = self.checkLine(idx, 0)
            rowCrop.append(crop)
        rowCrop = np.array(rowCrop)
        rowIndices = np.array(range(self.pixelData.shape[0]))[rowCrop]

        colCrop = []
        for idx, row in enumerate(self.pixelData[0, :, :]):
            crop = self.checkLine(idx, 1)
            colCrop.append(crop)
        colCrop = np.array(colCrop)
        colIndices = np.array(range(self.pixelData.shape[1]))[colCrop]

        newImage = self.pixelData[min(rowIndices): max(rowIndices) + 1, min(colIndices):max(colIndices) + 1, :]

        if overwrite:
            self.pixelData = newImage

        return newImage

    def cropToSize(self, size:pg.Vector2, overwrite=False):

        xLims = (int((self.pixelData.shape[0] - size.x) / 2), int((self.pixelData.shape[0] - size.x) / 2 + size.x))
        yLims = (int((self.pixelData.shape[1] - size.y) / 2), int((self.pixelData.shape[1] - size.y) / 2 + size.y))

        newImage = self.pixelData[xLims[0]:xLims[1], yLims[0]:yLims[1]]

        if overwrite:
            self.pixelData = newImage

        return newImage

    def resizeImage(self, size, overwrite=False):
        img = self.pixelData.copy()
        img = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)

        if overwrite:
            self.pixelData = img

    def scaleImage(self, scale, overwrite=False):
        img = self.pixelData.copy()
        size = (int(img.shape[1] * scale[0]), int(img.shape[0] * scale[1]))
        img = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)

        if overwrite:
            self.pixelData = img

    def showImage(self):
        cv2.imshow("Image", self.pixelData)
        cv2.waitKey()

    def cleanImage(self):
        self.eraseColour([255, 255, 255], overwrite=True)
        self.cropImage(overwrite=True)

    def createSurface(self, bgr=True):
        surf = pg.Surface((self.pixelData.shape[1], self.pixelData.shape[0]), pg.SRCALPHA)
        pixelArray = pg.PixelArray(surf)
        for row in range(self.pixelData.shape[0]):
            for col in range(self.pixelData.shape[1]):
                if bgr:
                    r = int(self.pixelData[row, col, 2])
                    g = int(self.pixelData[row, col, 1])
                    b = int(self.pixelData[row, col, 0])
                else:
                    r = int(self.pixelData[row, col, 0])
                    g = int(self.pixelData[row, col, 1])
                    b = int(self.pixelData[row, col, 2])

                colour = pg.Color(r, g, b, int(self.pixelData[row, col, 3]))
                pixelArray[col, row] = colour
        pixelArray.close()

        return surf


# editor = ImageEditor(file="Learn Move.png")
# editor.resizeImage((256, 192), overwrite=True)
# editor.saveImage(name="Learn Move edit.png")

