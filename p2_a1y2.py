# -*- coding: utf-8 -*-
"""VCP2_a1y2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xNi1Bk64QhNJpt3Esa_MQmtIK9sgb0b5
"""

# -*- coding: utf-8 -*-

#########################################################################
############ CARGAR LAS LIBRERÍAS NECESARIAS ############################
#########################################################################

# En caso de necesitar instalar keras en google colab,
# ejecutar la siguiente línea:
# !pip install -q keras
# Importar librerías necesarias
import numpy as np
import keras
import matplotlib.pyplot as plt
import keras.utils as np_utils

# Importar la función de split
from sklearn.model_selection import train_test_split

# Importar el optimizador a usar
from keras.optimizers import Adam

# Importar el conjunto de datos
from keras.datasets import cifar100

#########################################################################
######## FUNCIÓN PARA CARGAR Y MODIFICAR EL CONJUNTO DE DATOS ###########
#########################################################################

# A esta función solo se la llama una vez. Devuelve 4 
# vectores conteniendo, por este orden, las imágenes
# de entrenamiento, las clases de las imágenes de
# entrenamiento, las imágenes del conjunto de test y
# las clases del conjunto de test.
def cargarImagenes():
    # Cargamos Cifar100. Cada imagen tiene tamaño
    # (32 , 32, 3). Nos vamos a quedar con las
    # imágenes de 25 de las clases.
    (x_train, y_train), (x_test, y_test) = cifar100.load_data (label_mode ='fine')
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    train_idx = np.isin(y_train, np.arange(25))
    train_idx = np.reshape (train_idx, -1)
    x_train = x_train[train_idx]
    y_train = y_train[train_idx]
    test_idx = np.isin(y_test, np.arange(25))
    test_idx = np.reshape(test_idx, -1)
    x_test = x_test[test_idx]
    y_test = y_test[test_idx]
    
    # Transformamos los vectores de clases en matrices.
    # Cada componente se convierte en un vector de ceros
    # con un uno en la componente correspondiente a la
    # clase a la que pertenece la imagen. Este paso es
    # necesario para la clasificación multiclase en keras.
    y_train = np_utils.to_categorical(y_train, 25)
    y_test = np_utils.to_categorical(y_test, 25)
    
    return x_train , y_train , x_test , y_test

#########################################################################
######## FUNCIÓN PARA OBTENER EL ACCURACY DEL CONJUNTO DE TEST ##########
#########################################################################

# Esta función devuelve la accuracy de un modelo, 
# definida como el porcentaje de etiquetas bien predichas
# frente al total de etiquetas. Como parámetros es
# necesario pasarle el vector de etiquetas verdaderas
# y el vector de etiquetas predichas, en el formato de
# keras (matrices donde cada etiqueta ocupa una fila,
# con un 1 en la posición de la clase a la que pertenece y un 0 en las demás).
def calcularAccuracy(labels, preds):
    labels = np.argmax(labels, axis = 1)
    preds = np.argmax(preds, axis = 1)
    accuracy = sum(labels == preds)/len(labels)
    return accuracy

#########################################################################
## FUNCIÓN PARA PINTAR LA PÉRDIDA Y EL ACCURACY EN TRAIN Y VALIDACIÓN ###
#########################################################################

# Esta función pinta dos gráficas, una con la evolución
# de la función de pérdida en el conjunto de train y
# en el de validación, y otra con la evolución de la
# accuracy en el conjunto de train y el de validación.
# Es necesario pasarle como parámetro el historial del
# entrenamiento del modelo (lo que devuelven las
# funciones fit() y fit_generator()).
def mostrarEvolucion(hist):
    loss = hist.history['loss']
    val_loss = hist.history['val_loss']
    plt.plot(loss)
    plt.plot(val_loss)
    plt.legend(['Training loss', 'Validation loss'])
    plt.show()
    
    acc = hist.history['accuracy']
    val_acc = hist.history['val_accuracy']
    plt.plot(acc)
    plt.plot(val_acc)
    plt.legend(['Training accuracy','Validation accuracy'])
    plt.show()

