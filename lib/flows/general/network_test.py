#!/usr/bin/env python
# Copyright 2011 Google Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Test the connections listing module."""

from grr.lib import aff4
from grr.lib import rdfvalue
from grr.lib import test_lib


class NetstatTest(test_lib.FlowTestsBaseclass):
  """Test the process listing flow."""

  def testNetstat(self):
    """Test that the Netstat flow works."""

    class ClientMock(object):
      def Netstat(self, _):
        conn1 = rdfvalue.NetworkConnection(
            state=rdfvalue.NetworkConnection.Enum("LISTEN"),
            type=rdfvalue.NetworkConnection.Enum("SOCK_STREAM"),
            local_address=rdfvalue.NetworkEndpoint(
                ip="0.0.0.0",
                port=22),
            remote_address=rdfvalue.NetworkEndpoint(
                ip="0.0.0.0",
                port=0),
            pid=2136,
            ctime=0)
        conn2 = rdfvalue.NetworkConnection(
            state=rdfvalue.NetworkConnection.Enum("LISTEN"),
            type=rdfvalue.NetworkConnection.Enum("SOCK_STREAM"),
            local_address=rdfvalue.NetworkEndpoint(
                ip="192.168.1.1",
                port=31337),
            remote_address=rdfvalue.NetworkEndpoint(
                ip="1.2.3.4",
                port=6667),
            pid=1,
            ctime=0)
        return [conn1, conn2]

    # Set the system to Windows so the netstat flow will run as its the only
    # one that works at the moment.
    fd = aff4.FACTORY.Create(aff4.ROOT_URN.Add(self.client_id), "VFSGRRClient",
                             token=self.token)
    fd.Set(fd.Schema.SYSTEM("Windows"))
    fd.Close()

    for _ in test_lib.TestFlowHelper(
        "Netstat", ClientMock(), client_id=self.client_id, token=self.token):
      pass

    # Check the output file is created
    fd = aff4.FACTORY.Open(aff4.ROOT_URN.Add(self.client_id).Add("network"),
                           token=self.token)
    conns = fd.Get(fd.Schema.CONNECTIONS)

    self.assertEqual(len(conns), 2)
    self.assertEqual(conns[0].local_address.ip, "0.0.0.0")
    self.assertEqual(conns[0].local_address.port, 22)
    self.assertEqual(conns[1].local_address.ip, "192.168.1.1")
    self.assertEqual(conns[1].pid, 1)
    self.assertEqual(conns[1].remote_address.port, 6667)