import numpy as np
import cPickle as pickle
import scipy.sparse as sp
import networkx as nx
import threading
import Queue
import sys
import cv2
import math
import time
#np.random.seed(123)

class DataFetcher(threading.Thread):
	def __init__(self, file_list):
		super(DataFetcher, self).__init__()
		self.stopped = False
		self.queue = Queue.Queue(64)

		self.pkl_list = []
		with open(file_list, 'r') as f:
			while(True):
				line = f.readline().strip()
				if not line:
					break
				self.pkl_list.append(line)
		self.index = 0
		self.number = len(self.pkl_list)
		np.random.shuffle(self.pkl_list)

	def work(self, idx):
		pkl_path = self.pkl_list[idx]
		label = pickle.load(open(pkl_path, 'rb'))

		# load image file
		img_root = '/home/wnylol/data/ShapeNet/ShapeNetRendering/' # only thing need to change
		ids = pkl_path.split('/')[-1].split('_')
		img_path = img_root + ids[-3] + '/' + ids[-2] + '/rendering/' + ids[-1].replace('.dat','.png')
		img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

		img[np.where(img[:,:,3]==0)] = 255
		img = cv2.resize(img, (224,224))
		img_inp = img.astype('float32')/255.0

		return img_inp[:,:,:3], label, pkl_path.split('/')[-1]
	
	def run(self):
		while self.index < 9000000 and not self.stopped:
			self.queue.put(self.work(self.index % self.number))
			self.index += 1
			if self.index % self.number == 0:
				np.random.shuffle(self.pkl_list)
	
	def fetch(self):
		if self.stopped:
			return None
		return self.queue.get()
	
	def shutdown(self):
		self.stopped = True
		while not self.queue.empty():
			self.queue.get()

if __name__ == '__main__':
	file_list = sys.argv[1]
	data = DataFetcher(file_list)
	data.start()

	image,point,normal,_,_ = data.fetch()
	print image.shape
	print point.shape
	print normal.shape
	data.stopped = True
