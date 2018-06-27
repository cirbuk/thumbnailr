import numpy as np


from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications

# dimensions of our images.
img_width, img_height = 150, 150

top_model_weights_path = 'bottleneck_fc_model.h5'
train_data_dir = './th_data4/train'
validation_data_dir = './th_data4/validation'
test_data_dir = './th_data4/test'

nb_train_samples = 3472
nb_good_samples = 1989
nb_bad_samples = 1488
nb_validation_samples =736
nb_test_samples=128
epochs =10 
batch_size = 8
nb_bad_samples = nb_bad_samples - nb_bad_samples % batch_size
# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

def save_bottlebeck_features():
    print('saving bottleneck_features...')
    datagen = ImageDataGenerator(rescale=1. / 255)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet')
    print('1')
    generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    print('1.1')
    bottleneck_features_train = model.predict_generator(
        generator, nb_train_samples // batch_size)
    print('1.2')
    np.save(open('bottleneck_features_train.npy', 'wb'),
            bottleneck_features_train)
    print('1.3')
    generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    print('1.4')
    bottleneck_features_validation = model.predict_generator(
        generator, nb_validation_samples // batch_size)
    print('2')
    np.save(open('bottleneck_features_validation.npy', 'wb'),
            bottleneck_features_validation)

    generator = datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    print('2.1')
    bottleneck_features_test = model.predict_generator(
        generator, nb_test_samples // batch_size)
    print('2.2')
    np.save(open('bottleneck_features_test.npy', 'wb'),
            bottleneck_features_test)


def train_top_model():
    print('training model...')
    train_data = np.load(open('bottleneck_features_train.npy','rb'))
    train_labels = np.array([0]*nb_good_samples + [1]*nb_bad_samples)
        # [0] * int(nb_train_samples / 2) + [1] * int(nb_train_samples / 2))

    validation_data = np.load(open('bottleneck_features_validation.npy','rb'))
    validation_labels = np.array(
        [0] * int(nb_validation_samples / 2) + [1] * int(nb_validation_samples / 2))

    test_data = np.load(open('bottleneck_features_test.npy', 'rb'))
    test_labels = np.array([0]*int(nb_test_samples))
        # [0] * int(nb_test_samples / 2) + [1] * int(nb_test_samples / 2))

    model = Sequential()
    model.add(Flatten(input_shape=train_data.shape[1:]))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))
    print('3')
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy', metrics=['accuracy'])


    history = model.fit(train_data, train_labels,
              epochs=epochs,
              batch_size=batch_size,
              validation_data=(validation_data, validation_labels))
    model.save_weights(top_model_weights_path)
    model.save('second_model.h5')

    # scores = model.evaluate(test_data, test_labels,
    #                     epochs=epochs,
    #                     batch_size=batch_size,
    #                     validation_data=(test_data, test_labels))

    scores = model.evaluate(test_data, test_labels,
                            batch_size=batch_size,
                            verbose=1,
                            sample_weight=None,
                            steps=None)
    print("test_acc: ","%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))

   # loss, acc =model.evaluate(x, y, verbose=0)
   # print('\nTesting loss: {}, acc: {}\n'.format(loss, acc))
    # summarize history for accuracy
#    plt.plot(history.history['acc']) 
 #   plt.plot(history.history['val_acc'])
#    plt.title('model accuracy')
#    plt.ylabel('accuracy')
#    plt.xlabel('epoch')
#    plt.legend(['train', 'test'], loc='upper left')
#    plt.show()
    # summarize history for loss
#    plt.plot(history.history['loss'])
#    plt.plot(history.history['val_loss'])
#    plt.title('model loss')
#    plt.ylabel('loss')
#    plt.xlabel('epoch')
#    plt.legend(['train', 'test'], loc='upper left')

#    plt.plot(scores.scores['acc'])
#    plt.plot(scores.scores['val_acc'])
#    plt.title('test accuracy')
#    plt.show()
    print('4')

save_bottlebeck_features()
train_top_model()
