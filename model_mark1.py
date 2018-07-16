import numpy as np
import os
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model
from keras.layers import Dropout, Flatten, Dense, Conv2D, MaxPooling2D, Concatenate
from keras import initializers, regularizers, applications
from keras.optimizers import Adam, SGD
import datetime
import time
import glob
import shutil
from keras import backend as K

# dimensions of our images.
img_width, img_height = 150, 150
start = time.clock()

top_model_weights_path = 'bottleneck_fc_model.h5'
train_data_dir = './mark_1/train'
validation_data_dir = './mark_1/val'
test_data_dir = './mark_1/test'


def get_filecount(path_to_directory):
    if os.path.exists(path_to_directory):
        path, dirs, files = os.walk(path_to_directory).__next__()
        file_count = len(files)
        return file_count
    else:
        print("path does not exist")
        return 0


def round_off(dirc, no_dp):
    list_of_files = glob.glob(dirc + '/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    for i in range(no_dp):
        shutil.copy(latest_file, dirc + '/' + 'dub' + str(i + 1) + '.jpg')
        i += 1
    return


epochs = 10
batch_size = 8

nb_train_1_samples = get_filecount("mark_1/train/rate1")
nb_train_2_samples = get_filecount("mark_1/train/rate2")
nb_train_3_samples = get_filecount("mark_1/train/rate3")
nb_train_4_samples = get_filecount("mark_1/train/rate4")
nb_train_5_samples = get_filecount("mark_1/train/rate5")

# nb_train_samples = 3472

nb_train_1_samples = nb_train_1_samples - nb_train_1_samples % batch_size
nb_train_2_samples = nb_train_2_samples - nb_train_2_samples % batch_size
nb_train_3_samples = nb_train_3_samples - nb_train_3_samples % batch_size
nb_train_4_samples = nb_train_4_samples - nb_train_4_samples % batch_size
nb_train_5_samples = nb_train_5_samples - nb_train_5_samples % batch_size
nb_train_samples = nb_train_1_samples + nb_train_2_samples + nb_train_3_samples + nb_train_4_samples + nb_train_5_samples

nb_val_1_samples = get_filecount("mark_1/val/rate1")
nb_val_2_samples = get_filecount("mark_1/val/rate2")
nb_val_3_samples = get_filecount("mark_1/val/rate3")
nb_val_4_samples = get_filecount("mark_1/val/rate4")
nb_val_5_samples = get_filecount("mark_1/val/rate5")

# nb_validation_samples =740

nb_val_1_samples = nb_val_1_samples - nb_val_1_samples % batch_size
nb_val_2_samples = nb_val_2_samples - nb_val_2_samples % batch_size
nb_val_3_samples = nb_val_3_samples - nb_val_3_samples % batch_size
nb_val_4_samples = nb_val_4_samples - nb_val_4_samples % batch_size
nb_val_5_samples = nb_val_5_samples - nb_val_5_samples % batch_size
nb_validation_samples = nb_val_1_samples + nb_val_2_samples + nb_val_3_samples + nb_val_3_samples + nb_val_4_samples + nb_val_5_samples

nb_test_1 = get_filecount("mark_1/test/rate1")
nb_test_2 = get_filecount("mark_1/test/rate2")
nb_test_3 = get_filecount("mark_1/test/rate3")
nb_test_4 = get_filecount("mark_1/test/rate4")
nb_test_5 = get_filecount("mark_1/test/rate5")

nb_test_1 = nb_test_1 - nb_test_1 % batch_size
nb_test_2 = nb_test_2 - nb_test_2 % batch_size
nb_test_3 = nb_test_3 - nb_test_3 % batch_size
nb_test_4 = nb_test_4 - nb_test_4 % batch_size
nb_test_5 = nb_test_5 - nb_test_5 % batch_size
nb_test_samples = nb_test_1 + nb_test_2 + nb_test_3 + nb_test_4 + nb_test_5

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)


