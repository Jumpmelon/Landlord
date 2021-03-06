import os
import random
import sys
import json
import numpy as np
from collections import Counter

###################################################牌型编码###################################################
# 红桃 方块 黑桃 草花
# 3 4 5 6 7 8 9 10 J Q K A 2 joker & Joker
# (0-h3 1-d3 2-s3 3-c3) (4-h4 5-d4 6-s4 7-c4) …… 52-joker 53-Joker
###################################################牌型编码###################################################

priorityPokerType = {
    "火箭":3,
    "炸弹":2
}
multiplierPokerType = {
    "火箭":1,
    "炸弹":1,
}
errored = [None for i in range(3)]

def setError(player, reason):
    if errored[player] is None:
        errored[player] = reason
    if all(errored):
        print(json.dumps({
            "command": "finish",
            "content": {
                "0": -1,
                "1": -1,
                "2": -1
            },
            "display": {
                "0": -1,
                "1": -1,
                "2": -1,
                "errored": errored
            }
        }))
        sys.exit(0)

# 将数字换算成点数
def convertToPoint(x):
    return int(x/4) + 3 + (x==53)

def initGame(full_input):
    seedRandom = str(random.randint(0, 2147483647))

    if "initdata" not in full_input:
        full_input["initdata"] = {}
    try:
        full_input["initdata"] = json.loads(full_input["initdata"])
    except Exception:
        pass
    if type(full_input["initdata"]) is not dict:
        full_input["initdata"] = {}

    if "seed" in full_input["initdata"]:
        seedRandom = full_input["initdata"]["seed"] 
    
    random.seed(seedRandom)
    if "allocation" in full_input["initdata"]:
        allocation = full_input["initdata"]["allocation"]
    else: # 产生大家各自有什么牌
        allo = [i for i in range(54)]
        random.shuffle(allo)
        allocation = [allo[3:20], allo[20:37], allo[37:54]]

    if "publiccard" in full_input["initdata"]:
        publiccard = full_input["initdata"]["publiccard"]
    else:
        publiccard = allo[0:3]
    
    return full_input, seedRandom, allocation, publiccard

