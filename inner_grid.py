# Import necessary libraries
import shapely.wkt, shapely.geometry
import numpy as np
import pandas as pd
import json
import shapely
import shapely.geometry
import geopandas as gpd



class GridGenerator:

    def rectangles_inside_polygon(self, polygon, n=None, size=None, tol=0, clip=True, include_poly=False) -> gpd.geoseries.GeoSeries:
            assert (n is None and size is not None) or (n is not None and size is None)
            # Extract bounding box coordinates of the polygon
            
            a, b, c, d = gpd.GeoSeries(polygon).total_bounds
            

            # Generate grids along x-axis/y-axis on the n or size
            if not n is None:
                xa = np.linspace(a, c, n + 1)
                ya = np.linspace(b, d, n + 1)
            else:
                xa = np.arange(a, c + 1, size[0])
                ya = np.arange(b, d + 1, size[1])

            # Offsets for tolerance to prevent edge cases
            if tol != 0:
                tol_xa = np.arange(0, tol * len(xa), tol)
                tol_ya = np.arange(0, tol * len(ya), tol)

            else:
                tol_xa = np.zeros(len(xa))
                tol_ya = np.zeros(len(ya))

            # Combine placements of x&y with tolerance
            xat = np.repeat(xa, 2)[1:] + np.repeat(tol_xa, 2)[:-1]
            yat = np.repeat(ya, 2)[1:] + np.repeat(tol_ya, 2)[:-1]

            # Create a grid
            grid = gpd.GeoSeries(
                [
                    shapely.geometry.box(minx, miny, maxx, maxy)
                    for minx, maxx in xat[:-1].reshape(len(xa) - 1, 2)
                    for miny, maxy in yat[:-1].reshape(len(ya) - 1, 2)
                ]
            )

            # Ensure all returned polygons are within boundary
            if clip:
                # grid = grid.loc[grid.within(gpd.GeoSeries(np.repeat([polygon], len(grid))))]
                grid = gpd.sjoin(
                    gpd.GeoDataFrame(geometry=grid),
                    gpd.GeoDataFrame(geometry=[polygon]),
                    how="inner",
                    predicate="within",
                )["geometry"]
            # useful for visualisation
            if include_poly:
                grid = pd.concat(
                    [
                        grid,
                        gpd.GeoSeries(
                            polygon.geoms
                            if isinstance(polygon, shapely.geometry.MultiPolygon)
                            else polygon
                        ),
                    ]
                )
            return grid

    def rectangles_inside_geojson(geojson_data, size):
        """
        Generate a grid of rectangles fully inside all rectangular polygons in a GeoJSON FeatureCollection.

        Args:
            geojson_data (dict): GeoJSON FeatureCollection with rectangular polygons.
            size (tuple): (width, height) of each rectangle.

        Returns:
            gpd.GeoSeries: Grid of rectangles clipped to the original polygons.
        """
        dx, dy = size
        all_polygons = []

        # Extract all polygons/multipolygons from GeoJSON
        for feature in geojson_data.get("features", []):
            geom_type = feature["geometry"]["type"]
            coords = feature["geometry"]["coordinates"]

            if geom_type == "Polygon":
                all_polygons.append(shapely.geometry.Polygon(coords[0]))
            elif geom_type == "MultiPolygon":
                all_polygons.extend([shapely.geometry.Polygon(p[0]) for p in coords])

        # Combine into a single GeoDataFrame
        poly_gdf = gpd.GeoDataFrame(geometry=all_polygons)

        # Generate rectangles for each polygon's bounding box
        rectangles = []
        for poly in all_polygons:
            minx, miny, maxx, maxy = poly.bounds
            x_coords = np.arange(minx, maxx, dx)
            y_coords = np.arange(miny, maxy, dy)

            for x in x_coords:
                for y in y_coords:
                    rect = shapely.geometry.box(x, y, min(x + dx, maxx), min(y + dy, maxy))
                    rectangles.append(rect)

        # Build GeoDataFrame of all rectangles
        rect_gdf = gpd.GeoDataFrame(geometry=rectangles)

        # Clip using spatial join (returns only those within any polygon)
        clipped = gpd.sjoin(rect_gdf, poly_gdf, how="inner", predicate="within")

        return clipped["geometry"]