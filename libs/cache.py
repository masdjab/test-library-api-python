class CacheEntry:
    def __init__(self, val):
        self.val = val
        self.hits = 0

    def increment_hits(self):
        # avoid overflow
        if self.hits < 100000:
            self.hits += 1


class Cache:
    def __init__(self, max_keys, cleanup_size):
        self.__cache = {}
        self.__max_keys = max_keys
        self.__cleanup_size = cleanup_size if cleanup_size < max_keys else 1
        self.enabled = True

    def __remove_least_hits(self):
        if len(self.__cache.keys()) >= self.__max_keys:
            hit_list = [{"key": k, "cnt": self.__cache[k].hits} for k in self.__cache.keys()]
            tmp_list = sorted(hit_list, key=lambda x: x["cnt"], reverse=False)
            del_keys = list(map(lambda x: x["key"], tmp_list[0 : self.__cleanup_size : 1]))
            for k in del_keys:
                del self.__cache[k]

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def get(self, key, onmiss):
        if not self.enabled:
            return onmiss(key)

        if key in self.__cache:
            entry = self.__cache[key]
            entry.increment_hits()
            return entry.val

        val = onmiss(key)
        if val:

            self.__remove_least_hits()
            self.__cache[key] = CacheEntry(val)

        return val

    def update(self, key, val):
        if self.enabled:
            self.__cache[key] = CacheEntry(val)

    def delete(self, key):
        if self.enabled and (key in self.__cache):
            del self.__cache[key]
