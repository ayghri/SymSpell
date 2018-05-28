# SymSpell
Implementation in Python3
<br>
* For further details about the concept, check https://github.com/wolfgarbe/SymSpell
* This version if based on the functional implementation https://github.com/ppgmg/github_public/tree/master/spell

The idea is to use Lavenstein distance to correct words, but only using delete operation (without insertion or transposition). Since the delete cost is lower, the larger the dictionary the more computation are spared.

The algorithm is as follows:

0. Parameters : max_distance, words_list
1. Initiate Dictionary
2. for word in words_list:
  - if word in dictionary :
    - dicttionary[word] = (empty_word_list,0)
  - else:
    - dicttionary[word][1] += 1  (add one more occurence)
 - deletes = generate_deletes(word, max_distance)
 - for delete in deletes:
   - if delete in dictionary:
     - dictionary[delete][0].add(word)
   - else:
     - dictionary[delete][0]=([word],0)
     
     
Once the dictionary has been built, to correct a word:
- we generate its deletes,
- look for the deletes in the dictionary, 
- retrieve generative words and calculate distances from these words
- sort, in ascending order,by (distance, -occurences)
