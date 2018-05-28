
import sys
import utils        

class SymSpell(object):
    """
        Python Implementation of SymSpell
    """
    
    def __init__(self,list_words,max_distance = 3):
        
        self.max_distance = max_distance 
        self.dictionary = build_dictionary_entries(list_words,self.max_distance)
        

                        
    def corrections(self,string):
        """
            Return all words of the corpus that are in distance <= max_distance
            The values are : distance, number of occurencies
        """
        if (len(string) - self.max_length) > self.max_distance:
            return []        
        corrections_dict = {}
        min_correct_len = float('inf')
        
        queue = sorted(list(set([string]+utils.generate_deletes(string,self.max_distance))),key=len,reverse=True)

        while len(queue)>0:
            q_item = queue.pop(0)
            
            if ((len(corrections_dict)>0) and ((len(string)-len(q_item))>min_correct_len)):
                break
            if (q_item in self.dictionary) and (q_item not in corrections_dict):
                if (self.dictionary[q_item][1]>0):
                    corrections_dict[q_item] = (self.dictionary[q_item][1],len(string) - len(q_item))
                    if len(string)==len(q_item):
                        break
                    elif (len(string) - len(q_item)) < min_correct_len:
                        min_correct_len = len(string) - len(q_item)
                
                for sc_item in self.dictionary[q_item][0]:
                    if (sc_item not in corrections_dict):
                        if len(q_item)==len(string):
                            item_dist = len(sc_item) - len(q_item)
                            
                        item_dist = utils.levenshtein(sc_item, string)
                        
                        if item_dist>min_correct_len:
                            pass
                        elif item_dist<=self.max_distance:
                            corrections_dict[sc_item] = (self.dictionary[sc_item][1], item_dist)
                            if item_dist < min_correct_len:
                                min_correct_len = item_dist
                        
                        corrections_dict = {k:v for k, v in corrections_dict.items() if v[1]<=min_correct_len}
        
        return corrections_dict
    
    def best(self,string):
        """
            Returns the best word, sorted by distanc ethen by occurencies
        """
        try:
            as_list = self.get_corrections(string).items()
            outlist = sorted(as_list, key= lambda key,val : (val[1], -val[0]))
            return outlist[0][0]
        except:
            return None

def build_dictionary_entries(words, max_distance):
    dictionary = {}
    n = len(words)
    sys.stdout.write("Processing %d words to create SymSpell for edit distance %d \n"%(n,max_distance))
    for i in range(n):
        if not i%10000:
            sys.stdout.write("%d out of %d\r"%(i,n))
            sys.stdout.flush()
        w=words[i]
        if w in dictionary:
            dictionary[w] = (dictionary[w][0], dictionary[w][1] + 1)
        else:
            dictionary[w] = ([], 1)  
            max_length = max(max_distance, len(w))
            
        if dictionary[w][1]==1:
            deletes = utils.generate_deletes(w,max_length)
            for d in deletes:
                if d in dictionary:
                    dictionary[d][0].append(w)
                else:
                    dictionary[d] = ([w], 0)         
    
    return dictionary

