# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import cv2
import math, os
import tensorflow as tf
import matplotlib.pyplot as plt
from keras.layers import *
from category_encoders import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All"
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

FileList = []
base_path = 'kaggle/input/billboards-signs-and-branding/billboards-signs-and-branding.2022-08-07T102240Z/annotations/'
for file in os.listdir('kaggle/input/billboards-signs-and-branding/billboards-signs-and-branding.2022-08-07T102240Z/annotations/'):
    df = pd.read_csv(base_path + file)
    FileList.append(df)

dfMerge = pd.concat(FileList)
dfMerge.label.unique()

Target = {k: v for k, v in zip(['billboard', 'signage', 'branding'], list(range(3)))}
for i in range(dfMerge.shape[0]):
    dfMerge.iloc[i, -1] = Target[dfMerge.iloc[i, -1]]
X = np.array(dfMerge.iloc[:, 0:-1])
y = np.asarray(dfMerge.iloc[:, -1]).astype('int64')


def create_dataset(X_data, y_data):
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    X_train = tf.cast(X_train, tf.float32)
    X_test = tf.cast(X_test, tf.float32)
    y_train = tf.cast(y_train, tf.int64)
    y_test = tf.cast(y_test, tf.int64)

    return X_train, X_test, y_train, y_test


X_train, X_test, y_train, y_test = create_dataset(X, y)

print(X_train[0])

def GELU(x):
    res = 0.5 * x * (1 + tf.nn.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * (x ** 3))))
    return res


# 定义残差MLP结构块
class ResMLPBlock(tf.keras.layers.Layer):
    def __init__(self, units, residual_path):
        super(ResMLPBlock, self).__init__()
        self.residual_path = residual_path
        self.D1 = Dense(units, activation='relu')
        self.D2 = Dense(units, activation='relu')

        if self.residual_path:
            self.D3 = Dense(units)
            self.D4 = Dense(units)

    def call(self, inputs):
        residual = inputs

        x = self.D1(inputs)
        y = self.D2(x)

        if self.residual_path:
            residual = self.D3(inputs)
            residual = GELU(residual)
            residual = self.D4(residual)
            residual = GELU(residual)

        output = y + residual
        return output

class ResMLP(tf.keras.Model):
    def __init__(self, initial_filters, block_list, num_classes):
        super(ResMLP, self).__init__()
        self.initial_filters = initial_filters
        self.block_list = block_list

        self.D1 = Dense(self.initial_filters, activation='relu')
        self.B1 = BatchNormalization()

        self.blocks = tf.keras.models.Sequential()
        for block_id in range(len(block_list)):
            for layer_id in range(block_list[block_id]):
                if block_id != 0 and layer_id == 0:
                    block = ResMLPBlock(units=self.initial_filters, residual_path=True)
                else:
                    block = ResMLPBlock(units=self.initial_filters, residual_path=False)
                self.blocks.add(block)
            self.initial_filters *= 2

        self.D2 = Dense(num_classes, activation='softmax')


    def call(self, inputs):
        x = self.D1(inputs)
        x = self.B1(x)
        x = self.blocks(x)
        y = self.D2(x)
        return y

net = ResMLP(initial_filters=32, block_list=[2, 2, 2], num_classes=3)

net.compile(optimizer='adam',
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
            metrics=['sparse_categorical_accuracy'])

checkpoint_save_path = 'checkpoint/ResMLP.ckpt'
if os.path.exists(checkpoint_save_path + '.index'):
    print('-------------------------------------Loading-------------------------------------')
    net.load_weights(checkpoint_save_path)

cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_save_path,
                                                  save_weights_only=True,
                                                  save_best_only=True)

history = net.fit(X_train, y_train, batch_size=32, epochs=150, validation_data=(X_test, y_test))

# 打印网络结构
net.summary()

acc = history.history['sparse_categorical_accuracy']
val_acc = history.history['val_sparse_categorical_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(16, 8))
plt.subplot(1, 2, 1)
plt.plot(acc, label='Training Acc')
plt.plot(val_acc, label='Validation Acc')
plt.title('Training And Validation Acc')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.title('Training And Validation Loss')

plt.legend()
plt.show()

# evaluate the keras model
_, accuracy = net.evaluate(X, y)
print('Accuracy: %.2f' % (accuracy*100))

predictions = net.predict(X)

for i in range(687):
    print(X[i])
    print(predictions[i])
    print(y[i])