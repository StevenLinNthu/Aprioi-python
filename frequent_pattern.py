import re
import operator
import sys
import os
import itertools
import time


def abs_2_trans(abstract , stop_words):
    abstract = abstract.lower()
    abstract = re.sub('[\\n]',' ',abstract)
    abstract = re.sub('[!@#$%^&*()\\n$:;]+',' ',abstract)
    #sentences = re.split('[.,?]+',abstract)
    sentences = re.split('(?<![0-9])([\.,?])',abstract)
    stop_words.extend(['.',',','?'])
    ret = []
    for se in sentences:
        k = se.split(' ')
        a = []
        for s in k:
            if s not in stop_words and len(s)>0:
                a.append(s)
        if len(a)>0:
            ret.append(a)
    return ret
def sort_pattern(pat,inv_word_idx):
    items = pat.items()
    words = []
    freqs = []
    for k , v in items:
        word = []
        for w in k:
            word.append(inv_word_idx[w])
        word.sort()
        freqs.append(v)
        words.append(word)
    ls = [[words[i],freqs[i]] for i in range(len(words)) ]
    ls.sort()
    return ls 


wdcnt = dict()   
def add_wdcnt(wd, stopwd):
    if wd not in stopwd:
        if wd in wdcnt:
            wdcnt[wd] += 1
        else:
            wdcnt[wd] = 1
def word_count(lines, stop_words):
    for line in lines:
        for word in line:
            add_wdcnt(word, stop_words)
    return sorted(wdcnt.items(), key=operator.itemgetter(1),reverse = True)

# def set_minsup(minsup, items):
#     return [item for item in items if(item[1] >= minsup)]

# Apriori part
def is_apriori(items, Lksub):
    for item in items:
        sub_item = items.copy()
        sub_item.sort()
        sub_item.remove(item)
        if sub_item not in Lksub:
            return False
    return True
def generate_Ck(Lksub, k):
    Ck = []
    len_l = len(Lksub)
    list_l = Lksub.copy()
    list_l.sort()
    l1, l2 = [], []
    for i in range(len_l):
        for j in range(i+1, len_l):
            l1 += list_l[i][:]
            l2 += list_l[j][:]
            l1.sort()
            l2.sort()
            if l1[0:k-2] == l2[0:k-2]:
                Ck_item = list(set().union(l1, l2))
                if k == 2:
                    Ck.append(Ck_item)
                elif len(Ck_item) == k and is_apriori(Ck_item, Lksub):
                    Ck.append(Ck_item)
            l1, l2 = [], []
    
    return Ck  
def generate_Lk(dataset, Ck, min_support, total_cnt):
    Lk = []
    item_cnt = {}
    max_sup = 0
    for data in dataset:
        data = set(data)
        for item in Ck:
            item = set(item)
            if item.issubset(data):
                if frozenset(item) not in item_cnt:
                    item_cnt[frozenset(item)]= 1
                else:
                    item_cnt[frozenset(item)] += 1
    for item in item_cnt:
        if item_cnt[item] >= min_support:
            tmp = list(item)
            tmp.sort()
            Lk += [tmp]
            total_cnt[item] = item_cnt[item] 
            max_sup = 1
    return Lk , max_sup

if __name__ == "__main__":
    argv = sys.argv
    start = time.time()
    min_support = int(argv[3])
    with open(argv[1],'r') as f:  # read sample input, just for example
        lines = f.readlines()
    with open('stop_words.txt','r') as f: # read stop word list
        words = f.readlines()
        stop_words = []
        for word in words:
            word = word.strip('\n')
            stop_words.append(word)
        stop_words.append('-')
    inset = []
    max_set_len = 0
    for line in lines:
        tmp = abs_2_trans(line, stop_words)
        for i in range(len(tmp)):
            tmp[i] = list(set(tmp[i]))
            tmp[i].sort()
            if len(tmp[i]) > max_set_len:
                max_set_len = len(tmp[i])
        inset += tmp

    sorted_wdcnt = word_count(inset, stop_words)
    L1 = [item for item in sorted_wdcnt if(item[1] >= min_support)]
    #L1 done
    #generate Lk
    L = [x[0] for x in L1] # list of L1
    L.sort()
    Lksub = L.copy()
    sorted(Lksub)
    for i in range(len(Lksub)):
        Lksub[i] = [Lksub[i]]

    total_cnt = {}
    freq_list = []
    for item in L1:
        total_cnt[frozenset([item[0]])] = item[1]
    for i in range(2, max_set_len+1):
        Ci = generate_Ck(Lksub, i)
        Li, cur_sup = generate_Lk(inset, Ci, min_support, total_cnt)
        if cur_sup == 0:
            break
        Lksub = Li.copy()
    #sort
    freq_list = list(set(freq_list))
    freq_list.sort()
    freq_dic = dict()
    freq_dic_rev = dict()
    idx = 0
    for item in L:
        freq_dic[item] = idx
        freq_dic_rev[idx] = item
        idx += 1
    dic_for_sort = dict()
    for items in total_cnt:
        tmp = list(items)
        tmp.sort()
        tmp_l = []
        for item in tmp:
            tmp_l += [freq_dic[item]]
        dic_for_sort[frozenset(tmp_l)] = total_cnt[items]
    ls = sort_pattern(dic_for_sort, freq_dic_rev)



    with open(argv[2],'w') as f:
        for item in ls:
            for i in item[0]:
                f.write(str(i) + ' ')
            f.write(str(item[1]) + '\n');
        f.close()
    end = time.time()
    # print(end - start)