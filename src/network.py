#!/usr/bin/env python
"""
DBSCAN Project - M2 SSI - Istic, Univ. Rennes 1.

Andriamilanto Tompoariniaina <tompo.andri@gmail.com>

Plugin to process network capture files into .csv files for statistics
"""

# -- Imports
import os
import sys
from contextlib import redirect_stdout, redirect_stderr

# Import scapy with blocking stderr messages because of useless warning message
with open(os.devnull, 'w') as _:
    with redirect_stderr(_):
        from scapy.all import PcapReader, TCP, IP


# -- Classes
class Capture(object):
    """Capture class to represent a network capture."""

    FORMAT = {
        '1': 'mean_packet_size',
        '2': 'number_packets_client_server',
        '3': 'number_packets_server_client',
        '4': 'total_number_packets',
        '5': 'bytes_client_server',
        '6': 'bytes_server_client',
        '7': 'total_bytes'
    }

    def __init__(self, filename):
        """Initialize a capture only from its filename."""
        self._filename = filename
        self._conversations = {}
        self.__process_file()

    @property
    def conversations(self):
        """Getter for conversations."""
        return self._conversations

    def build_csv(self, output, format):
        """
        Build a csv file to the output path provided in the asked format.

        The format is provided as a string containing between 1 to 3 digits
        which corresponds to the following informations in order (ex: '516').
            1- Mean IP packet size
            2- Number of packets (client -> server)
            3- Number of packets (server -> client)
            4- Total number of packets
            5- Number of bytes sent (client -> server)
            6- Number of bytes sent (server -> client)
            7- Total number of bytes sent
        """
        # Process the file into a scope
        with open(output, 'w') as f:

            # Write the header
            header = 'index'
            for char in format:
                header += ', %s' % self.FORMAT[char]
            f.write('%s\n' % header)

            # Then write the datas
            for index, conv in self._conversations.items():

                # Only for the client => server side
                if index[0] == conv.client:
                    row = '%s/%s' % (index[0], index[1])
                    for char in format:
                        row += ', %s' % getattr(conv, self.FORMAT[char])
                    f.write('%s\n' % row)

    def __process_file(self):
        """Process the capture file into a list of conversations."""
        print(
            'Began to process %s pcap file, take a cup of' % self._filename,
            'coffee it can take some time'
        )

        # Redirect stdout because of useless messages
        packets = []
        with open(os.devnull, 'w') as f:
            with redirect_stdout(f):

                # Process directly the pcap using PcapReader
                reader = PcapReader(self._filename)

                # Put it into a try/finally because the reader is not closed
                # automatically
                try:
                    packets = reader.read_all()
                finally:
                    reader.close()

        print('Correctly read %d packets' % len(packets))

        # Then process packets into conversations
        self.__packets_to_conversations(packets)

        print('Found %d conversations' % len(self._conversations))

    def __packets_to_conversations(self, packets):
        """Process packets into conversations."""
        # For every packet, only process TCP ones (we assume TCP is over IP)
        for p in packets:
            if TCP in p:

                # Fetch usefull informations
                # src = '%s:%s' % (p[IP].src, p[TCP].sport)
                # dst = '%s:%s' % (p[IP].dst, p[TCP].dport)
                sport = p[TCP].sport
                dport = p[TCP].dport
                src = p[IP].src
                dst = p[IP].dst

                # Check if a conversation is already pending or not
                self.__add_packet(src, dst, sport, dport, p)

    def __add_packet(self, src, dst, sport, dport, packet):
        """Add a packet to a conversation."""
        # If there is no conversations between these hosts into the conv list
        if (src, dst) not in self._conversations:

            # Create the dict of it in the two orders
            # self._conversations[(src, dst)] = []
            # self._conversations[(dst, src)] = []

            # NOTE: Here we can find a way to use IP:port as index for
            # conversations

            conv = Conversation(src, dst)
            self._conversations[(src, dst)] = conv
            self._conversations[(dst, src)] = conv

        # Finally append it
        self._conversations[(src, dst)].add(packet)


