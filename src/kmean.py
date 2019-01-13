#!/usr/bin/env python
"""
DBSCAN Project - M2 SSI - Istic, Univ. Rennes 1.

Andriamilanto Tompoariniaina <tompo.andri@gmail.com>

This module is an implementation of K-mean algorithm to confront it with our
implementation of the DBSCAN one.
"""

# -- Imports
import sys
import random
import operator
from pandas import DataFrame
from pathlib import Path
from datas import (read_dataset, dataframe_to_points, display_clusters, Center,
                   Cluster)


# -- Classes
class Kmean(object):
    """The class representation of our implementation of Kmean."""

    def __init__(self, dataset, k, precision=1):
        """Initialization function, called when creating a new object."""
        # Type checking the dataset
        if not isinstance(dataset, DataFrame) or dataset.empty:
            raise TypeError(
                'Dataset given to Kmean class has to be a non empty',
                'pandas.DataFrame instance'
            )

        # If asking more clusters than the number of points
        if k > dataset.size:
            raise ValueError(
                'k cannot be superior than dataset size (> %d)' % dataset.size
            )

        # Initialize private attributes
        self._k = k
        self._precision = precision
        self._points = []
        self._clusters = []
        self._neighbour_counter = {}

        # Create the Point objects from the DataFrame one
        self._points = dataframe_to_points(dataset)

        # Initialize the neighbour counter
        for point in self._points:
            self._neighbour_counter[point] = 0

        # DEBUG: Display initial state of the algorithm
        # display_clusters(self._clusters, self._points)

    def _turn(self):
        """Run a turn of the algorithm till we reach the convergence point."""
        # Varible put to False only to enter the first time into the loop
        converged = False
        nb_loop = 0

        # While we still haven't reached the point of convergence
        while not converged:

            # DEBUG: Display the state at each loop
            # display_clusters(self._clusters)

            # Put the converged value back to True, if a point changes its
            # cluster, we will know that we still haven't converged
            converged = True

            # For every point (we assume that they are already into a cluster)
            for p in self._points:

                # The closest is the current cluster of the point
                closest = p.cluster
                curr_dist = p.dist(closest.center)

                # Parse all the other clusters
                for cluster in self._clusters:

                    # If one is closest than the current one
                    if p.dist(cluster.center) < curr_dist:
                        closest = cluster
                        curr_dist = p.dist(closest.center)

                # If the closest cluster is different than the current one,
                # assign this point to this cluster and we know that we still
                # haven't converged
                if p.cluster != closest:
                    closest.assign(p)
                    converged = False

            # Reassign the center of the clusters
            self._update_cluster_center()

            # Simple counter
            nb_loop += 1

        # Return the number of loops that this turn took
        return nb_loop

    def run(self):
        """Run the algorithm a precision number of times."""
        # Do a precision number of turns
        nb_loop = 0
        for turn in range(self._precision):

            # Initialization with random centers
            self._initialization()

            # Execute the turn and counting its number of loops
            nb_loop += self._turn()

            # Count the number of neighbour points of each points
            self._count_neighbours()

        # Execute the last turn with optimized centers
        opt_loop = self._optimized_turn()

        # At the end, print the final convergence time
        print('%d, %d, %d' % (self._k, nb_loop/self._precision, opt_loop))

        # Display the final state of the clusters
        display_clusters(self._clusters)
        # for c in self._clusters:
        #     print(c)

    def _optimized_turn(self):
        """Optimized turn to get the 'best' centers for clusters."""
        # Get k points with the max neighbours which will make better centers
        best_centers = []
        for i in range(self._k):

            # Get the id of the point with maximum neighbours (better center)
            new_max_point = max(
                self._neighbour_counter.items(),
                key=operator.itemgetter(1)
            )[0]

            # For every point into the cluster of the maximum one, remove them
            # in order to not select two centers into the same cluster
            cluster = new_max_point.cluster
            # closest = cluster.points[0]
            closest = new_max_point
            for point in cluster.points:
                # if point.dist(cluster.center) < closest.dist(cluster.center):
                #     closest = point
                self._neighbour_counter[point] = 0

            # Just add the created center into the center list
            best_centers.append(Center(i, closest.x, closest.y))

        # Clear the clusters
        self._clear_clusters()

        # Create the clusters with their optimized centers
        for center in best_centers:
            c = Cluster()
            c.center = center
            self._clusters.append(c)

        # Assign each point to its closest cluster
        self._assign_point_to_closest_cluster()

        # Reassign the center of the clusters
        self._update_cluster_center()

        # Execute the final and optimized turn and counting its number of loops
        return self._turn()

    def _count_neighbours(self):
        """Count the number of neighbours of each point."""
        for point in self._points:
            self._neighbour_counter[point] += len(point.cluster.points)

    def _initialization(self):
        """Initialization part of the algorithm.

        Note that the points will be assigned to their nearest cluster and the
        center points of the clusters are scattered on the diagonal going from
        left bottom to top right.
        """
        # Clear the clusters
        self._clear_clusters()

        # Initialize the clusters
        self._init_clusters()

        # Assign each point to its closest cluster
        self._assign_point_to_closest_cluster()

        # Reassign the center of the clusters
        self._update_cluster_center()

    def _update_cluster_center(self):
        """Update the cluster's center."""
        # Update the center of each cluster if there are points into it
        for cluster in self._clusters:

            # Get the number of points into this cluster
            nb_points = len(cluster.points)
            if nb_points > 0:

                # Update the way of getting sums and centers for 3D points

                # Add all x and y values of each point of this cluster
                x_sum, y_sum = 0, 0
                for point in cluster.points:
                    x_sum += point.x
                    y_sum += point.y

                # Reassign the center of this cluster by getting the mean
                cluster.center.x = x_sum / nb_points
                cluster.center.y = y_sum / nb_points

            # DEBUG: Display the new centers approximations
            # print(
            #     'center.x=%s and center.y=%s' %
            #     (cluster.center.x, cluster.center.y)
            # )

    def _clear_clusters(self):
        """Clear the clusters between each turn."""
        for point in self._points:
            point.cluster = None
        self._clusters.clear()

    def _init_clusters(self):
        """Initialize the clusters."""
        # Select randomly k points and put them as cluster centers
        for index in range(self._k):

            # Select a random point
            random_point = random.choice(self._points)

            # Update what is needed for 3D centers using 3D points

            # Create a new cluster with this a random point as its center
            c = Cluster()
            c.center = Center(index, random_point.x, random_point.y)
            self._clusters.append(c)

    def _assign_point_to_closest_cluster(self):
        """Assign each point to its closes cluster."""
        for p in self._points:

            # The closest is the first cluster in the list (for the moment)
            closest = self._clusters[0]
            curr_dist = p.dist(closest.center)

            # Parse all the other clusters
            for cluster in self._clusters[1:]:

                # If one is closest than the current one
                if p.dist(cluster.center) < curr_dist:
                    closest = cluster
                    curr_dist = p.dist(closest.center)

            # Assign this point to its closest cluster
            closest.assign(p)


