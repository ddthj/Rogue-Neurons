import numpy as np

'''
mlp.py - contains the ML model

'''
class brain:
    def __init__(self):
        #these inportshave to be inside here because RLBot multiprocessing shenanigans won't have it any other way
        from keras.models import Sequential, load_model
        from keras.layers import Dense
        self.model = load_model("rogue.h5")
        print("Loaded model!")
    def get_state(self,pack): #returns predicted state given the pack of features
        y = self.model.predict(np.expand_dims(np.array(pack), axis=0)).tolist()[0]
        state = y.index(max(y))+1 #+1 because the atba() state isn't used and it's the 0th state
        #print(state)
        return state

'''
raw = np.array(pickle.load(open("data.dat","rb")))
np.random.seed(1)

def convert(y):
    temp = np.zeros(shape=(5,1))
    temp[y-1] = 1
    return temp
    
X,Y = raw[:,:-1],raw[:,-1] #splits data into features/labels
Y = np.array([convert(int(y)) for y in Y]) 
Y = Y.reshape(Y.shape[:2]) #reshapes labels


#test XOR data to make sure I knew what I was doing
d = np.array([
    [0,0],
    [1,0],
    [0,1],
    [1,1]])

e = np.array([
    [0],
    [1],
    [1],
    [0]])


z = Sequential()
z.add(Dense(16, input_dim=8,activation='relu'))
z.add(Dense(8,activation='relu'))
z.add(Dense(5,activation='sigmoid'))
z.compile(loss='binary_crossentropy',optimizer='adam')
z.fit(X,Y,epochs=300)
print(z.predict(X))
'''
