from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos import Point
from django.utils import simplejson
from django.core.serializers import json 
from django.http import HttpResponse

def get_summaries_and_benefits(obj):
    try:
        # Note: 'aggregate' is a queryset method
        # while 'aggregates' is a tricky related_name of some custom models!
        # look ma: AggregateNeighborhood.objects.all()[0].location.aggregates
        agg = obj.aggregates
    except AttributeError:
        try:
            obj.annual_stormwater_management
            agg = obj
        except Exception, e:
            print str(e)
            return None, None
    if agg:
        summaries = {} #TODO assumes incorrectly that we have aggregate
        #fields = ['annual_stormwater_management', 'annual_electricity_conserved', 
        #          'annual_natural_gas_conserved', 'annual_air_quality_improvement', 
        #          'annual_co2_sequestered', 'total_co2_stored', 
        #          'total_trees', 'distinct_species']
        for f in agg._meta.get_all_field_names():
            if f.startswith('total') or f.startswith('annual'):
                summaries[f] = getattr(agg,f)
        benefits = agg.get_benefits()
    return summaries, benefits


def get_pt_or_bbox(rg):
    """
    parse out lat/lon or bbox from request.get and return geos geom
    """
    lat = rg.get('lat','')
    lon = rg.get('lon','')
    if lat and lon: 
        return Point(float(lon), float(lat), srid=4326)
    bbox = rg.get('bbox','')
    if bbox:
        b = eval(bbox)
        p1 = Point((b[0][1],b[0][0]))
        p2 = Point((b[1][1],b[1][0]))
        return p1.union(p2).envelope
    return None


def render_to_geojson(query_set, geom_field=None, mimetype='text/plain', pretty_print=True, excluded_fields=[], simplify='', additional_data=None):
    '''
    
    Shortcut to render a GeoJson FeatureCollection from a Django QuerySet.
    Currently computes a bbox and adds a crs member as a sr.org link
    
    '''
    collection = {}
    # Find the geometry field
    # qs.query._geo_field()

    excluded_fields += ['current_geometry'] 

    fields = query_set.model._meta.fields
    geo_fields = [f for f in fields if isinstance(f, GeometryField)]
    
    #attempt to assign geom_field that was passed in
    if geom_field:
        #print 'geom_field',geom_field
        geo_fieldnames = [x.name for x in geo_fields]
        try:
            geo_field = geo_fields[geo_fieldnames.index(geom_field)]
        except:
            raise Exception('%s is not a valid geometry on this model' % geom_field)
    else:
        geo_field = geo_fields[0] # no support yet for multiple geometry fields
        
        
    #remove other geom fields from showing up in attributes    
    if len(geo_fields) > 1:
        for gf in geo_fields:
            if gf.name not in excluded_fields: excluded_fields.append(gf.name)
        excluded_fields.remove(geo_field.name)    
    # Gather the projection information
    crs = {}
    crs['type'] = "link"
    crs_properties = {}
    crs_properties['href'] = 'http://spatialreference.org/ref/epsg/%s/' % geo_field.srid
    crs_properties['type'] = 'proj4'
    crs['properties'] = crs_properties 
    collection['crs'] = crs
    
    
    # Build list of features
    features = []
    if query_set:
      for item in query_set:
        feat = {}
        feat['type'] = 'Feature'
        d = item.__dict__.copy()
        
        #special attribs for trees:
        if  query_set.model.__name__ == 'Tree':
            #if item.site_type:
            #    d['site_type'] = item.get_site_type_display()
            if item.species:
                d['scientific_name'] = item.species.scientific_name
                d['common_name'] = item.species.common_name
                d['flowering'] = item.species.flower_conspicuous
                d['native'] = item.species.native_status
            if d.has_key('distance'):
                d['distance'] = d['distance'].ft
                
        #set up special attribs for geographies
        # todo - make more generic?
        if query_set.model.__name__ in ['Neighborhood','ZipCode']:
            try:
              summaries, benefits = get_summaries_and_benefits(item)
            except:
              print 'FAIL getting summaries/benefits for %s' % item
            
                
        g = getattr(item,geo_field.name)
        if simplify:
            g = g.simplify(simplify)
        d.pop(geo_field.name)
        for field in excluded_fields:
            if d.has_key(field): d.pop(field)
        if d.has_key('_state'): d.pop('_state')

        feat['geometry'] = simplejson.loads(g.geojson)
        feat['properties'] = d
        features.append(feat)
    else:
        pass #features.append({'type':'Feature','geometry': {},'properties':{}})

    # Label as FeatureCollection and add Features
    collection['type'] = "FeatureCollection"    
    collection['features'] = features
    
    # Attach extent of all features
    if query_set:
        collection['bbox'] = [x for x in query_set.extent()]
    
    if additional_data:
        collection.update(additional_data)
    # Return response
    response = HttpResponse()
    if pretty_print:
        response.write('%s' % simplejson.dumps(collection, indent=1, cls=json.DateTimeAwareJSONEncoder))

    else:
        response.write('%s' % simplejson.dumps(collection, cls=json.DateTimeAwareJSONEncoder))    
    response['Content-length'] = str(len(response.content))
    response['Content-Type'] = mimetype
    return response
