import numpy as np
import os
import time
from CNN_LSTM_load_data import load_cholec_data, generator
from CNN_LSTM_split_data import split_cholec_data, train_test_data_split
import tensorflow

from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.optimizers import Nadam

os.environ['KMP_DUPLICATE_LIB_OK']='True'

base_dir = "/Users/madhuhegde/Downloads/cholec80/"
image_dir = base_dir+"images/"
label_dir = base_dir+"labels/"

class_labels = {"Preparation":0, "CalotTriangleDissection":1, "ClippingCutting":2, 
           "GallbladderDissection":3, "GallbladderPackaging":4, "CleaningCoagulation":5, "GallbladderRetraction":6}


num_classes = 7

# just rename some varialbes
frames = 4
channels = 3
rows = 224
columns = 224 



video = Input(shape=(frames,rows,columns,channels))

cnn_base = VGG16(input_shape=(rows,columns,channels),
                 weights="imagenet",
                 include_top=False)
                             

cnn_out = GlobalAveragePooling2D()(cnn_base.output)

cnn = Model(inputs=cnn_base.input, outputs=cnn_out)

#cnn.trainable = True

#Use Transfer learning and train only last 4 layers                 
for layer in cnn.layers[:-5]:
   layer.trainable = False     


cnn.summary()

#for layer in cnn.layers:
#   print(layer.trainable)
      
encoded_frames = TimeDistributed(cnn)(video)

#encoded_sequence = LSTM(256)(encoded_frames)
encoded_sequence = LSTM(80)(encoded_frames)

#hidden_layer = Dense(output_dim=1024, activation="relu")(encoded_sequence)
hidden_layer = Dense(units=80, activation="relu")(encoded_sequence)

outputs = Dense(units=num_classes, activation="softmax")(hidden_layer)

model = Model([video], outputs)

model.summary()

optimizer = Nadam(lr=0.002,
                  beta_1=0.9,
                  beta_2=0.999,
                  epsilon=1e-08,
                  schedule_decay=0.004)


model.compile(loss="categorical_crossentropy",
              optimizer=optimizer,
              metrics=["categorical_accuracy"]) 





#%%

#training parameters
BATCH_SIZE = 2 # increase if your system can cope with more data
nb_epochs = 4 # I once achieved 50% accuracy with 400 epochs. Feel free to change


#generate indices for train_array an test_array with train_test_split_ratio = 0.
train_test_split_ratio = 0.2
#[train_array, test_array] = split_cholec_data(image_dir, label_dir, train_test_split_ratio)
[train_samples, validation_samples]  = train_test_data_split(image_dir, label_dir, 0.2)

print ("Loading train data")
# load training data
train_generator = generator(train_samples, batch_size=BATCH_SIZE, frames_per_clip=frames)
validation_generator = generator(validation_samples, batch_size=BATCH_SIZE, frames_per_clip=frames)

model.fit_generator(train_generator, 
            steps_per_epoch=int(len(train_samples)/BATCH_SIZE), 
            validation_data=validation_generator, 
            validation_steps=int(len(validation_samples)/BATCH_SIZE), 
            epochs=2, verbose=1)




