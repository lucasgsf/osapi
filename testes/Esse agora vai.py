import cv2
import imutils
import numpy as np

def resize(img, height=800):
    """ Resize image to given height """
    rat = height / img.shape[0]
    return cv2.resize(img, (int(rat * img.shape[1]), height))

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
 
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
 
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
 
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
	# return the warped image
	return warped

photosTrace = ['prova/originais/provaImpressa/gabarito.jpg', 'prova/originais/provaImpressa/aluno.jpg', 'prova/originais/provaImpressa/provaO.jpg'] #adicionar prova em branco
photos = []
for photoTrace in photosTrace:
	im_gray = cv2.imread(photoTrace, cv2.IMREAD_GRAYSCALE)
	im_gray = cv2.medianBlur(im_gray,9)
	ratio = im_gray.shape[0] / 800.0
	orig = im_gray.copy()
	im_gray = resize(im_gray)
	blur = cv2.GaussianBlur(im_gray, (5, 5), 0)
	edged = cv2.Canny(blur, 75, 200)
	
	cv2.imwrite("edged.png", edged)

	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break

	cv2.drawContours(im_gray, [screenCnt], -1, (0, 255, 0), 2)

	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	im_lim = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 81, 20)
	warped = (warped > im_lim).astype("uint8") * 255

	photos.append(imutils.resize(warped, height = 800))

gabarito =  photos[0]
aluno = photos[1]
prova = photos[2]

#Redimensiona

min = gabarito.shape[1]

if(min > aluno.shape[1]):
	min = aluno.shape[1]
elif(min > prova.shape[1]):
	min = prova.shape[1]


gabarito = cv2.resize(gabarito, (min, 800))
aluno = cv2.resize(aluno, (min, 800))
prova = cv2.resize(prova, (min, 800))

cv2.imwrite("prova/resultados/gabarito_lim.jpeg", gabarito)
cv2.imwrite("prova/resultados/aluno_lim.jpeg", aluno)
cv2.imwrite("prova/resultados/prova_lim.jpeg", prova)

subtractGabarito = cv2.subtract(gabarito, aluno)
cv2.imwrite("prova/resultados/subtractGabarito.jpeg", subtractGabarito)

subtractProva = cv2.subtract(prova, gabarito)
cv2.imwrite("prova/resultados/subtractProva.jpeg", subtractProva)

kernel = np.ones((5,5),np.uint8)

medianGabarito = cv2.medianBlur(subtractGabarito,3)
medianProva = cv2.medianBlur(subtractProva,3)

medianGabarito = cv2.dilate(medianGabarito,kernel, iterations = 13)
medianProva = cv2.dilate(medianProva,kernel, iterations = 10)

cv2.imwrite("prova/resultados/medianGabarito.jpeg", medianGabarito)
cv2.imwrite("prova/resultados/medianProva.jpeg", medianProva)

(cntsGabarito, _) = cv2.findContours(medianGabarito.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
(cntsProva, _) = cv2.findContours(medianProva.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print("QUESTÕES: " + str(len(cntsProva)))
print("ERROS: " + str(len(cntsGabarito)))
print("NOTA: " + str(len(cntsProva) - len(cntsGabarito)))