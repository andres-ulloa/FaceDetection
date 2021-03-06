
import numpy as np
import pandas as pd
from fully_connected_layer import classification_layer
import matplotlib.pyplot as plt 

label_position = 28 * 28

num_epochs = 10000
hidden_layer_size = 20
learning_rate = 0.005

class class_performance:

    def __init__(self, F, P, PDR, NDR):
        self.F = F
        self.precision = P
        self.positive_detection_rate = PDR
        self.negative_detection_rate = NDR

    def print_roc(self):
        print('PRINTING ROC METRICS: ')
        print('F = ', self.F)
        print('P = ', self.precision)
        print('PDR = ', self.positive_detection_rate)
        print('NDR = ', self.negative_detection_rate)


def find_highest_scoring_class(vector):

    sorted_list = vector.copy()
    sorted_list.sort()
    target = sorted_list[len(sorted_list) - 1]
    best_score_index = 0

    for i in range(0, len(vector)):

        if vector[i] == target:
            best_score_index = i
            break

    return best_score_index


def map_ones_to_integer(binary_vector):
    for i in range(0 , len(binary_vector)):
        if binary_vector[i] == 1:
            return i 


def classify(dataset, true_labels ,model, identities):

    examples_counter = 0
    predictions = model.classify(dataset)
    results = []

    for num_example in range(0 , len(predictions)):

        highest_scoring_class = find_highest_scoring_class(predictions[num_example])
        label = (num_example, highest_scoring_class, map_ones_to_integer(true_labels[num_example]), identities[num_example])
        results.append(label)

    return results

def is_already_inside(saved, candidate, max_per_fold = 2):
    
    count = 0
    
    for member in saved:
        if np.array_equal(member, candidate):
            count += 1

    if count < max_per_fold:
        return False
    else:
        return True


def trim_dataset(dataset, train_set_size, test_set_size):
    
    training_set = list()
    test_set = list()
    
    for i in range(0, train_set_size + test_set_size):
        if i < train_set_size:
            training_set.append(dataset[i])
        if i >= train_set_size:
            test_set.append(dataset[i])

    return training_set, test_set



def compute_confution_matrix(labels, num_classes):
    
    confution_matrix_list = list()
    roc_metrics = list()

    for class_index  in range(0 , num_classes):

        true_positives = 0
        true_negatives = 0
        false_positives = 0
        false_negatives = 0
        
        PDR = NDR = P = F = 0 

        for label in labels:

            assigned_label = label[1]
            true_label = label[2]

            if assigned_label == true_label and assigned_label == class_index:
                true_positives += 1
                
            elif assigned_label == true_label and assigned_label != class_index:
                true_negatives += 1

            elif assigned_label !=  true_label and assigned_label != class_index:
                false_negatives += 1
                
            elif assigned_label != true_label and assigned_label == class_index:
                false_positives += 1
        
        if true_positives + false_negatives != 0:

            PDR = true_positives / (true_positives + false_negatives)

        if false_negatives + false_positives != 0:

            NDR = true_negatives/ (true_negatives + false_positives)
        if true_positives + false_positives != 0:

            P = true_positives/(true_positives + false_positives)
        if PDR + P != 0:
            F = ( 2 * PDR * P)/ (PDR + P)
        
        roc = class_performance(F,P,PDR,NDR)
        confution_matrix = np.array([[true_positives, false_positives],[false_negatives, true_negatives]])
        confution_matrix_list.append(confution_matrix)
        roc_metrics.append(roc)

    return confution_matrix_list, roc_metrics



def train(neural_net, dataset, num_epochs):

  
    print('------------------------------------------------------------------------------------------------------')
    print('----------------------------------INITIALIZING TRAINING-----------------------------------------------')
    print('------------------------------------------------------------------------------------------------------\n\n')
    print('Epochs = ', num_epochs)
    print('Alpha_rate = ', neural_net.learning_rate)
    print('Hidden layers = ', neural_net.num_hidden_layers)
    print('Input layer size = ', neural_net.input_layer_size)
    print('Hidden layer size = ', neural_net.hidden_layer_size)
    print('Output layer size = ', neural_net.output_layer_size)
    input('\nPress enter to continue...')
    print('\n\nTraining...')
    neural_net.initialize_weights()

    for i in range(0 , num_epochs):
        
        neural_net.run_shallow_activation_pass()
        neural_net.run_shallow_backpropagation()

    print('\nDone.')


def ensemble_model_from_file():

    input_layer_size = 28 * 28 #there are going to be as much input neurons as there are pixels in each image
    num_classes = 10
    num_hidden_layers = 1
    global hidden_layer_size  #not considering bias units so a + 1 size in each layer should always be taken into account
    global num_epochs
    training_set_size = 900
    test_set_size = 100
    num_layers = num_hidden_layers + 1
    global learning_rate 
    neural_net = classification_layer(input_layer_size, num_classes, num_hidden_layers, hidden_layer_size, learning_rate, num_layers, [0], [0]) 
    neural_net.load_weights_from_memory()

    print('Current model architecture: \n')
    print('Epochs = ', num_epochs)
    print('Alpha_rate = ', neural_net.learning_rate)
    print('Hidden layers = ', neural_net.num_hidden_layers)
    print('Input layer size = ', neural_net.input_layer_size)
    print('Hidden layer size = ', neural_net.hidden_layer_size)
    print('Output layer size = ', neural_net.output_layer_size)

    return neural_net