def save_bottlebeck_features():
    print('\n\nsaving bottleneck_features...')
    datagen = ImageDataGenerator(rescale=1. / 255)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet', classes=5)
    print('1, VGG16 model has been loaded\n')

    # For the training data
    generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_train = model.predict_generator(
        generator, nb_train_samples // batch_size)

    np.save(open('bottleneck_features_train.npy', 'wb'),
            bottleneck_features_train)
    print("bottleneck features for the training data has been stored")

    # for the validation data
    generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_validation = model.predict_generator(
        generator, nb_validation_samples // batch_size)
    np.save(open('bottleneck_features_validation.npy', 'wb'),
            bottleneck_features_validation)
    print("bottleneck features for the validation data has been stored")

    # For the test data
    generator = datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_test = model.predict_generator(
        generator, nb_test_samples // batch_size)
    np.save(open('bottleneck_features_test.npy', 'wb'),
            bottleneck_features_test)
    print("bottleneck features for the test data has been stored")


def train_top_model():
    print('training model...')
    train_data = np.load(open('bottleneck_features_train.npy', 'rb'))
    train_labels = np.array(
        [-2] * int(nb_train_1_samples) + [-1] * int(nb_train_2_samples) + [0] * int(nb_train_3_samples) + [1] * int(
            nb_train_4_samples) + [2] * int(nb_train_5_samples))

    validation_data = np.load(open('bottleneck_features_validation.npy', 'rb'))
    validation_labels = np.array([-2] * int(nb_val_1_samples) + [-1] * int(nb_val_2_samples) + [0] * int(nb_val_3_samples) +[1] *
        int(nb_val_4_samples)+ [2] * int(nb_val_5_samples))

    test_data = np.load(open('bottleneck_features_test.npy', 'rb'))
    test_labels = np.array(
        [-2] * int(nb_test_1) + [-1] * int(nb_test_2) + [0] * int(nb_test_3) + [1] * int(nb_test_4) + [2] * int(
            nb_test_5))

    model = Sequential()

    # Inception Model

    # Block1 = Sequential()
    # Block2 = Sequential()
    # Block3 = Sequential()
    # Block4 = Sequential()
    #
    # Block1.add(Conv2D(256, (1, 1), activation='relu', padding='same',input_shape=train_data.shape[1:]))
    # Block1.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
    #
    # Block2.add(Conv2D(256, (1, 1), activation='relu', padding='same',input_shape=train_data.shape[1:]))
    # Block2.add(Conv2D(64, (5, 5), activation='relu', padding='same'))
    #
    # Block3.add(Conv2D(128, (1, 1), activation='relu', padding='same', input_shape=train_data.shape[1:]))
    #
    # Block4.add(Conv2D(256, (1, 1), activation='relu', padding='same', input_shape=train_data.shape[1:]))
    # Block4.add(MaxPooling2D(pool_size=(2, 2), strides=1, padding='same'))
    #
    # model.add(Concatenate([Block1, Block2, Block3, Block4],input_shape=train_data.shape[1:]))

    # model.add(merged ,input_shape=train_data.shape[1:])

    # Inception over

    model.add(Flatten(input_shape=train_data.shape[1:]))
    model.add(Dense(4096, kernel_initializer=initializers.glorot_uniform(seed=None), kernel_regularizer=regularizers.l2(0.01),
              activation='relu'))
    model.add(Dropout(0.4))
    model.add(Dense(5, activation='softmax'))
    print('3')

    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
    sgd = SGD(lr=1e-4, decay=1e-6, momentum=0.9, nesterov=True)

    # optimizer = sgd
    optimizer = adam
    model.compile(optimizer=optimizer,
                  loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    print(len(train_data))
    print(len(train_labels))
    print(len(validation_data))
    print(len(validation_labels))

    print("shape of the model output = ", model.output_shape)
    model.fit(train_data, train_labels,
              epochs=epochs,
              batch_size=batch_size,
              validation_data=(validation_data, validation_labels))
    # model.save_weights(top_model_weights_path)
    name = 'Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    model.save('model_two_adam2_with_conv2D.h5')

    scores = model.evaluate(test_data, test_labels,
                            batch_size=batch_size,
                            verbose=2,
                            sample_weight=None,
                            steps=None)

    scores1 = model.predict(test_data, batch_size=batch_size, verbose=2)
    print("\n\n")
    print(scores1)
    print("\n\n")
    print(scores)
    print("\n\n")
    diff = scores - scores1
    print(diff)
    print("test_acc: ", "%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))

    print('4 : Done and Dusted')


save_bottlebeck_features()
train_top_model()
print("\n\ntime taken =", time.clock() - start)
