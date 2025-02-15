import os.path as osp
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from pathlib import Path
from .registry import DATASETS
from .xml_style import XMLDataset

@DATASETS.register_module
class GrapheneDataset(XMLDataset):

    CLASSES = ('mono-layer')

    def __init__(self, **kwargs):
        super(GrapheneDataset, self).__init__(**kwargs)

    
    def load_annotations(self, ann_file):
        """ 
            ann_file is the pandas dataframe
        """
        df = pd.read_csv(ann_file)
        img_infos = []
        for xml in df.path:
            filename = Path(xml).with_suffix('.jpg')
            tree = ET.parse(xml)
            root = tree.getroot()
            size = root.find('size')
            width = int(size.find('width').text)
            height = int(size.find('height').text)
            img_infos.append(
                dict(id=Path(xml).stem,\
                     filename=filename,\
                     ann=xml, \
                     width=width,\
                     height=height))
        return img_infos

    def get_ann_info(self, idx):
        xml_path = self.img_infos[idx]['ann']
        
        tree = ET.parse(xml_path)
        root = tree.getroot()
        bboxes = []
        labels = []
        bboxes_ignore = []
        labels_ignore = []
        for obj in root.findall('object'):
            name = obj.find('name').text
            label = self.cat2label[name]
            difficult = int(obj.find('difficult').text)
            bnd_box = obj.find('bndbox')
            bbox = [
                int(bnd_box.find('xmin').text),
                int(bnd_box.find('ymin').text),
                int(bnd_box.find('xmax').text),
                int(bnd_box.find('ymax').text)
            ]
            ignore = False
            if self.min_size:
                assert not self.test_mode
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                if w < self.min_size or h < self.min_size:
                    ignore = True
            if difficult or ignore:
                bboxes_ignore.append(bbox)
                labels_ignore.append(label)
            else:
                bboxes.append(bbox)
                labels.append(label)
        if not bboxes:
            bboxes = np.zeros((0, 4))
            labels = np.zeros((0, ))
        else:
            bboxes = np.array(bboxes, ndmin=2) - 1
            labels = np.array(labels)
        if not bboxes_ignore:
            bboxes_ignore = np.zeros((0, 4))
            labels_ignore = np.zeros((0, ))
        else:
            bboxes_ignore = np.array(bboxes_ignore, ndmin=2) - 1
            labels_ignore = np.array(labels_ignore)
        ann = dict(
            bboxes=bboxes.astype(np.float32),
            labels=labels.astype(np.int64),
            bboxes_ignore=bboxes_ignore.astype(np.float32),
            labels_ignore=labels_ignore.astype(np.int64))
        return ann
