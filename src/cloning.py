import numpy as np
import cv2

config = {
    'background_image_path': r'test/ice-coast.png',
    'test_image_path': r'test/polarbear.png',
    'result_image_path': r'result.png',
    'temp_image_path': r'image/temp/',
    'paste_position_x': 200,
    'paste_position_y': 200,
    'kernel': np.ones((3, 3), np.uint8),
    'object_threshold': 500
}

def get_edge_image(test_image):
    # convert to gray image
    gray_test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(config['temp_image_path']+'gray.png', gray_test_image)

    # denoise and detect edge
    blurred_test_image = cv2.GaussianBlur(gray_test_image, (13, 13), 0)
    cv2.imwrite(config['temp_image_path']+'blurred.png', blurred_test_image)
    canny_test_image = cv2.Canny(blurred_test_image, 20, 60)
    cv2.imwrite(config['temp_image_path']+'canny.png', canny_test_image)
    
    # use dilation method to connect edge
    dilate_test_image = cv2.dilate(canny_test_image, config['kernel'], iterations = 1)
    _, dilate_test_image = cv2.threshold(dilate_test_image, 127, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite(config['temp_image_path']+'dilate.png', dilate_test_image)
    return dilate_test_image

def get_object_map(edge_image):
    # use connected components method to get labels map
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(edge_image)
    
    # get object(max) label number and drop small object
    max_label = 0
    for i in range(num_labels):
        if(stats[i, 4] > stats[max_label, 4]):
            max_label = i
    for y in range(labels.shape[0]):
        for x in range(labels.shape[1]):
            if(stats[labels[y, x], 4] < config['object_threshold']):
                labels[y, x] = max_label
    
    # get object image
    labels*=20
    cv2.imwrite(config['temp_image_path']+'label.png', labels)
    
    # set 0 for not object part
    for y in range(labels.shape[0]):
        for x in range(labels.shape[1]):
            if(labels[y, x] != max_label*20):
                labels[y, x] = 0
            else:
                labels[y, x] = 255
    
    # dilate again to cover edge
    object_map = cv2.dilate(np.uint8(labels), config['kernel'], iterations = 2)
    cv2.imwrite(config['temp_image_path']+'object_map.png', object_map)
    return object_map

def get_object_image(test_image):
    obj_image = test_image.copy()

    # use object map to extract object from test image (background = [255, 255, 255])
    edge_image = get_edge_image(test_image)
    object_map = get_object_map(edge_image)
    for y in range(obj_image.shape[0]):
        for x in range(obj_image.shape[1]):
            if(object_map[y, x] == 0):
                obj_image[y, x] = [255, 255, 255]

    cv2.imwrite(config['temp_image_path']+'object.png', obj_image)
    return obj_image

def paste_image(bkg_image, obj_image, pos_x, pos_y):
    result_image = bkg_image.copy()
    
    # paste object according to pos and [255, 255, 255]
    for y in range(result_image.shape[0]):
        for x in range(result_image.shape[1]):
            if(x >= pos_x and x < obj_image.shape[1]+pos_x
               and y >= pos_y and y < obj_image.shape[0]+pos_y
               and not (obj_image[y-pos_y, x-pos_x] == [255, 255, 255]).all()):
                result_image[y, x] = obj_image[y-pos_y, x-pos_x]
    return result_image

def cloning_api(bkg_image, test_image, pos_x, pos_y):
    # get object image and paste
    obj_image = get_object_image(test_image)
    return paste_image(bkg_image, obj_image, pos_x, pos_y)


if __name__ == '__main__':
    # read test images
    bkg_image = cv2.imread(config['background_image_path'])
    test_image = cv2.imread(config['test_image_path'])

    # output result image
    result_image = cloning_api(
        bkg_image, test_image, config['paste_position_x'], config['paste_position_y'])
    
    cv2.imwrite(config['result_image_path'], result_image)
