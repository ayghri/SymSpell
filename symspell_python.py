import sys
import utils


class SymSpell(object):
    def __init__(self, list_words, max_distance=3):
        self.max_distance = max_distance
        self.dictionary = {}
        self.max_length = 0
        self.progbar = utils.Progbar(len(list_words))
        self.build(list_words)

    def build(self, words):
        n = len(words)
        self.progbar.__init__(n)
        sys.stdout.write(
            "Processing %d words to create SymSpell for edit distance %d \n"
            % (n, self.max_distance)
        )
        for i in range(n):
            self.progbar.add(1)
            w = words[i]
            if w in self.dictionary:
                self.dictionary[w] = (self.dictionary[w][0], self.dictionary[w][1] + 1)
            else:
                self.dictionary[w] = ([], 1)
                self.max_length = max(self.max_length, len(w))

            if self.dictionary[w][1] == 1:
                deletes = utils.generate_deletes(w, self.max_distance)
                for d in deletes:
                    if d in self.dictionary:
                        self.dictionary[d][0].append(w)
                    else:
                        self.dictionary[d] = ([w], 0)

    def correct(self, string):
        if (len(string) - self.max_length) > self.max_distance:
            return []

        corrections_dict = {}
        min_correct_len = float("inf")
        queue = sorted(
            list(set([string] + utils.generate_deletes(string, self.max_distance))),
            key=len,
            reverse=True,
        )

        while len(queue) > 0:
            q_item = queue.pop(0)

            if (len(corrections_dict) > 0) and (
                (len(string) - len(q_item)) > min_correct_len
            ):
                break

            if (q_item in self.dictionary) and (q_item not in corrections_dict):
                if self.dictionary[q_item][1] > 0:
                    corrections_dict[q_item] = (
                        self.dictionary[q_item][1],
                        len(string) - len(q_item),
                    )
                    if len(string) == len(q_item):
                        break

                    elif (len(string) - len(q_item)) < min_correct_len:
                        min_correct_len = len(string) - len(q_item)

                for sc_item in self.dictionary[q_item][0]:
                    if sc_item not in corrections_dict:
                        if len(q_item) == len(string):
                            item_dist = len(sc_item) - len(q_item)

                        item_dist = utils.levenshtein(sc_item, string)

                        if item_dist > min_correct_len:
                            pass

                        elif item_dist <= self.max_distance:
                            corrections_dict[sc_item] = (
                                self.dictionary[sc_item][1],
                                item_dist,
                            )
                            if item_dist < min_correct_len:
                                min_correct_len = item_dist

                        corrections_dict = {
                            k: v
                            for k, v in corrections_dict.items()
                            if v[1] <= min_correct_len
                        }

        return corrections_dict

    def best(self, string):
        try:
            as_list = self.correct(string).items()
            outlist = sorted(as_list, key=lambda item: (item[1][1], -item[1][0]))
            return outlist[0][0]
        except:
            return None
