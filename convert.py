from shapely import wkt
import geojson


def convert_polygon(polygon):
    # Convert WKT to Shapely geometry
    from shapely.geometry import mapping

    # Convert to GeoJSON dict
    geojson_obj = geojson.Feature(geometry=mapping(polygon))

    return geojson.dumps(geojson_obj)
