import cv2
import io
import os
import subprocess
import glob
import numpy as np
import random
base_dir = "/home/madhu_hegde/cs230/data/cholec_mini_data/"
base_image_dir = base_dir +"images/"
train_image_dir = base_image_dir+"train/"
test_image_dir = base_image_dir+"test/"
#label_dir = base_dir+"labels/"


class_labels = {"Preparation":0, "CalotTriangleDissection":1, "ClippingCutting":2, 
           "GallbladderDissection":3, "GallbladderPackaging":4, "CleaningCoagulation":5, "GallbladderRetraction":6}




def generator_old(samples, batch_size=32, frames_per_clip=4):
    num_samples = len(samples)
    
    while 1: # Loop forever so the generator never terminates
        random.shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            phases = []
            for batch_sample in batch_samples:
                image_file = image_dir+batch_sample[0]
                #phase = batch_sample[1]
                phase = class_labels[batch_sample[1].split('\t')[1].strip()]
                image = cv2.imread(image_file)
                image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_CUBIC)
                #image = (image-128.0)/128.0;
                image = image/255.0
                
                images.append([image]*frames_per_clip)
                phases.append(phase)

            
            # trim image to only see section with road
            X_batch = np.array(images)
            classes_one_hot = np.zeros((len(phases), len(class_labels)))
            classes_one_hot[np.arange(len(phases)), phases] = 1  
            y_batch = classes_one_hot
            yield (X_batch, y_batch)    
            
              
def generator_train(samples, batch_size=32, frames_per_clip=4):
    num_samples = len(samples)
    
    while 1: # Loop forever so the generator never terminates
        
        for offset in range(0, num_samples, batch_size*frames_per_clip):
            batch_samples = samples[offset:offset+batch_size*frames_per_clip]
            
            print('\t',offset, len(batch_samples))

            images = []
            phases = []
            for i in range(batch_size):
              # Read only one label for each frames_per_clip
              batch_sample = batch_samples[frames_per_clip*i]
              
              phase = class_labels[batch_sample[1].split('\t')[1]]
              phases.append(phase)
              
              consecutive_images = []
              #Read frame_per_clip images for every one label
              for j in range(frames_per_clip):
                
                batch_sample = batch_samples[j+i*frames_per_clip]
                image_file = train_image_dir+batch_sample[0]
                
                image = cv2.imread(image_file)
                image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_CUBIC)
                #image = (image-128.0)/128.0;
                image = image/255.0
               
                consecutive_images.append(image)
               
                
              images.append(consecutive_images)
               

            
            # trim image to only see section with road
        
            X_batch = np.array(images)
            classes_one_hot = np.zeros((len(phases), len(class_labels)))
            classes_one_hot[np.arange(len(phases)), phases] = 1  
            y_batch = classes_one_hot
            yield (X_batch, y_batch)   
            
            
def generator_test(samples, batch_size=32, frames_per_clip=4):
    num_samples = len(samples)
    
    while 1: # Loop forever so the generator never terminates
        
        for offset in range(0, num_samples, batch_size*frames_per_clip):
            batch_samples = samples[offset:offset+batch_size*frames_per_clip]
    

            images = []
            phases = []
            for i in range(batch_size):
              # Read only one label for each frames_per_clip
              batch_sample = batch_samples[frames_per_clip*i]
              
              phase = class_labels[batch_sample[1].split('\t')[1]]
              phases.append(phase)
              
              consecutive_images = []
              #Read frame_per_clip images for every one label
              for j in range(frames_per_clip):
                
                batch_sample = batch_samples[j+i*frames_per_clip]
                image_file = test_image_dir+batch_sample[0]
                
                image = cv2.imread(image_file)
                image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_CUBIC)
                #image = (image-128.0)/128.0;
                image = image/255.0
                consecutive_images.append(image)
               
                
              images.append(consecutive_images)
               

            
            # trim image to only see section with road
        
            X_batch = np.array(images)
            classes_one_hot = np.zeros((len(phases), len(class_labels)))
            classes_one_hot[np.arange(len(phases)), phases] = 1  
            y_batch = classes_one_hot
            yield (X_batch, y_batch)             
