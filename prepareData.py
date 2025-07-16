import geopandas as gpd


def prepare_data(file):
    # Read JSON
    gdf = gpd.read_file(file)
    # print(gdf["geometry"])

    records = []

    for i, polygon in enumerate(gdf["geometry"]):
        # Get bounds: [minx, miny, maxx, maxy]
        minx, miny, maxx, maxy = polygon.bounds
        records.append(
            {
                "id": str(minx) + ":" + str(miny),
                "geometry": polygon,
                "min_lon": minx,
                "max_lon": maxx,
                "min_lat": miny,
                "max_lat": maxy,
            }
        )

    # Create new GeoDataFrame with geometry and bounds
    bounds_gdf = gpd.GeoDataFrame(records)

    return bounds_gdf

    #  # Show result
    # print(bounds_gdf)


if __name__ == "__main__":
    file = "50mtest.json"
    bounds_gdf = prepare_data(file)
    print(bounds_gdf)
    # filtered = bounds_gdf[bounds_gdf["max_lon"] == 73.794751955927467]
    # filtered2 = bounds_gdf[bounds_gdf["max_lat"] == 18.637463033658467]
    # print(filtered)
