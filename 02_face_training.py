import cv2
import numpy as np
from PIL import Image
import os
import numpy as np
import cv2
import os
import h5py
import dlib
from imutils import face_utils
from keras.models import load_model
import sys
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D,Dropout
from keras.layers import Dense, Activation, Flatten
from keras.utils import to_categorical
from keras import backend as K 
from sklearn.model_selection import train_test_split
from Model import model
from keras import callbacks
import matplotlib.pyplot as plt
# Path for face image database

# face_id = 0
# while(face_id < 5):
#     j = 1
#     while(j<61):
#         cv2.imwrite("dataset/User." + str(face_id) + '.' + str(j) + ".jpg",cv2.COLOR_BGR2GRAY )
#         j += 1
#     face_id += 1
path = 'dataset'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");


def downsample_image(img):
    img = Image.fromarray(img.astype('uint8'), 'L')
    img = img.resize((32,32), Image.ANTIALIAS)
    return np.array(img)



# function to get the images and label data
def getImagesAndLabels(path):
    
    path = 'dataset'
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths:
        
        #if there is an error saving any jpegs
        try:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        except:
            continue    
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faceSamples.append(img_numpy)
        ids.append(id)
    return faceSamples,ids

print ("\n [INFO] Training faces now.")
faces,ids = getImagesAndLabels(path)

K.clear_session()
n_faces = len(set(ids))
model = model((32,32,1),n_faces)
faces = np.asarray(faces)
faces = np.array([downsample_image(ab) for ab in faces])
ids = np.asarray(ids)
faces = faces[:,:,:,np.newaxis]
print("Shape of Data: " + str(faces.shape))
print("Number of unique faces : " + str(n_faces))


ids = to_categorical(ids)

faces = faces.astype('float32')
faces /= 255.

x_train, x_test, y_train, y_test = train_test_split(faces,ids, test_size = 0.2, random_state = 0)

checkpoint = callbacks.ModelCheckpoint('trained_model.h5', monitor='val_acc',
                                           save_best_only=True, save_weights_only=True, verbose=1)
                                    
history = model.fit(x_train, y_train,
             batch_size=16,
             epochs=40,
             validation_data=(x_test, y_test),
             shuffle=True,callbacks=[checkpoint])

loss, acc = model.evaluate(x_test,y_test)

#plotting 
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model_accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train','Test'], loc = 'upper left')
plt.show()
plt.savefig('Model_Accuracy.jpg')

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model_loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train','Test'], loc = 'upper left')
plt.show()
plt.savefig('Model_loss.jpg')

model.save('trained_model.h5')
             

# Print the numer of faces trained and end program
print("\n [INFO] " + str(n_faces) + " faces trained. Exiting Program")
