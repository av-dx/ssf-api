#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import re
import locale

#sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


class Coreference_entity():
    def __init__(self, uniqueid) :
        self.lines = []
        self.headnode = None
        self.nodes = []
        self.wordwithpos = []
        self.headstring = None
        self.chainid = None
        self.entityheadtext = None
        self.uniqueid = uniqueid
        self.startlineno = None
        self.endlineno = None
        self.normaltext = None
        self.crefmodtext = ''
        self.crefmodheadtext = ''
        self.hindistring = ''
        self.modeid = None
        self.modestartline = None
        self.modeendline = None
        self.upper = None
        self.parent = None
        self.parentrelation = None

class Coreference_chain() :
    def __init__(self, chainid):
        self.text= []
        self.nodeList = []
        self.chainid = chainid
        self.chainhead = None
        self.chainstart = None
        self.chainend = None
class Node_vandan() :
    def __init__(self,text,upper,linenumber,relation) :
        self.text = text
        self.lex = None
        self.type = None
        self.__attributes = {}
        self.errors = []
        self.name = None
        self.parent = '0'
        self.parentRelation = 'root'
        self.isparent=None
        self.alignedTo = None
        self.fsList = None
        self.upper = upper
        self.linenumber = linenumber
        self.chunkparentRelation = relation
        self.childList = []
        
        self.number='any'
        self.person='none'
        self.gender=None
        self.morphroot=None
        self.case=None
        self.morphPOS=None
        self.tamUtf=None
        self.tamWx=None
        
        self.analyzeNode(self.text)
        if self.getAttribute('af')!=None:
            aa= self.getAttribute('af').strip().split(',')
            self.morphroot=aa[0]
            self.morphPOS=aa[1]
            self.number=aa[3]
            self.person=aa[4]
            self.gender=aa[2]
            self.case=aa[5]
            self.tamUtf=aa[6]
            self.tamWx=aa[7]


    def analyzeNode(self, text) :
        [token, tokenType, fsDict, fsList] = getTokenFeats(text.strip().split())
        attributeUpdateStatus = self.updateAttributes(token, tokenType, fsDict, fsList)
        acrefMod = self.getAttribute('acrefMod')
        if acrefMod != None :
            acrefModtemp = acrefMod.split(',')
            for i in acrefModtemp :
                uniqid = i.split(':')[1]
                modeid = i.split(':')[0]
                modeidpart = modeid.split('%')[1]
                modeid = modeid.split('%')[0]
                
                if self.checkuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid) :
                    unique = self.getuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid)
                else:
                    unique = Coreference_entity(uniqid) # new entity creation
                    unique.startlineno = self.linenumber
                    unique.modeid = modeid
                    self.upper.upper.acoreferenceEntityNodeList.append(unique)

                unique.lines.append(self.linenumber)
                unique.nodes.append(self)
                unique.wordwithpos.append(self.lex+'_'+self.type)
                unique.crefmodtext = unique.crefmodtext+self.lex+' '

                if unique.modestartline == None :
                    unique.modestartline = self.linenumber
                if modeidpart.strip() == '1' :
                    unique.modeendline = self.linenumber

        acrefModhead = self.getAttribute('acrefModHead')
        if acrefModhead != None :
            acrefModheadtemp=acrefModhead.split(',')
            for i in acrefModheadtemp :
                modeid = i.split(':')[1]
                modehead = i.split(':')[0]
                unique=self.getmodeinmodelistbymode(self.upper.upper.acoreferenceEntityNodeList,modeid)
                unique.crefmodheadtext=modehead
                
        cref=self.getAttribute('cref')
        if cref:
            creftemp=cref.split(',')
            for i in creftemp:
                if i.strip() == '':
                    continue
                uniqidp=i.split(':')[0]
                uniqidpart=uniqidp.split('%')[1]
                uniqid=uniqidp.split('%')[0]
                chainid=i.split(':')[1]
                if not self.checkforchainlist(self.upper.upper.coreferenceChainNodeList,chainid) :
                    chain = Coreference_chain(chainid)  #new chain creation
                    chain.chainstart = str(self.linenumber)

                    if not self.checkuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid) :
                        unique = Coreference_entity(uniqid) #new entity creation
                        unique.chainid=chainid
                        unique.startlineno = self.linenumber
                    else :
                        unique = self.getuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid)
                    unique.hindistring += self.lex
                    unique.endlineno = self.linenumber
                    chain.nodeList.append(unique) #added entity to chainnodelist
                    self.upper.upper.coreferenceChainNodeList.append(chain) #added chain to doc nodelist

                else:
                    chain = self.getchainfromchainlist(self.upper.upper.coreferenceChainNodeList,chainid) #get chain from nodelist
                    if not self.checkforentityinchainlist(chain ,uniqid) :
                        if not self.checkuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid) :
                            unique = Coreference_entity(uniqid) #new entity creation
                            unique.startlineno = self.linenumber
                            unique.chainid=chainid
                        else :
                            unique = self.getuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid)
                        unique.hindistring += self.lex
                        chain.nodeList.append(unique) #added entity to chainnodelist
                    else :
                        unique = self.getentityfromchainlist(chain ,uniqid)	#get entity from
                        unique.hindistring += ' '+ self.lex
                        unique.endlineno = self.linenumber
                unique.lines.append(self.linenumber)
                unique.nodes.append(self)
                unique.wordwithpos.append(self.lex+'_'+self.type)
                if uniqidpart.strip() == '1':
                    unique.endlineno = self.linenumber
        crefHead=self.getAttribute('crefHead')
        if crefHead:
            listforentity=[]
            crefHeadtemp=crefHead.split(',')
            for i in crefHeadtemp :
                head=i.split(':')[0]
                uniqid=i.split(':')[1]
                unique=self.getentity(self.upper.upper.coreferenceChainNodeList,uniqid)
                unique.headstring=head
                unique.headnode=self
                listforentity.append(unique)
            crefType = self.getAttribute('crefType')
            if crefType:
                crefTypetemp = crefType.split(',')
                for i in crefTypetemp:
                    ctype = i.split(':')[0]
                    cuniqueid = i.split(':')[1]
                    unique=listforentity.pop(0)
                    unique.parent=self.getentity(self.upper.upper.coreferenceChainNodeList,cuniqueid)
                    unique.parentrelation=ctype
                    
        crefChainHead=self.getAttribute('crefChainHead')
        if crefChainHead:
            crefChainHeadtemp = crefChainHead.split(',')
            for i in crefChainHeadtemp :
                uniqid=i.split(':')[0]
                chainid=i.split(':')[1]
                chain = self.getchainfromchainlist(self.upper.upper.coreferenceChainNodeList,chainid)
                unique = self.getentityfromchainlist(chain ,uniqid)
                chain.chainhead=unique
        if attributeUpdateStatus == 0 :
            self.errors.append("Can't update attributes for node")
            self.probSent = True

    def checkforchainlist(self,commingList,chainid) :
        for i in commingList:
            if i.chainid == chainid :
                return True
        return False

    def getchainfromchainlist(self,commingList,chainid) :
        for i in commingList:
            if i.chainid == chainid :
                return i
        return None

    def checkmodeinmodelistbymode (self,commingList, modeid) :
        for i in commingList :
            if i.modeid == modeid :
                return True
        return False

    def getmodeinmodelistbymode (self,commingList, modeid) :
        for i in commingList :
            if i.modeid == modeid :
                return i
        return None

    def checkuniqueEntityinmodelist (self,commingList, uniqueid):
        for i in commingList :
            if i.uniqueid == uniqueid :
                return True
        return False

    def getuniqueEntityinmodelist (self,commingList, uniqueid) :
        for i in commingList :
            if i.uniqueid == uniqueid :
                return i
        return None

    def checkforentityinchainlist(self, chain ,uniqueid) :
        for i in chain.nodeList :
            if i.uniqueid == uniqueid :
                return True
        return False


    def getentityfromchainlist(self, chain ,uniqueid) :
        for i in chain.nodeList :
            if i.uniqueid == uniqueid :
                return i
        return None

    def getentity(self, chain ,uniqueid) :
	#print '\n',uniqueid
        for i in chain :
            for j in i.nodeList:
                #print 'in',j.uniqueid,j.chainid,uniqueid
                if j.uniqueid == uniqueid :
                    return j
        return None

    def updateAttributes(self,token, tokenType, fsDict, fsList) :
        self.fsList = fsList
        self.lex = token
        self.type = tokenType
        for attribute in fsDict.keys() :
            self.__attributes[attribute] = fsDict[attribute]
        self.assignName()
	#self.updateDrel()

    def assignName(self) :
        if 'name' in self.__attributes:
            self.name = self.getAttribute('name')
        else :
            self.errors.append('No name for this token Node')

    def printValue(self) :
        return self.lex

    def printSSFValue(self, prefix, allFeat) :
        returnValue = [prefix , self.printValue() , self.type]
        if allFeat == False :
            fs = ['<fs']
            for key in sorted(self.__attributes.keys()) :
                fs.append(key + "='" + self.getAttribute(key) + "'")
            delim = ' '
            fs[-1] = fs[-1] + '>\n'

        else :
            fs = self.fsList
            delim = '|'

        return ('\t'.join(x for x in returnValue) + '\t' + delim.join(x for x in fs))

    def getAttribute(self,key) :
        if key in self.__attributes:
            return self.__attributes[key]
        else :
            return None

    def addAttribute(self,key,value) :
        self.__attributes[key] = value

    def deleteAttribute(self,key) :
        del self.__attributes[key]

    def updateDrel(self) :
        if self.__attributes.has_key('drel') :
            drelList = self.getAttribute('drel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('drel').split(':')[0]
        elif self.__attributes.has_key('dmrel') :
            drelList = self.getAttribute('dmrel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('dmrel').split(':')[0]

class Node() :
    def __init__(self,text,upper,linenumber) :
        self.text = text
        self.lex = None
        self.type = None
        self.__attributes = {}
        self.errors = []
        self.name = None
        self.parent = None
        self.parentRelation = None
        self.alignedTo = None
        self.fsList = None
        self.upper = upper
        self.linenumber = linenumber
        
        self.number='any'
        self.person='none'
        self.gender=None
        self.morphroot=None
        self.case=None
        self.morphPOS=None
        self.tamUtf=None
        self.tamWx=None

        self.analyzeNode(self.text)
        if self.getAttribute('af')!=None:
            aa= self.getAttribute('af').strip().split(',')
            self.morphroot=aa[0]
            self.morphPOS=aa[1]
            self.number=aa[3]
            self.person=aa[4]
            self.gender=aa[2]
            self.case=aa[5]
            self.tamUtf=aa[6]
            self.tamWx=aa[7]


    def analyzeNode(self, text) :
        [token, tokenType, fsDict, fsList] = getTokenFeats(text.strip().split())
        attributeUpdateStatus = self.updateAttributes(token, tokenType, fsDict, fsList)
        acrefMod = self.getAttribute('acrefMod')
        if acrefMod != None :
            acrefModtemp = acrefMod.split(',')
            for i in acrefModtemp:
                uniqid = i.split(':')[1]
                modeid = i.split(':')[0]
                modeidpart = modeid.split('%')[1]
                modeid = modeid.split('%')[0]
                if not self.checkuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid) :
                        unique = Coreference_entity(uniqid) # new entity creation
                        unique.startlineno = self.linenumber
                        unique.modeid = modeid
                        self.upper.upper.acoreferenceEntityNodeList.append(unique)
                else :
                        unique = self.getuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid)

                unique.lines.append(self.linenumber)
                unique.nodes.append(self)
                unique.wordwithpos.append(self.lex+'_'+self.type)
                unique.crefmodtext = unique.crefmodtext+self.lex+' '

                if unique.modestartline == None :
                        unique.modestartline = self.linenumber
                if modeidpart.strip() == '1' :
                        unique.modeendline = self.linenumber
                        
        acrefModhead = self.getAttribute('acrefModHead')
        if acrefModhead != None :
            acrefModheadtemp=acrefModhead.split(',')
            for i in acrefModheadtemp :
                modeid = i.split(':')[1]
                modehead = i.split(':')[0]
                unique=self.getmodeinmodelistbymode(self.upper.upper.acoreferenceEntityNodeList,modeid)
                unique.crefmodheadtext=modehead
                
        cref=self.getAttribute('cref')
        if cref!=None :
            creftemp=cref.split(',')
            for i in creftemp:
                    if i.strip() == '':
                            continue
                    uniqidp=i.split(':')[0]
                    uniqidpart=uniqidp.split('%')[1]
                    uniqid=uniqidp.split('%')[0]
                    chainid=i.split(':')[1]
                    if not self.checkforchainlist(self.upper.upper.coreferenceChainNodeList,chainid) :
                            chain = Coreference_chain(chainid)  #new chain creation
                            chain.chainstart = str(self.linenumber)

                            if not self.checkuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid) :
                                    unique = Coreference_entity(uniqid) #new entity creation
                                    unique.chainid=chainid
                                    unique.startlineno = self.linenumber
                            else :
                                    unique = self.getuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid)
                            unique.hindistring += self.lex
                            unique.endlineno = self.linenumber
                            chain.nodeList.append(unique) #added entity to chainnodelist
                            self.upper.upper.coreferenceChainNodeList.append(chain) #added chain to doc nodelist

                    else:
                            chain = self.getchainfromchainlist(self.upper.upper.coreferenceChainNodeList,chainid) #get chain from nodelist
                            if not self.checkforentityinchainlist(chain ,uniqid) :

                                    if not self.checkuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid) :
                                            unique = Coreference_entity(uniqid) #new entity creation
                                            unique.startlineno = self.linenumber
                                            unique.chainid=chainid
                                    else :
                                            unique = self.getuniqueEntityinmodelist(self.upper.upper.acoreferenceEntityNodeList,uniqid)
                                    unique.hindistring += self.lex
                                    chain.nodeList.append(unique) #added entity to chainnodelist
                            else :
                                    unique = self.getentityfromchainlist(chain ,uniqid)	#get entity from
                                    unique.hindistring += ' '+ self.lex
                                    unique.endlineno = self.linenumber
                    unique.lines.append(self.linenumber)
                    unique.nodes.append(self)
                    unique.wordwithpos.append(self.lex+'_'+self.type)
                    if uniqidpart.strip() == '1':
                            unique.endlineno = self.linenumber
                            
        crefHead=self.getAttribute('crefHead')
        if crefHead!=None :
            listforentity=[]
            crefHeadtemp=crefHead.split(',')
            for i in crefHeadtemp :
                    head=i.split(':')[0]
                    uniqid=i.split(':')[1]
                    unique=self.getentity(self.upper.upper.coreferenceChainNodeList,uniqid)
                    unique.headstring=head
                    unique.headnode=self
                    listforentity.append(unique)
            crefType = self.getAttribute('crefType')
            if crefType != None :
                    crefTypetemp = crefType.split(',')
                    for i in crefTypetemp:
                            ctype = i.split(':')[0]
                            cuniqueid = i.split(':')[1]
                            unique=listforentity.pop(0)
                            unique.parent=self.getentity(self.upper.upper.coreferenceChainNodeList,cuniqueid)
                            unique.parentrelation=ctype
                            
        crefChainHead=self.getAttribute('crefChainHead')
        if crefChainHead != None:
            crefChainHeadtemp = crefChainHead.split(',')
            for i in crefChainHeadtemp :
                uniqid=i.split(':')[0]
                chainid=i.split(':')[1]
                chain = self.getchainfromchainlist(self.upper.upper.coreferenceChainNodeList,chainid)
                unique = self.getentityfromchainlist(chain ,uniqid)
                chain.chainhead=unique
                
        if attributeUpdateStatus == 0 :
            self.errors.append("Can't update attributes for node")
            self.probSent = True

    def checkforchainlist(self,commingList,chainid) :
        for i in commingList:
            if i.chainid == chainid :
                return True
        return False

    def getchainfromchainlist(self,commingList,chainid) :
        for i in commingList:
            if i.chainid == chainid :
                return i
        return None

    def checkmodeinmodelistbymode (self,commingList, modeid) :
        for i in commingList :
            if i.modeid == modeid :
                return True
        return False

    def getmodeinmodelistbymode (self,commingList, modeid) :
        for i in commingList :
            if i.modeid == modeid :
                return i
        return None

    def checkuniqueEntityinmodelist (self,commingList, uniqueid) :
        for i in commingList :
            if i.uniqueid == uniqueid :
                return True
        return False

    def getuniqueEntityinmodelist (self,commingList, uniqueid) :
        for i in commingList :
            if i.uniqueid == uniqueid :
                return i
        return None

    def checkforentityinchainlist(self, chain ,uniqueid) :
        for i in chain.nodeList :
            if i.uniqueid == uniqueid :
                return True
        return False


    def getentityfromchainlist(self, chain ,uniqueid) :
        for i in chain.nodeList :
            if i.uniqueid == uniqueid :
                return i
        return None

    def getentity(self, chain ,uniqueid) :
        for i in chain :
            for j in i.nodeList:
                if j.uniqueid == uniqueid :
                    return j
        return None

    def updateAttributes(self,token, tokenType, fsDict, fsList) :
        self.fsList = fsList
        self.lex = token
        self.type = tokenType
        for attribute in fsDict.keys() :
            self.__attributes[attribute] = fsDict[attribute]
        self.assignName()

    def assignName(self) :
        if self.__attributes.has_key('name') :
            self.name = self.getAttribute('name')
        else :
            self.errors.append('No name for this token Node')

    def printValue(self) :
        return self.lex

    def printSSFValue(self, prefix, allFeat) :
        returnValue = [prefix , self.printValue() , self.type]
        if allFeat == False :
            fs = ['<fs']
            for key in self.__attributes.keys() :
                fs.append(key + "='" + self.getAttribute(key) + "'")
            delim = ' '
            fs[-1] = fs[-1] + '>\n'

        else :
            fs = self.fsList
            delim = '|'

        return ('\t'.join(x for x in returnValue) + '\t' + delim.join(x for x in fs))

    def getAttribute(self,key) :
        if self.__attributes.has_key(key) :
            return self.__attributes[key]
        else :
            return None

    def addAttribute(self,key,value) :
        self.__attributes[key] = value

    def deleteAttribute(self,key) :
        del self.__attributes[key]

