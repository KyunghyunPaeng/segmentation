import os
import sys
sys.path.append('./') # WSL lib denpendancy
import lib
import caffe
from lib.pascal_db import pascal_db
from lib.net_wrapper import net_wrapper
from lib.analyzer import analyzer
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import scipy


if __name__ == '__main__' :

	gpu_id = sys.argv[1]
	arch = sys.argv[2]
	setting = sys.argv[3]

	# load pascal db
	pascal = pascal_db('val','2012','/data/PASCAL/VOCdevkit/', 'seg')
	
	deploy = './0__MODELS/' + arch + '/' + setting + '/test.prototxt'
	model  = './0__MODELS/' + arch + '/' + setting + '/ft_models/final.caffemodel'
	net = net_wrapper(deploy, model, int(gpu_id))
	
	comp_id = setting
	save_path = os.path.join(pascal._devkit_path, 'results', 'VOC' + pascal._year, 'Segmentation', comp_id + '_' + pascal._image_set + '_cls' )
	if not os.path.exists( save_path ) :
		os.makedirs( save_path )
	
	for i, ind in enumerate(pascal._image_index) :
		image_path = os.path.join( pascal._data_path, 'JPEGImages', ind + pascal._image_ext )
		net.run_forward(image_path)
		res = net._output['prob']
		label_map = np.argmax(res[0],axis=0).astype(np.uint8)
		gt_path = os.path.join( pascal._data_path, 'SegmentationClass', ind + '.png' )
		gt = Image.open(gt_path)
		res_map = scipy.misc.toimage(label_map, pal=pascal._color_map, mode='P')
		res_map = res_map.resize( gt.size, Image.NEAREST )
		save_name = os.path.join( save_path, ind + '.png' )
		res_map.save(save_name)
		print '{:d} th image saved {}'.format(i, save_name)

	pascal.do_matlab_eval_seg(comp_id)