def demo():

    print('------------------------------------------------------------------------------------------------------')
    print('------------------------------------------RUNNING DEMO--------------------------------------------------')
    print('----------------------------------------------------------------------------------------------------\n\n')
    neural_net = ensemble_model_from_file()
    input('\nPress enter to continue...\n')

    test_set, test_identities, names = load_dataset('test_embeddings.csv','test_identities.txt','test_classes.txt')
    
    test_identities.pop()
    names.pop()

    test_labels = []

    for name in names: 
        test_labels.append(map_name_to_class(name))


    print('\nRunning retrieved model on Test set... \n')
    predictions = classify(test_set, test_labels, neural_net, test_identities)
    print(predictions)
    results, roc = compute_confution_matrix(predictions, 11)
    print('\nRESULTS = \n')
    for i in range(0, len(results)): print('Class ', i, '\n', results[i], '\n')
    print('\nROC PER CLASS = \n')
    for i in range(0, len(roc)): 
        print('Class ', i, '\n')
        roc[i].print_roc()
        print('\n')

    print('\nMEAN ROC PERFORMANCE = \n')
    PDR,NDR,P,F = mean_roc_performance(roc)
    print('F = ', F)
    print('P = ', P)
    print('PDR = ', PDR)
    print('NDR = ', NDR)


def plot_error_registry(error_registry):
    plt.plot(error_registry, linewidth = 3)
    plt.show()


def load_dataset(data_path, identities_path, labels_path):
    
    emebeddings = identities = labels = None
    
    emebeddings = np.loadtxt(data_path, delimiter = ',')
    
    identities_file = open(identities_path, "r")
    identities = identities_file.read().split('\n')
    identities_file.close()

    labels_file = open(labels_path, "r")
    labels = labels_file.read().split('\n')
    labels_file.close()

    return emebeddings, identities, labels


def map_name_to_class(name):
    
    if 'Aaron_Eckhart' == name:
        return np.array([1,0,0,0,0,0,0,0,0,0,0])

    elif 'Al_Pacino' == name:
        return np.array([0,1,0,0,0,0,0,0,0,0,0])

    elif 'Adrien_Brody' == name:
        return np.array([0,0,1,0,0,0,0,0,0,0,0])

    elif 'Leonardo_DiCaprio' == name:
        return np.array([0,0,0,1,0,0,0,0,0,0,0])

    elif 'Brad_Pitt' == name:
        return np.array([0,0,0,0,1,0,0,0,0,0,0])

    elif 'Angelina_Jolie' == name:
        return np.array([0,0,0,0,0,1,0,0,0,0,0])

    elif 'Matthew_Perry' == name:
        return np.array([0,0,0,0,0,0,1,0,0,0,0])

    elif 'Harrison_Ford' == name:
        return np.array([0,0,0,0,0,0,0,1,0,0,0])
    
    elif 'Vin_Diesel' == name:
        return  np.array([0,0,0,0,0,0,0,0,1,0,0])

    elif 'Adam_Sandler' == name:
        return np.array([0,0,0,0,0,0,0,0,0,1,0])

"""
      self.F = F
        self.precision = P
        self.positive_detection_rate = PDR
        self.negative_detection_rate = NDR
"""

def mean_roc_performance(roc_metrics):

    PDR = NDR = P = F = 0 
    for roc in roc_metrics:
        PDR += roc.positive_detection_rate
        NDR += roc.negative_detection_rate
        F += roc.F
        P += roc.precision
    
    PDR = PDR/len(roc_metrics)
    NDR = NDR/len(roc_metrics)
    F = F/len(roc_metrics)
    P = P/len(roc_metrics)

    return PDR,NDR,P,F


def shift_dataset(dataset, labels, identities, num_classes = 10):

    current = None
    test_set = []
    test_labels = []
    test_identities = []
    print(len(dataset))
    count_classes = 0

    for example in range(0 , len(dataset)):
        
        print(example)
        current = labels[example]

        if is_already_inside(current, test_labels) == True:
            print('we aint doing shit')
       
        else:
            
            test_set.append(dataset[example])
            dataset = np.delete(dataset, example)
            test_labels.append(labels[example])
            del labels[example]
            test_identities.append(identities[example])
            del identities[example]
            example = 0
            count_classes += 1
    
        if count_classes == num_classes:
            break

    print(len(dataset), ' ',len(test_set))

    return dataset, labels, identities, test_set, test_labels, test_identities


def train_model():

    training_set, identities_training, names = load_dataset('training_embeddings.csv','training_identities.txt','training_classes.txt')
    
    identities_training.pop()
    names.pop()

    training_labels = []

    for name in names: 
        training_labels.append(map_name_to_class(name))

    training_set_size = 100
    test_set_size = 20

    input_layer_size = 128
    num_classes = 11
    num_hidden_layers = 1

    global hidden_layer_size  #not considering bias units so a + 1 size in each layer should always be taken into consideration
    global num_epochs
  
    num_layers = num_hidden_layers + 1
    global learning_rate

    neural_net = classification_layer(input_layer_size, num_classes, num_hidden_layers, hidden_layer_size, learning_rate, num_layers, training_set, training_labels) 
    train(neural_net, training_set, num_epochs)
    neural_net.save_weights()
    print('Final error = ', neural_net.error_registry[len(neural_net.error_registry) - 1])
    plot_error_registry(neural_net.error_registry)
    
    
    results = classify(training_set, training_labels, neural_net, identities_training)
    
    print(results)
    confution_matrix, roc  = compute_confution_matrix(results, 11)
    print('\nRESULTS = \n')
    for i in range(0, len(results)): print('Class ', i, '\n', results[i], '\n')
    


if __name__ == '__main__':
    
    u_input = input('Train a new architecture?(Y/N)\n')
    if u_input.lower() == 'y':
        train_model()
    else:
        demo()
    
 