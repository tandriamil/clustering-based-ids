#!/usr/bin/env python
"""
DBSCAN Project - M2 SSI - Istic, Univ. Rennes 1.

Andriamilanto Tompoariniaina <tompo.andri@gmail.com>

Dataset manager to get the datas as Pandas structure from a .csv file.
"""

# -- Imports
import sys
import pandas as pd
import matplotlib.pyplot as plt
from numpy import power, linalg, array
from math import sqrt, isnan
from pathlib import Path


# -- Classes
class Point(object):
    """Class to represent a Point into a bidimensional space."""

    DIMENSIONS = ('x', 'y')

    def __init__(self, index, x, y):
        """Initializer, just initializes the attributes."""
        try:
            if isnan(x):
                raise TypeError
        except TypeError:
            raise TypeError('Point %s: x has to be a number' % index)
        try:
            if isnan(y):
                raise TypeError
        except TypeError:
            raise TypeError('Point %s: y has to be a number' % index)
        self._index = index
        self._x = x
        self._y = y
        self._cluster = None

    @property
    def index(self):
        """Getter for index attribute (No setter)."""
        return self._index

    @property
    def x(self):
        """Getter for x attribute (No setter)."""
        return self._x

    @property
    def y(self):
        """Getter for y attribute (No setter)."""
        return self._y

    @property
    def cluster(self):
        """Getter for the Cluster of this Point."""
        return self._cluster

    @cluster.setter
    def cluster(self, cluster):
        """Setter for the Cluster of this Point."""
        self._cluster = cluster

    def dist(self, p):
        """Compute the distance from this Point to the Point p."""
        # This version doesn't work with big values because of a value overflow
        # return sqrt(power(self.x - p.x, 2) + power(self.y - p.y, 2))
        vect1 = array([self.x, self.y])
        vect2 = array([p.x, p.y])
        return linalg.norm(vect1 - vect2, 2, 0)

    def __str__(self):
        """Get a string representation of this object."""
        return 'Point %s [%f, %f]' % (str(self._index), self._x, self._y)


class Center(Point):
    """Class to represent the Center of a Cluster.

    It is simply a Point which position can be redefined.
    """

    @property
    def x(self):
        """Getter for x attribute."""
        return self._x

    @x.setter
    def x(self, x):
        """Setter for x attribute."""
        try:
            if isnan(x):
                raise TypeError
        except TypeError:
            raise TypeError('Center %s: x has to be a number' % self)
        self._x = x

    @property
    def y(self):
        """Getter for y attribute."""
        return self._y

    @y.setter
    def y(self, y):
        """Setter for y attribute."""
        try:
            if isnan(y):
                raise TypeError
        except TypeError:
            raise TypeError('Center %s: y has to be a number' % y)
        self._y = y

    def __str__(self):
        """Get a string representation of this object."""
        return 'Center %s [%f, %f]' % (str(self._index), self._x, self._y)


class Cluster:
    """The Cluster class which represent a Cluster."""

    def __init__(self):
        """Initializer, just initializes the attributes."""
        self._center = None
        self._points = []

    @property
    def points(self):
        """
        Getter for points attribute, list of points belonging to the cluster.

        No setter allowed.
        """
        return self._points

    @property
    def center(self):
        """Getter for Center attribute, which is a Center object."""
        return self._center

    @center.setter
    def center(self, center):
        """Setter for Center attribute, which is a Center object."""
        center.cluster = self
        self._center = center

    def assign(self, point):
        """Assign a Point to this cluster.

        The Cluster attribute of the Point will also be automatically updated.
        """
        # If the point was already assigned to a cluster, remove it from
        if point.cluster:
            point.cluster.points.remove(point)

        # Assign this cluster to this point and add it to its point list
        point.cluster = self
        self._points.append(point)

    def __str__(self):
        """Get a string representation of this object."""
        ret = 'Cluster {\n  %s\n  Points: [\n' % self._center
        for point in self._points:
            ret += '    %s\n' % point
        ret += '  ]\n}'
        return ret


class Point3D(Point):
    """Class representation of a Point in a 3 dimensional space."""

    # The dimensions of a 3D point
    DIMENSIONS = ('x', 'y', 'z')

    def __init__(self, index, x, y, z):
        """Initializer, just initializes the attributes."""
        self._z = None
        super().__init__(index, x, y)
        try:
            if isnan(z):
                raise TypeError
        except TypeError:
            raise TypeError('Point3D %s: z has to be a number' % self)
        self._z = z

    @property
    def z(self):
        """Getter for z attribute (No setter)."""
        return self._z

    def dist(self, p):
        """Compute the distance from this Point to the Point p."""
        return sqrt(sum([
            power(self.x - p.x, 2),
            power(self.y - p.y, 2),
            power(self.z - p.z, 2)
        ]))

    def __str__(self):
        """Get a string representation of this object."""
        return 'Point %s [%f, %f, %f]' % (
            str(self._index), self._x, self._y, self._z
        )


