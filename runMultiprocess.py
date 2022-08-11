import os
import time
import shutil
import subprocess as sp

logDir = 'logs'

maxProcessNum = 8
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
                stdout, stderr = process.communicate()
                print(stdout)
                print(stderr)
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
                stdout, stderr = process.communicate()
                print(stdout)
                print(stderr)
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)

    process = sp.Popen("bash runGz.sh {} {} &> {}".format(pid, bid, os.path.join(logDir, pid+'-'+bid+'.log')), shell=True, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
    processPool.append((process, pid + '-' + bid))
    print('===== Start {}-{} ====='.format(pid, bid))

def main():
    os.makedirs(logDir, exist_ok=True)
    for pid in ['Chart', 'Lang', 'Math', 'Time', 'Mockito', 'Closure']:
        if pid == 'Chart':
            bidList = list(range(1, 27))
        if pid == 'Lang':
            bidList = list(range(1, 66))
            bidList.remove(2)
        if pid == 'Math':
            bidList = list(range(1, 107))
        if pid == 'Time':
            bidList = list(range(1, 28))
            bidList.remove(21)
        if pid == 'Mockito':
            bidList = list(range(1, 39))
        if pid == 'Closure':
            bidList = list(range(1, 134))
            bidList.remove(63)
            bidList.remove(93)

        for bid in bidList:
            runGz(pid, str(bid))

    waitPatchPoolFinish()

if __name__ == '__main__':
    main()
    