#########################################################################
################## DEFINICIÓN DEL MODELO BASENET ########################
#########################################################################
def apartado1():
    #########################################################################
    ################## DEFINICIÓN DE HIPERPARÁMETROS ########################
    #########################################################################

    batch_size = 64

    epocas = 30

    # Cargar imágenes

    x_train, y_train, x_test, y_test = cargarImagenes()

    print("Ejercicio 1\n")

    print("Apartado 1")
    print("Generando modelo BaseNet...")

    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(6, (5,5), activation='relu', input_shape=(32,32,3)))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(16, (5,5), activation='relu'))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(50, activation='relu'))
    model.add(keras.layers.Dense(25, activation='softmax'))

    #model.summary()

    #########################################################################
    ######### DEFINICIÓN DEL OPTIMIZADOR Y COMPILACIÓN DEL MODELO ###########
    #########################################################################

    print("Compilando modelo...")

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])


    # Una vez tenemos el modelo base, y antes de entrenar, vamos a guardar los
    # pesos aleatorios con los que empieza la red, para poder reestablecerlos
    # después y comparar resultados entre no usar mejoras y sí usarlas.
    weights = model.get_weights()

    #########################################################################
    ###################### ENTRENAMIENTO DEL MODELO #########################
    #########################################################################

    print("Entrenando modelo...")

    model.set_weights(weights)

    datagen = keras.preprocessing.image.ImageDataGenerator(validation_split=0.1)

    historial = model.fit(datagen.flow(x_train,y_train,batch_size=batch_size, subset='training'),
                        steps_per_epoch=len(x_train)*0.9/batch_size,
                        epochs=epocas,
                        validation_data=datagen.flow(x_train,y_train,batch_size=batch_size, subset='validation'),
                        validation_steps=len(x_train)*0.1/batch_size)

    mostrarEvolucion(historial)

    #########################################################################
    ################ PREDICCIÓN SOBRE EL CONJUNTO DE TEST ###################
    #########################################################################

    test_loss, test_acc = model.evaluate(x_test,  y_test, verbose=0)
    print("Test loss:", test_loss)
    print("Test accuracy:", test_acc)


#########################################################################
########################## MEJORA DEL MODELO ############################
#########################################################################

