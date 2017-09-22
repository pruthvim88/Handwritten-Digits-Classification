import numpy as np
from scipy.optimize import minimize
from scipy.io import loadmat
from math import sqrt
import pickle

def initializeWeights(n_in, n_out):
    """
    # initializeWeights return the random weights for Neural Network given the
    # number of node in the input layer and output layer

    # Input:
    # n_in: number of nodes of the input layer
    # n_out: number of nodes of the output layer

    # Output: 
    # W: matrix of random initial weights with size (n_out x (n_in + 1))"""

    epsilon = sqrt(6) / sqrt(n_in + n_out + 1)
    W = (np.random.rand(n_out, n_in + 1) * 2 * epsilon) - epsilon
    return W


def sigmoid(z):
    """# Notice that z can be a scalar, a vector or a matrix
    # return the sigmoid of input z"""
    z = np.array(z,dtype='float')
    s = 1.0 / (1.0 + np.exp(-1.0 * z))

    return s # your code here

def preprocess():

    mat = loadmat('mnist_all.mat')  # loads the MAT object as a Dictionary

    # Pick a reasonable size for validation data

    train0 = mat.get('train0')
    train1 = mat.get('train1')
    train2 = mat.get('train2')
    train3 = mat.get('train3')
    train4 = mat.get('train4')
    train5 = mat.get('train5')
    train6 = mat.get('train6')
    train7 = mat.get('train7')
    train8 = mat.get('train8')
    train9 = mat.get('train9')
    test0 = mat.get('test0')
    test1 = mat.get('test1')
    test2 = mat.get('test2')
    test3 = mat.get('test3')
    test4 = mat.get('test4')
    test5 = mat.get('test5')
    test6 = mat.get('test6')
    test7 = mat.get('test7')
    test8 = mat.get('test8')
    test9 = mat.get('test9')

    total = np.concatenate((train0,train1,train2,train3,train4,train5,train6,train7,train8,train9,test0,test1,test2,test3,test4,test5,test6,test7,test8,test9),axis=0)

    variance=np.var(total, axis=0)
    mask = (variance > 1)

    # ------------Initialize preprocess arrays----------------------#
    train_preprocess = np.zeros(shape=(50000, 784))
    validation_preprocess = np.zeros(shape=(10000, 784))
    test_preprocess = np.zeros(shape=(10000, 784))
    train_label_preprocess = np.zeros(shape=(50000,))
    validation_label_preprocess = np.zeros(shape=(10000,))
    test_label_preprocess = np.zeros(shape=(10000,))
    # ------------Initialize flag variables----------------------#
    train_len = 0
    validation_len = 0
    test_len = 0
    train_label_len = 0
    validation_label_len = 0
    # ------------Start to split the data set into 6 arrays-----------#
    for key in mat:
        # -----------when the set is training set--------------------#
        if "train" in key:
            label = key[-1]  # record the corresponding label
            tup = mat.get(key)
            sap = range(tup.shape[0])
            tup_perm = np.random.permutation(sap)
            tup_len = len(tup)  # get the length of current training set
            tag_len = tup_len - 1000  # defines the number of examples which will be added into the training set

            # ---------------------adding data to training set-------------------------#
            train_preprocess[train_len:train_len + tag_len] = tup[tup_perm[1000:], :]
            train_len += tag_len

            train_label_preprocess[train_label_len:train_label_len + tag_len] = label
            train_label_len += tag_len

            # ---------------------adding data to validation set-------------------------#
            validation_preprocess[validation_len:validation_len + 1000] = tup[tup_perm[0:1000], :]
            validation_len += 1000

            validation_label_preprocess[validation_label_len:validation_label_len + 1000] = label
            validation_label_len += 1000

            # ---------------------adding data to test set-------------------------#
        elif "test" in key:
            label = key[-1]
            tup = mat.get(key)
            sap = range(tup.shape[0])
            tup_perm = np.random.permutation(sap)
            tup_len = len(tup)
            test_label_preprocess[test_len:test_len + tup_len] = label
            test_preprocess[test_len:test_len + tup_len] = tup[tup_perm]
            test_len += tup_len
            # ---------------------Shuffle,double and normalize-------------------------#
    train_size = range(train_preprocess.shape[0])
    train_perm = np.random.permutation(train_size)
    train_data = train_preprocess[train_perm]
    train_data = np.double(train_data)
    train_data = train_data / 255.0
    train_label = train_label_preprocess[train_perm]

    validation_size = range(validation_preprocess.shape[0])
    vali_perm = np.random.permutation(validation_size)
    validation_data = validation_preprocess[vali_perm]
    validation_data = np.double(validation_data)
    validation_data = validation_data / 255.0
    validation_label = validation_label_preprocess[vali_perm]

    test_size = range(test_preprocess.shape[0])
    test_perm = np.random.permutation(test_size)
    test_data = test_preprocess[test_perm]
    test_data = np.double(test_data)
    test_data = test_data / 255.0
    test_label = test_label_preprocess[test_perm]

    # Feature selection
    train_data = np.delete(train_data,np.where(mask==False),axis=1)
    validation_data = np.delete(validation_data,np.where(mask==False),axis=1)
    test_data = np.delete(test_data,np.where(mask==False),axis=1)
    
    selected_features = np.where(mask == True)[0]
    print('preprocess done')

    return selected_features, train_data, train_label, validation_data, validation_label, test_data, test_label

