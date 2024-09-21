import unittest, json
from libs.response import Response


class TestResponse(unittest.TestCase):
  def test_response(self):
    data = [{"key": "value"}]

    examples = [
      (Response.success(data), 200, "", data), 
      (Response.error(401, "some info"), 401, "some info", None), 
      (Response.bad_request("err 400"), 400, "err 400", None), 
      (Response.not_found("err 404"), 404, "err 404", None), 
      (Response.internal_server_error("err 500"), 500, "err 500", None), 
    ]

    for ex in examples:
      self.assertIsInstance(ex[0], Response)
      self.assertEqual(ex[0].code, ex[1])
      self.assertEqual(ex[0].message, ex[2])
      self.assertEqual(ex[0].data, ex[3])

      r, c = ex[0].resp()
      status = "success" if ex[1] == 200 else "error"
      self.assertEqual(json.loads(r), {"meta": {"status": status, "message": ex[2]}, "data": ex[3]})
      self.assertEqual(c, ex[1])
