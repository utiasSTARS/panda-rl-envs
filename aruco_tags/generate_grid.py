import argparse

import cv2
import cv2.aruco as aruco

parser = argparse.ArgumentParser()
# parser.add_argument('--first_id', type=int, default=0)
# parser.add_argument('--last_id', type=int, default=11)
parser.add_argument('--width', type=int, default=3)
parser.add_argument('--height', type=int, default=4)
parser.add_argument('--tag_width', type=float, default=0.045)
parser.add_argument('--dictionary', type=str, default='DICT_4X4_50')
parser.add_argument('--ppi', type=int, default=300)
args = parser.parse_args()

gridboard = aruco.GridBoard(
    size=(args.width, args.height),
    markerLength=args.tag_width,
    markerSeparation=.01,
    dictionary=aruco.getPredefinedDictionary(getattr(aruco, args.dictionary))
)

ppm = args.ppi / 2.54 * 100

total_width = args.width * args.tag_width + (args.width - 1) * .01


img = gridboard.generateImage((85, 110), marginSize=100)
cv2.imwrite('test_gridboardasdf.png', img)