import unittest
from libs.cache import Cache


class TestCache(unittest.TestCase):
  def test_enable_disable(self):
    cache = Cache(100, 20)
    self.assertTrue(cache.enabled)
    cache.disable()
    self.assertFalse(cache.enabled)
    cache.enable()
    self.assertTrue(cache.enabled)

  def test_get(self):
    valmap = {
      "100": "cache value for 100", 
      "110": "cache value for 110", 
      "120": "cache value for 120", 
      "130": "cache value for 130", 
      "140": "cache value for 140", 
      "150": "cache value for 150", 
      "160": "cache value for 160", 
      "170": "cache value for 170", 
      "180": "cache value for 180", 
      "190": "cache value for 190", 
      "200": "cache value for 200", 
      "210": "cache value for 210", 
      "220": "cache value for 220", 
    }

    def onmiss(k):
      return valmap[k]

    def dummy(k):
      return "dummy"

    cache = Cache(10, 3)
    self.assertEqual(cache.get("100", onmiss), valmap["100"])

    cache.disable()
    self.assertEqual(cache.get("100", dummy), "dummy")
    self.assertEqual(cache.get("110", onmiss), valmap["110"])
    self.assertEqual(cache.get("110", dummy), "dummy")

    cache.enable()
    self.assertEqual(cache.get("100", dummy), valmap["100"])
    self.assertEqual(cache.get("110", onmiss), valmap["110"])
    self.assertEqual(cache.get("110", dummy), valmap["110"])

    # test for cache cleanup when max keys reached
    for k in ["120", "130", "140", "150", "160", "170", "180", "190"]:
      self.assertEqual(cache.get(k, onmiss), valmap[k])

    for i in range(10):
      for k in ["130", "140", "150", "160", "170", "180", "190"]:
        self.assertEqual(cache.get(k, onmiss), valmap[k])

    self.assertEqual(cache.get("200", onmiss), valmap["200"])

    for k in ["100", "110", "120"]:
      self.assertEqual(cache.get(k, dummy), "dummy")

  def test_update(self):
    def onmiss(k):
      return "default"

    def dummy(k):
      return "dummy"

    cache = Cache(100, 4)
    self.assertEqual(cache.get(100, onmiss), "default")
    
    cache.update(100, "update success")
    self.assertEqual(cache.get(100, onmiss), "update success")

    cache.disable()
    cache.update(100, "update once again")
    self.assertEqual(cache.get(100, dummy), "dummy")

    cache.enable()
    self.assertEqual(cache.get(100, dummy), "update success")

  def test_delete(self):
    def onmiss(k):
      return "default"

    def dummy(k):
      return "dummy"

    cache = Cache(10, 4)
    self.assertEqual(cache.get(100, onmiss), "default")
    self.assertEqual(cache.get(100, dummy), "default")

    cache.delete(100)
    self.assertEqual(cache.get(100, dummy), "dummy")

    cache.disable()
    cache.delete(100)
    cache.enable()
    self.assertEqual(cache.get(100, onmiss), "dummy")
