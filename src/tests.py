#!/usr/bin/env python
"""
DBSCAN Project - M2 SSI - Istic, Univ. Rennes 1.

Andriamilanto Tompoariniaina <tompo.andri@gmail.com>.

Test module to unit test the functions used here.
"""

import unittest
import scapy
from datas import Point, Center, Point3D, Cluster
from network import Capture

index = 1
x = 5
y = 42
z = 9.5


class TestPoint(unittest.TestCase):
    """Class to test Point class."""

    def test_init(self):
        """Test initialization."""
        p = Point(index, x, y)
        self.assertEqual(p.index, index)
        self.assertEqual(p.x, x)
        self.assertEqual(p.y, y)
        with self.assertRaises(TypeError):
            p = Point(index, 'NaN', y)
        with self.assertRaises(TypeError):
            p = Point(index, x, 'NaN')

    def test_rewritte(self):
        """Test rewritte."""
        p = Point(index, x, y)
        with self.assertRaises(AttributeError):
            p.x = y
        with self.assertRaises(AttributeError):
            p.y = x

    def test_cluster(self):
        """Test cluster."""
        p = Point(index, x, y)
        c = Cluster()
        p.cluster = c
        self.assertEqual(p.cluster, c)

    def test_dist(self):
        """Test dist."""
        p1 = Point(1, 0, 0)
        p2 = Point(2, 0, 1)
        self.assertEqual(p1.dist(p2), p2.dist(p1))
        self.assertEqual(p1.dist(p2), 1)
        self.assertEqual(p2.dist(p1), 1)


class TestCenter(unittest.TestCase):
    """Class to test Center class."""

    def test_init(self):
        """Test initialization."""
        c = Center(index, x, y)
        self.assertEqual(c.index, index)
        self.assertEqual(c.x, x)
        self.assertEqual(c.y, y)
        with self.assertRaises(TypeError):
            c = Center(index, 'NaN', y)
        with self.assertRaises(TypeError):
            c = Center(index, x, 'NaN')

    def test_rewritte(self):
        """Test rewritte."""
        c = Center(index, x, y)
        c.x = y
        self.assertEqual(c.x, y)
        c.y = x
        self.assertEqual(c.y, x)

    def test_cluster(self):
        """Test cluster."""
        c = Center(index, x, y)
        cluster = Cluster()
        c.cluster = cluster
        self.assertEqual(c.cluster, cluster)

    def test_dist(self):
        """Test dist."""
        c = Center(1, 0, 0)
        c2 = Center(2, 0, 1)
        p = Point(3, 0, 1)
        self.assertEqual(c.dist(p), p.dist(c))
        self.assertEqual(c.dist(p), 1)
        self.assertEqual(p.dist(c), 1)
        self.assertEqual(c.dist(c2), c2.dist(c))
        self.assertEqual(c.dist(c2), 1)
        self.assertEqual(c2.dist(c), 1)


class TestPoint3D(unittest.TestCase):
    """Class to test Point3D class."""

    def test_init(self):
        """Test initialization."""
        p3d = Point3D(index, x, y, z)
        self.assertEqual(p3d.index, index)
        self.assertEqual(p3d.x, x)
        self.assertEqual(p3d.y, y)
        self.assertEqual(p3d.z, z)
        with self.assertRaises(TypeError):
            p3d = Point3D(index, 'NaN', y, z)
        with self.assertRaises(TypeError):
            p3d = Point3D(index, x, 'NaN', z)
        with self.assertRaises(TypeError):
            p3d = Point3D(index, x, y, 'NaN')

    def test_rewritte(self):
        """Test rewritte."""
        p3d = Point3D(index, x, y, z)
        with self.assertRaises(AttributeError):
            p3d.x = z
        with self.assertRaises(AttributeError):
            p3d.y = x
        with self.assertRaises(AttributeError):
            p3d.z = y

    def test_cluster(self):
        """Test cluster."""
        p3d = Point3D(index, x, y, z)
        c = Cluster()
        p3d.cluster = c
        self.assertEqual(p3d.cluster, c)

    def test_dist(self):
        """Test dist."""
        p3d1 = Point3D(1, 0, 0, 0)
        p3d2 = Point3D(2, 0, 0, 1)
        self.assertEqual(p3d1.dist(p3d2), p3d2.dist(p3d1))
        self.assertEqual(p3d1.dist(p3d2), 1)
        self.assertEqual(p3d2.dist(p3d1), 1)


class TestCapture(unittest.TestCase):
    """Class to test Capture class."""

    def test_init(self):
        """Test initialization."""
        Capture('../network_captures/example.pcap')
        with self.assertRaises(scapy.error.Scapy_Exception):
            Capture('../datasets/example.csv')
        with self.assertRaises(FileNotFoundError):
            Capture('../no_file_given')


# Main function to be launched when this script is called
if __name__ == "__main__":
    unittest.main()