class Conversation:
    """Conversation class to represent a conversation between two hosts.

    The hosts are the client and the server. Note that the client is the one
    initializing the connection. Each information provided will be computed
    only on demand for performance improvments.
    """

    def __init__(self, client, server):
        """Initialize a conversation by defining the client and the server."""
        # Informations about this conversation
        self._client = client
        self._server = server
        self._packets = []

        # The different informations to be filled when asked
        self._mean_packet_size = None
        self._number_packets_client_server = None
        self._number_packets_server_client = None
        self._total_number_packets = None
        self._bytes_server_client = None
        self._bytes_client_server = None
        self._total_bytes = None

    @property
    def client(self):
        """Getter for client."""
        return self._client

    @property
    def server(self):
        """Getter for server."""
        return self._server

    def add(self, packet):
        """Function to add a packet to the conversation."""
        self._packets.append(packet)

    @property
    def mean_packet_size(self):
        """Function to get the mean packet size."""
        if self._mean_packet_size is None:
            packets_size = 0
            for p in self._packets:
                packets_size += p[IP].len
            self._mean_packet_size = packets_size / len(self._packets)

            # Update the total size by the way
            if self._total_bytes is None:
                self._total_bytes = packets_size

        return self._mean_packet_size

    @property
    def number_packets_client_server(self):
        """Function to get the number of Client => Server packets."""
        # Local variables to avoid having very long lines
        cli_serv = self._number_packets_client_server
        serv_cli = self._number_packets_server_client
        total = self.total_number_packets

        # If the value that is asked is not initialized
        if cli_serv is None:

            # If the other one isn't initialized too, compute both of them
            if serv_cli is None:
                cli_serv = 0
                for p in self._packets:
                    if p[IP].src == self._client:
                        cli_serv += 1
                self._number_packets_client_server = cli_serv
                self._number_packets_server_client = total - cli_serv

            # If the other one is initialized get the value of this one from it
            else:
                self._number_packets_client_server = total - serv_cli

        # Return the asked value
        return self._number_packets_client_server

    @property
    def number_packets_server_client(self):
        """Function to get the number of Server => Client packets."""
        # Local variables to avoid having very long lines
        cli_serv = self._number_packets_client_server
        serv_cli = self._number_packets_server_client
        total = self.total_number_packets

        # If the value that is asked is not initialized
        if serv_cli is None:

            # If the other one isn't initialized too, compute both of them
            if cli_serv is None:
                serv_cli = 0
                for p in self._packets:
                    if p[IP].src == self._server:
                        serv_cli += 1
                self._number_packets_server_client = serv_cli
                self._number_packets_client_server = total - serv_cli

            # If the other one is initialized get the value of this one from it
            else:
                self._number_packets_server_client = total - cli_serv

        # Return the asked value
        return self._number_packets_server_client

    @property
    def total_number_packets(self):
        """Function to get the total number of packets."""
        if self._total_number_packets is None:
            self._total_number_packets = len(self._packets)
        return self._total_number_packets

    @property
    def bytes_client_server(self):
        """Get the number of bytes sent of Client => Server packets."""
        # Local variables to avoid having very long lines
        cli_serv = self._bytes_client_server
        serv_cli = self._bytes_server_client
        total = self.total_bytes

        # If the value that is asked is not initialized
        if cli_serv is None:

            # If the other one isn't initialized too, compute both of them
            if serv_cli is None:
                cli_serv = 0
                for p in self._packets:
                    if p[IP].src == self._client:
                        cli_serv += p[IP].len
                self._bytes_client_server = cli_serv
                self._bytes_server_client = total - cli_serv

            # If the other one is initialized get the value of this one from it
            else:
                self._bytes_client_server = total - serv_cli

        # Return the asked value
        return self._bytes_client_server

    @property
    def bytes_server_client(self):
        """Get the number of bytes sent of Server => Client packets."""
        # Local variables to avoid having very long lines
        cli_serv = self._bytes_client_server
        serv_cli = self._bytes_server_client
        total = self.total_bytes

        # If the value that is asked is not initialized
        if serv_cli is None:

            # If the other one isn't initialized too, compute both of them
            if cli_serv is None:
                serv_cli = 0
                for p in self._packets:
                    if p[IP].src == self._server:
                        serv_cli += p[IP].len
                self._bytes_server_client = serv_cli
                self._bytes_client_server = total - serv_cli

            # If the other one is initialized get the value of this one from it
            else:
                self._bytes_server_client = total - cli_serv

        # Return the asked value
        return self._bytes_server_client

    @property
    def total_bytes(self):
        """Function to get the total unique bytes sent."""
        if self._total_bytes is None:
            self._total_bytes = 0
            for p in self._packets:
                self._total_bytes += p[IP].len
        return self._total_bytes

    def __str__(self):
        """Get a string representation of this object."""
        return 'Conversation [%s => %s] with %d packets' % (
            self._client, self._server, len(self._packets)
        )


def __get_params(argv):
    """Function to manage input parameters."""
    # Correct syntax
    syntax = '%s pcap_input csv_output format' % argv[0]

    # Not enough parameters
    if len(argv) != 4:
        print('Usage: %s' % syntax)
        exit()

    # Return the parameters
    return argv[1], argv[2], argv[3]


# Main function to be launched when this script is called
if __name__ == "__main__":
    params = __get_params(sys.argv)
    capture = Capture(params[0])
    capture.build_csv(params[1], params[2])
    # for index, conv in capture.conversations.items():
    #     print(conv)
    #     print(conv.mean_packet_size)
    #     print(conv.total_number_packets)
    #     print(conv.number_packets_server_client)
    #     print(conv.number_packets_client_server)
    #     print(conv.total_bytes)
    #     print(conv.bytes_server_client)
    #     print(conv.bytes_client_server)
    # if sys.argv[1] is not None:
    #     format = '123' if sys.argv[2] is None else sys.argv[2]
    #     capture.build_csv(sys.argv[1], format)

    # TODO: Use PORTS to separate conversations between two hosts!!!

    """
    In the future, it will be good to have a real way of getting conversations
    because here we only sort packets using the two hosts corresponding and not
    the actual different TCP flows.

    => Datas to be fetched from the network captures:
        - Mean Inter-Arrival Time
        - Connection duration

    => Use each TCP connection as a 'point' or as 'index'
    """
