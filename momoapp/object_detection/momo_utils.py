import base64
import time
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
# import tensorflow.compat.v1 as tf
import zipfile
import cv2

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from IPython.display import display
# This is needed since the notebook is stored in the object_detection folder.
# sys.path.append("..")
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.9.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.9.* or later!')




from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

dir_path = os.path.dirname(os.path.realpath(__file__))
# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = dir_path +'/' + MODEL_NAME + '/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(dir_path+'/'+'data', 'mscoco_label_map.pbtxt')


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)




tensor_dict = {}

def detect(img):
        imageString = base64.b64decode(img)

        #  convert binary data to numpy array
        nparr = np.fromstring(imageString, np.uint8)

        #  let opencv decode image to correct format
        img = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)

        def run_inference_for_single_image(image, graph):
                if 'detection_masks' in tensor_dict:
                        # The following processing is only for single image
                        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[0], image.shape[1])
                        detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                        # Follow the convention by adding back the batch dimension
                        tensor_dict['detection_masks'] = tf.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

                # Run inference
                output_dict = sess.run(tensor_dict,
                                        feed_dict={image_tensor: np.expand_dims(image, 0)})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                        'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                        output_dict['detection_masks'] = output_dict['detection_masks'][0]
                return output_dict




        with detection_graph.as_default():
                with tf.Session() as sess:
                        # Get handles to input and output tensors
                        ops = tf.get_default_graph().get_operations()
                        all_tensor_names = {output.name for op in ops for output in op.outputs}
                        
                        for key in [
                        'num_detections', 'detection_boxes', 'detection_scores',
                        'detection_classes', 'detection_masks'
                        ]:
                                tensor_name = key + ':0'
                                if tensor_name in all_tensor_names:
                                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)

                        image_np = np.array(img)
                        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                        image_np_expanded = np.expand_dims(image_np, axis=0)
                        # Actual detection.
                        output_dict = run_inference_for_single_image(image_np, detection_graph)
                        # Visualization of the results of a detection.
                        vis_util.visualize_boxes_and_labels_on_image_array(
                                image_np,
                                output_dict['detection_boxes'],
                                output_dict['detection_classes'],
                                output_dict['detection_scores'],
                                category_index,
                                instance_masks=output_dict.get('detection_masks'),
                                use_normalized_coordinates=True,
                                line_thickness=8)
                        
                        img_height,img_width,img_depth = image_np.shape
                        result = []
                        for index,box in enumerate(output_dict['detection_boxes']):
                                if(output_dict['detection_scores'][index]<=0.7):
                                        break
                                class_name = category_index.get(output_dict['detection_classes'][index]).copy()
                                #                 box is of shape ymin,xmin,ymax,xmax
                                ymin,xmin,ymax,xmax = box
                                left,right,top,bottom = xmin*img_width,xmax*img_width,ymin*img_height,ymax*img_height
                                class_name['box'] = {'left':left,'right':right,'top':top,'bottom':bottom}
                                result.append(class_name)
                                #                 index = index + 1

                        print (result)
                        return result


def disp(img):
        #  read encoded image
        imageString = base64.b64decode(img)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)

        #  convert binary data to numpy array
        nparr = np.fromstring(imageString, np.uint8)

        #  let opencv decode image to correct format
        img = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
        cv2.imshow("frame", img)
        cv2.waitKey(0)

def hello():
        return 'Hello World'


