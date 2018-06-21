#12/06/18 willo
import os

print 'LUS2 willo'

#OFFSET FOLDERS
DATA = '../data/'
TEMPLATES = '../templates/'
SANDBOX = 'sandbox/'
RESULT = '../result/'

#TRAIN FILES
train_data_in = DATA + 'NLSPARQL.train.data'
test_data_in = DATA + 'NLSPARQL.test.data'

#TEST FILES
train_file_crf = SANDBOX + 'train.data'
test_file_crf = SANDBOX + 'test.data'

#SELECTED TEMPLATE
template_file = TEMPLATES + 'baseline/b1'

#WORKING FILES
model_file = SANDBOX + 'model'
encoded_test = SANDBOX + 'encoded_test.txt'
result_file = RESULT + 'performances.txt'


def import_data(in_file):
    """ Import the SENTENCE, POS, LEMMAS and CONCEPTS of the specified train file, the feats need to be in the same folder
    :param in_file: position of the .data file used to train and relative feats
        :type in_file: str
    :return: sentences, poss, lemmas, concepts
        :rtype sentences: list of list
        :rtype poss: list of list
        :rtype lemmas: list of list
        :rtype concepts: list of list
    """

    print '\n\tImport data'
    sentence = []
    concept = []
    sentences = []
    concepts = []
    for line in open(in_file, 'r'):
        if line != '\n':
            sentence += [ line.split()[0] ]
            concept += [ line.split()[1] ]
        else:
            sentences += [ sentence ]
            concepts += [ concept ]
            sentence = [ ]
            concept = [ ]
    pos = []
    lemma = []
    poss = []
    lemmas = []
    for line in open(in_file.replace('.data', '.feats.txt'), 'r'):
        if line != '\n':
            pos += [ line.split()[ 1 ] ]
            lemma += [ line.split()[ 2 ] ]
        else:
            poss += [ pos ]
            lemmas += [ lemma ]
            pos = [ ]
            lemma = [ ]
    print '\t--done'
    return sentences, poss, lemmas, concepts


def write_crf_input(out_file, sentences, poss, lemmas, concepts):
    """ Writes out the input in a crf compatible format all the four lists need to be the same dimension.
    :param out_file: the file in which the input will be written
    :param sentences: a list of sentence list
    :param poss: list of pos tag relative to the sentences
    :param lemmas: list of lemmas relative to the sentences
    :param concepts: list of concepts relative to the sentences
        :type out_file: str
        :type sentences: list of list
        :type poss: list of list
        :type lemmas: list of list
        :type concepts: list of list
    """

    print '\n\tWrite out data in crf compliant format'
    f = open(out_file, 'w+')
    for position_i in range(len(sentences)):
        for position_j in range(len(sentences[position_i])):
            f.write(
                sentences[ position_i ][ position_j ] + '\t' +
                poss[ position_i ][ position_j ] + '\t' +
                lemmas[ position_i ][ position_j ] + '\t' +
                concepts[ position_i ][ position_j ]
                + '\n'
            )
        f.write('\n')
    f.close()
    print '\t--done'


def train_crf(threads=3, hyperparameter_crf='1.5', cut_off='5', alg='CRF-L2'):
    """ Train the crf with the selected parameters on the TRAIN_SET, with the TEMPLATE_FILE, regards the crf parameters
    please refer to http://taku910.github.io/crfpp/
    :param threads: number of thread used by the train procedure
    :param hyperparameter_crf: set the hyperparameter of the crf, for larger values the crf tends to overfit
    :param cut_off: set the minimum amount of occourrences for the features to be took into consideration
    :param alg: changes the regularisation algorithm choose between: ['MIRA', 'CRF-L1', 'CRF-L2']
        :type threads: str
        :type hyperparameter_crf: str
        :type cut_off: str
        :type alg: str
    """

    print '\n\ttrain crf'
    os.system('crf_learn -p ' + threads +
              ' -c ' + hyperparameter_crf +
              ' -f ' + cut_off +
              ' -a ' + alg +
              ' ' + template_file + ' ' + train_file_crf + ' ' + model_file)
    print '\t--done\n'


def test_crf():
    """ Test the crf model in the MODEL_FILE with the TEST_FILE_CRF file and writes out the result in the ENCODED_TEST
    """

    print '\n\ttest crf'
    os.system('crf_test -m ' + model_file + ' ' + test_file_crf + ' -o ' + encoded_test)
    print '\t--done'


def evaluate_model():
    """ Evaluate the predictions contained in the ENCODED_TEST and writes the relative performances in the RESULT_FILE
    """

    print '\n\tevaluate result'
    os.system('./conlleval.pl -d \'\t\' < ' + encoded_test + ' >> ' + result_file)
    print '\t--done\n'


if __name__ ==  '__main__':

    #STEP 0: set hyperparameters
    threads='10'
    cut_off='5'
    hyperparameter_crf='1.5'
    alg='CRF-L2'

    #STEP 1: import train data and write out in crf compliant format
    sentences, poss, lemmas, concepts = import_data(train_data_in)
    write_crf_input(train_file_crf, sentences, poss, lemmas, concepts)

    #STEP 2: import test data and write out in crf compliant format
    sentences, poss, lemmas, concepts = import_data(test_data_in)
    write_crf_input(test_file_crf, sentences, poss, lemmas, concepts)

    #STEP 3: train crf
    train_crf(threads, hyperparameter_crf, cut_off, alg)

    #STEP 4: test output
    test_crf()

    #STEP 5: evaluate result
    evaluate_model()

    #OPTIONAL STEP 6: clean up sandbox
    os.system('rm ' + SANDBOX + '*')


print '\n--DONE'
