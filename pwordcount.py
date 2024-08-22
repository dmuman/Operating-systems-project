### Grupo: SO-TI-02
### Aluno 1: Guilherme Lima (fc56699)
### Aluno 2: Dmytro Umanskyi (fc59348)
### Aluno 3: Duarte Fernandes (fc55327)

import os
import sys
import time
from multiprocessing import Process, Value, Array, Lock, Queue, Manager
import signal
from datetime import datetime

#global variables
startTime = time.perf_counter()
programName = sys.argv[0]
arguments = sys.argv[1:]

filesPaths = []
numProcesses = 1
logInterval = 3
lastLogTime = 0

sharedValue = Value('i', 0) #creating shared value. array and dict
sharedArray = Array('i', [0] * numProcesses)
sharedDict = Manager().dict()
lock = Lock() #implementing lock and queue
queue = Queue()

MODE_MEANING = {
    't': 'total',
    'u': 'únicas',
    'o': 'ocorrências'
}

#function that is used to count the total amount of words and distribute the whole text or only it's parts between the modes
def countWords(fileContent, mode):
    words = fileContent.split()
    global sharedValue, lock, queue

    if mode == "t": #counting the total amount of words
        with lock:
            sharedValue.value += len(words) #shared_value is used
    elif mode == "u": #counting the number of the unique words
        uniqueWords = set(words)
        queue.put(uniqueWords) #putting the result into the queue
    elif mode == "o": #the number of occorencias of words
        wordCount = {} #creates a dict for store the values
        for word in words:
            wordCount[word] = wordCount.get(word, 0) + 1 #creates the key with the name of the word and value with number of occorencias
        queue.put(wordCount) #putting the dict to the queue
    
def countUniqueWords(): #function for counting the unique words

    global queue, sharedArray, lock

    while not queue.empty(): #if queue isn't empty
        uniqueWords = queue.get() #getting the unique words from queue

    with lock: #sincronization
        sharedArray[0] = len(uniqueWords) #put the result into the shared_array

def gettingOccorencias():
    totalWordCount = Manager().dict() #creating the new dict, using Manager, so it'll be possible to store and cound from the shared_array

    global queue, sharedDict, sharedArray, lock

    while not queue.empty(): #if queue isn't empty
        wordCount = queue.get() #getting the dict with words from queue
        for word, count in wordCount.items(): #searcing through the dict
            totalWordCount[word] = totalWordCount.get(word, 0) + count #adding stuff to the right dict

    with lock: #sincronization
        sharedDict.update(totalWordCount) #saving stuff into shared_dict and array
        sharedArray[0] += 1

def writeLogFile(logFileName): #function for writing the .log file
    global startTime, sharedValue, numProcesses, filesPaths, lock, lastLogTime

    elapsedTime = int((time.perf_counter() - startTime) * 10**8)

    with lock:
        countedWords = sharedValue.value #nimber of counted words

        processedFiles = len(filesPaths) - len(sharedArray) #counting the number of processed and remaining files
        remainingFiles = len(sharedArray)

    currentTime = time.perf_counter()
    if currentTime - lastLogTime >= logInterval:
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S") #creating the timestamp and the resulted string
        #print(f"{timestamp} {elapsedTime} {countedWords} {processedFiles} {remainingFiles}")
        resultString = f"{timestamp} {elapsedTime} {countedWords} {processedFiles} {remainingFiles}\n"

        with open(logFileName, 'a') as logFile:
            logFile.write(resultString) #writing into the file

        lastLogTime = currentTime #updating the lastLogTime

def criarProcessos(fileContent, mode):

    global numProcesses, sharedValue, lock, queue

    #dividimos fileContent para multiplos partes
    partSize = len(fileContent.split()) // numProcesses

    #criamos processos
    processos = []
    for i in range(numProcesses):
        startIndex = i * partSize #criamos start index e end index para criar multiplos partes com início e fim
        endIndex = len(fileContent) #por omissão temos end index = len do file => whole file

        if i < numProcesses - 1:
            endIndex = (i + 1) * partSize #updating the end_index
        
        filePart = fileContent[startIndex:endIndex] #parte, não é partilhado

        processos.append(Process(target=countWords, args=(filePart, mode)))

    #Iniciamos os processos
    for process in processos:
        process.start()

    #Esparamos os processos para finalizar
    for process in processos:
        process.join()

    
def main(args):

    global filesPaths, numProcesses, logInterval, sharedArray, sharedValue, sharedDict, queue, lock

    if len(args) < 2:
        print("Uso: ./pwordcount [-m t|u|o] [-p n] ficheiros..") #preventing errors if there're no args 
        return

    mode = "t" #default mode is "t"

    for i in range(len(args)):
        if args[i] == "-m": #getting the mode
            mode = args[i + 1]
        elif args[i] == "-p": #getting the number of processes
            numProcesses = int(args[i + 1])
        elif args[i] == "-i":  #getting the interval
            logInterval = int(args[i + 1])
        elif args[i] == "-l":  #getting the name of the log file
            logFileName = args[i + 1]
        elif args[i][-4:] == ".txt": #getting files paths
            filesPaths.append(args[i])

    for filePath in filesPaths: #serching through files

        sharedValue = Value('i', 0)  #reseting the values so they'll be different for different files
        sharedArray = Array('i', [0] * numProcesses)
        sharedDict = Manager().dict()
        lock = Lock()

        if filePath is None:
            print("É necessário fornecer um arquivo para contar palavras.") #preventing error if the're no files
            return

        try:
            with open(filePath, "r") as file:
                fileContent = file.read() #reading through files

                try:
                    criarProcessos(fileContent, mode) #creating the processes
                    writeLogFile(logFileName)
                    
                except OSError as e:
                    print("Falha ao criar os processos ", e.errno, '-', e.strerror, file=sys.stderr) #raising error if failed
                    sys.exit(1)

                if mode == "t": #operation if mode is total
                    print(f"Contagem {MODE_MEANING[mode]} de palavras em {filePath}: {sharedValue.value}")
                elif mode == "u": #uniques
                    countUniqueWords()
                    print(f"Contagem {MODE_MEANING[mode]} de palavras em {filePath}: {sharedArray[0]}")
                else: #occorencias
                    gettingOccorencias()
                    for word, count in sharedDict.items():
                        print(f"Palavra {word} occoreu: {count} vezes em {filePath}")

        except IOError as e:
            print("open failed ", e.errno, '-', e.strerror, file=sys.stderr) #raising error if failed opening the file
            sys.exit(1)

if __name__ == "__main__":
   main(arguments)