# -- Private functions
def __get_params(argv):
    """Function to manage input parameters."""
    # Correct syntax
    syntax = '%s filename k [precision]' % argv[0]

    # Not enough parameters
    if len(argv) not in (3, 4):
        print('Usage: %s' % syntax)
        exit()

    # Get the parameter k
    try:
        k = int(argv[2])
        if k < 1:
            raise ValueError
    except ValueError:
        print(
            'Parameter k as %s is invalid, must be a positive integer'
            % argv[2]
        )
        exit()

    # Get the filename after checking that the file exists and is a .csv
    f = Path(argv[1])
    if not f.is_file() or f.suffix != '.csv':
        print('The file %s was not found' % argv[1])
        exit()

    # Get the precision value
    try:
        precision = int(argv[3])
        if precision < 1:
            raise ValueError
    except IndexError:
        precision = 1
    except ValueError:
        print(
            'Parameter precision as %s is invalid, must be a positive integer'
            % argv[3]
        )
        exit()

    # Return the parameters
    return argv[1], k, precision


if __name__ == "__main__":
    """Main function to be launched when this script is called """

    # -- Normal functionment
    # Get parameters and execute K-mean algorithm
    dataset, k, precision = __get_params(sys.argv)
    Kmean(read_dataset(dataset), k, precision).run()

    # -- Convergence measurement gives 3 columns csv file
    # => (k | normal convergence time | optimized version convergence time)
    # datasets = [
    #     'carnet2.csv',
    #     'carnet_bis.csv',
    #     'circles.csv',
    #     'density_gap.csv',
    #     'example.csv',
    #     'stats_reseaux_ping_download.csv'
    # ]
    #
    # from contextlib import redirect_stdout
    # for ds in datasets:
    #     with open('../Report/convergences/' + ds, 'w') as f:
    #         with redirect_stdout(f):
    #             print('k, convergence_time')
    #             try:
    #                 for k in range(1, 100):
    #                     Kmean(read_dataset('../datasets/' + ds), k).run()
    #             except ValueError:
    #                 pass
