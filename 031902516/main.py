# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""
from collections import defaultdict
import re
import pinyin
import sys
__all__ = ['NaiveFilter', 'BSFilter', 'DFAFilter']


pinyin_list=[]
English_word_list=[]
re_pattern_list=[]
total_list=[]
index=1
SUM_LIST=[]

class NaiveFilter():
    '''Filter Messages from keywords
    very simple filter implementation
    >>> f = NaiveFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keywords = set([])

    def parse(self, path):
        for keyword in open(path):
            self.keywords.add(keyword.strip().decode('utf-8').lower())

    def filter(self, message, repl="*"):
        message = message.lower()
        for kw in self.keywords:
            message = message.replace(kw, repl)
        return message


class BSFilter:
    '''Filter Messages from keywords
    Use Back Sorted Mapping to reduce replacement times
    >>> f = BSFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keywords = []
        self.kwsets = set([])
        self.bsdict = defaultdict(set)
        self.pat_en = re.compile(r'^[0-9a-zA-Z]+$')  # english phrase or not

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        if keyword not in self.kwsets:
            self.keywords.append(keyword)
            self.kwsets.add(keyword)
            index = len(self.keywords) - 1
            for word in keyword.split():
                if self.pat_en.search(word):
                    self.bsdict[word].add(index)
                else:
                    for char in word:
                        self.bsdict[char].add(index)

    def parse(self, path):
        with open(path, "r") as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        for word in message.split():
            if self.pat_en.search(word):
                for index in self.bsdict[word]:
                    message = message.replace(self.keywords[index], repl)
            else:
                for char in word:
                    for index in self.bsdict[char]:
                        message = message.replace(self.keywords[index], repl)
        return message


class DFAFilter():
    '''Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='UTF-8') as f:
            
            for keyword in f:
                keyword=keyword.replace("\n", "")
                if isChinese(keyword):
                    pinyin_list.append(pinyin.get(keyword, format='strip', delimiter=""))
                    haha_pattern=""
                    for ch in keyword:
                        haha_pattern=haha_pattern+ch
                        haha_pattern+='.{0,20}'
                    re_pattern_list.append(haha_pattern[:-7])
                    total_list.append(keyword)
                    
                    
                    tt_word=keyword
                    for tt_cha in tt_word:
                        ttt_word=keyword
                        #print(pinyin.get(tt_cha, format='strip', delimiter=""))
                        ttt_word=ttt_word.replace(tt_cha, pinyin.get(tt_cha, format='strip', delimiter=""))
                        #print(ttt_word)
                        self.add(ttt_word)
                        haha_pattern=""
                        for ch in ttt_word:
                            haha_pattern=haha_pattern+ch
                            haha_pattern+='.{0,20}'
                        re_pattern_list.append(haha_pattern[:-7])
                        #print(haha_pattern[:-7])
                        total_list.append(keyword)
                    
                    
                else:
                    hh_pattern=""
                    for ch in keyword:
                        hh_pattern=hh_pattern+ch
                        hh_pattern+='.{0,20}'
                    re_pattern_list.append(hh_pattern[:-7])
                    English_word_list.append(keyword)
                    total_list.append(keyword) 
                self.add(keyword.strip())
            for temp_word in pinyin_list:
                self.add(temp_word.strip())
                hh_pattern=""
                for ch in temp_word:
                    hh_pattern=hh_pattern+ch
                    hh_pattern+='.{0,20}'
                re_pattern_list.append(hh_pattern[:-7])
                total_list.append(keyword)
        #print(self.keyword_chains)

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        back = message
        message = message.lower()
        for i in range(len(re_pattern_list)):
            message=re.sub(re_pattern_list[i], total_list[i], message)
        ret = []
        start = 0
        fd=open("MyAnswer.txt", "a")
        tmp_char=""
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        count_num = start
                        while(1):
                            if back[count_num] == message[start + step_ins]:
                                break
                            tmp_char=tmp_char+back[count_num]
                            count_num += 1
                        ret.append(repl * step_ins)
                        print("Line", end="")
                        print(index, end="")#?????? index???????????????
                        print("<", end="")
                        print(message[start:start+step_ins], end="")#?????????
                        print(">")
                        print(tmp_char)
                        # fd.write("Line")
                        # fd.write(str(index))
                        # fd.write("<")
                        # fd.write(message[start:start+step_ins])
                        # fd.write(">\n")
                        temp_str="Line"+str(index)+"<"+message[start:start+step_ins]+"> "+tmp_char+"\n"
                        tmp_char=""
                        
                        #print(temp_line[start:start+step_ins])#??????????????????
                        SUM_LIST.append(temp_str)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    tmp_char = ""
                    break
            else:
                ret.append(message[start])
            start += 1
        fd.close()

        return ''.join(ret)

    def is_contain_sensi_key_word(self, message):
        repl = '_-__-'
        dest_string = self.filter(message=message, repl=repl)
        if repl in dest_string:
            return True
        return False

def replace_char(matched):
    return ""

def test_first_character():
    gfw = DFAFilter()
    gfw.add("1989???")
    assert gfw.filter("1989", "*") == "1989"
    
def isChinese(word):#?????????????????????
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False
temp_line=""
if __name__ == "__main__":
    # gfw = NaiveFilter()
    # gfw = BSFilter()
    gfw = DFAFilter()
    #keywords = sys.argv[1]
    #org = sys.argv[2]
    #MyAnswer = sys.argv[3]
    gfw.parse(sys.argv[1])
    import time

    t = time.process_time()
    #print(gfw.filter("??????fd??? ????????????fucck", "*"))
    #print(gfw.filter("??????????????? ????????????", "*"))
    #print(gfw.filter("??????????????? ????????????", "*"))
    #print(gfw.filter("???????????? ????????????", "*"))
    print('Cost is %6.6f' % (time.process_time() - t))
    print(gfw.is_contain_sensi_key_word('?????????'))
    with open(sys.argv[2], encoding='UTF-8') as ff:
        for line in ff:
            temp_line=line
            gfw.filter(line)
            index=index+1
    fd=open(sys.argv[3], "w")
    fd.write("Total:")
    fd.write(str(len(SUM_LIST)))
    fd.write("\n")
    for res in SUM_LIST:
        fd.write(res)
    fd.close()
    print(len(SUM_LIST))
    #test_first_character()