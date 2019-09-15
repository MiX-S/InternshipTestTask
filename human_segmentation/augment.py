import tensorflow as tf
import tensorflow.contrib as tfcontrib
import functools


img_shape = (128, 128, 3)



def _process_pathnames(fname, label_path):
    # We map this function onto each pathname pair  
    img_str = tf.read_file(fname)
    img = tf.image.decode_jpeg(img_str, channels=3)

    label_img_str = tf.read_file(label_path)
    label_img = tf.image.decode_png(label_img_str)
    # The label image should only have values of 1 or 0, indicating pixel wise
    # object (car) or not (background). We take the first channel only. 
    label_img = label_img[:, :, 0]
    label_img = tf.expand_dims(label_img, axis=-1)
    return img, label_img



def shift_img(output_img, label_img, width_shift_range, height_shift_range):
    """performs the horizontal or vertical shift"""
    if width_shift_range or height_shift_range:
        if width_shift_range:
            width_shift_range = tf.random_uniform([],  
                                                  -width_shift_range * img_shape[1],
                                                  width_shift_range * img_shape[1])
        if height_shift_range:
            height_shift_range = tf.random_uniform([],
                                                   -height_shift_range * img_shape[0],
                                                   height_shift_range * img_shape[0])
        # Translate both 
        output_img = tfcontrib.image.translate(output_img,
                                               [width_shift_range, height_shift_range])
        label_img = tfcontrib.image.translate(label_img,
                                              [width_shift_range, height_shift_range])
    return output_img, label_img



def flip_img(horizontal_flip, tr_img, label_img):
    """performs flipping the image"""
    if horizontal_flip:
        flip_prob = tf.random_uniform([], 0.0, 1.0)
        tr_img, label_img = tf.cond(tf.less(flip_prob, 0.5),
                                    lambda: (tf.image.flip_left_right(tr_img), tf.image.flip_left_right(label_img)),
                                    lambda: (tr_img, label_img))
    return tr_img, label_img



def _augment(img,
             label_img,
             resize=None,  # Resize the image to some size e.g. [256, 256]
             scale=1,  # Scale image e.g. 1 / 255.
             hue_delta=0,  # Adjust the hue of an RGB image by random factor
             horizontal_flip=False,  # Random left right flip,
             width_shift_range=0,  # Randomly translate the image horizontally
             height_shift_range=0):  # Randomly translate the image vertically 
    if resize is not None:
        # Resize both images
        label_img = tf.image.resize_images(label_img, resize)
        img = tf.image.resize_images(img, resize)
  
    if hue_delta:
        img = tf.image.random_hue(img, hue_delta)
  
    img, label_img = flip_img(horizontal_flip, img, label_img)
    img, label_img = shift_img(img, label_img, width_shift_range, height_shift_range)
    label_img = tf.to_float(label_img) * scale
    img = tf.to_float(img) * scale 
    return img, label_img