# J,Q,K,A,2-11,12,13,14,15
# 单张：1 一对：2 三带：零3、一4、二5 单顺：>=5 双顺：>=6
# 四带二：6、8 飞机：>=6
def checkPokerType(poker): # poker：list，表示一个人出牌的牌型
    poker.sort()
    lenPoker = len(poker)

    ################################################# 0张 #################################################
    if lenPoker == 0:
        return "空", [], []

    ################################################# 1张 #################################################
    if lenPoker == 1:
        return "单张", poker, []

    ################################################# 2张 #################################################
    if lenPoker == 2 and poker == [52, 53]:
        return "火箭", poker, []
    if lenPoker == 2 and convertToPoint(poker[0]) == convertToPoint(poker[1]):
        return "一对", poker, []
    if lenPoker == 2:
        return "错误", poker, []

    #################################### 转换成点数，剩下牌一定大于等于3张 ###################################
    # 扑克牌点数
    ptrOfPoker = [convertToPoint(i) for i in poker]
    firstPtrOfPoker = ptrOfPoker[0]
    # 计数 
    cntPoker = Counter(ptrOfPoker)
    keys, vals = list(cntPoker.keys()), list(cntPoker.values())

    ################################################# 4张 #################################################
    if lenPoker == 4 and vals.count(4) == 1:
        return "炸弹", poker, []
    
    ############################################## >=5张 单顺 #############################################
    singleSeq = [firstPtrOfPoker+i for i in range(lenPoker)]
    if (lenPoker >= 5) and (15 not in singleSeq) and (ptrOfPoker == singleSeq):
        return "单顺", poker, []
    
    ############################################## >=6张 双顺 #############################################
    pairSeq = [firstPtrOfPoker+i for i in range(int(lenPoker / 2))]
    pairSeq = [j for j in pairSeq for i in range(2)]
    if (lenPoker >= 6) and (lenPoker % 2 == 0) and (15 not in pairSeq) and (ptrOfPoker == pairSeq):
        return "双顺", poker, []
    
    ################################################# 3张带 ################################################
    if (lenPoker <= 5) and (vals.count(3) == 1):
        if vals.count(1) == 2:
            return "错误", poker, [] 
        specialPoker = keys[vals.index(3)]
        triplePoker = [i for i in poker if convertToPoint(i) == specialPoker]
        restPoker = [i for i in poker if i not in triplePoker]
        tripleNames = ["三带零", "三带一", "三带二"]
        return tripleNames[lenPoker - 3], triplePoker, restPoker

    ############################################## 6张 四带二只 ############################################
    if (lenPoker == 6) and (vals.count(4) == 1) and (vals.count(1) == 2):
        specialPoker = keys[vals.index(4)]
        quadruplePoker = [i for i in poker if convertToPoint(i) == specialPoker]
        restPoker = [i for i in poker if i not in quadruplePoker]
        return "四带两只", quadruplePoker, restPoker        

    ############################################## 8张 四带二对 ############################################
    if (lenPoker == 8) and (vals.count(4) == 1) and (vals.count(2) == 2):
        specialPoker = keys[vals.index(4)]
        quadruplePoker = [i for i in poker if convertToPoint(i) == specialPoker]
        restPoker = [i for i in poker if i not in quadruplePoker]
        return "四带两对", quadruplePoker, restPoker        
 
    # 分别表示张数有0、1、2、3张的是什么点数的牌
    keyList = [[], [], [], [], []]
    for idx in range(len(vals)):
        keyList[vals[idx]] += [keys[idx]]
    lenKeyList = [len(i) for i in keyList]
    for i in range(5):
        keyList[i].sort()
    ################################################## 飞机 ################################################ 
    if lenKeyList[3] > 1 and 15 not in keyList[3] and \
        (keyList[3] == [keyList[3][0] + i for i in range(lenKeyList[3])]):
        if lenKeyList[3] * 3 == lenPoker:
            return "飞机不带翼", poker, []
        triplePoker = [i for i in poker if convertToPoint(i) in keyList[3]]
        restPoker = [i for i in poker if i not in triplePoker]
        if (lenKeyList[3] == lenKeyList[1]) and (lenKeyList[1] * 4 == lenPoker):
            return "飞机带小翼", triplePoker, restPoker
        if (lenKeyList[3] == lenKeyList[2]) and (lenKeyList[2] * 5 == lenPoker):
            return "飞机带大翼", triplePoker, restPoker
        
    ################################################# 航天飞机 ############################################## 
    if lenKeyList[4] > 1 and lenKeyList[3] == 0 and 15 not in keyList[4] and \
        (keyList[4] == [keyList[4][0] + i for i in range(lenKeyList[4])]):
        if lenKeyList[4] * 4 == lenPoker:
            return "航天飞机不带翼", poker, []
        quadruplePoker = [i for i in poker if convertToPoint(i) in keyList[4]]
        restPoker = [i for i in poker if i not in quadruplePoker]
        if (lenKeyList[4] == lenKeyList[1]) and (lenKeyList[1] * 5 == lenPoker):
            return "航天飞机带小翼", quadruplePoker, restPoker
        if (lenKeyList[4] == lenKeyList[2]) and (lenKeyList[2] * 6 == lenPoker):
            return "航天飞机带大翼", quadruplePoker, restPoker
    
    return "错误", poker, []
        
def recover(history): # 只考虑倒数3个，返回最后一个有效牌型及主从牌，且返回之前有几个人选择了pass；id是为了防止某一出牌人在某一牌局后又pass，然后造成连续pass
    lenHistory = len(history)
    typePoker, mainPoker, restPoker, cntPass = "任意牌", [], [], 0

    while(lenHistory > 0):
        lastPoker = history[lenHistory - 1]
        typePoker, mainPoker, restPoker = checkPokerType(lastPoker)
        if typePoker == "空":
            cntPass += 1
            lenHistory -= 1
            continue
        break
    return typePoker, mainPoker, restPoker, cntPass

