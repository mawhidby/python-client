import os
import unittest

from braid import Client, VertexQuery, EdgeQuery, EdgeKey

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        host = os.environ["BRAID_HOST"]
        account_id = os.environ["BRAID_ACCOUNT_ID"]
        secret = os.environ["BRAID_SECRET"]
        self.client = Client(host, account_id, secret, scheme="http")

    def test_get_vertices(self):
        uuid = self.client.create_vertex("foo")
        results = self.client.get_vertices(VertexQuery.vertex(uuid))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, uuid)

    def test_delete_vertices(self):
        uuid = self.client.create_vertex("foo")
        self.client.delete_vertices(VertexQuery.vertex(uuid))
        results = self.client.get_vertices(VertexQuery.vertex(uuid))
        self.assertEqual(len(results), 0)

    def test_get_edges(self):
        outbound_id = self.client.create_vertex("foo")
        inbound_id = self.client.create_vertex("foo")
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.client.create_edge(key, 0.5)
        results = self.client.get_edges(EdgeQuery.edge(key))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key.outbound_id, outbound_id)
        self.assertEqual(results[0].key.type, "bar")
        self.assertEqual(results[0].key.inbound_id, inbound_id)
        self.assertEqual(results[0].weight, 0.5)

    def test_get_edge_count(self):
        outbound_id = self.client.create_vertex("foo")
        inbound_id = self.client.create_vertex("foo")
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.client.create_edge(key, 0.5)
        count = self.client.get_edge_count(EdgeQuery.edge(key))
        self.assertEqual(count, 1)

    def test_delete_edges(self):
        outbound_id = self.client.create_vertex("foo")
        inbound_id = self.client.create_vertex("foo")
        key = EdgeKey(outbound_id, "bar", inbound_id)
        self.client.create_edge(key, 0.5)
        self.client.delete_edges(EdgeQuery.edge(key))
        count = self.client.get_edge_count(EdgeQuery.edge(key))
        self.assertEqual(count, 0)

    def test_run_script(self):
        result = self.client.run_script("echo.lua", dict(foo="bar"))
        self.assertEqual(result, dict(foo="bar"))
