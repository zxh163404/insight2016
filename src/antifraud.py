#%%
#Python 3.5
import sys
import csv

def load_data(filename):
    id1 = []  
    id2 = []
    amount = []
    message = [] 
    # The badlines indicate whether a line is a line with bad information 
    badlines = []

    infile=open(filename, "r", encoding="latin-1")
    ct = 0
    for row in csv.reader(infile):
        ct = ct + 1                                                  
        if len(row) >= 5:    #a valid row
            #This will skip the header line and those lines with bad quality data or not clean
            try:                                            
                id1.append(int(row[1]))
                id2.append(int(row[2]))
                amount.append(float(row[3]))
                message.append(row[4])                
                badlines.append(0)                
            except Exception as e:    
                id1.append(-1)
                id2.append(-1)
                amount.append(-1.0)
                message.append("-1")                  
                badlines.append(1)                
                #print(str(ct),row,'\n')  

        else:
            id1.append(-1)
            id2.append(-1)
            amount.append(-1.0)
            message.append("-1")                  
            badlines.append(1)                
            #print(str(ct),row,'\n')  
            
    infile.close()            
    
    # remove the header line
    del id1[0], id2[0], amount[0], message[0], badlines[0]
    return id1, id2, amount, message, badlines  
    
# Define Graph, Vertex, and Queue
# I acknowledge the class definitions of Graph, Vertex, and Queue in pythonds made by:
# Bradley N. Miller, David L. Ranum
class Graph:
    def __init__(self):
        self.vertices = {}
        self.numVertices = 0
        
    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertices[key] = newVertex
        return newVertex
    
    def getVertex(self,n):
        if n in self.vertices:
            return self.vertices[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertices
    
    def addEdge(self,f,t,cost=0):
            if f not in self.vertices:
                nv = self.addVertex(f)
            if t not in self.vertices:
                nv = self.addVertex(t)                
            self.vertices[f].addNeighbor(self.vertices[t],cost)
    
    def getVertices(self):
        return list(self.vertices.keys())
        
    def __iter__(self):
        return iter(self.vertices.values())
                
class Vertex:
    def __init__(self,num):
        self.id = num
        self.connectedTo = {}
        self.color = 'white'
        self.dist = sys.maxsize

    def addNeighbor(self,nbr,weight=0):
        self.connectedTo[nbr] = weight
        
#    To keep track of its progress, BFS colors each of the vertices white, gray, 
#    or black. All the vertices are initialized to white when they are constructed. 
#    A white vertex is an undiscovered vertex. When a vertex is initially discovered
#    it is colored gray, and when BFS has completely explored a vertex it is colored
#    black. This means that once a vertex is colored black, it has no white vertices
#    adjacent to it. A gray node, on the other hand, may have some white vertices
#    adjacent to it, indicating that there are still additional vertices to explore.
    def setColor(self,color):
        self.color = color
        
    def setDistance(self,d):
        self.dist = d
        
    def getDistance(self):
        return self.dist
        
    def getColor(self):
        return self.color
    
    # Return all the connections     
    def getConnections(self):
        return self.connectedTo.keys()

    # Return connection within certain level of network    
    def getConnections_level(self,level):
        return [vertex for vertex, weight in self.connectedTo.items() if weight <= level]
        
    def getWeight(self,nbr):
        return self.connectedTo[nbr]
                
    def __str__(self):
        return str(self.id) + ":color " + self.color + ":dist " + str(self.dist) + "]\n"
    
    def getId(self):
        return self.id
        
class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)        

# buildUndirectedGraph is used to build a undirected graph to represent the 
# "1st degree friend network" based on transcations recorded in batch_payment.csv
def buildUndirectedGraph(id1, id2): 
           
    g = Graph() 
    for i in range(0,len(id1)):      
        g.addEdge(id1[i],id2[i],1)
        g.addEdge(id2[i],id1[i],1)
        
    '''
    # For test, needs to be commented when running with big data        
    for v in g:
        for w in v.getConnections():
            print("( %s , %s, %s )" % (v.getId(), w.getId(), v.getWeight(w)))  
    '''
    return g 
    
