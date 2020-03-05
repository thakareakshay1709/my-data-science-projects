__author__ = 'user'
# http://pythonprogramming.net/support-vector-machine-svm-example-tutorial-scikit-learn-python/

import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn import svm

digits = datasets.load_digits()
print(digits)
print(digits.target)
#print(digits.data)

classifier = svm.SVC(gamma=0.0001, C=100)

print(len(digits.data))

x = digits.data[:7]
y = digits.target[:7]

#print(x)
classifier.fit(x, y)

print('Prediction1:', classifier.predict(digits.data[6:]))


plt.imshow(digits.images[6], cmap=plt.cm.gray_r, interpolation='nearest')

plt.show()