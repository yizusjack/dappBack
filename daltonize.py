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

def imageTransform(base64_image, tipo_daltonismo, simulacion):
    imageStream = getImage(base64_image)

    im = Image.open(imageStream)

    if im.mode in ['1', 'L']:  # Imagen en escala de grises
        return None

    im = im.copy()
    im = im.convert('RGB')
    RGB = numpy.asarray(im, dtype=float)

    deutan = numpy.array([[1.135, -0.05, 0], [0.280085, 0.692501, 0.047413], [-0.011820, 0.042940, 0.968881]])
    protan = numpy.array([[0,2.02344,-2.52581],[0,1,0],[0,0,1]])
    tritanope = numpy.array([[1,0,0],[0,1,0],[-0.395913,0.801109,0]])

    if tipo_daltonismo == 'Deuteranopia':
        lms2lms_deficit = deutan
    elif tipo_daltonismo == 'Protanopia':
        lms2lms_deficit = protan
    elif tipo_daltonismo == 'Tritanopia':
        lms2lms_deficit = tritanope
    else:
        return None

    # Colorspace transformation matrices
    rgb2lms = numpy.array([[17.8824, 43.5161, 4.11935], [3.45565, 27.1554, 3.86714], [0.0299566, 0.184309, 1.46709]])
    lms2rgb = numpy.linalg.inv(rgb2lms)

    # matriz de error
    err2mod = numpy.array([[0, 0, 0], [0.7, 1, 0], [0.7, 0, 1]])

    # transformación a LMS (sistema de color que representa los conos del ojo)
    LMS = numpy.tensordot(RGB, rgb2lms.T, axes=([2], [0]))

    # calcular la imagen bajo la vista daltónica
    _LMS = numpy.tensordot(LMS, lms2lms_deficit.T, axes=([2], [0]))

    # Convertir de regreso a RGB
    _RGB = numpy.tensordot(_LMS, lms2rgb.T, axes=([2], [0]))

    #Si se busca simular el daltonismo la imagen se retorna a RGB
    if(simulacion):
        dtpm = _RGB
    
    else:

        # calcula el error entre la imagen original y la imagen transformada
        error = (RGB - _RGB)

        # daltonización
        ERR = numpy.tensordot(error, err2mod.T, axes=([2], [0]))

        dtpm = ERR + RGB  # suma la matriz original con la matriz de error

    # ajusta los valores para que estén entre 0 y 255
    result = numpy.clip(dtpm, 0, 255).astype('uint8')

    # genera imagen transformada
    im_converted = Image.fromarray(result, mode='RGB')
    im_file = BytesIO()
    im_converted.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    convertedBase64 = base64.b64encode(im_bytes).decode("utf-8")

    return convertedBase64