class Center3D(Point3D):
    """Class to represent the Center of a Cluster in a 3 dimensional space.

    It is simply a 3D Point which can be redefined.
    """

    @property
    def x(self):
        """Getter for x attribute."""
        return self._x

    @x.setter
    def x(self, x):
        """Setter for x attribute."""
        try:
            if isnan(x):
                raise TypeError
        except TypeError:
            raise TypeError('Center3D %s: x has to be a number' % self)
        self._x = x

    @property
    def y(self):
        """Getter for y attribute."""
        return self._y

    @y.setter
    def y(self, y):
        """Setter for y attribute."""
        try:
            if isnan(y):
                raise TypeError
        except TypeError:
            raise TypeError('Center3D %s: y has to be a number' % self)
        self._y = y

    @property
    def z(self):
        """Getter for z attribute."""
        return self._z

    @z.setter
    def z(self, z):
        """Setter for z attribute."""
        try:
            if isnan(z):
                raise TypeError
        except TypeError:
            raise TypeError('Center3D %s: z has to be a number' % self._index)
        self._z = z

    def __str__(self):
        """Get a string representation of this object."""
        return 'Center %s [%f, %f, %f]' % (
            str(self._index), self._x, self._y, self._z
        )


# -- Public functions
def read_dataset(filename):
    """Get a DataFrame object from a .csv file."""
    # Get the DataFrame object from the file
    df = pd.read_csv(filename)

    # Return the DataFrame
    return df


def dataframe_to_points(dataframe):
    """Convert a DataFrame object into a set of Point objects."""
    # Get the columns names of the data frame and put them as labels
    # Note that the call to plt is saved into context and will be used when
    # calling plt.plot() to display the graph with clusters
    col_names = list(dataframe)
    plt.xlabel(col_names[1])
    plt.ylabel(col_names[2])

    # Add each row of the dataframe into a list of Point objects and return it
    points = []
    for index, value in dataframe.iterrows():
        points.append(Point(value[0], value[1], value[2]))
    return points


def display_clusters(clusters, add_points=None):
    """Display the graph with the points."""
    # Parse the clusters and display them
    for cluster in clusters:

        # If there are points into this cluster
        if len(cluster.points) > 0:

            # Feed the datas
            x = []
            y = []
            for point in cluster.points:
                # plt.annotate(point.index, (point.x, point.y))
                x.append(point.x)
                y.append(point.y)

            # Put the datas representing the points (note that this function
            # add each new data with a new color until we call show())
            plt.scatter(x=x, y=y)

        # Display the center of the cluster in red / black color
        if cluster.center is not None:
            plt.scatter(
                x=[cluster.center.x],
                y=[cluster.center.y],
                c=(0, 0, 0),
                edgecolors='red',
                alpha=0.5
            )

    # If there are additional points, display them in black
    if add_points is not None:
        # Feed the datas
        x = []
        y = []
        for point in add_points:
            x.append(point.x)
            y.append(point.y)

        # Put the datas representing the points (note that this function
        # add each new data with a new color until we call show())
        plt.scatter(x=x, y=y, c='black')

    # Display the graph with the clusters in different colors
    plt.show()


def display_graph(data_frame):
    """Display the graph using a dataframe object."""
    # Get the columns names of the data frame and put them as labels
    col_names = list(data_frame)

    # Add the points to the figure
    data_frame.plot.scatter(x=col_names[1], y=col_names[2])

    # Add the annotation (index value of points displayed), comment if unwanted
    for _, v in data_frame.iterrows():
        plt.annotate(str(v[0]), (v[1], v[2]))

    # Finally show the figure
    plt.show()


def save_results(file_name, clusters):
    """Save results in a file."""
    f = open(file_name, 'w')
    for cluster in clusters:
        if len(cluster.points) > 0:
            f.write('%s\n' % cluster)
    f.close()


# -- Private functions
def __get_params(argv):
    """Function to manage input parameters."""
    # Correct syntax
    syntax = '%s [filename]' % argv[0]

    # Not enough parameters
    if len(argv) != 2:
        print('Usage: %s' % syntax)
        exit()

    # Return the filename after checking that the file exists and is a .csv
    f = Path(argv[1])
    if f.is_file() and f.suffix == '.csv':
        return {'filename': argv[1]}
    else:
        print('The file %s was not found' % argv[1])
        exit()


# Main function to be launched when this script is called
if __name__ == "__main__":
    """
    This scope is made to test the functions below
    """

    # Get the name of the file from the first parameter
    params = __get_params(sys.argv)

    # Fetch DataFrame object from the file
    df = read_dataset(params['filename'])

    # Print its values
    # print('### DataFrame object:')
    # print(df)
    # print('\n')

    # Display the graph
    display_graph(df)