def nnObjFunction(params, *args):

    n_input, n_hidden, n_class, training_data, training_label, lambdaval = args

    w1 = params[0:n_hidden * (n_input + 1)].reshape((n_hidden, (n_input + 1)))
    w2 = params[(n_hidden * (n_input + 1)):].reshape((n_class, (n_hidden + 1)))
    obj_val = 0

    # Adding  bias to the training data

    #1 of k encoding
    training_label=(np.equal.outer(training_label, np.arange(n_class)).astype(np.float))

    b = np.ones((training_data.shape[0],training_data.shape[1]+1))
    b[:,:-1] = training_data
    training_data = b

    #Computing the sigmoid on the output from input layers
    zj = sigmoid(np.dot(training_data,w1.T))

    # Adding  bias to the hidden layers
    b = np.ones((zj.shape[0],zj.shape[1]+1))
    b[:,:-1] = zj
    zj = b

    #Computing the sigmoid on the output from hidden layers
    ol = sigmoid(np.dot(zj,w2.T))

    #Objective Function
    obj_val_reg_less = -np.sum(np.multiply(training_label,np.log(ol))+np.multiply((1-training_label),np.log(1-ol)))/training_data.shape[0]
    #Regularized objective function
    obj_val_reg = (lambdaval/(2*training_data.shape[0]))*(np.sum(np.square(w1))+np.sum(np.square(w2)))
    obj_val = obj_val_reg + obj_val_reg_less

    #Gradient computation
    #Back Propogation
    delta_l = ol - training_label
    grad_w2_reg_less = np.dot(delta_l.T,zj)
    grad_w1_reg_less = np.dot(np.multiply(np.multiply((1-zj),zj),np.dot(delta_l,w2)).T,training_data)
    grad_w1_reg_less = np.delete(grad_w1_reg_less,n_hidden,axis=0)
    
    #Regularized gradient
    grad_w1  = (grad_w1_reg_less + lambdaval*w1)/training_data.shape[0]
    grad_w2  = (grad_w2_reg_less + lambdaval*w2)/training_data.shape[0]

    #Flattened array of the gradient
    obj_grad = np.concatenate((grad_w1.flatten(), grad_w2.flatten()),0)

    return (obj_val, obj_grad)

def nnPredict(w1, w2, data):

    labels = np.array([])

    b = np.ones((data.shape[0],data.shape[1]+1))
    b[:,:-1] = data
    data = b
    
    zj = np.dot(data,w1.T)
    zj = sigmoid(zj)

    b = np.ones((zj.shape[0],zj.shape[1]+1))
    b[:,:-1] = zj
    zj = b

    ol = np.dot(zj,w2.T)
    ol = sigmoid(ol) 
    
    labels = np.argmax(ol,axis=1)

    return labels


"""**************Neural Network Script Starts here********************************"""

selected_features, train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

#  Train Neural Network

# set the number of nodes in input unit (not including bias unit)
n_input = train_data.shape[1]

# set the number of nodes in hidden unit (not including bias unit)
n_hidden = 80

# set the number of nodes in output unit
n_class = 10

# initialize the weights into some random matrices
initial_w1 = initializeWeights(n_input, n_hidden)
initial_w2 = initializeWeights(n_hidden, n_class)

# unroll 2 weight matrices into single column vector
initialWeights = np.concatenate((initial_w1.flatten(), initial_w2.flatten()), 0)

# set the regularization hyper-parameter
lambdaval = 10

args = (n_input, n_hidden, n_class, train_data, train_label, lambdaval)

# Train Neural Network using fmin_cg or minimize from scipy,optimize module. Check documentation for a working example

opts = {'maxiter': 50}  # Preferred value.

nn_params = minimize(nnObjFunction, initialWeights, jac=True, args=args, method='CG', options=opts)

# In Case you want to use fmin_cg, you may have to split the nnObjectFunction to two functions nnObjFunctionVal
# and nnObjGradient. Check documentation for this function before you proceed.
# nn_params, cost = fmin_cg(nnObjFunctionVal, initialWeights, nnObjGradient,args = args, maxiter = 50)


# Reshape nnParams from 1D vector into w1 and w2 matrices
w1 = nn_params.x[0:n_hidden * (n_input + 1)].reshape((n_hidden, (n_input + 1)))
w2 = nn_params.x[(n_hidden * (n_input + 1)):].reshape((n_class, (n_hidden + 1)))

# Test the computed parameters

predicted_label = nnPredict(w1, w2, train_data)

# find the accuracy on Training Dataset
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')

predicted_label = nnPredict(w1, w2, validation_data)

# find the accuracy on Validation Dataset

print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')

predicted_label = nnPredict(w1, w2, test_data)

# find the accuracy on Validation Dataset

print('\n Test set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')

obj = [selected_features, n_hidden, w1, w2, lambdaval]
# selected_features is a list of feature indices that you use after removing unwanted features in feature selection step
pickle.dump(obj, open('params.pickle', 'wb'))