def getFinalBid(bidHistory):
    base = 1
    for i in bidHistory:
        if i > base:
            base = i
    return base

def getMultiplier(history, bidHistory, rest, currLandlord):
    multiplier, times = max(bidHistory + [1]), 0
    lenH = len(history)
    for i in range(lenH):
        currPoker = history[i]
        typePoker, mainPoker, _ = checkPokerType(currPoker)
        times += multiplierPokerType.get(typePoker, 0)

    farmer_1, farmer_2 = (currLandlord + 1) % 3, (currLandlord + 2) % 3, 
    # 春天 只有地主在出牌，农民都没有出牌
    if len(rest[currLandlord]) == 0 and len(rest[farmer_1]) == 17 and len(rest[farmer_2]) == 17:
        times += 1

    # 反春天 地主只出了一手牌，有一个农民出完了
    if len(rest[currLandlord]) == (20 - len(history[0])) and \
        (len(rest[farmer_1]) == 0 or len(rest[farmer_2]) == 0):
        times += 1

    return (multiplier << times)

def printRequest(nextTurn, printContent, currTurn, currLandlord, solution, bidHistory):
    solution = solution[-2:]
    if len(solution) == 1:
        solution = [[]] + solution
    printContent["history"] = solution
    printJson = {
        "command": "request",
        "content": {
            str(nextTurn): printContent
        },
        "display": {
            "landlord": currLandlord,
            "bid": bidHistory,
            "errored": errored
        }
    } if not errored[nextTurn] else {
        "command": "request",
        "content": {},
        "display": {
            "landlord": currLandlord,
            "bid": bidHistory,
            "errored": errored
        }
    }
    if currTurn != -1:
        printJson["display"]["event"] = {
            "player": currTurn,
            "action": solution[-1]
        }     
    print(json.dumps(printJson))
    exit(0)

# 记分规则：https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997#6
def printFinish(currTurn, currLandlord, solution, multiplier):
    assert currTurn >= 0 and currLandlord >= 0 and currLandlord <= 2, \
        "invalid currTurn %d or currLandlord %d" % (currTurn, currLandlord)
    score, s = [0, 0, 0], [-1, 2]
    isLandlordWin = currTurn == currLandlord
    for i in range(3):
        score[i] = multiplier * s[int(i == currLandlord)]
        if not isLandlordWin:
            score[i] *= -1
    print(json.dumps({
        "command": "finish",
        "content": {
            "0": score[0],
            "1": score[1],
            "2": score[2]
        },
        "display": {
            "event": {
                "player": currTurn,
                "action": solution[-1]
            },
            "0": score[0],
            "1": score[1],
            "2": score[2],
            "landlord": currLandlord
        }
    }))  
    exit(0) 

def checkLandlord(log):
    # 返回值：地主玩家下标，叫地主的log长度
    l, tmpLandlord, tmpScore = len(log), -1, 0
    bidHistory = []
    for i in range(1, l, 2):
        curr = (i - 1) // 2
        try:
            s = int(log[i][str(curr)]["response"])
        except:
            log[i][str(curr)]["response"] = 0
            return None, None, curr, 'INVALID_BID'
        if s != 0 and (s > 3 or s <= tmpScore):
            log[i][str(curr)]["response"] = 0
            return None, None, curr, 'INVALID_BID'
        bidHistory.append(s)
        if s == 3:
            return curr, bidHistory, None, None
        if tmpScore < s:
            tmpLandlord, tmpScore = curr, s
    if l < 6:
        tmpLandlord = -1
    elif tmpLandlord == -1:
        tmpLandlord = 0
    return tmpLandlord, bidHistory, None, None

def printBidding(currPlayer, allocation, bidHistory, publiccard, seedRandom):
    # 玩家可以根据bid字段的值知道自己是几号，根据own字段的值知道自己的牌
    # content叫谁
    printContent = {
        "own": allocation[currPlayer],
        "bid": bidHistory
    }
    printJson = {
        "command": "request",
        "content": {
            str(currPlayer): printContent
        },
        "display": {
            "allocation": allocation,
            "publiccard": publiccard,
            "bid": bidHistory,
        }
    }
    if currPlayer == 0:
        printJson["initdata"] =  {
            "allocation": allocation,
            "publiccard" : publiccard,
            "seed": seedRandom
        }
    print(json.dumps(printJson))
    exit(0)