# bfs not only check tobecheckId is within the level_max network of start, but 
# also update graph g during the search process for future time saving     
def bfs(g,start,tobecheckId,level_max):

    # The flag is used to indicate whether the element is found or not
    flag = "unverified"

    # Check if the tobecheckId is within the level_max network of the start
    nbr_level = []
    for nbr in start.getConnections_level(level_max):
        nbr_level.append(nbr.getId())
    if tobecheckId in nbr_level:
        flag = "trusted"
        return g, flag   
        
    # When the tobecheckId is outside of the level_max network of the start         
    start.setDistance(0)
    vertQueue = Queue()
    vertQueue.enqueue(start)    
    
    visited = []
    visited.append(start)

    while (vertQueue.size() > 0):
        currentVert = vertQueue.dequeue()
        if currentVert.getDistance() < level_max:
            for nbr in currentVert.getConnections_level(1):
                if (nbr.getColor() == 'white'):
                    nbr.setColor('gray')
                    nbr.setDistance(currentVert.getDistance() + 1)
                    vertQueue.enqueue(nbr)

                    # update g if nbr is not inside the original network of start
                    if not (nbr.getId() in nbr_level):
                        g.addEdge(start.getId(),nbr.getId(),nbr.getDistance())
                        g.addEdge(nbr.getId(),start.getId(),nbr.getDistance())
                    
                    visited.append(nbr)                    
                    #print(nbr.getId(),nbr.getDistance())    
                    
                    if nbr.getId() == tobecheckId:
                        # Recover all the visited elements to the original values         
                        for v in visited:
                            v.setColor('white')                
                            v.dis = sys.maxsize               
                        
                        flag = "trusted"
                        return g, flag

            currentVert.setColor('black')
        else:
            currentVert.setColor('black')    
            
    # Recover all the visited elements to the original value         
    for v in visited:
        v.setColor('white')                
        v.dis = sys.maxsize               

    return g, flag                  
    
# The filename_train specifies the file used for building the initial state of 
# the entire user network
filename_train = sys.argv[1]     
# The filename_test specifies the file used for testing whether there's a 
# possibility of fraud and a warning should be triggerd.  
filename_test = sys.argv[2]    
# The filename_out specifies the output files.
filename_out = []
filename_out.append(sys.argv[3])
filename_out.append(sys.argv[4])
filename_out.append(sys.argv[5])

id1_train,id2_train,amount_train,message_train,badlines_train = load_data(filename_train)    
id1_test,id2_test,amount_test,message_test,badlines_test = load_data(filename_test)    

# Get the union of unique values of id1 and id2
id_train = list(set(id1_train) | set(id2_train))  

# Build Graph
g_train = buildUndirectedGraph(id1_train,id2_train)

# Specify level_max to let bfs stops at level_max, the values are chosen 
# according to definitions of feature 1, 2 and 3
level_max_array = [1, 2, 4]

#Initialize a flag_trusted
flag_trusted = ["unverified" for x in range(0,len(badlines_test))]
for i in range(0,len(level_max_array)):
    level_max = level_max_array[i]

    # Complete the filename for output        
    outfile = open(filename_out[i],"w")
    
    for j in range(0,len(id1_test)):    
        # Not a bad line and the transaction is not verified yet
        if (badlines_test[j] == 0) and (flag_trusted[j] == "unverified") and \
           (id1_test[j] in id_train) and (id2_test[j] in id_train):
            # Apply BFS to determine if the two people are within level_max degree network  
            g_train,flag_trusted[j] = bfs(g_train, g_train.vertices[id1_test[j]], id2_test[j], level_max)
        
        outfile.write(flag_trusted[j] + "\n")               
                   
    outfile.close()    
        
#%%