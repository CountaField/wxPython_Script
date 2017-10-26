from numpy import *
import operator

def createDataSet():
    group=array([[3.0,1.1],
                 [5.0,1.0],
                 [0,0],
                 [0,0.1],
                 [3,3]
                 ])
    labels=['A','A','B','B','C']
    return group,labels


def classify0(inX,dataSet,labels,k):
    dataSetSize=dataSet.shape[0]
    print "this is shape",dataSetSize
    print"this is tile",tile(inX, (dataSetSize, 1)).min(0)
    diffMat=tile(inX,(dataSetSize,1)) - dataSet

    sqDiffMat=diffMat**2
    sqDistances=sqDiffMat.sum(axis=1)
    distances=sqDistances**0.5
    sortedDistIndicies=distances.argsort()
    classCount={}
    for i in range(k):
        voteIlabel=labels[sortedDistIndicies[i]]
        classCount[voteIlabel]=classCount.get(voteIlabel,0)+1
        sortedClassCount=sorted(classCount.iteritems(),
                                key=operator.itemgetter(1),
                                reverse=True
                                )
    return sortedClassCount[0][0]
group,labels=createDataSet()
#print classify0([5,5],group,labels,3)
print group.min(1)

