import argparse
import os.path
import cv2
import numpy as np


def on_change_r(x):
    global prev_r 
    if x == 0:
        x = 1
    if x != prev_r:
        prev_r = x
        print(f"Radius:  {x}")


def on_change_s(x):
    global prev_s 
    if x != prev_s:
        prev_s = x
        print(f"Spacing: {x}")


def update_img(img):
    # retrieve current configs
    r = cv2.getTrackbarPos("Circle Radius", "Configs")
    spacing = cv2.getTrackbarPos("Circle Spacing", "Configs")
    brightness = cv2.getTrackbarPos("Brightness", "Configs")

    # Can't change min val from 0 on trackbar, if r=0 set to 1
    if r == 0:
        r = 1
    
    # Make canvas from brightness
    canvas = np.ones_like(img)*brightness

    # Calculate number of circles and spacing params
    circle_space = 2*r + spacing
    n_cols = (w)//circle_space
    n_rows = (h)//circle_space
    off_x = (w % circle_space + spacing)//2
    off_y = (h % circle_space + spacing)//2

    # use resize interpolation to get color for circles
    img_resize = cv2.resize(img, (n_cols, n_rows), cv2.INTER_CUBIC)

    for x in range(n_cols):
        for y in range(n_rows):
            x_cen = x*circle_space + r + off_x
            y_cen = y*circle_space + r + off_y

            # weird stuff with cv2 types, need explicit element-wise cast 
            color = [int(x) for x in img_resize[y, x, :]] 
            # color = [int(x) for x in img[y_cen, x_cen, :]] # this sets circle color from center pixel color in source img

            cv2.circle(canvas, (x_cen, y_cen), radius=r, color=color, thickness=-1)
    
    return canvas


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="img_path", help="path to source image")

    args = parser.parse_args()
    if not os.path.exists(args.img_path):
        parser.error(f"The file [{args.img_path}] does not exist!")
    
    # Retrieve Image
    img = cv2.imread(args.img_path)
    h, w = img.shape[:2]

    # Set up slider window
    configWin = "Configs"
    r_init = 20
    s_init = 5
    cv2.namedWindow(configWin, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Circle Radius", configWin, r_init, 75, on_change_r)
    cv2.createTrackbar("Circle Spacing", configWin, s_init, 25, on_change_s)
    cv2.createTrackbar("Brightness", configWin, 0, 255, lambda x: None)
    cv2.resizeWindow(configWin, 400, 30)

    # vars to help reduce terminal spam on changing trackbar
    prev_r = r_init
    prev_s = s_init

    # Draw initial image
    canvas = update_img(img)

    while True:
        cv2.imshow("Image", canvas)
        k = cv2.waitKey(0) & 0xFF

        if k == ord(" "):
            # Spacebar, update image with new configs
            canvas = update_img(img)
            
        elif k == ord("s"):
            # s key, save image
            dst = input(f"\n{'='*15}\n\nSave as: ")
            print(f"Saving image as [{dst}]\n\n{'='*15}\n")
            cv2.imwrite(dst, canvas)

        elif k == 27:
            # Esc key, exit program
            # Get final params to print
            r = cv2.getTrackbarPos("Circle Radius", "Configs")
            spacing = cv2.getTrackbarPos("Circle Spacing", "Configs")
            print(f"\n{'='*15}\n\nFinal Radius:  {r}\nFinal Spacing: {spacing}\n\n{'='*15}\n")
            
            cv2.destroyAllWindows()
            exit()
