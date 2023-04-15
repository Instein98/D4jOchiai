import os
import time
import shutil
import subprocess as sp

logDir = 'logs'

maxProcessNum = 6
processPool = []  # storing (process, "pid-bid")

def waitPatchPoolFinish():
    while (len(processPool) > 0):
        time.sleep(1)
        valuesToRemove = []
        for process, projId in processPool:
            exitCode = process.poll()
            if exitCode is None:
                continue
            else:
                if exitCode != 0:
                    print('[ERROR] process {} finished with non-zero exit code!'.format(projId))
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)

def runGz(pid: str, bid: str):
    while (len(processPool) >= maxProcessNum):
        time.sleep(1)
        valuesToRemove = []
        for process, projId in processPool:
            exitCode = process.poll()
            if exitCode is None:
                continue
            else:
                if exitCode != 0:
                    print('[ERROR] process {} finished with non-zero exit code!'.format(projId))
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)
    logPath = os.path.join(logDir, pid+'-'+bid+'.log')
    with open(logPath, 'w') as f:
        process = sp.Popen("bash runGz.sh {} {}".format(pid, bid), stdout=f, stderr=f, shell=True, universal_newlines=True)
        # process = sp.Popen("echo {}-{}".format(pid, bid), stdout=f, stderr=f, shell=True, universal_newlines=True)
    processPool.append((process, pid + '-' + bid))
    print('===== Start {}-{} ====='.format(pid, bid))

d4j200ProjNames = ['Chart', 'Cli', 'Closure', 'Codec', 'Collections', 'Compress', 'Csv', 'Gson', 'JacksonCore', 'JacksonDatabind', 'JacksonXml', 'Jsoup', 'JxPath', 'Lang', 'Math', 'Mockito', 'Time']

def getD4jProjNameFromSimpleName(simpleName):
    for projName in d4j200ProjNames:
        if simpleName == projName.lower():
            return projName
    print('Cannot find the project name for the simple name: {}'.format(simpleName))
    exit -1

projDict = {
    'Chart': (list(range(1, 27)), []),
    'Cli': (list(range(1, 41)), [6]),
    'Closure': (list(range(1, 177)), [63, 93]),
    'Codec': (list(range(1, 19)), []),
    'Collections': (list(range(1, 29)), list(range(1, 25))),
    'Compress': (list(range(1, 48)), []),
    'Csv': (list(range(1, 17)), []),
    'Gson': (list(range(1, 19)), []),
    'JacksonCore': (list(range(1, 27)), []),
    'JacksonDatabind': (list(range(1, 113)), []),
    'JacksonXml': (list(range(1, 7)), []),
    'Jsoup': (list(range(1, 94)), []),
    'JxPath': (list(range(1, 23)), []),
    'Lang': (list(range(1, 66)), [2]),
    'Math': (list(range(1, 107)), []),
    'Mockito': (list(range(1, 39)), []),
    'Time': (list(range(1, 28)), [21])
}

def main():
    os.makedirs(logDir, exist_ok=True)
    for pid in projDict:
        bidList = projDict[pid][0]
        deprecatedBidList = projDict[pid][1]
        bidList = [bid for bid in bidList if bid not in deprecatedBidList]

        for bid in bidList:
            bidResultDir = 'results/{}/{}'.format(pid, bid)
            if os.path.isdir(bidResultDir):
                ochiaiFile = 'results/{}/{}/ochiai.ranking.csv'.format(pid, bid)
                linesNum = sp.check_output('cat results/{}/{}/ochiai.ranking.csv | wc -l '.format(pid, bid), shell=True, universal_newlines=True).strip()
                if not os.path.isfile(ochiaiFile) or (os.path.isfile(ochiaiFile) and linesNum == '1'):
                    print('Removing {} because the result is invalid'.format(bidResultDir))
                    shutil.rmtree(bidResultDir)
                else:
                    print("results/{}/{} already exists, skipping".format(pid, bid))
                    continue
            if os.path.isfile(os.path.join(logDir, pid + '-' + str(bid)+'.log')):
                os.remove(os.path.join(logDir, pid + '-' + str(bid)+'.log'))
            runGz(pid, str(bid))

    waitPatchPoolFinish()

if __name__ == '__main__':
    main()
    