/*
* Rendering code adapted from 'Comic Book Narrative Charts'
* Nancy Iskander, Matthew Thorne and Craig Kaplan
* http://csclub.uwaterloo.ca/~n2iskand/?page_id=13
*/

var NL = {
    namespace: function (ns)    {
        var parts = ns.split("."),
            object = this,
            i, len;
        for(i=0, len=parts.length; i < len; i++)   {
            if(!object[parts[i]])  {
                object[parts[i]] = {};
            }
            object = object[parts[i]];
        }
        return object;
    }
};

/* Based on Alex Arnell's inheritance implementation. */
/** section: Language
 * class Class
 *
 *  Manages Prototype's class-based OOP system.
 *
 *  Refer to Prototype's web site for a [tutorial on classes and
 *  inheritance](http://prototypejs.org/learn/class-inheritance).
**/
(function(globalContext) {
/* ------------------------------------ */
/* Import from object.js                */
/* ------------------------------------ */
var _toString = Object.prototype.toString,
    NULL_TYPE = 'Null',
    UNDEFINED_TYPE = 'Undefined',
    BOOLEAN_TYPE = 'Boolean',
    NUMBER_TYPE = 'Number',
    STRING_TYPE = 'String',
    OBJECT_TYPE = 'Object',
    FUNCTION_CLASS = '[object Function]';
function isFunction(object) {
  return _toString.call(object) === FUNCTION_CLASS;
}
function extend(destination, source) {
  for (var property in source) if (source.hasOwnProperty(property)) // modify protect primitive slaughter
    destination[property] = source[property];
  return destination;
}
function keys(object) {
  if (Type(object) !== OBJECT_TYPE) { throw new TypeError(); }
  var results = [];
  for (var property in object) {
    if (object.hasOwnProperty(property)) {
      results.push(property);
    }
  }
  return results;
}
function Type(o) {
  switch(o) {
    case null: return NULL_TYPE;
    case (void 0): return UNDEFINED_TYPE;
  }
  var type = typeof o;
  switch(type) {
    case 'boolean': return BOOLEAN_TYPE;
    case 'number':  return NUMBER_TYPE;
    case 'string':  return STRING_TYPE;
  }
  return OBJECT_TYPE;
}
function isUndefined(object) {
  return typeof object === "undefined";
}
/* ------------------------------------ */
/* Import from Function.js              */
/* ------------------------------------ */
var slice = Array.prototype.slice;
function argumentNames(fn) {
  var names = fn.toString().match(/^[\s\(]*function[^(]*\(([^)]*)\)/)[1]
    .replace(/\/\/.*?[\r\n]|\/\*(?:.|[\r\n])*?\*\//g, '')
    .replace(/\s+/g, '').split(',');
  return names.length == 1 && !names[0] ? [] : names;
}
function wrap(fn, wrapper) {
  var __method = fn;
  return function() {
    var a = update([bind(__method, this)], arguments);
    return wrapper.apply(this, a);
  }
}
function update(array, args) {
  var arrayLength = array.length, length = args.length;
  while (length--) array[arrayLength + length] = args[length];
  return array;
}
function merge(array, args) {
  array = slice.call(array, 0);
  return update(array, args);
}
function bind(fn, context) {
  if (arguments.length < 2 && isUndefined(arguments[0])) return this;
  var __method = fn, args = slice.call(arguments, 2);
  return function() {
    var a = merge(args, arguments);
    return __method.apply(context, a);
  }
}

/* ------------------------------------ */
/* Import from Prototype.js             */
/* ------------------------------------ */
var emptyFunction = function(){};

var Class = (function() {
  
  // Some versions of JScript fail to enumerate over properties, names of which 
  // correspond to non-enumerable properties in the prototype chain
  var IS_DONTENUM_BUGGY = (function(){
    for (var p in { toString: 1 }) {
      // check actual property name, so that it works with augmented Object.prototype
      if (p === 'toString') return false;
    }
    return true;
  })();
  
  function subclass() {};
  function create() {
    var parent = null, properties = [].slice.apply(arguments);
    if (isFunction(properties[0]))
      parent = properties.shift();

    function klass() {
      this.initialize.apply(this, arguments);
    }

    extend(klass, Class.Methods);
    klass.superclass = parent;
    klass.subclasses = [];

    if (parent) {
      subclass.prototype = parent.prototype;
      klass.prototype = new subclass;
      try { parent.subclasses.push(klass) } catch(e) {}
    }

    for (var i = 0, length = properties.length; i < length; i++)
      klass.addMethods(properties[i]);

    if (!klass.prototype.initialize)
      klass.prototype.initialize = emptyFunction;

    klass.prototype.constructor = klass;
    return klass;
  }

  function addMethods(source) {
    var ancestor   = this.superclass && this.superclass.prototype,
        properties = keys(source);

    // IE6 doesn't enumerate `toString` and `valueOf` (among other built-in `Object.prototype`) properties,
    // Force copy if they're not Object.prototype ones.
    // Do not copy other Object.prototype.* for performance reasons
    if (IS_DONTENUM_BUGGY) {
      if (source.toString != Object.prototype.toString)
        properties.push("toString");
      if (source.valueOf != Object.prototype.valueOf)
        properties.push("valueOf");
    }

    for (var i = 0, length = properties.length; i < length; i++) {
      var property = properties[i], value = source[property];
      if (ancestor && isFunction(value) &&
          argumentNames(value)[0] == "$super") {
        var method = value;
        value = wrap((function(m) {
          return function() { return ancestor[m].apply(this, arguments); };
        })(property), method);

        value.valueOf = bind(method.valueOf, method);
        value.toString = bind(method.toString, method);
      }
      this.prototype[property] = value;
    }

    return this;
  }

  return {
    create: create,
    Methods: {
      addMethods: addMethods
    }
  };
})();

if (globalContext.exports) {
  globalContext.exports.Class = Class;
}
else {
  globalContext.Class = Class;
}
})(NL);

/*
* CLASSES AND OBJECTS
*/

NL.namespace("NL.curvature");
NL.curvature = 0.5;

NL.namespace("NL.getKeys");
NL.getKeys = function(object) {
    var results = [];
    for (var property in object) {
        if (object.hasOwnProperty(property)) {
            results.push(property);
        }
    }
    return results;
},

NL.namespace("NL.getValues");
NL.getValues = function(object) {
    var results = [];
    for (var property in object) {
        if (object.hasOwnProperty(property)) {
            results.push(object[property]);
        }
    }
    return results;
},

NL.namespace("NL.arrayAvg");
NL.arrayAvg = function(array) {
    var s;
    var i;
    var len = array.length;
    if (len == 0)   {
        return 0;
    } else {
        for (i = 0; i < len; i++)   {
            s += array[i];
        }
        return s/len;
    }
},

NL.namespace("NL.getPath");
NL.getPath = function(link, hoffset) {
    var x0 = link.x0;
    var x1 = link.x1;
    var xi = d3.interpolateNumber(x0, x1);
    var x2 = xi(NL.curvature);
    var x3 = xi(1 - NL.curvature);
    var y0 = link.y0 - hoffset;
    var y1 = link.y1 - hoffset;

    return "M" + x0 + "," + y0
        + "C" + x2 + "," + y0
        + " " + x3 + "," + y1
        + " " + x1 + "," + y1;
},

NL.namespace("NL.User");
NL.User = function(name, id, rgb, index, nodes) {
    this.name = name;
    this.rgb = rgb;
    this.id = id;
    this.index = index;
    this.nodes = nodes;
    this.first_post = null;
    this.median_count = 0;
    this.order = index;
    this.min = -1;
    this.max = -1;
    this.node_ptr = null;
};

NL.namespace("NL.Link");
NL.Link = function(from, to, id) {
    // to and from are ids of scenes
    this.from = from;
    this.to = to;
    this.id = id;
    this.x0 = 0;
    this.y0 = -1;
    this.x1 = 0;
    this.y1 = -1;
    this.user_ptr = null;
}

NL.namespace("NL.Node");
NL.Node = function(users, date, type, id) {
    this.users = users;
    this.date = date;
    this.type = type;
    this.id = id;
    this.name;
    this.user_ptrs = [];
    this.x = 0;
    this.y = 0;
    this.width = 20; //node_width; // Same for all nodes
    this.height = 0; // Will be set later; proportional to link count
    this.in_links = [];
    this.out_links = [];
    this.user_node = false;
    this.first_post = null; // Only defined for user_node true
    this.median_user = null;
    this.rgb = "#cccccc";
    
    this.has_user = function(id) {
        var i;
	    for (i = 0; i < this.users.length; i++) {
	        if (id == this.users[i]) 
		    return true;
	    }
	    return false;
    }
    
    this.user_index = function(id) {
        var i;
	    for (i = 0; i < this.users.length; i++) {
	        if (id == this.users[i])    {
	            if(this.median_user)    {
		            return this.median_user.index - i;
		        } else {
		            return i;
		        }
		    }
	    }
	    return -1;
    }
    
    this.user_link_index = function(id) {
        var i;
        var j = 0;
	    for (i = 0; i < this.in_links.length; i++) {
	        if (id == this.in_links[i].id)    {
		        return i;
		    }
	    }
	    return -1;
    }
};

NL.namespace("NL.gainFocus");
NL.gainFocus = function(id)  {
    d3.selectAll("[charid=\"" + id + "\"]")
        .style("opacity", "1")
        .style("stroke-width", 4);
    d3.selectAll("[nameid=\"" + id + "\"]").style("opacity", "1");
}

NL.namespace("NL.gainHalfFocus");
NL.gainHalfFocus = function(id)  {
    d3.selectAll("[charid=\"" + id + "\"]").style("opacity", "0.7");
    d3.selectAll("[nameid=\"" + id + "\"]").style("opacity", "0.7");
}

NL.namespace("NL.loseFocus");
NL.loseFocus = function(id)  {
    d3.selectAll("[charid=\"" + id + "\"]")
        .style("opacity", "0.3")
        .style("stroke-width", 2);
    d3.selectAll("[nameid=\"" + id + "\"]").style("opacity", "0.3");
}

NL.namespace("NL.timeFmt");
NL.timeFmt = d3.time.format("%c");

NL.namespace("NL.timeStr");
NL.timeStr = function(timestamp)  {
    return NL.timeFmt(new Date(timestamp));
}

NL.namespace("NL.longTimeFmt");
NL.longTimeFmt = d3.time.format("%A %d %B %Y %H:%M:%S");

NL.namespace("NL.longTimeStr");
NL.longTimeStr = function(timestamp)  {
    return NL.longTimeFmt(new Date(timestamp));
}

NL.namespace("NL.FbAdDetail");
NL.FbAdDetail = NL.Class.create( {
    gridUnit: 20,
    textHeight: 12,
    infoHeight: 120,
    initialize: function(args) {
        this.dataURL = args.dataURL;
        this.viewSelector = args.viewSelector;
        
        this.fullHeight = args.height || 260;
        this.fullWidth = args.width || 200;
        
        this.loader = args.loader;

        this.initTemplates();
        this.hideDetail();
    },
    
    initTemplates: function()   {
        this.detail_info_html = Handlebars.compile($("#fbad-info-html").html());
        this.detail_content_html = Handlebars.compile(
                                            $("#fbad-content-html").html());
    },
    
    getHeading: function(data)   {
        switch(data["type"]) {
            case "fbsp":
                return "Facebook Sponsored Story";
            case "fbad":
                return "Facebook Ad";
            default:
                return null;
        }
    },

    setDetailInfo: function(data)   {
        return this.detail_info_html({
            heading: this.getHeading(data),
            date: NL.longTimeStr(parseInt(data["date"])*1000),
            title: data["title"]
        }); 
    },  
    
    setDetailContent: function(data)   {
        return this.detail_content_html({
            text: data["text"],
            images: data["images"]
        }); 
    },  
    
    hideDetail: function()  {
	    $(this.viewSelector).hide();
	},
    
    showDetail: function(data)  {
        
	    $(this.viewSelector + " #detail-info").html(this.setDetailInfo(data));
	    $(this.viewSelector + " #detail-content").html(
	                                            this.setDetailContent(data));
	    var element = $(this.viewSelector); 
	    var graph = $(this.viewSelector + " #detail-content");
	    var headHeight = 60;
	    $(this.viewSelector + " #detail-head").height(headHeight);
	    element.width(this.fullWidth);
	    element.css({
	        top: $(window).scrollTop() + 40,
	        left: $(window).scrollLeft() + ($(window).width() - element.width())/2,
	        height: this.fullHeight
	    }); 
	    $(this.viewSelector + " #detail-info").width(
	        element.width() - $(this.viewSelector + " #detail-ctrls").width() - 40);
	    element.show();
	},
	
	getDetail: function(ad, adtype)  {
	    this.loader.show();
	    
	    var url = this.dataURL + adtype + "/" + ad.id + "/";
        console.log("url: " + url);
        $.ajax( {
			url: url,
			dataType: 'json',
			success: this.success.bind(this),
			error: this.error.bind(this)
		} );
	},
	
	success: function(data, status) {
	    this.loader.hide();
	    
	    if(data['type'] == "error") {
	        console.log("error "+data['message']);
	    } else {
	        console.log("success ");
	        this.clearDisplay();
	        this.showDetail(data);
	    }
	},
	
	error: function() {
	    console.log("get detail error");
	    this.hideDetail();
	    this.loader.error("Unable to load data.");
	},
	
	clearDisplay: function()   {
	    var _hideDetail = this.hideDetail.bind(this);
        $('body').on('click', this.viewSelector + " #detail-head a.close-btn", function(event) {
            event.stopPropagation();
            _hideDetail();
            return false;
        });
        $(this.viewSelector + " #detail-info").empty();
        $(this.viewSelector + " #detail-content").empty();
	}
});

NL.namespace("NL.AdDetail");
NL.AdDetail = NL.Class.create( {
    gridUnit: 20,
    textHeight: 12,
    infoHeight: 120,
    // METHODS
    initialize: function(args) {
        this.dataURL = args.dataURL;
        this.viewSelector = args.viewSelector;
        
        this.fullHeight = args.height || 400;
        this.fullWidth = args.width || 300;
        
        this.loader = args.loader;

        this.initTemplates();
        this.hideDetail();
    },
    
    initTemplates: function()   {
        this.detail_info_html = Handlebars.compile($("#ad-info-html").html());
    },
    
    setDetailInfo: function(data)   {
        var start = parseInt(data.dates.start) * 1000;
        return this.detail_info_html({
            date: NL.longTimeStr(start),
            duration: countdown(start, 
                        parseInt(data.dates.end) * 1000).toString()
        }); 
    },
    
    hideDetail: function()  {
	    $(this.viewSelector).hide();
	},
	
	showDetail: function(data)  {
	    $(this.viewSelector + " #detail-info").html(this.setDetailInfo(data));
	    var element = $(this.viewSelector); 
	    var graph = $(this.viewSelector + " #detail-content");
	    var headHeight = 60;
	    $(this.viewSelector + " #detail-head").height(headHeight);
	    element.width(this.width + this.margin.left + 120);
	    element.css({
	        top: $(window).scrollTop() + 40,
	        left: $(window).scrollLeft() + ($(window).width() - element.width())/2,
	        height: $(window).height() - 80
	    }); 
	    if (this.fullHeight > element.height() - headHeight)    {
	        graph.css({
	            height: element.height() - headHeight
	        }); 
	    } else {
	        element.css({
	            height: this.fullHeight + headHeight
	        }); 
	    }
	    element.show();
	},
	
	getDetail: function(hour)  {
	    this.loader.show();
	    
	    var url = this.dataURL + hour + "/";
        console.log("AD url: " + url);
        $.ajax( {
			url: url,
			dataType: 'json',
			success: this.success.bind(this),
			error: this.error.bind(this)
		} );
	},
	
	success: function(data, status) {
	    this.loader.hide();
	    
	    if(data['type'] == "error") {
	        console.log("error "+data['message']);
	    } else {
	        console.log("success "+data['hour']);
	        this.clearDisplay();
	        this.prepareData(data);
	        this.prepareGraph(data);
	        this.drawAds(data);
	        this.drawAdDomains();
	        this.drawRefDomains();
	        this.showDetail(data);
	    }
	},
	
	error: function() {
	    console.log("get detail error");
	    this.hideDetail();
	    this.loader.error("Unable to load data.");
	},
	
	clearDisplay: function()   {
	    var _hideDetail = this.hideDetail.bind(this);
            
        $('body').on('click', this.viewSelector + " #detail-head a.close-btn", function(event) {
            event.stopPropagation();
            _hideDetail();
            return false;
        });
        
        // clear
        $(this.viewSelector + " #detail-info").empty();
        $(this.viewSelector + " #detail-content").empty();
	},
	
	prepareData: function(data)   {
	    this.domains = NL.getKeys(data.ads);
        this.domains.sort();
        this.refs = data.refs
        this.refs.sort();
        this.totalRefs = this.refs.length;
	    this.totalAds = this.domains.length;
	    this.buildRefMap(data);
	    this.buildAdsMap(data);
	},
	
	buildRefMap: function(data) {
	    this.ref_map = {};
	    var i, j, domain, refs, ref;
	    for(i = 0; i < this.domains.length; i++)    {
	        domain = this.domains[i];
	        refs = data.ads[domain];
	        for(j = 0; j < refs.length; j++)    {
	            ref = refs[j][0];
	            if (this.ref_map.hasOwnProperty(ref)) {
                    this.ref_map[ref].push(domain);
                } else {
                    this.ref_map[ref] = [domain];
                }
	        }
	    }
	},
	
	buildAdsMap: function(data) {
	    this.ads_map = {};
	    var i, j, domain, refs, ref;
	    for(i = 0; i < this.domains.length; i++)    {
	        domain = this.domains[i];
	        refs = data.ads[domain];
	        for(j = 0; j < refs.length; j++)    {
	            ref = refs[j][0];
	            if (this.ads_map.hasOwnProperty(domain)) {
                    this.ads_map[domain].push(ref);
                } else {
                    this.ads_map[domain] = [ref];
                }
	        }
	    }
	},
	
	getMaxNameLength: function(names)    {
	    var l;
	    var maxn = 0;
	    names.forEach(function(name) {
	        maxn = Math.max(name.length*7.2, maxn);
	    });
	    return maxn;
	},
	
	prepareGraph: function(data)   {
	    this.margin = {
	                top: 20, 
	                right: 120, 
	                bottom: this.getMaxNameLength(this.refs)+10, 
	                left: this.getMaxNameLength(this.domains)+10};
        this.width = this.totalRefs*this.gridUnit;
        this.height = this.totalAds*this.gridUnit;
        this.fullHeight = this.height + this.margin.left + this.margin.right;
        
	    // graph SVG
        this.svg = d3.select(this.viewSelector + " #detail-content").append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g")
            .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");
            
        // axes
        this.x = d3.scale.ordinal()
            .domain(this.refs)
            .rangeRoundBands([0, this.width], 0.1);
                    
        this.y = d3.scale.ordinal()
            .domain(this.domains)
            .rangeRoundBands([0, this.height], 0.1);
	},
	
	drawAdDomains: function()   {
	    var _x = this.x;
        var _y = this.y;
        var _gu = this.gridUnit;
        var _d = this.dispatch;
        var _ads_map = this.ads_map;

        var node = this.svg.append("g").selectAll(".domain")
            .data(this.domains)
            .enter().append("g")
            .attr("class", "domain")
            .attr("transform", function(d) {
                        return "translate(" + 0 + "," + _y(d) + ")"; })
            .on("mouseover", function(d)   {
                    d3.selectAll("[adsid=\"ads_" + d + "\"]").style("opacity", "0.6");
                    d3.selectAll("[nameid=\"ads_" + d + "\"]").style("opacity", "1.0");
                    _ads_map[d].forEach(function(ref)  {
                        d3.selectAll("[nameid=\"ref_" + ref + "\"]").style("opacity", "1.0");
                    });
                })
            .on("mouseout", function(d)   {
                    d3.selectAll("[adsid=\"ads_" + d + "\"]").style("opacity", "0.3");
                    d3.selectAll("[nameid=\"ads_" + d + "\"]").style("opacity", "0.5");
                    _ads_map[d].forEach(function(ref)  {
                        d3.selectAll("[nameid=\"ref_" + ref + "\"]").style("opacity", "0.5");
                    });
                });
        
        node.append("rect")
            .attr("x", function(d) { return -((d.length)*7.2); })
            .attr("y", function(d) { return -8; })
            .attr("width", function(d) { return (d.length)*7.2; })
            .attr("height", _gu)
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("transform", null)
            .attr("fill", "#fff")
            .style("opacity", 0);
            
        node.append("text")
            .attr("x", -4)
            .attr("y", 0)
            .attr("dy", ".35em")
            .attr("text-anchor", "end")
            .attr("transform", null)
            .text(function(d) { return d; })
            .attr("nameid", function(d) { return "ads_" + d; })
            .style("opacity", "0.5")
            .style("fill", "#000")
            .style("stroke", "#000");
	},
	
	drawRefDomains: function()   {
	    var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _gu = this.gridUnit;
        var _d = this.dispatch;
        var _ref_map = this.ref_map;

        var node = this.svg.append("g").selectAll(".domain")
            .data(this.refs)
            .enter().append("g")
            .attr("class", "domain")
            .attr("transform", function(d) {
                        return "translate(" + _x(d) + "," + _h + ")rotate(60)"; })
            .on("mouseover", function(d)   {
                    d3.selectAll("[refid=\"ref_" + d + "\"]").style("opacity", "0.6");
                    d3.selectAll("[nameid=\"ref_" + d + "\"]").style("opacity", "1.0");
                    _ref_map[d].forEach(function(domain)  {
                        d3.selectAll("[nameid=\"ads_" + domain + "\"]").style("opacity", "1.0");
                    });
                })
            .on("mouseout", function(d)   {
                    d3.selectAll("[refid=\"ref_" + d + "\"]").style("opacity", "0.3");
                    d3.selectAll("[nameid=\"ref_" + d + "\"]").style("opacity", "0.5");
                    _ref_map[d].forEach(function(domain)  {
                        d3.selectAll("[nameid=\"ads_" + domain + "\"]").style("opacity", "0.5");
                    });
                });
            
        node.append("rect")
            .attr("x", -4)
            .attr("y", -8)
            .attr("width", function(d) { return (d.length)*7.2; })
            .attr("height", _gu)
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("transform", null)
            .attr("fill", "#fff")
            .style("opacity", 0);
        
        node.append("text")
            .attr("x", -4)
            .attr("y", 0)
            .attr("dy", ".35em")
            .attr("text-anchor", "start")
            .attr("transform", null)
            .text(function(d) { return d; })
            .attr("nameid", function(d) { return "ref_" + d; })
            .style("opacity", "0.5")
            .style("fill", "#000")
            .style("stroke", "#000");
	},
	
	drawAds: function(data)   {
	    var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _th = this.textHeight;
        var _gu = this.gridUnit;
        var _svg = this.svg;
        var _gain = this.gainAdFocus;
        var _lose = this.loseAdFocus;
        var miny = 0;
        var maxx = 0;
        
        this.domains.forEach(function(domain) {
            var node = _svg.append("g").selectAll(".admark")
                .data(data.ads[domain])
                .enter().append("g")
                .attr("class", "admark")
                .attr("transform", function(d) {
                     return "translate(" + _x(d[0]) + "," + _y(domain) + ")"; })
                .on("mouseover", function(d)  {
                        d3.selectAll("[nameid=\"ad_" + d[0] + "_" + domain + "\"]").style("opacity", "0.6");
                        d3.selectAll("[nameid=\"ref_" + d[0] + "\"]").style("opacity", "1.0");
                        d3.selectAll("[nameid=\"ads_" + domain + "\"]").style("opacity", "1.0");
                    })
                .on("mouseout", function(d)  {
                        d3.selectAll("[nameid=\"ad_" + d[0] + "_" + domain + "\"]").style("opacity", "0.3");
                        d3.selectAll("[nameid=\"ref_" + d[0] + "\"]").style("opacity", "0.5");
                        d3.selectAll("[nameid=\"ads_" + domain + "\"]").style("opacity", "0.5");
                    });
            
            node.append("circle")
                .attr("r", function(d) { 
                        var r = Math.sqrt(d[1]*3);
                        miny = Math.min(miny, _y(domain) - r);
                        maxx = Math.max(maxx, _x(d[0]) + r);
                        return r; })
                .style("fill", "#f00")
                .style("stroke-width", 0)
                .style("opacity", 0.3)
                .attr("nameid", function(d) { return "ad_" + d[0] + "_" + domain; })
                .attr("refid", function(d) { return "ref_" + d[0]; })
                .attr("adsid", function(d) { return "ads_" + domain; })
                .append("title")
                .text(function(d) { 
                    return domain + " - " + d[0] + " " + d[1]});
        });
        
        if (maxx > this.width + this.margin.right)  {
            this.margin.right = this.margin.right + (maxx - this.width);
        }
        if (miny > this.height - this.margin.top)  {
            this.margin.top = this.margin.top + (miny - this.height);
        }
	}
});

NL.namespace("NL.Detail");
NL.Detail = NL.Class.create( {
    // PROPERTIES
    text_height: 10,
    timeUnit: 3600000, // 1 hour
    timeSpace: 40,
    timeMin: 240,
    timeMax: 640,
    tuMin: 0.5,
    tuMax: 72,
    userSpace: 20,
    y_offset: 10,
    colWidth: 20,
    // METHODS
    initialize: function(args) {
        this.dataURL = args.dataURL;
        this.viewSelector = args.viewSelector;
        
        this.fullHeight = args.height || 400;
        this.fullWidth = args.width || 300;
        
        this.loader = args.loader;

        this.initTemplates();
        this.hideDetail();
    },
    
    initTemplates: function()   {
        this.detail_info_html = Handlebars.compile($("#detail-info-html").html());
    },
    
    timeLinesUnit: function(timeUnits)    {
        if (timeUnits < this.tuMin)  {
            return d3.time.second;
        } else if (timeUnits > this.tuMax)  {
            return d3.time.hour;
        } else {
            return d3.time.minute;
        }
    },
    
    timeLinesSize: function(timeUnits)    {
        if (timeUnits < this.tuMin)  {
            return 10;
        } else if (timeUnits > this.tuMax)  {
            return 3;
        } else {
            return 30;
        }
    },
    
    timeAxisUnit: function(timeUnits)    {
        if (timeUnits < this.tuMin)  {
            return d3.time.minute;
        } else if (timeUnits > this.tuMax)  {
            return d3.time.day;
        } else {
            return d3.time.hour;
        }
    },
    
    timeAxisSize: function(timeUnits)    {
        if (timeUnits < this.tuMin)  {
            return 1;
        } else if (timeUnits > this.tuMax) {
            return 1;
        } else {
            return 2;
        }
    },
    
    timeMargin: function(timeUnits)    {
        if (timeUnits < this.tuMin)  {
            return 30000; // 30 seconds
        } else if (timeUnits > this.tuMax) {
            return this.timeUnit*3;
        } else {
            return this.timeUnit;
        }
    },
    
    getDescription: function(data)  {
        switch(data["type"]) {
            case "post":
                return data["description"];
            case "photo":
                return data["caption"];
            case "link":
                return data["title"];
            case "video":
                return data["title"];
            case "status":
                return data["message"];
            case "album":
                return data["name"];
            case "event":
                return data["name"];
            default:
                return null;
        }
    },
    
    getHeading: function(data)   {
        switch(data["type"]) {
            case "post":
                return "Wall posting";
            case "photo":
                return "Photograph";
            case "link":
                return "Shared link";
            case "video":
                return "Video";
            case "status":
                return "Status message";
            case "album":
                return "Album";
            case "event":
                return "Event";
            default:
                return "Facebook";
        }
    },
    
    getLink: function(data)  {
        var link;
        switch(data["type"]) {
            case "post":
                link = data["permalink"];
                break;
            case "photo":
                link = data["link"];
                break;
            case "link":
                link = data["url"];
                break;
            case "video":
                link = data["link"];
                break;
            case "status":
                link = null;
                break;
            case "album":
                link = data["link"];
                break;
            case "event":
                link = null;
                break;
            default:
                link = null;
        }
        return link === "anonymised" ? null : link;
    },
    
    setDetailInfo: function(data, duration)   {
        return this.detail_info_html({
            heading: this.getHeading(data),
            from: data["source_name"],
            description: this.getDescription(data),
            created: NL.longTimeStr(parseInt(data["created_time"])*1000),
            ended: NL.longTimeStr(parseInt(data["dates"]["end"])*1000),
            duration: countdown(parseInt(data["created_time"])*1000, 
                        parseInt(data["dates"]["end"])*1000).toString(),
            link: this.getLink(data)
        }); 
    },
    
    hideDetail: function()  {
	    $(this.viewSelector).hide();
	},
	
	showDetail: function(data)  {
	    var element = $(this.viewSelector); 
	    var graph = $(this.viewSelector + " #detail-content");
	    var headHeight = 160;
	    $(this.viewSelector + " #detail-head").height(headHeight);
	    element.width(Math.min(
	            this.width + this.margin.left + 120, $(window).width() - 80));
	    element.css({
	        top: $(window).scrollTop() + 40,
	        left: $(window).scrollLeft() + ($(window).width() - element.width())/2,
	        height: $(window).height() - 80
	    });  
	    if (this.fullHeight > element.height() - headHeight)    {
	        graph.css({
	            height: element.height() - headHeight
	        }); 
	    } else {
	        element.css({
	            height: this.fullHeight + headHeight
	        }); 
	    }
	    element.show();
	},
	
	getDetail: function(node)  {
	    var url = this.dataURL;
	    if(node.user_node)  {
            url += "user/" + node.id + "/";
        } else {
            url += node.type + "/" + node.id + "/";
        }
        console.log("url: " + url);
        this.loader.show();
        $.ajax( {
			url: url,
			dataType: 'json',
			success: this.success.bind(this),
			error: this.error.bind(this)
		} );
	},
	
	success: function(data, status) {
	    this.loader.hide();
	    if(data['type'] == "error") {
	        console.log("error "+data['message']);
	    } else {
	        console.log("success "+data['type']);
	        this.displayPost(data);
	        this.showDetail();
	    }
	},
	
	error: function() {
	    console.log("get detail error");
	    this.hideDetail();
	    this.loader.error("Unable to load data.");
	},
	
	displayPost: function(data)   {
	    this.parseDates(data['dates']);
	    this.parseUsers(data['users']);
	    this.prepareGraph(data);
		this.drawGraph(data);
	},
	
	parseDates: function(jdates)   {
        this.start_date = parseInt(jdates['start']) * 1000;
        this.end_date = parseInt(jdates['end']) * 1000;
        this.total_duration = this.end_date - this.start_date;
        this.totalUnits = Math.ceil(this.total_duration / this.timeUnit);
    },
	
	parseUsers: function(jusers)   {
        this.users = [];
        this.user_map = [];
        this.user_nodes = [];
        var i;
        var unode;
        for (i = 0; i < jusers.length; i++) {
            this.users[this.users.length] = new NL.User(
                                                    jusers[i].name, 
                                                    jusers[i].id, 
                                                    jusers[i].rgb, 
                                                    i);
            this.user_map[jusers[i].id] = this.users[this.users.length-1];
        }
    },
    
    // PREPARE
    prepareGraph: function(data)  {
        // canvas
        this.margin = {top: 40, right: 40, bottom: 30, left: 200};
        this.width = Math.max((this.totalUnits*this.timeSpace), this.timeMin);
        this.height = this.users.length*this.userSpace;
        this.fullWidth = this.width + this.margin.left + this.margin.right;
        this.fullHeight = this.height + this.margin.top + this.margin.bottom;
        var _hideDetail = this.hideDetail.bind(this);
            
        $('body').on('click', this.viewSelector + " #detail-head a.close-btn", function(event) {
            event.stopPropagation();
            _hideDetail();
            return false;
        });
        
        // clear
        $(this.viewSelector + " #detail-content").empty();
        $(this.viewSelector + " #detail-info").empty();
        $(this.viewSelector + " #detail-content").empty();
        // display
        $(this.viewSelector + " #detail-info")
            .html(this.setDetailInfo(data, this.total_duration));
        
        // graph SVG
        this.svg = d3.select(this.viewSelector + " #detail-content").append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g")
            .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");
            
        // axes
        this.x = d3.time.scale.utc()
                    .domain([
                            this.start_date - this.timeMargin(this.totalUnits), 
                            this.end_date + this.timeMargin(this.totalUnits)
                        ])
                    .range([0, this.width]);
                    
        this.y = d3.scale.linear()
                    .domain([0, this.users.length])
                    .rangeRound([0, this.height]);
                    
        // post area
        var bgX0 = this.x(this.start_date);
        var bgX1 = this.x(this.end_date);
        this.svg.append("rect")
            .attr("class", "grid-background")
            .attr("x", bgX0)
            .attr("y", 0)
            .attr("width", this.width - bgX0 - (this.width - bgX1))
            .attr("height", this.height);
        this.svg.append("line")
            .attr("class", "grid-background-line")
            .attr("x1", bgX0)
            .attr("y1", 0)
            .attr("x2", bgX0)
            .attr("y2", this.height);
        this.svg.append("line")
            .attr("class", "grid-background-line")
            .attr("x1", bgX1)
            .attr("y1", 0)
            .attr("x2", bgX1)
            .attr("y2", this.height);
                     
        var xLines = d3.svg.axis()
            .scale(this.x)
            .ticks(this.timeLinesUnit(this.totalUnits), 
                    this.timeLinesSize(this.totalUnits))
            .tickSize(-this.height);

        this.svg.append("g")
            .attr("class", "grid")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xLines);

        var xValues = d3.svg.axis()
            .scale(this.x)
            .ticks(this.timeAxisUnit(this.totalUnits), 
                    this.timeAxisUnit(this.totalUnits));

        this.svg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xValues); 
    },
    
    // DRAW
    drawGraph: function(data)  {
        this.drawUsers();
        if (data.hasOwnProperty('comments'))    {
            this.drawComments(data);
            
        }
        if (data.hasOwnProperty('message') && data.message != null)   {
            this.drawMessage([{
                    text: data.message,
                    fromid: data.source_id,
                    created_time: data.created_time
                }]);
        }
        if (data.hasOwnProperty('likers'))    {
            this.drawLikes(data);
        }
        if (data.hasOwnProperty('tagged'))    {
            this.drawTagged(data);
        }
    },
    
    drawUsers: function()   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _yo = this.y_offset;
        var _th = this.text_height;
        var _cw = this.colWidth;
        
        var node = this.svg.append("g").selectAll(".node")
            .data(this.users)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { return "translate(" + (-_cw*2) + "," + (_h - _y(d.index) - _yo) + ")"; })
            .classed("usernode", true)
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb);
            
        node.append("rect")
            .attr("x", function(d) { return -((d.name.length)*7.2); })
            .attr("y", function(d) { return -8; })
            .attr("width", function(d) { return (d.name.length)*7.2; })
            .attr("height", _th*1.5)
            .attr("transform", null)
            .attr("fill", "#fff")
            .style("opacity", 0.6);
        
        node.append("text")
            .attr("x", -4)
            .attr("y", 0)
            .attr("dy", ".35em")
            .attr("text-anchor", "end")
            .attr("transform", null)
            .text(function(d) { return d.name; })
            .attr("nameid", function(d) { return "user_" + d.id; })
            .style("opacity", "0.5")
            .style("fill", function(d) { return d.rgb; })
            .style("stroke", function(d) { return d.rgb; });
            
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d.id);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d.id);
        }
    },
    
    getUserY: function(user_id) { 
        return this.height - this.y(this.user_map[user_id].index) - this.y_offset;
    },
    
    getUserRGB: function(user_id) {
        return this.user_map[user_id].rgb;
    },
    
    drawComments: function(data)   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _yo = this.y_offset;
        var _th = this.text_height;
        var _gy = this.getUserY.bind(this);
        var _rgb = this.getUserRGB.bind(this);
        
        var node = this.svg.append("g").selectAll(".node")
            .data(data.comments)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { 
                    return "translate(" + (_x(d.created_time*1000) - 10) + "," + (_gy(d.fromid) - _yo) + ")"; })
            .attr("nameid", function(d) { return "user_" + d.fromid; })
            .style("opacity", "0.5")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb);

        node.append("rect")
            .attr("width", 20)
            .attr("height", 20)
            .style("fill", function(d) { return _rgb(d.fromid); })
            .style("stroke-width", 0)
            .append("title")
            .text(function(d) { 
                return NL.timeStr(d.created_time*1000) + "\n" + d.message; 
            });
            
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d.fromid);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d.fromid);
        }
    },
    
    drawMessage: function(messages)   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _yo = this.y_offset;
        var _th = this.text_height;
        var _gy = this.getUserY.bind(this);
        var _rgb = this.getUserRGB.bind(this);
        
        var node = this.svg.append("g").selectAll(".node")
            .data(messages)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { 
                    return "translate(" + (_x(d.created_time*1000) - 10) + "," + (_gy(d.fromid) - _yo) + ")"; })
            .attr("nameid", function(d) { return "user_" + d.fromid; })
            .style("opacity", "0.5")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb);

        node.append("circle")
            .attr("cx", 10)
            .attr("cy", 10)
            .attr("r", 8)
            .style("fill", function(d) { return _rgb(d.fromid); })
            .style("stroke-width", 0)
            .append("title")
            .text(function(d) { return NL.timeStr(d.created_time*1000) + "\n" + d.text; });
            
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d.fromid);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d.fromid);
        }
    },
    
    drawLikes: function(data)   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _yo = this.y_offset;
        var _th = this.text_height;
        var _cw = this.colWidth;
        var _gy = this.getUserY.bind(this);
        var _rgb = this.getUserRGB.bind(this);
        
        var node = this.svg.append("g").selectAll(".node")
            .data(data.likers)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { 
                    return "translate(" + (-_cw*2) + "," + (_gy(d) - _yo) + ")"; })
            .attr("nameid", function(d) { return "user_" + d; })
            .style("opacity", "0.5")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb);

        node.append("circle")
            .attr("cx", _cw/2)
            .attr("cy", _cw/2)
            .attr("r", 4)
            .style("fill", function(d) { return _rgb(d); })
            .style("stroke-width", 0)
            .append("title")
            .text("Liked");
            
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d);
        }
    },
    
    drawTagged: function(data)   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _yo = this.y_offset;
        var _th = this.text_height;
        var _cw = this.colWidth;
        var _gy = this.getUserY.bind(this);
        var _rgb = this.getUserRGB.bind(this);
        
        var node = this.svg.append("g").selectAll(".node")
            .data(data.tagged)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { 
                    return "translate(" + (-_cw) + "," + (_gy(d) - _yo) + ")"; })
            .attr("nameid", function(d) { return "user_" + d; })
            .style("opacity", "0.5")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb);

        node.append("rect")
            .attr("width", 6)
            .attr("height", 6)
            .attr("x", (_cw-6)/2)
            .attr("y", (_cw-6)/2)
            .style("fill", function(d) { return _rgb(d); })
            .style("stroke-width", 0)
            .append("title")
            .text("Tagged");
            
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d);
        }
    },

});

