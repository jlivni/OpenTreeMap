var tm_urls = {
    eactive_key : '898cfa06a63e5ad7a427a30896cd95c2',
    tc_url : 'http://tc.sdtrees.beardedmaps.com/tilecache.py/',
    geo_url: 'http://tc2.sdtrees.beardedmaps.com/cgi-bin/mapserv?transparent=true&',
    //tc_url : 'http://sajara01:8080/cgi-bin/mapserv.exe?map=E:\\Projects\\UrbanForestMap\\mapserver\\trees.map',
    qs_tile_url : '/qs_tiles/1.0.0/foo/' // layername is pulled from request.GET, can remove 'foo' eventually
};

tm.map_center_lon = -117.13;
tm.map_center_lat = 32.75;
tm.start_zoom = 12;
tm.add_start_zoom = 11;
tm.add_zoom = 18;
tm.edit_zoom = 18;
tm.initial_location_string = "San Diego, CA";
tm.initial_species_string = "All trees";
tm.popup_minSize = new OpenLayers.Size(450,200);
tm.popup_maxSize = new OpenLayers.Size(450,450);

tm.google_bounds = new google.maps.LatLngBounds(new google.maps.LatLng(37.62,-122.62), new google.maps.LatLng(37.88,-122.19));
tm.geo_layer = "sf:sf_treemap_tree"
tm.geo_layer_style = "sanfrancisco_tree_highlight"
tm.panoAddressControl = false;

tm.init_base_map = function(div_id, controls){
    if (!div_id) {
        div_id = "map";
    };
    if (!controls) {
        tm.map = new OpenLayers.Map(div_id, {
            maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
            //restrictedExtent: new OpenLayers.Bounds(-13049000,3852890,-13037000,3862000),
            units: 'm',
            projection: new OpenLayers.Projection("EPSG:4326"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            controls: [new OpenLayers.Control.Attribution(),
                       new OpenLayers.Control.Navigation(),
                       new OpenLayers.Control.ArgParser(),
                       new OpenLayers.Control.PanPanel(),
                       new OpenLayers.Control.ZoomPanel()]
        });
    }
    else {
        tm.map = new OpenLayers.Map(div_id, {
            maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
            //restrictedExtent: new OpenLayers.Bounds(-13049000,3852890,-13037000,3862000),
            units: 'm',
            projection: new OpenLayers.Projection("EPSG:4326"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            controls: controls
        });
    }
    

   tm.baseLayer = new OpenLayers.Layer.Google("Google Streets", {
        sphericalMercator: true,
        numZoomLevels: 21
    });
  
    tm.aerial = new OpenLayers.Layer.Google("Hybrid", {
        type: google.maps.MapTypeId.HYBRID,            
        sphericalMercator: true,
        numZoomLevels: 21
    });
    
    tm.tms = new OpenLayers.Layer.TMS('TreeLayer', 
        tm_urls.tc_url,
        {
            layername: 'SanDiego',
            type: 'png',
            isBaseLayer: false,
            wrapDateLine: true,
            attribution: "(c) UrbanForestMap.org"
        }
    );
    tm.tms.buffer = 0;

    tm.xyz = new OpenLayers.Layer.XYZ('TreeLayer',
         tm_urls.qs_tile_url + "${z}/${x}/${y}.png?", 
         {sphericalmercator : true}
     );

    tm.baseLayer.buffer = 0;
    tm.aerial.buffer = 0;
    tm.map.addLayers([tm.baseLayer, tm.aerial, tm.tms]);
    tm.map.setBaseLayer(tm.baseLayer);
    tm.baseLayer.mapObject.setTilt(0);
    tm.aerial.mapObject.setTilt(0);
};
