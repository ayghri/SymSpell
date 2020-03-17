import numpy as np
import re
import sys
import time
import collections


def generate_deletes(string, max_distance):
    deletes = []
    queue = [string]
    for d in range(max_distance):
        temp_queue = []
        for word in queue:
            if len(word) > 1:
                for c in range(len(word)):  # character index
                    word_minus_c = word[:c] + word[c + 1 :]
                    if word_minus_c not in deletes:
                        deletes.append(word_minus_c)
                    if word_minus_c not in temp_queue:
                        temp_queue.append(word_minus_c)
        queue = temp_queue

    return deletes


def levenshtein(string1, string2):

    if len(string1) < len(string2):
        return levenshtein(string2, string1)
    if len(string2) == 0:
        return len(string1)

    arr_string1 = np.array(list(string1))
    arr_string2 = np.array(list(string2))

    last_row = np.arange(arr_string2.size + 1)
    for s in arr_string1:
        current_row = last_row + 1

        current_row[1:] = np.minimum(
            current_row[1:], np.add(last_row[:-1], arr_string2 != s)
        )

        # Deletion (string2 grows shorter than string1):
        current_row[1:] = np.minimum(current_row[1:], current_row[0:-1] + 1)

        last_row = current_row

    return last_row[-1]


def read_corpus(path):
    f = open(path, "r")
    words = []
    for w in f.readlines():
        words.append(w.split()[0].lower())
    f.close()
    return words


def create_dictionary(fname):
    dictionary = []
    with open(fname) as file:
        for line in file:
            # separate by words by non-alphabetical characters
            words = re.findall("[a-z]+", line.lower())
            for word in words:
                dictionary.append(word)
    return dictionary


def tweet_words(tweets):
    words = []
    for tweet in tweets:
        for w in re.findall("[a-z]+", tweet):
            words.append(w)
    return words


def correct_series(word, dict_corpus):
    # print(word)
    if word in dict_corpus:
        return word, True
    if len(word) == 0:
        return "", True
    i = 2
    corrections = {}
    order = 0
    while i <= len(word):
        # print(i)
        if word[:i] in dict_corpus:
            correct, possible = correct_series(word[i:], dict_corpus)
            if possible:
                corrections[word[:i] + " " + correct] = (
                    order,
                    len(word[:i] + " " + correct),
                )
                order += 1
        i = i + 1

    if len(corrections) == 0:
        return "", False
    else:
        return (
            sorted(corrections.items(), key=lambda term, val: (val[1], val[0]))[0][0],
            True,
        )


class Progbar(object):
    """Displays a progress bar.

    # Arguments
        target: Total number of steps expected, None if unknown.
        width: Progress bar width on screen.
        verbose: Verbosity mode, 0 (silent), 1 (verbose), 2 (semi-verbose)
        stateful_metrics: Iterable of string names of metrics that
            should *not* be averaged over time. Metrics in this list
            will be displayed as-is. All others will be averaged
            by the progbar before display.
        interval: Minimum visual progress update interval (in seconds).
    """

    def __init__(
        self, target, width=30, verbose=1, interval=0.05, stateful_metrics=None
    ):
        self.target = target
        self.width = width
        self.verbose = verbose
        self.interval = interval
        if stateful_metrics:
            self.stateful_metrics = set(stateful_metrics)
        else:
            self.stateful_metrics = set()

        self._dynamic_display = (
            hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        ) or "ipykernel" in sys.modules
        self._total_width = 0
        self._seen_so_far = 0
        self._values = collections.OrderedDict()
        self._start = time.time()
        self._last_update = 0

    def update(self, current, values=None):
        """Updates the progress bar.

        # Arguments
            current: Index of current step.
            values: List of tuples:
                `(name, value_for_last_step)`.
                If `name` is in `stateful_metrics`,
                `value_for_last_step` will be displayed as-is.
                Else, an average of the metric over time will be displayed.
        """
        values = values or []
        for k, v in values:
            if k not in self.stateful_metrics:
                if k not in self._values:
                    self._values[k] = [
                        v * (current - self._seen_so_far),
                        current - self._seen_so_far,
                    ]
                else:
                    self._values[k][0] += v * (current - self._seen_so_far)
                    self._values[k][1] += current - self._seen_so_far
            else:
                self._values[k] = v
        self._seen_so_far = current

        now = time.time()
        info = " - %.0fs" % (now - self._start)
        if self.verbose == 1:
            if (
                now - self._last_update < self.interval
                and self.target is not None
                and current < self.target
            ):
                return

            prev_total_width = self._total_width
            if self._dynamic_display:
                sys.stdout.write("\b" * prev_total_width)
                sys.stdout.write("\r")
            else:
                sys.stdout.write("\n")

            if self.target is not None:
                numdigits = int(np.floor(np.log10(self.target))) + 1
                barstr = "%%%dd/%d [" % (numdigits, self.target)
                bar = barstr % current
                prog = float(current) / self.target
                prog_width = int(self.width * prog)
                if prog_width > 0:
                    bar += "=" * (prog_width - 1)
                    if current < self.target:
                        bar += ">"
                    else:
                        bar += "="
                bar += "." * (self.width - prog_width)
                bar += "]"
            else:
                bar = "%7d/Unknown" % current

            self._total_width = len(bar)
            sys.stdout.write(bar)

            if current:
                time_per_unit = (now - self._start) / current
            else:
                time_per_unit = 0
            if self.target is not None and current < self.target:
                eta = time_per_unit * (self.target - current)
                if eta > 3600:
                    eta_format = "%d:%02d:%02d" % (
                        eta // 3600,
                        (eta % 3600) // 60,
                        eta % 60,
                    )
                elif eta > 60:
                    eta_format = "%d:%02d" % (eta // 60, eta % 60)
                else:
                    eta_format = "%ds" % eta

                info = " - ETA: %s" % eta_format
            else:
                if time_per_unit >= 1:
                    info += " %.0fs/step" % time_per_unit
                elif time_per_unit >= 1e-3:
                    info += " %.0fms/step" % (time_per_unit * 1e3)
                else:
                    info += " %.0fus/step" % (time_per_unit * 1e6)

            for k in self._values:
                info += " - %s:" % k
                if isinstance(self._values[k], list):
                    avg = np.mean(self._values[k][0] / max(1, self._values[k][1]))
                    if abs(avg) > 1e-3:
                        info += " %.4f" % avg
                    else:
                        info += " %.4e" % avg
                else:
                    info += " %s" % self._values[k]

            self._total_width += len(info)
            if prev_total_width > self._total_width:
                info += " " * (prev_total_width - self._total_width)

            if self.target is not None and current >= self.target:
                info += "\n"

            sys.stdout.write(info)
            sys.stdout.flush()

        elif self.verbose == 2:
            if self.target is None or current >= self.target:
                for k in self._values:
                    info += " - %s:" % k
                    avg = np.mean(self._values[k][0] / max(1, self._values[k][1]))
                    if avg > 1e-3:
                        info += " %.4f" % avg
                    else:
                        info += " %.4e" % avg
                info += "\n"

                sys.stdout.write(info)
                sys.stdout.flush()

        self._last_update = now

    def add(self, n, values=None):
        self.update(self._seen_so_far + n, values)