NL.namespace("NL.Loader");
NL.Loader = NL.Class.create( {
    initialize: function(args) {
        this.viewSelector = args.viewSelector;
    },

    show: function() {
        var element = $(this.viewSelector);
	    element.css({
	        top: $(window).scrollTop() + ($(window).height() / 5),
	        left: $(window).scrollLeft() + ($(window).width() - element.width())/2,
	    }); 
        element.show();
    },
    
    hide: function() {
        $(this.viewSelector).hide();
    },
    
    reset: function() {
        $(this.viewSelector).html(
                    '<span>Loading</span> <span id="ellipsis">...</span>');
    },
    
    close: function() {
        this.hide();
        this.reset();
    },
    
    timedClose: function() {
        this.timeout = setTimeout(this.close.bind(this), 5000);
    },
    
    error: function(message) {
        $(this.viewSelector).html('<span class="error">' + message + '</span>');
        console.log("ERROR: " + message); 
        this.timedClose();
    },
    
    setText: function(message) {
        $(this.viewSelector).html('<span>' + message + '</span>');
        console.log("ERROR: " + message);
    },
});

NL.namespace("NL.Graph");
NL.Graph = NL.Class.create( {
    // PROPERTIES
    link_width: 4, //1.8,
    link_gap: 4,
    raw_chart_height: 360,
    raw_chart_width: 1000,
    text_height: 10,
    nameShift: 60,
    shiftUnit: 10,
    panel_width: 15,
    panel_shift: 100,
    y_offset: 12,
    userSpace: 20,
    hOffset: 0,
    maxy:0,
    _seeSingleUsers: true,
    _seeUsers: true,
    _seePosts: true,
    _seeAds: true,
    _seeFbAds: true,
    // METHODS
    initialize: function(args) {

        this.dataURL = args.dataURL;
        this.viewSelector = args.viewSelector;
        this.detailView = args.detailView;
        this.adView = args.adView;
        this.fbAdView = args.fbAdView;
        
        this.fullHeight = args.height || 500;
        this.fullWidth = args.width || 1000;
        
        this.loader = args.loader;
        
        this.request();
    },

    request: function()    {
        console.log("request: " + this.dataURL);
        this.loader.reset();
        this.loader.show();
        $.ajax( {
			url: this.dataURL,
			dataType: 'json',
			success: this.success.bind(this),
			error: this.error.bind(this)
		} );
    },
    
    error: function() {
		console.log("error loading dataURL: " + this.dataURL);
		this.loader.error("Unable to load data.");
	},

	success: function(data, status) {
		this.parseDates(data['dates']);
		this.parseUsers(data['users']);
		this.parseFBObjects(data['fbobjects']);
		this.prepareGraph();
		this.prepareData();
		this.drawGraph(data);
		this.loader.hide();
		this.scrollToView();
	},
	
	scrollToView: function()    {
	    $(window).resize();
	    var scrmidy = 
	        $(this.viewSelector).offset().top + this.height + this.margin.top;
	    console.log("scrmidy: " + scrmidy);
	    console.log("$(window).height(): " + $(window).height());
	    if(scrmidy > $(window).height())    {
	        scrmidy = 
	            $(this.viewSelector).offset().top + this.midy;
	        $(window).scrollTop(scrmidy);
	        console.log("scrollTop: " + scrmidy);
	    }
	},
	
	// PARSE DATA
	parseDates: function(jdates)   {
        this.start_date = parseInt(jdates['start']) * 1000;
        this.end_date = parseInt(jdates['end']) * 1000;
        this.total_duration = this.end_date - this.start_date;
    },
    
    parseUsers: function(jusers)   {
        this.users = [];
        this.user_map = [];
        this.user_nodes = [];
        this.singleUsers = []
        var i;
        var unode;
        for (i = 0; i < jusers.length; i++) {
            this.users[this.users.length] = new NL.User(
                                                    jusers[i].name, 
                                                    jusers[i].id, 
                                                    jusers[i].rgb, 
                                                    i,
                                                    jusers[i].nodes);
            this.user_map[jusers[i].id] = this.users[this.users.length-1];
            if (jusers[i].nodes.length == 1)    {
                this.singleUsers.push(jusers[i].id);
            }
        }
    },
    
    parseFBObjects: function(jposts)   {
        this.posts = [];
        this.node_map = [];
        this.max_node_users = 0;
        var i;
        var post;
        for (var i = 0; i < jposts.length; i++) {
            post = new NL.Node(
                                jposts[i]['users'], 
                                parseInt(jposts[i]['date'])*1000,
                                jposts[i]['type'],
                                jposts[i]['id']);
            post.name = jposts[i]['info'];
            post.plus = jposts[i]['plus'] ? true : false;
            post.height = this.link_gap + (post.users.length * (this.link_width + this.link_gap));
            this.posts[this.posts.length] = post;
            this.node_map[jposts[i].id] = post;
            if(post.users.length > this.max_node_users) {
                this.max_node_users = post.users.length;
            }
        }
        this.posts.sort(function(a, b) { return a.date - b.date; });
    },
    
    prepareGraph: function()  {
        // canvas
        this.margin = {top: 20, right: 40, bottom: 30, left: 200};
        this.width = this.fullWidth - this.margin.left - this.margin.right;
        this.height = Math.max(
                        this.fullHeight, this.max_node_users*this.userSpace);
        this.midy = this.height/2;
        this.medy = this.midy;
         
        // axes
        this.x = d3.time.scale.utc()
                    .domain([this.start_date, this.end_date])
                    .range([0, this.width]);
                    
        this.y = d3.scale.linear()
                    .domain([0, this.users.length])
                    .rangeRound([0, this.height]);
                    
        this.ady = d3.scale.sqrt()
                    .domain([0, 1000])
                    .rangeRound([0, this.height/2]);
    },
     
    drawTimeline: function()  {   
        var xLines = d3.svg.axis()
            .scale(this.x)
            .ticks(20)
            .tickSize(-this.height);

        this.svg.append("g")
            .attr("class", "grid")
            .attr("transform", "translate(0," + this.height + ")")
            .call(xLines)
            .selectAll(".tick")
            .data(this.x.ticks(10), function(d) { return d; })
            .exit()
            .classed("minor", true);

        var xValues = d3.svg.axis()
            .scale(this.x)
            .ticks(10)
            .tickSize(0)
            .tickFormat(d3.time.format("%b %e %Y"));
            
        this.svg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + (this.height + 10) + ")")
            .call(xValues);
            
        this.svg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + (- this.margin.top) + ")")
            .call(xValues);
    },
    
    drawGraph: function(data)  {
        $(this.viewSelector).empty();
        this.svg = d3.select(this.viewSelector).append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g")
            .attr("transform", 
                "translate(" + this.margin.left + "," + this.margin.top + ")");
        this.drawAds(data["ads"]);
        this.drawTimeline();
        if(this.posts.length > 0)   {
            this.drawLinks();
            this.drawUserNodes();
            this.drawPostNodes();
        }
        this.drawFBSponsored(data["fbsps"]);
        this.drawFBAds(data["fbads"]);
        //this.drawNameAreas();
    },
    
    drawUserNodes: function()   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _th = this.text_height;
        var _ho = this.hOffset;
        var _getDetail = this.detailView.getDetail.bind(this.detailView);
        
        var node = this.svg.append("g").selectAll(".usernode")
            .data(this.user_nodes)
            .enter().append("g")
            .attr("class", "usernode")
            .attr("transform", function(d) { 
                    return "translate(" + d.x + "," + (d.y - _ho) + ")"; })
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb)
            .on("mouseup", _getDetail);
            
        node.append("rect")
            .attr("rectid", function(d) { return "user_" + d.id; })
            .attr("x", function(d) { return -((d.name.length)*7.2); })
            .attr("y", function(d) { return -8; })
            .attr("width", function(d) { return (d.name.length)*7.2; })
            .attr("height", _th*1.5)
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("transform", null)
            .attr("fill", "#fff")
            .style("opacity", 0.6);
        
        node.append("text")
            .attr("x", -4)
            .attr("y", 0)
            .attr("dy", ".35em")
            .attr("text-anchor", "end")
            .attr("transform", null)
            .text(function(d) { return d.name; })
            .attr("nameid", function(d) { return "user_" + d.id; })
            .style("opacity", "0.3")
            .style("fill", function(d) { return d.rgb; })
            .style("stroke", function(d) { return d.rgb; });
        
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d.id);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d.id);
        }
    },
    
    drawFBSponsored: function(fbsps)   {
        var _x = this.x;
        var _h = this.height;
        var _ho = this.hOffset;
        var _my = this.medy;
        var _prev = null;
        var _getDetail = this.fbAdView.getDetail.bind(this.fbAdView);
        
        var node = this.svg.append("g").selectAll(".fbsp")
            .data(fbsps)
            .enter().append("g")
            .attr("class", "node")
            .attr("class", "fbsp")
            .attr("transform", function(d) { 
                    d["x"] = _x(d.date*1000) - 10;
                    d["y"] = _my;
                    if (_prev)  {
                        if (d.x - _prev.x < 16)   {
                            d.y = _prev.y + 16;
                        }
                    }
                    _prev = d;
                    return "translate(" + d.x + "," + (d.y - _ho) + ")"; })
            .attr("nameid", function(d) { return "fbsps_" + d.id; })
            .style("opacity", "0.3")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb)
            .on("mouseup", mouseup_cb);

        node.append("circle")
            .attr("cx", 10)
            .attr("cy", 10)
            .attr("r", 8)
            .attr("class", "fbsps")
            .append("title")
            .text(function(d) { return d.title; });
            
        function mouseover_cb(d) {
            NL.gainFocus("fbsps_" + d.id);
        }

        function mouseout_cb(d) {
            NL.loseFocus("fbsps_" + d.id);
        }
        
        function mouseup_cb(d) {
            _getDetail(d, "fbsp");
        }
    },
    
    drawFBAds: function(fbads)   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _ho = this.hOffset;
        var _my = this.medy;
        var _prev = null;
        var _getDetail = this.fbAdView.getDetail.bind(this.fbAdView);
        
        var node = this.svg.append("g").selectAll(".fbad")
            .data(fbads)
            .enter().append("g")
            .attr("class", "node")
            .attr("class", "fbad")
            .attr("transform", function(d, i) { 
                    d["x"] = _x(d.date*1000) - 10;
                    d["y"] = _my;
                    if (_prev)  {
                        if (d.x - _prev.x < 8)   {
                            d.y = _prev.y + 8;
                        }
                    }
                    _prev = d;
                    return "translate(" + d.x + "," + (d.y - _ho) + ")"; })
            .attr("nameid", function(d) { return "fbads_" + d.id; })
            .style("opacity", "0.3")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb)
            .on("mouseup", mouseup_cb);

        node.append("circle")
            .attr("cx", 10)
            .attr("cy", 10)
            .attr("r", 4)
            .attr("class", "fbads")
            .append("title")
            .text(function(d) { return d.title; });
            
        function mouseover_cb(d) {
            NL.gainFocus("fbads_" + d.id);
        }

        function mouseout_cb(d) {
            NL.loseFocus("fbads_" + d.id);
        }
        
        function mouseup_cb(d) {
            _getDetail(d, "fbad");
        }
    },
    
    drawAds: function(ads)   {
        var _x = this.x;
        var _y = this.ady;
        var _h = this.height;
        var _ho = this.hOffset;
        var _my = this.medy;
        var _prev = null;
        var _w = _x(this.start_date+3600000);
        var _getDetail = this.adView.getDetail.bind(this.adView);
        
        var node = this.svg.append("g").selectAll(".adnode")
            .data(ads)
            .enter().append("g")
            .attr("class", "adnode")
            .attr("transform", function(d) { 
                   return "translate(" + _x(d[0]*1000) + "," + (- _ho) + ")"; })
            .attr("nameid", function(d) { return "ads_" + d[0]; })
            .style("opacity", "0.3")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb)
            .on("mouseup", mouseup_cb);
        
        node.append("rect")
            .attr("width", _w)
            .attr("height", _h)
            .attr("class", "adbg")
            .append("title")
            .text(function(d) { return ""+d[1]; });
            
        node.append("rect")
            .attr("width", _w)
            .attr("height", function(d) { return _y(d[1]); })
            .attr("y", function(d) { return _my-(_y(d[1])/2); })
            .attr("class", "ads")
            .append("title")
            .text(function(d) { return ""+d[1]; });
            
        function mouseover_cb(d) {
            NL.gainFocus("ads_" + d[0]);
        }

        function mouseout_cb(d) {
            NL.loseFocus("ads_" + d[0]);
        }
        
        function mouseup_cb(d) {
            _getDetail(d[0]);
        }
    },
    
    drawPostNodes: function()   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _ho = this.hOffset;
        var _lg = this.link_gap;
        var _getDetail = this.detailView.getDetail.bind(this.detailView);
        
        var node = this.svg.append("g").selectAll(".node")
            .data(this.posts)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { 
                    return "translate(" + d.x + "," + (d.y-_lg-_ho) + ")"; })
            .on("mouseup", _getDetail);

        node.append("rect")
            .attr("width", function(d) { return d.width; })
            .attr("height", function(d) { return d.height; })
            .attr("class", "scene")
            .attr("rx", 4)
            .attr("ry", 4)
            .append("title")
            .text(function(d) { return d.name; });
            
        node.append("path")
            .filter(function(d) { return d.plus; })
            .attr("transform", function(d) { return "translate(" + (d.width/2) + "," + (d.height - d.width/2) + ")"; })
            .attr("d", d3.svg.symbol().type("cross"))
            .style("stroke-width", 1)
            .style("stroke", function(d) { return "#666"; });
    },
     
    drawLinks: function()   {
        var _ho = this.hOffset;
        var link = this.svg.append("g").selectAll(".link")
            .data(this.links)
            .enter().append("path")
            .attr("class", "link")
            .attr("d", function(d) { return NL.getPath(d, _ho); })
            .attr("from", function(d) { return "post_" + d.from.id; })
            .attr("to", function(d) { return "post_" +  d.to.id; })
            .attr("charid", function(d) { return "user_" + d.id; })
            .style("stroke", function(d) { return d.user_ptr.rgb; })
            .style("stroke-width", 2)
            .style("opacity", "0.3")
            .style("stroke-linecap", "round")
            .on("mouseover", mouseover_cb)
            .on("mouseout", mouseout_cb)
            .append("title")
            .text(function(d) { return d.user_ptr.name; });
        
        function mouseover_cb(d) {
            NL.gainFocus("user_" + d.id);
        }

        function mouseout_cb(d) {
            NL.loseFocus("user_" + d.id);
        }
    },
    
    showSingleUsers: function()   {
        var i, m;
        for(i=0, m = this.singleUsers.length; i < m; i++)   {
            d3.selectAll("[charid=\"user_" + this.singleUsers[i] + "\"]").attr("visibility", "visible");
            d3.selectAll("[nameid=\"user_" + this.singleUsers[i] + "\"]").attr("visibility", "visible");
            d3.selectAll("[rectid=\"user_" + this.singleUsers[i] + "\"]").attr("visibility", "visible");
        }
        this._seeSingleUsers = true;
    },
    
    hideSingleUsers: function()   {
        var i, m;
        for(i=0, m = this.singleUsers.length; i < m; i++)   {
            d3.selectAll("[charid=\"user_" + this.singleUsers[i] + "\"]").attr("visibility", "hidden");
            d3.selectAll("[nameid=\"user_" + this.singleUsers[i] + "\"]").attr("visibility", "hidden");
            d3.selectAll("[rectid=\"user_" + this.singleUsers[i] + "\"]").attr("visibility", "hidden");
        }
        this._seeSingleUsers = false;
    },
    
    toggleSingleUsers: function()   {
        if(this._seeSingleUsers)  {
            this.hideSingleUsers();
        } else {
            this.showSingleUsers();
        }
        return this._seeSingleUsers;
    },
    
    showUsers: function()   {
        d3.selectAll(".usernode").attr("visibility", "visible");
        d3.selectAll(".link").attr("visibility", "visible");
        this._seeUsers = true;
    },
    
    hideUsers: function()   {
        d3.selectAll(".usernode").attr("visibility", "hidden");
        d3.selectAll(".link").attr("visibility", "hidden");
        this._seeUsers = false;
    },
    
    toggleUsers: function()   {
        if(this._seeUsers)  {
            this.hideUsers();
        } else {
            this.showUsers();
        }
        return this._seeUsers;
    },
    
    togglePosts: function()   {
        if(this._seePosts)  {
            d3.selectAll(".node").attr("visibility", "hidden");
            this._seePosts = false;
        } else {
            d3.selectAll(".node").attr("visibility", "visible");
            this._seePosts = true;
        }
        return this._seePosts;
    },
    
    toggleAds: function()   {
        if(this._seeAds)  {
            d3.selectAll(".adnode").attr("visibility", "hidden");
            this._seeAds = false;
        } else {
            d3.selectAll(".adnode").attr("visibility", "visible");
            this._seeAds = true;
        }
        return this._seeAds;
    },
    
    toggleFbAds: function()   {
        if(this._seeFbAds)  {
            d3.selectAll(".fbad").attr("visibility", "hidden");
            d3.selectAll(".fbsp").attr("visibility", "hidden");
            this._seeFbAds = false;
        } else {
            d3.selectAll(".fbad").attr("visibility", "visible");
            d3.selectAll(".fbsp").attr("visibility", "visible");
            this._seeFbAds = true;
        }
        return this._seeFbAds;
    },

    // PREPARE DATA
    prepareData: function()  {
        if (this.posts.length)  {
            this.findFirstPosts();
            this.findMedianUsers();
            this.createUserNodes();
            this.generateLinks();
            this.overlappingPosts();
            this.createNameAreas();
            this.overlappingNames();
            this.positionUserNodes();
            this.calculateLinkPositions();
        }
    },
    
    createUserNodes: function()  {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _yo = this.y_offset;
        var _user_nodes = this.user_nodes;
        var _link_width = this.link_width;
        var _start_date = this.start_date;
        var _ns = this.nameShift;
        var _su = this.shiftUnit;
        var _ml = -this.margin.left;
        
        this.users.forEach(function(user) {
            _user_nodes[_user_nodes.length] = new NL.Node(
                                                    [user.id], 
                                                    user.first_post.date, 
                                                    "usernode", 
                                                    user.id);
            unode = _user_nodes[_user_nodes.length-1];
            unode.user_node = true;
            unode.y = _h - _y(user.first_post.user_index(user.id)) - _yo;
            unode.x = Math.max(_ml, _x(user.first_post.date) - _ns - 
                        (_su * user.first_post.users.length));
            unode.width = 5;
            unode.height = _link_width;
            unode.name = user.name
            unode.rgb = user.rgb;
            user.node_ptr = unode;
        });
    },
    
    findFirstPosts: function()  {
        var user_map = this.user_map;
        var user;
        var i;
        this.posts.forEach(function(post) {
            for (i = 0; i < post.users.length; i++) {
                user = user_map[post.users[i]];
                if(user.first_post != null) {
                    if(user.first_post.date > post.date)    {
                        user.first_post = post;
                    }
                } else {
                    user.first_post = post;
                }
            }
        });
    },
    
    findMedianUsers: function() {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _my = this.midy;
        var user_map = this.user_map;
        var i;
	    var med_user;
	    var max_count;
	    var yp;
        this.posts.forEach(function(post) {
	        if (!post.user_node) {
	            for (i = 0; i < post.users.length; i++) {
                    med_user = user_map[post.users[i]];
	                med_user.median_count += 1;
	            }
	        }
        });
        this.posts.forEach(function(post) {
            max_count = 0;
            post.x = _x(post.date);
            for (i = 0; i < post.users.length; i++) {
                med_user = user_map[post.users[i]];
                if (med_user.median_count > max_count)  {
                    max_count = med_user.median_count;
                    post.median_user = med_user;
                    yp = Math.max(_y(med_user.index), _my);
                    //console.log("_y(med_user.index) " + yp);
                    //post.y = (_h - _y(med_user.index));
                    post.y = (_h - yp);
                    //console.log("post.y " + post.y);
                }
            }
        });
    },
    
    generateLinks: function()  {
        this.links = [];
        var i, j;
        var user;
        var unode;
        for (i = 0; i < this.users.length; i++) {
            user = this.users[i];
            var user_posts = [];
            for (j = 0; j < this.posts.length; j++) {
                if (this.posts[j].has_user(user.id)) {
                    user_posts[user_posts.length] = this.posts[j];
                }
            }
            user.first_post = user_posts[0];
            for (j = 1; j < user_posts.length; j++) {
                this.links[this.links.length] = new NL.Link(
                                                    user_posts[j-1], 
                                                    user_posts[j],  
                                                    user.id);
                this.links[this.links.length-1].user_ptr = user;
                user_posts[j-1].out_links[user_posts[j-1].out_links.length] = 
                                            this.links[this.links.length-1];
                user_posts[j].in_links[user_posts[j].in_links.length] = 
                                                this.links[this.links.length-1];
            }
            if (user.first_post != null) {
                unode = this.user_nodes[i];
                var l = new NL.Link(
                                unode, 
                                user.first_post, 
                                user.id);
                l.user_ptr = user;
                unode.out_links[unode.out_links.length] = l;
                user.first_post.in_links[user.first_post.in_links.length] = l;
                this.links[this.links.length] = l;
                unode.first_post = user.first_post;
                user_posts[user_posts.length] = unode;
                unode.median_user = user.first_post.median_user;
            }
        }
    },
    
    
    getNamedUsers: function(post)   {
        var _um = this.user_map;
        var i, user;
        var named = [];
        
        for(i = 0; i < post.users.length; i++)   {
            user = _um[post.users[i]];
            if(user.first_post == post) {
                named.push(user);
            }
        }
        return named;
    },
    
    getMaxNameWidth: function(users)    {
        var w = 0;
        users.forEach(function(user) {
            var l = user.name.length*7.2;
            if(l > w)   {
                w = l;
            }
        });
        return w;
    },
    
    createNameAreas: function()   {
        var _gnu = this.getNamedUsers.bind(this);
        var _gmnw = this.getMaxNameWidth.bind(this);
        var _ns = this.nameShift;
        var _su = this.shiftUnit;
        var _us = this.userSpace;
        var _ml = -this.margin.left;
        
        this.posts.forEach(function(post) {
            var named = _gnu(post);
            var width = _gmnw(named);
            post.namebox = {
                h: named.length * _us,
                w: width,
                x: post.x - width - _ns - (_su * post.users.length),
                y: post.y
            };
        });
    },
    
    drawNameAreas: function()   {
        var _x = this.x;
        var _y = this.y;
        var _h = this.height;
        var _ho = this.hOffset;
        
        var node = this.svg.append("g").selectAll(".namebox")
            .data(this.posts)
            .enter().append("g")
            .attr("class", "namebox")
            .attr("transform", function(d) { 
                return "translate(" + 
                            d.namebox.x + "," + (d.namebox.y - _ho) + ")"; });
            
        node.append("rect")
            .attr("width", function(d) { return d.namebox.w; })
            .attr("height", function(d) { return d.namebox.h; })
            .style("fill", function(d) { return "#f00"; })
            .style("stroke", function(d) { return "#000"; })
            .style("opacity", "0.3");
            
        var node = this.svg.append("g").selectAll(".intbox")
            .data(this.intboxes)
            .enter().append("g")
            .attr("class", "intbox")
            .attr("transform", function(d) { 
                        return "translate(" + d.x + "," + (d.y - _ho) + ")"; });
            
        node.append("rect")
            .attr("width", function(d) { return d.w; })
            .attr("height", function(d) { return d.h; })
            .style("fill", function(d) { return "#0f0"; })
            .style("stroke", function(d) { return "#0f0"; })
            .style("fill-opacity", "0.3");
    },
    
    xIntersectBoxes: function(a, b)   {
        return this.intersect(a.x, a.w, b.x, b.w);
    },
    
    yIntersectBoxes: function(a, b)   {
        return this.intersect(a.y, a.h, b.y, b.h);
    },
    
    intersect: function(ap, ad, bp, bd)   {
        var ar = ad/2;
        var br = bd/2;
        var ac = ap + ar;
        var bc = bp + br;
        return Math.abs(bc - ac) <= Math.abs(ar + br);
    },
    
    boxBoxIntersect: function(a, b)  {
        return this.xIntersectBoxes(a,b) && this.yIntersectBoxes(a,b);
    },
    
    postBoxIntersect: function(post, box)  {
        return this.intersect(post.x, post.width, box.x, box.w) &&
                    this.intersect(post.y, post.height, box.y, box.h);
    },
    
    stretchIntBox: function(box, x, y, w, h)    {
        box.x = x < box.x ? x : box.x;
        box.y = y < box.y ? y : box.y;
        box.w = x+w > box.x + box.w ? x+w - box.x : box.w;
        box.h = y+h > box.y + box.h ? y+h - box.y : box.h;
    },
    
    overlappingNames: function()  {
        var i, j;
        var post, prev, prevb, box;
        var intbox;
        this.intboxes = []
        var miny = this.height;
        var minx = this.posts[0].namebox.x;
        var maxy = this.maxy;
        for (i=1; i < this.posts.length; i++)  {
            post = this.posts[i];
            box = post.namebox;
            intbox = {x:this.height, y:this.width, w:0, h:0};
            for (j=0; j < i; j++)  {
                prev = this.posts[j];
                prevb = prev.namebox;
                if (this.postBoxIntersect(prev, box)) {
                    this.stretchIntBox(
                            intbox, prev.x, prev.y, prev.width, prev.height);
                    if (post.y > this.medy) {
                        box.y = intbox.y + intbox.h + this.userSpace;
                    } else {
                        box.y = intbox.y - box.h - this.userSpace;
                    }
                }
                if (this.boxBoxIntersect(prevb, box)) {
                      this.stretchIntBox(
                                intbox, prevb.x, prevb.y, prevb.w, prevb.h);
                    if (post.y > this.medy) {
                        box.y = intbox.y + intbox.h + this.userSpace;
                    } else {
                        box.y = intbox.y - box.h - this.userSpace;
                    }
                }
            }
            minx = Math.min(box.x, minx);
            miny = Math.min(box.y, miny);
            maxy = Math.max(box.y+box.h, maxy);
            this.intboxes.push(intbox);
        }
        if(miny == this.height) {
            this.hOffset = 0;
        } else {
            this.hOffset = miny;
        }
        //this.height = maxy-miny;
        this.height = Math.max(this.fullHeight, maxy-miny);
        if (minx < 0)   {
            this.margin.left = Math.abs(Math.min(minx - 20, this.margin.left));
        }
        console.log("names minx: " + minx);
        console.log("names miny: " + miny);
        console.log("names maxy: " + maxy);
        console.log("names maxy-miny: " + (maxy-miny));
        console.log("names height: " + this.height);
        console.log("names hOffset: " + this.hOffset);
        console.log("names midy: " + this.midy);
        console.log("names medy: " + this.medy);
    },
    
    userNameOrder: function(user, post) {
        var i, other;
        var j = 0;
	    for (i = 0; i < post.in_links.length; i++) {
	        other = this.user_map[post.in_links[i].id];
	        if (user.id == post.in_links[i].id)    {
		        return j;
		    }
	        if (other.first_post == post)   {
	            j++;
	        }
	    }
	    return -1;
    },
    
    positionUserNodes: function()   {
        var i;
        var user, nb;
        
        for (i = 0; i < this.users.length; i++) {
            user = this.users[i];
            nb = user.first_post.namebox;
            this.user_nodes[i].x = nb.x + nb.w;
            this.user_nodes[i].y = nb.y + 
                  (this.userNameOrder(user, user.first_post) * this.userSpace);
        }
    },
    
    overlappingPosts: function()  {
        var i;
        var post, prev, newh;
        var miny = this.height;
        var maxy = 0;
        var pymin = 0;
        var pymax = 0;
        var key;
        var mkey;
        var y1, y2;
        var c = this.height;
        var len = this.posts.length;
        for (i=1; i < len; i++)  {
            prev = this.posts[i-1];
            post = this.posts[i];
            if(!post.user_node)    {
                if(post.x - prev.x < 20)  {
                    post.y = prev.y + prev.height;
                }
                newh = post.y + post.height;
                if (newh > this.height) {
                    this.height = newh;
                }
                if (newh > maxy) {
                    maxy = newh;
                }
                if (post.y < miny) {
                    miny = post.y;
                }
                pymin += post.y;
                pymax += newh;
            }
        }
        this.midy = miny + ((maxy-miny)/2);
        this.medy = miny + ((pymax-pymin)/len)/2;
        this.miny = miny;
        this.maxy = maxy;
        console.log("miny: " + miny);
        console.log("maxy: " + maxy);
        console.log("midy: " + this.midy);
        console.log("medy: " + this.medy);
    },
    
    calculateLinkPositions: function()    {
        var p;
        for (p = 0; p < this.posts.length; p++) {
            this.calculatePostLinks(this.posts[p]);
        }
        for (p = 0; p < this.user_nodes.length; p++) {
            this.calculatePostLinks(this.user_nodes[p]);
        }
    },
    
    calculatePostLinks: function(post)    {
        var i;
        for (i = 0; i < post.out_links.length; i++) {
            post.out_links[i].y0 = -1;
        }

        var j = 0;
        for (i = 0; i < post.in_links.length; i++) {
            post.in_links[i].y1 = post.y + 
                    i*(this.link_width+this.link_gap) + this.link_width/2.0;
            post.in_links[i].x1 = post.x + 0.5*post.width;
            
            if (j < post.out_links.length && 
                        post.out_links[j].id == post.in_links[i].id) {
                post.out_links[j].y0 = post.in_links[i].y1;
                j++;      
            }
        }

        for (i = 0; i < post.out_links.length; i++) {
            if (post.out_links[i].y0 == -1) {
                post.out_links[i].y0 = post.y + 
                    i*(this.link_width+this.link_gap) + this.link_width/2.0;
            }
            post.out_links[i].x0 = post.x + 0.5*post.width;
        }
    },
    
    // PRINT
    printLinks: function() {
        this.links.forEach(function(link) {
            var lstr = "LINK id: "+ link.id +
                " from: " + link.from.id +
                " to: " + link.to.id +
                " x0: " + link.x0 +
                " y0: " + link.y0 +
                " x1: " + link.x1 +
                " y1: " + link.y1 +
                " user_ptr: " + link.user_ptr.name;
            console.log(lstr);
        });
    },
    
    printPosts: function() {
        this.posts.forEach(function(post) {
            var lstr = "POST id: "+ post.id +
                " date: " + post.date +
                " x: " + post.x +
                " y: " + post.y;
            console.log(lstr);
        });
    },
    
    printUsers: function() {
        this.users.forEach(function(user) {
            var lstr = "USER: "+ user.name +
                " rgb: " + user.rgb +
                " id: " + user.id +
                " index: " + user.index +
                " first_post: " + user.first_post +
                " median_count: " + user.median_count +
                " order: " + user.order +
                " min: " + user.min +
                " max: " + user.max;
            console.log(lstr);
        });
    },

});