def getSmallest(pokers):
    pokers.sort()
    return [pokers[0]]

_online = os.environ.get("USER", "") == "root"
# 第一关地主pass的话会出错


def main(full_input):

    pokerDown = [0 for i in range(54)]
    solution = []
    currLandlord, currTurn = -1, -1
    allDown = False

    full_input, seedRandom, allocation, publiccard = initGame(full_input)    
    logs = full_input["log"]
    
    currLandlord, bidHistory, currErrorPlayer, errInfo = checkLandlord(logs[:6])
    if currLandlord == None:
        setError(currErrorPlayer, errInfo)
        return

    # 还在叫牌阶段，按序告诉玩家都有什么牌，此时不告诉玩家明牌是什么
    if currLandlord == -1:
        printBidding((int(len(logs) / 2)) % 3, allocation, bidHistory, publiccard, seedRandom)

    # 已经确定了地主，且成为地主的是第 len(bidHistory) 个玩家
    rest = [[i for i in j] for j in allocation]
    rest[currLandlord].extend(publiccard)
    lenBidForLandlord = 2 * len(bidHistory)
    # 此时的log就从地主开始，地主已经指定了
    logs = logs[lenBidForLandlord:]
    lenLog = len(logs)
        
    printContent = {
        "history":[]
    }
    if lenLog < 6:
        currPlayer = (currLandlord + int(lenLog / 2)) % 3
        printContent["own"] = allocation[currPlayer]
        printContent["publiccard"] = publiccard
        printContent["landlord"] = currLandlord
        printContent["pos"] = ((lenLog // 2) + currLandlord) % 3
        printContent["finalbid"] = getFinalBid(bidHistory)
    
    if lenLog == 0:
        printRequest(currLandlord, printContent, -1, currLandlord, [[], []], bidHistory)

    if str(currLandlord) not in logs[1]:
        logs[1][str(currLandlord)] = {"verdict": "OK", "response":[]}
    botResult = logs[1][str(currLandlord)]
    # 地主玩家代码出问题了
    if botResult["verdict"] != "OK" or "response" not in botResult or type(botResult["response"]) is not list:
        setError(currLandlord, "INVALID_INPUT_VERDICT_" + botResult["verdict"])
        botResult["verdict"] = "OK"
        botResult["response"] = []
        return
    tmp = botResult["response"]
    if len(tmp) == 0: 
        setError(currLandlord, "INVALID_PASS") # 地主第一回合就pass，显然是错误的
        botResult["response"] = getSmallest(rest[currLandlord])
        return

    currTurn = (currLandlord + 2) % 3
    for _i in range(1, lenLog, 2):
        currTurn = (currTurn + 1) % 3 
        restOwn = rest[currTurn]
        if _i + 1 < lenLog and logs[_i + 1]["output"]["display"]:
            display = logs[_i + 1]["output"]["display"]
            if "event" in display:
                logs[_i][str(currTurn)] = {"verdict": "OK", "response": display["event"]["action"]}
        if str(currTurn) not in logs[_i]:
            logs[_i][str(currTurn)] = {"verdict": "OK", "response":[]}
        botResult = logs[_i][str(currTurn)]
        if botResult["verdict"] != "OK" or "response" not in botResult or type(botResult["response"]) is not list:
            setError(currTurn, "INVALID_INPUT_VERDICT_" + botResult["verdict"])
            botResult["verdict"] = "OK"
            botResult["response"] = []
            return
        resp = botResult["response"]
        solution += [resp]
        for i in resp:
            if (currTurn == currLandlord and (i not in publiccard and i not in allocation[currTurn])) \
                or (currTurn != currLandlord and i not in allocation[currTurn]):
                setError(currTurn, "MISSING_CARD") # 这个人不应该有这张牌
                solution[-1].clear()
                return
            if not (i >= 0 and i <= 53):
                setError(currTurn, "OUT_OF_RANGE") # 给的牌超出了范围
                solution[-1].clear()
                return
            if pokerDown[i]:
                setError(currTurn, "REPEATED_CARD") # 这张牌之前已经被出过了
                solution[-1].clear()
                return
            pokerDown[i] = True
            restOwn.remove(i)
        if len(restOwn) == 0:
            allDown = True
        
    currTypePoker, currMainPoker, currRestPoker = checkPokerType(solution[-1])
    if currTypePoker == "错误":
        setError(currTurn, "INVALID_CARDTYPE") # 牌型错误
        solution[-1].clear()
        return

    multiplier = getMultiplier(solution, bidHistory, rest, currLandlord)
    lenSolve = len(solution) # currTurn == (lenSolve - 1) % 3
    nextTurn = (lenSolve + currLandlord) % 3
    lastTypePoker, lastMainPoker, lastRestPoker, cntPass = recover(solution[:-1])
    if lastTypePoker == "任意牌" or lastTypePoker == "空" or cntPass == 2:
        if currTypePoker == "空":
            setError(currTurn, "INVALID_PASS") # 不合理的pass，显然是错误的
            solution[-1] += getSmallest(rest[currTurn])
            return
        else: # 任意出或者前二者都不要的话，自己可以随意出，因为上一轮也是自己的牌
            if allDown: # 这一回合的出牌者已经把牌都出完了，赢得了最终胜利
                printFinish(currTurn, currLandlord, solution, multiplier)          
            else:
                printRequest(nextTurn, printContent, currTurn, currLandlord, solution, bidHistory)
    if currTypePoker == "空":
        printRequest(nextTurn, printContent, currTurn, currLandlord, solution, bidHistory)

    # PPT是priorityPokerType的缩写（生草.jpg
    lastPPT, currPPT = priorityPokerType.get(lastTypePoker, 1), priorityPokerType.get(currTypePoker, 1)
    if lastPPT < currPPT: # 现在的牌型比上一个牌型要大，直接过，这时候要考虑当前玩家所有牌都出完的情况
        if allDown:
            printFinish(currTurn, currLandlord, solution, multiplier) 
        else:    
            printRequest(nextTurn, printContent, currTurn, currLandlord, solution, bidHistory)
    if lastPPT > currPPT:
        setError(currTurn, "LESS_COMPARE") # 现在的牌型比上一个牌型要小
        solution[-1].clear()
        return
    if lastTypePoker != currTypePoker:
        setError(currTurn, "MISMATCH_CARDTYPE") # 牌型不一致
        solution[-1].clear()
        return
    lenCom = len(currMainPoker)
    if len(lastMainPoker) != lenCom or len(currRestPoker) != len(lastRestPoker):
        setError(currTurn, "MISMATCH_CARDLENGTH") # 牌型长度不一致
        solution[-1].clear()
        return

    currComMP, lastComMP = [convertToPoint(i) for i in currMainPoker], [convertToPoint(i) for i in lastMainPoker]
    comRes = [currComMP[i] > lastComMP[i] for i in range(lenCom)]
    if all(comRes):
        if allDown: # 这一回合的出牌者已经把牌都出完了，赢得了最终胜利
            printFinish(currTurn, currLandlord, solution, multiplier)        
        else:
            printRequest(nextTurn, printContent, currTurn, currLandlord, solution, bidHistory)
    else:
        setError(currTurn, "LESS_COMPARE") # 现在的牌型比上一个牌型要小
        solution[-1].clear()
        return

if __name__ == '__main__':
    if True or _online:
        full_input = json.loads(input())
    else:
        with open("judgelogs.json") as fo:
            full_input = json.load(fo)
    for x in full_input["log"]:
        if "output" in x and "display" in x["output"] and "errored" in x["output"]["display"]:
            errored = x["output"]["display"]["errored"]
    while True:
        main(full_input)