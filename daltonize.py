import base64
import numpy
from PIL import Image
from io import BytesIO

def getImage(base64_image):
    if "data:image" in base64_image:
        base64_image = base64_image.split(",")[1]

    imageBytes = base64.b64decode(base64_image)
    imageStream = BytesIO(imageBytes)

    return imageStream

def imageTransform(base64_image, tipo_daltonismo):
    imageStream = getImage(base64_image)

    im = Image.open(imageStream)

    if im.mode in ['1', 'L']:  # Imagen en escala de grises
        return null

    im = im.copy()
    im = im.convert('RGB')
    RGB = numpy.asarray(im, dtype=float)

    # lms2lms_deficit = numpy.array([[1,0,0],[0.494207,0,1.24827],[0,0,1]])
    # ver saturación de rojo, es mucha, mejor intentar balancear el verde
    # lms2lms_deficit = numpy.array([[1.135,-0.05,0],[0.469,0.22,1.05],[0,0,1]])
    lms2lms_deficit = numpy.array([[1.135, -0.05, 0], [0.280085, 0.692501, 0.047413], [-0.011820, 0.042940, 0.968881]])

    # Colorspace transformation matrices
    rgb2lms = numpy.array([[17.8824, 43.5161, 4.11935], [3.45565, 27.1554, 3.86714], [0.0299566, 0.184309, 1.46709]])
    lms2rgb = numpy.linalg.inv(rgb2lms)

    # matriz de error
    err2mod = numpy.array([[0, 0, 0], [0.7, 1, 0], [0.7, 0, 1]])

    # transformación a LMS (sistema de color que representa los conos del ojo)
    LMS = numpy.zeros_like(RGB)
    for i in range(RGB.shape[0]):
        for j in range(RGB.shape[1]):
            rgb = RGB[i, j, :3]  # obtiene los valores rgb del pixel actual
            LMS[i, j, :3] = numpy.dot(rgb2lms,
                                      rgb)  # transforma el pixel de rgb a lms al multiplicarlo por su matriz de transformacion

    # calcular la imagen bajo la vista daltónica
    _LMS = numpy.zeros_like(RGB)
    for i in range(RGB.shape[0]):
        for j in range(RGB.shape[1]):
            lms = LMS[i, j, :3]
            _LMS[i, j, :3] = numpy.dot(lms2lms_deficit, lms)

    _RGB = numpy.zeros_like(RGB)
    for i in range(RGB.shape[0]):
        for j in range(RGB.shape[1]):
            _lms = _LMS[i, j, :3]
            _RGB[i, j, :3] = numpy.dot(lms2rgb, _lms)

    # calcula el error entre la imagen original y la imagen transformada
    error = (RGB - _RGB)

    # daltonización
    ERR = numpy.zeros_like(RGB)
    for i in range(RGB.shape[0]):
        for j in range(RGB.shape[1]):
            err = error[i, j, :3]
            ERR[i, j, :3] = numpy.dot(err2mod, err)

    dtpm = ERR + RGB  # suma la matriz original con la matriz de error

    # ajusta los valores para que estén entre 0 y 255
    for i in range(RGB.shape[0]):
        for j in range(RGB.shape[1]):
            dtpm[i, j, 0] = max(0, dtpm[i, j, 0])
            dtpm[i, j, 0] = min(255, dtpm[i, j, 0])
            dtpm[i, j, 1] = max(0, dtpm[i, j, 1])
            dtpm[i, j, 1] = min(255, dtpm[i, j, 1])
            dtpm[i, j, 2] = max(0, dtpm[i, j, 2])
            dtpm[i, j, 2] = min(255, dtpm[i, j, 2])

    # redondea valores
    result = dtpm.astype('uint8')

    # genera imagen transformada
    im_converted = Image.fromarray(result, mode='RGB')
    im_file = BytesIO()
    im_converted.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    convertedBase64 = base64.b64encode(im_bytes).decode("utf-8")

    return convertedBase64