def apartado2():
    print("Ejercicio 2")

    #########################################################################
    ################## DEFINICIÓN DE HIPERPARÁMETROS ########################
    #########################################################################

    batch_size = 64

    epocas = 30

    # Cargar imágenes

    x_train, y_train, x_test, y_test = cargarImagenes()
    print("Generando modelo BaseNet...")

    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(6, (5,5), activation='relu', input_shape=(32,32,3)))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(16, (5,5), activation='relu'))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(50, activation='relu'))
    model.add(keras.layers.Dense(25, activation='softmax'))

    #model.summary()

    #########################################################################
    ######### DEFINICIÓN DEL OPTIMIZADOR Y COMPILACIÓN DEL MODELO ###########
    #########################################################################

    print("Compilando modelo...")

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])


    # Una vez tenemos el modelo base, y antes de entrenar, vamos a guardar los
    # pesos aleatorios con los que empieza la red, para poder reestablecerlos
    # después y comparar resultados entre no usar mejoras y sí usarlas.
    weights = model.get_weights()


    # NORMALIZACION

    print("Entrenando modelo con datos normalizados...")

    model.set_weights(weights)

    datagen_tr = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_tr.fit(x_train)
    datagen_va = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_va.fit(x_train)

    x_train, y_train, x_test, y_test = cargarImagenes()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=46)

    historial = model.fit(datagen_tr.flow(x_train,y_train,batch_size=batch_size),
                        steps_per_epoch=len(x_train)/batch_size,
                        epochs=epocas,
                        validation_data=datagen_va.flow(x_val,y_val,batch_size=batch_size),
                        validation_steps=len(x_val)/batch_size)

    print("Resultados con datos normalizados:")

    mostrarEvolucion(historial)

    input("\n--- Pulse cualquier tecla para continuar ---\n")

    # DATA AUGMENTATION

    print("Entrenando modelo con data augmentation...")

    model.set_weights(weights)

    datagen_tr = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True,
                                                            featurewise_std_normalization=True,
                                                            rotation_range=45,
                                                            horizontal_flip=True)
    datagen_tr.fit(x_train)
    datagen_va = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_va.fit(x_train)

    x_train, y_train, x_test, y_test = cargarImagenes()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=46)

    historial = model.fit(datagen_tr.flow(x_train,y_train,batch_size=batch_size),
                        steps_per_epoch=len(x_train)/batch_size,
                        epochs=epocas,
                        validation_data=datagen_va.flow(x_val,y_val,batch_size=batch_size),
                        validation_steps=len(x_val)/batch_size)

    print("Resultados con data augmentation:")

    mostrarEvolucion(historial)

    input("\n--- Pulse cualquier tecla para continuar ---\n")

    # AUMENTO DE PROFUNDIDAD

    print("Generando modelo más profundo...")

    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(16, (3,3), padding='same', activation='relu', input_shape=(32,32,3)))
    model.add(keras.layers.Conv2D(16, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(32, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.Conv2D(32, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(50, activation='relu'))
    model.add(keras.layers.Dense(25, activation='softmax'))

    #model.summary()

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])

    weights = model.get_weights()

    datagen_tr = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True,
                                                            featurewise_std_normalization=True,
                                                            rotation_range=45,
                                                            horizontal_flip=True)

    print("Entrenando modelo más profundo...")
    datagen_tr.fit(x_train)
    datagen_va = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_va.fit(x_train)

    x_train, y_train, x_test, y_test = cargarImagenes()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=46)

    historial = model.fit(datagen_tr.flow(x_train,y_train,batch_size=batch_size),
                        steps_per_epoch=len(x_train)/batch_size,
                        epochs=epocas,
                        validation_data=datagen_va.flow(x_val,y_val,batch_size=batch_size),
                        validation_steps=len(x_val)/batch_size)

    print("Resultados de modelo más profundo:")

    mostrarEvolucion(historial)

    input("\n--- Pulse cualquier tecla para continuar ---\n")

    # EARLY STOPPING

    model.set_weights(weights)

    datagen_tr = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True,
                                                            featurewise_std_normalization=True,
                                                            rotation_range=45,
                                                            horizontal_flip=True)
    datagen_tr.fit(x_train)
    datagen_va = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_va.fit(x_train)

    e_stopping = keras.callbacks.EarlyStopping(monitor='val_accuracy',patience=7,restore_best_weights=True)

    x_train, y_train, x_test, y_test = cargarImagenes()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=46)

    historial = model.fit(datagen_tr.flow(x_train,y_train,batch_size=batch_size),
                        steps_per_epoch=len(x_train)/batch_size,
                        epochs=epocas,
                        callbacks=[e_stopping],
                        validation_data=datagen_va.flow(x_val,y_val,batch_size=batch_size),
                        validation_steps=len(x_val)/batch_size)

    mostrarEvolucion(historial)

    # BATCH NORMALIZATION

    print("Generando modelo con Batch Normalization...")

    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(16, (3,3), padding='same', activation='relu', input_shape=(32,32,3)))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Conv2D(16, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(32, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Conv2D(32, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(50, activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Dense(25, activation='softmax'))

    print("Compilando modelo con Batch Normalization...")

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])

    datagen_tr = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True,
                                                            featurewise_std_normalization=True,
                                                            rotation_range=45,
                                                            horizontal_flip=True)
    datagen_tr.fit(x_train)
    datagen_va = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_va.fit(x_train)

    e_stopping = keras.callbacks.EarlyStopping(monitor='val_accuracy',patience=7,restore_best_weights=True)

    x_train, y_train, x_test, y_test = cargarImagenes()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=46)

    print("Entrenando modelo con Batch Normalization...")

    historial = model.fit(datagen_tr.flow(x_train,y_train,batch_size=batch_size),
                        steps_per_epoch=len(x_train)/batch_size,
                        epochs=epocas,
                        callbacks=[e_stopping],
                        validation_data=datagen_va.flow(x_val,y_val,batch_size=batch_size),
                        validation_steps=len(x_val)/batch_size)

    print("Resultados de modelo con Batch Normalization:")

    mostrarEvolucion(historial)

    input("\n--- Pulse cualquier tecla para continuar ---\n")

    # DROPOUT

    print("Generando modelo con Dropour...")

    model = keras.models.Sequential()
    model.add(keras.layers.Conv2D(16, (3,3), padding='same', activation='relu', input_shape=(32,32,3)))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Conv2D(16, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(32, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Conv2D(32, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.MaxPooling2D((2,2)))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dropout(0.25))
    model.add(keras.layers.Dense(50, activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Dropout(0.25))
    model.add(keras.layers.Dense(25, activation='softmax'))

    print("Compilando modelo con Dropout...")

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])

    datagen_tr = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True,
                                                            featurewise_std_normalization=True,
                                                            rotation_range=45,
                                                            horizontal_flip=True)
    datagen_tr.fit(x_train)
    datagen_va = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_va.fit(x_train)

    e_stopping = keras.callbacks.EarlyStopping(monitor='val_accuracy',patience=7,restore_best_weights=True)

    x_train, y_train, x_test, y_test = cargarImagenes()
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=46)

    print("Entrenando modelo con Dropout...")

    historial = model.fit(datagen_tr.flow(x_train,y_train,batch_size=batch_size),
                        steps_per_epoch=len(x_train)/batch_size,
                        epochs=epocas,
                        callbacks=[e_stopping],
                        validation_data=datagen_va.flow(x_val,y_val,batch_size=batch_size),
                        validation_steps=len(x_val)/batch_size)

    print("Resultados de modelo con Dropout:")

    mostrarEvolucion(historial)

    input("\n--- Pulse cualquier tecla para continuar ---\n")

    #########################################################################
    ################ PREDICCIÓN SOBRE EL CONJUNTO DE TEST ###################
    #########################################################################

    datagen_te = keras.preprocessing.image.ImageDataGenerator(featurewise_center=True, featurewise_std_normalization=True)
    datagen_te.fit(x_test)

    acc = calcularAccuracy(y_test,model.predict(datagen_te.flow(x_test,y_test,batch_size=1,shuffle=False)))

    print("Test accuracy:", acc)
    
apartado1()
input("\n--- Pulse cualquier tecla para continuar ---\n")
apartado2()