class ChunkNode() :

    def __init__(self, header) :
        self.text = []
        self.header = header
        self.footer = None
        self.nodeList = []
        self.parent = '0'
        self.__attributes = {}
        self.parentRelation = 'root'
        self.name = None
        self.type = None
        self.head = None
        self.isParent = False
        self.errors = []
        self.upper = None
        self.updateDrel()
        self.type = None
        self.fsList = None
        self.isPronoun=False
        self.PrePronounrefstm=None
        self.PrePronounrefnode=None
        self.isPronounresolved=False

        self.number='any'
        self.person='none'
        self.gender=None
        self.morphroot=None
        self.case=None
        self.morphPOS=None
        self.tamUtf=None
        self.tamWx=None

    def analyzeChunk(self)  :
        [chunkType,chunkFeatDict,chunkFSList] = getChunkFeats(self.header)
        self.fsList = chunkFSList
        self.type = chunkType
        self.updateAttributes(chunkFeatDict)
        self.text = '\n'.join([line for line in self.text])

    def updateAttributes(self,fsDict) :
        for attribute in fsDict.keys() :
            self.__attributes[attribute] = fsDict[attribute]
        self.assignName()
        self.updateDrel()

    def assignName(self) :
        if self.__attributes.has_key('name') :
            self.name = self.getAttribute('name')
        else :
            self.errors.append('No name for this chunk Node')

    def updateDrel(self) :
        if self.__attributes.has_key('drel') :
            drelList = self.getAttribute('drel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('drel').split(':')[0]
        elif self.__attributes.has_key('dmrel') :
            drelList = self.getAttribute('dmrel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('dmrel').split(':')[0]

    def printValue(self) :
        returnString = []
        for node in self.nodeList :
            returnString.append(node.printValue())
        return ' '.join(x for x in returnString)

    def printSSFValue(self, prefix, allFeat) :
        returnStringList = []
        returnValue = [prefix , '((' , self.type]
        if allFeat == False :
            fs = ['<fs']
            for key in self.__attributes.keys() :
                fs.append(key + "='" + self.getAttribute(key) + "'")
            delim = ' '
            fs[-1] = fs[-1] + '>'

        else :
            fs = self.fsList
            delim = '|'

        returnStringList.append('\t'.join(x for x in returnValue) + '\t' + delim.join(x for x in fs))
        nodePosn = 0
        for node in self.nodeList :
            nodePosn += 1
            if isinstance(node,ChunkNode) :
                returnStringList.extend(node.printSSFValue(prefix + '.' + str(nodePosn), allFeat))
            else :
                returnStringList.append(node.printSSFValue(prefix + '.' + str(nodePosn), allFeat))
        returnStringList.append('\t' + '))')
        return returnStringList

    def getAttribute(self,key) :
        if self.__attributes.has_key(key) :
            return self.__attributes[key]
        else :
            return None

    def addAttribute(self,key,value) :
        self.__attributes[key] = value

    def deleteAttribute(self,key) :
        del self.__attributes[key]



class ChunkNode_vandan() :

    def __init__(self, name) :
        self.text = []
        self.name = name
        self.footer = None
        self.nodeList = []
        self.parent = '0'
        self.__attributes = {}
        self.parentRelation = 'root'
        #self.name = None
        self.type = None
        self.head = None
        self.isParent = False
        self.errors = []
        self.upper = None
        self.updateDrel()
        self.type = None
        self.fsList = None
        self.isPronoun=False
        self.PrePronounrefstm=None
        self.PrePronounrefnode=None
        self.isPronounresolved=False

        self.number='any'
        self.person='none'
        self.gender=None
        self.morphroot=None
        self.case=None
        self.morphPOS=None
        self.tamUtf=None
        self.tamWx=None

    def analyzeChunk(self)  :
        [chunkType,chunkFeatDict,chunkFSList] = getChunkFeats(self.header)
        self.fsList = chunkFSList
        self.type = chunkType
        self.updateAttributes(chunkFeatDict)
        self.text = '\n'.join([line for line in self.text])

    def updateAttributes(self,fsDict) :
        for attribute in fsDict.keys() :
            self.__attributes[attribute] = fsDict[attribute]
        self.assignName()
        self.updateDrel()

    def assignName(self) :
        if self.__attributes.has_key('name') :
            self.name = self.getAttribute('name')
        else :
            self.errors.append('No name for this chunk Node')

    def updateDrel(self) :
        if 'drel' in self.__attributes:
            drelList = self.getAttribute('drel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('drel').split(':')[0]
        elif 'dmrel' in self.__attributes:
            drelList = self.getAttribute('dmrel').split(':')
            if len(drelList) == 2 :
                self.parent = drelList[1]
                self.parentRelation = self.getAttribute('dmrel').split(':')[0]

    def printValue(self) :
        returnString = []
        for node in self.nodeList :
            returnString.append(node.printValue())
        return ' '.join(x for x in returnString)

    def printSSFValue(self, prefix, allFeat,nodePosn) :
        returnStringList = []
        #returnValue = [prefix , '((' , self.type]
        #if allFeat == False :
        #    fs = ['<fs']
        #    for key in self.__attributes.keys() :
        #        fs.append(key + "='" + self.getAttribute(key) + "'")
        #    delim = ' '
        #    fs[-1] = fs[-1] + '>'
        #else :
        #    fs = self.fsList
        #    delim = '|'
        #returnStringList.append('\t'.join(x for x in returnValue) + '\t' + delim.join(x for x in fs))
        #nodePosn = 0
        for node in self.nodeList :
            nodePosn += 1
            if isinstance(node,ChunkNode) :
                #returnStringList.extend(node.printSSFValue(prefix + '.' + str(nodePosn), allFeat))
                returnStringList.extend(node.printSSFValue(str(nodePosn), allFeat))
            else :
                #returnStringList.append(node.printSSFValue(prefix + '.' + str(nodePosn), allFeat))
                returnStringList.append(node.printSSFValue(str(nodePosn), allFeat))
        #returnStringList.append('\t' + '))')
        return returnStringList,nodePosn

    def getAttribute(self,key) :
        if key in self.__attributes:
            return self.__attributes[key]
        else :
            return None

    def addAttribute(self,key,value) :
        self.__attributes[key] = value

    def deleteAttribute(self,key) :
        del self.__attributes[key]





class Sentence() :
    def __init__(self, sentence, upper, ignoreErrors = True, nesting = True, dummySentence = False) :
        self.ignoreErrors = ignoreErrors
        self.nesting = nesting
        self.sentence = None
        self.sentenceID = None
        self.sentenceType = None
        self.length = 0
        self.tree = None
        self.nodeList = []
        self.edges = {}
        self.nodes = {}
        self.tokenNodes = {}
        self.rootNode = None
        self.fileName = None
        self.comment = None
        self.probSent = False
        self.errors = []
        self.upper = upper
        self.dummySentence = dummySentence
        self.dependencyRoot = None
        #self.linecount = 0
        if self.dummySentence == False :
            self.header = sentence.group('header')
            self.footer = sentence.group('footer')
            self.name = sentence.group('sentenceID')
            self.text = sentence.group('text')
            self.analyzeSentence()

    def analyzeSentence(self, ignoreErrors = False, nesting = True) :
        lastContext = self
        lastContext_ex = self
        currentChunkNode = None
        previous_chunk_name = ''
        #linecount = 0
        for line in self.text.split('\n') :
            stripLine = line.strip()

            if stripLine=="" :
                continue
            elif stripLine[0]=="<" and ignoreErrors == False :
                    self.errors.append('Encountered a line starting with "<"')
                    self.probSent = True
            else :
                splitLine = stripLine.split()
                if len(splitLine)>0 and splitLine[0] == '))' :
                    currentChunkNode.footer = line + '\n'
                    currentChunkNode.analyzeChunk()

                    if currentChunkNode.getAttribute('af')!=None:
                        aa= currentChunkNode.getAttribute('af').strip().split(',')
                        if len(aa)>=6:
                            currentChunkNode.morphroot=aa[0];currentChunkNode.morphPOS=aa[1]
                            currentChunkNode.number=aa[3];currentChunkNode.person=aa[4]
                            currentChunkNode.gender=aa[2];currentChunkNode.case=aa[5]
                            currentChunkNode.tamUtf=aa[6];currentChunkNode.tamWx=aa[7]

                    lastContext = currentChunkNode.upper
                elif len(splitLine)>1 and splitLine[1] == '((' :
                    currentChunkNode = ChunkNode(line + '\n')
                    currentChunkNode.upper = lastContext
                    currentChunkNode.upper.nodeList.append(currentChunkNode)
                    if currentChunkNode.upper.__class__.__name__ != 'Sentence' :
                        currentChunkNode.upper.text.append(line)
                    lastContext = currentChunkNode
                else :
                    self.upper.linecount += 1
                    #currentNode = Node(line + '\n',lastContext ,self.upper.linecount)
                    #lastContext.nodeList.append(currentNode)
                    #currentNode.upper = lastContext
		    # newer part vandan
                    if len(splitLine)>0 :
                        chunk_split = ''.join ([x for x in splitLine if 'chunkType=' in x]).replace('>','').split('=')[1].replace("'","").split(':')
                        chunk_name = chunk_split[1]
                        chunk_relation = chunk_split[0]
                        currentNode_ext = Node_vandan(line + '\n',lastContext ,self.upper.linecount, chunk_relation)
                        if  previous_chunk_name != chunk_name :
                            currentChunkNode = ChunkNode_vandan(chunk_name)
                            currentChunkNode.nodeList.append(currentNode_ext)
                            currentNode_ext.upper = currentChunkNode
                            currentChunkNode.upper = lastContext
                            currentChunkNode.upper.nodeList.append(currentChunkNode)
                            if currentChunkNode.upper.__class__.__name__ != 'Sentence' :
                                currentChunkNode.upper.text.append(line)
                        else:
                            currentChunkNode.nodeList.append(currentNode_ext)
                            currentNode_ext.upper = currentChunkNode
                        previous_chunk_name = chunk_name
                        
        for i in lastContext.nodeList:
            for j in i.nodeList:
                drel = j.getAttribute('drel')
                if drel == None:
                    dmrel = j.getAttribute('dmrel')
                    if dmrel == None:
                        j.parent = j
                        j.parentRelation = '0'
                        j.upper.upper.dependencyRoot = j
                        if 'head:' in j.text:
                            i.parentRelation = '0'
                            i.parent = j.upper.name
                    else:
                        d_temp = dmrel.split(':')
                        j.parentRelation = d_temp[0]
                        j.parent = self.find_dependency_parent_node(lastContext.nodeList,d_temp[1])
                        j.parent.childList.append(j)
                        if 'head:' in j.text:
                            i.parentRelation = d_temp[0]
                            i.parent = self.find_dependency_parent_node(lastContext.nodeList,d_temp[1]).upper.name

                else:
                    d_temp = drel.split(':')
                    j.parentRelation = d_temp[0]
                    j.parent = self.find_dependency_parent_node(lastContext.nodeList,d_temp[1])
                    j.parent.childList.append(j)
                    if 'head:' in j.text:
                        i.parentRelation = d_temp[0]
                        i.parent = self.find_dependency_parent_node(lastContext.nodeList,d_temp[1]).upper.name
            
    def find_dependency_parent_node (self, nodeList,name):
        for i in nodeList:
            for j in i.nodeList:
                if j.getAttribute('name') == name :
                    return j
        return None
			
	
    def addEdge(self, parent , child) :
        if parent in self.edges.iterkeys() :
            if child not in self.edges[parent] :
                self.edges[parent].append(child)
        else :
            self.edges[parent] = [child]

    def updateAttributes(self) :
        populateNodesStatus = self.populateNodes()
        populateEdgesStatus = self.populateEdges()
        self.sentence = self.generateSentence()
        if populateEdgesStatus == 0 or populateNodesStatus == 0:
            return 0
        return 1

    def printSSFValue(self, allFeat = True) :
        returnStringList = []
        returnStringList.append("<Sentence id='" + str(self.name) + "'>\n")
        if self.nodeList != [] :
            nodeList = self.nodeList
            nodePosn = 0
            for node in nodeList :
                #print node.__class__.__name__
                #nodePosn += 1
                nodewisestring,nodePosn=node.printSSFValue(str(nodePosn), allFeat,nodePosn)
                returnStringList.extend(nodewisestring)
        returnStringList.append( '</Sentence>\n')
        return ''.join(x for x in returnStringList)

    def populateTokenNodes(self , naming = 'Manual') :
        tokenList = returnTokenList(self.nodeList)
        #assignTokenNodeNames(tokenList)
        for nodeElement in tokenList :
            self.tokenNodes[nodeElement.name] = nodeElement

    def populateNodes(self , naming = 'strict') :
        if naming == 'strict' :
            for nodeElement in self.nodeList :
                assert nodeElement.name is not None
                self.nodes[nodeElement.name] = nodeElement
        return 1

    def populateEdges(self) :
        for node in self.nodeList :
            nodeName = node.name
            if node.parent == '0'  or node == self.rootNode:
                self.rootNode = node
                continue
            elif node.parent not in self.nodes.iterkeys() :
#                self.errors.append('Error : Bad DepRel Parent Name ' + self.fileName + ' : ' + str(self.name))
                return 0
            assert node.parent in self.nodes.iterkeys()
            self.addEdge(node.parent , node.name)
        return 1

    def generateSentence(self) :
        sentence = []
        for nodeName in self.nodeList :
            sentence.append(nodeName.printValue())
        return ' '.join(x for x in sentence)

class Document() :

    def __init__(self, fileName) :
        self.header = None
        self.footer = None
        self.text = None
        self.nodeList = []
        self.fileName = fileName
        self.upper = None
        self.linecount=0
        self.coreferenceChainNodeList = []
        self.acoreferenceEntityNodeList = []
        #self.coreferencechain = Coreference_chain()
        #self.coreferenceentity = Coreference_entity()
        self.analyzeDocument()

    def analyzeDocument(self) :

        inputFD = codecs.open(self.fileName, 'r', encoding='UTF-8')
        sentenceList = getSentenceIter(inputFD)
        for sentence in sentenceList :
            tree = Sentence(sentence, self, ignoreErrors = True, nesting = True, dummySentence = False)
            tree.upper = self
            self.nodeList.append(tree)
        inputFD.close()
        returnErrors=[]
def getAddressNode(address, node, level = 'ChunkNode') :

    ''' Returns the node referenced in the address string relative to the node in the second argument.
        There are levels for setting the starting address-base. These are "ChunkNode", "Node" , "Sentence" , "Document" , "Relative".
        The hierarchy of levels for interpretation is :
        "Document" -> "Sentence" -> "ChunkNode" -> "Node"
        "Relative" value starts the base address from the node which contains the address. This is also the default option.
    '''

    currentContext = node

    if level != 'Relative' :
        while(currentContext.__class__.__name__ != level) :
            currentContext = currentContext.upper

    currentContext = currentContext.upper

    stepList = address.split('%')

    for step in stepList :
        if step == '..' :
            currentContext = currentContext.upper
        else :
            refNode = [iterNode for iterNode in currentContext.nodeList if iterNode.name == step][0]
            currentContext = refNode
    return refNode

def returnTokenList(nodeList) :
    tokenList = []
    for nodeIter in nodeList :
        if isinstance(nodeIter, ChunkNode)==True :
            tokenList.extend(returnTokenList(nodeIter.nodeList))
        elif isinstance(nodeIter, Node)==True:
            tokenList.append(nodeIter)
    return tokenList

def returnChunkList(nodeList) :
    tokenList = []
    for nodeIter in nodeList :
        if isinstance(nodeIter, ChunkNode)==True :
            tokenList.append(nodeIter)
            tokenList.extend(returnChunkList(nodeIter.nodeList))
    return tokenList

def getChunkFeats(line) :
    lineList = line.strip().split()
    chunkType = None
    fsList = []
    if len(lineList) >= 3 :
        chunkType = lineList[2]

    returnFeats = {}
    multipleFeatRE = r'<fs.*?>'
    featRE = r'(?:\W*)(\S+)=([\'|\"])?([^ \t\n\r\f\v\'\"]*)([\'|\"])?(?:.*)'
    fsList = re.findall(multipleFeatRE, ' '.join(lineList))
    for x in lineList :
        feat = re.findall(featRE, x)
        if feat!=[] :
            if len(feat) > 1 :
                returnErrors.append('Feature with more than one value')
                continue
            returnFeats[feat[0][0]] = feat[0][2]

    return [chunkType,returnFeats,fsList]

def getTokenFeats(lineList) :
    tokenType, token = None , None
    returnFeats = {}
    fsList = []
    if len(lineList) >=3 :
        tokenType = lineList[2]

    token = lineList[1]
    multipleFeatRE = r'<fs.*?>'
    featRE = r'(?:\W*)(\S+)=([\'|\"])?([^ \t\n\r\f\v\'\"]*)([\'|\"])?(?:.*)'
    fsList = re.findall(multipleFeatRE, ' '.join(lineList))
    for x in lineList :
        feat = re.findall(featRE, x)
        if feat!=[] :
            if len(feat) > 1 :
                returnErrors.append('Feature with more than one value')
                continue
            returnFeats[feat[0][0]] = feat[0][2]
    return [token,tokenType,returnFeats,fsList]

def getSentenceIter(inpFD) :

    sentenceRE = r'''(?P<complete>(?P<header><Sentence id=[\'\"]?(?P<sentenceID>\d+)[\'\"]?>)(?P<text>.*?)(?P<footer></Sentence>))'''
    text = inpFD.read()
    return re.finditer(sentenceRE, text, re.DOTALL)

def folderWalk(folderPath):
    import os
    fileList = []
    for dirPath , dirNames , fileNames in os.walk(folderPath) :
        for fileName in fileNames :
            fileList.append(os.path.join(dirPath , fileName))
    return fileList


'''
if __name__ == '__main__' :

    #inputPath = sys.argv[1]
    fileList = folderWalk('/home/vandan/workspace/input/')
    newFileList = []
    for fileName in fileList :
        xFileName = fileName.split('/')[-1]
        if xFileName == 'err.txt' or xFileName.split('.')[-1] in ['comments','bak'] or xFileName[:4] == 'task' :
            continue
        else :
            newFileList.append(fileName)

    for fileName in newFileList :
        d = Document(fileName)
        print d.fileName
        for tree in d.nodeList :
            print tree.text
            for chunkNode in tree.nodeList :
                for node in chunkNode.nodeList :
                    print node.lex
                print '\n\nVandan mujadia\n\n'
		print chunkNode.getAttribute('semprop')
'''

#                        print tree.printSSFValue()
#                        print tree.header + tree.text + tree.footer
#                        tree(nodeList) means sentence in SSF structure
#


