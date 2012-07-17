var model = function(model, jQuery) {
////// visible ////////////////////////////////////////////////////////////////
    var visible = {};
    
    
    // pseudo constants ///////////////////////////////////////////////////////
    visible.ATTR_NAME = "__ATTR_NAME__";
    visible.ATTR_ROUTE = "__ATTR_ROUTE__";
    visible.ATTR_FREQUENCY = "__ATTR_FREQUENCY__";
    visible.ATTR_DOSAGE = "__ATTR_DOSAGE__";
    visible.ATTR_DRUG_CLASS = "__ATTR_DRUG_CLASS__";
    visible.ATTR_SUBITEM = "__ATTR_SUBITEM__";
    visible.ATTR_INSTRUCTIONS = "__ATTR_INSTRUCTIONS__";
    
    visible.ATTR_TYPE_NUMERIC = "__ATTR_TYPE_NUMERIC__";
    visible.ATTR_TYPE_GENERAL = "__ATTR_TYPE_GENERAL__";
    visible.ATTR_TYPE_CATEGORICAL = "__ATTR_TYPE_CATEGORICAL__";

    visible.DATASET_SAMPLE_JSON = "__DATASET_SAMPLE_JSON__";
    visible.DATASET_DEFAULT = visible.DATASET_SAMPLE_JSON;

    visible.AFTER_ACTION_GRAYOUT = "__AFTER_ACTION_GRAYOUT__";
    visible.AFTER_ACTION_REMOVE = "__AFTER_ACTION_REMOVE__";
    
    visible.FILTER_DELAY_SCALE = 4;
    
    
    // data ///////////////////////////////////////////////////////////////////
    visible.dataset = "";
    visible.items = {};
    
    visible.shadows = {};
    visible.itemsToShadows = {};
    visible.shadowsToItems = {};
    visible.hidden = {};
    
    visible.list1 = {
                id: "list0",
                name: "Intake",
                source: []
            };
    visible.list2 = {
                id: "list1",
                name: "Hospital",
                source: []
            };
    
    visible.viewData = function(sort, filter) {
        var viewData = visible.list1.source.concat(visible.list2.source);
        
        if (visible.multigroup && visible.groupBy) {
            for (var shadowID in visible.shadows) {
                var shadow = visible.shadows[shadowID];
                
                if (visible.groupBy in shadow.attributes &&
                        shadow.attributes[visible.groupBy].length > 1) {
                    viewData.push(shadowID);
                    
                    if (shadowID in visible.hidden) {
                        delete visible.hidden[shadowID];
                        visible.toggleItem($("#" + shadowID),
                                controller.toggleOnDelay, true);
                    }
                } else {
                    visible.toggleItem($("#" + shadowID),
                            controller.toggleOffDelay, false);
                    visible.hidden[shadowID] = true;
                }
            }
        } else {
            // no multigroup + groupBy = no shadows
            for (var shadowID in visible.shadows) {
                visible.toggleItem($("#" + shadowID),
                        controller.toggleOffDelay, false);
                visible.hidden[shadowID] = true;
            }
        }

        if (filter) {
            viewData = viewData.filter(unifiedFilter);
        }
        
        if (sort || filter) {
            viewData = viewData.sort(groupThenSort);
        }
        return viewData;
    }
    
    visible.attributes = {};

    visible.groupBy = "";
    visible.sortBy = "";
    visible.__defineGetter__("filterOn", function() {
        return filterOn;
    });
    visible.__defineSetter__("filterOn", function(value) {
        filterOn = value.toLowerCase();
    });
    visible.multigroup = false;
    
    visible.afterAction = visible.AFTER_ACTION_GRAYOUT;
    
    visible.unique1 = [];
    visible.unique2 = [];
    visible.identical = {};
    visible.similar = {};
    
    
    // methods ////////////////////////////////////////////////////////////////
    visible.loadData = function(data) {
        populateList("list1", data);
        populateList("list2", data);
        detectAttributes();
        detectRelationships(data);
        populateShadows();
    }
    
    visible.getIdentical = function(id) {
        var identical = [];
        
        if (id in visible.identical) {
            identical = visible.identical[id].slice();
        }
        identical.splice(identical.indexOf(parseFloat(id)), 1);
        
        return identical.filter(unifiedFilter);
    };
    
    visible.getSimilar = function(id) {
        var similar = [];
        
        if (id in visible.similar) {
            similar = visible.similar[id].items.slice();
        }
        similar.splice(similar.indexOf(parseFloat(id)), 1);

        return similar.filter(unifiedFilter);
    };
    
    visible.getRelated = function(id) {
        var identical = visible.getIdentical(id);
        var similar = visible.getSimilar(id);
        var hash = {};
        var length = Math.min(identical.length, similar.length); 
        
        // remove duplicates
        for (var i = 0; i < length; i++) {
            hash[identical[i]] = true;
            hash[similar[i]] = true;
        }
        
        if (length < identical.length) {
            for ( ; i < identical.length; i++) {
                hash[identical[i]] = true;
            }
        } else if (length < similar.length) {
            for ( ; i < similar.length; i++) {
                hash[similar[i]] = true;
            }
        }
        
        // convert results into array format
        var related = [];
        
        for (var hashedID in hash) {
            related.push(hashedID);
        }
        return related;
    };
    
    visible.getShadows = function(id) {
        if (id in visible.itemsToShadows) {
            return visible.itemsToShadows[id];
        }
        return [];
    };
    
    visible.getShadowed = function(id) {
        if (id in visible.shadowsToItems) {
            return visible.shadowsToItems[id];
        }
        return undefined;
    };
    
    visible.getVisibleShadows = function(id) {
        var visibleShadows = [];
        
        if (id in visible.itemsToShadows) {
            var shadows = visible.getShadows(id);
            
            for (var i = 0; i < shadows.length; i++) {
                var shadowID = shadows[i];
                var shadow = visible.items[shadowID];
                
                if (visible.hidden[shadowID] === undefined) {
                    visibleShadows.push(shadowID);
                }
            }
        }
        return visibleShadows;
    };
    
    
    visible.toggleItem = function($item, delay, show) {
        if (show) {
            if (visible.hidden[$item.attr("id")] === undefined) {
                $item.show();
                
                setTimeout(function() {
                    $item.css("opacity", "1");
                }, delay);
            }
        } else {
            setTimeout(function() {
                $item.css("opacity", "0");
                
                setTimeout(function() {
                    $item.hide();
                    $item.removeClass("undecided-hover item-hover");
                }, delay);
            }, delay);
        }
    };
    
    
////// hidden /////////////////////////////////////////////////////////////////
    var filterOn = "";
    
    // initialization
    function populateList(listName, data) {
        var listID, newList, dstList, medType;
        
        if (listName === "list1") {
            listID = visible.list1.id;
            newList = data.new_list_1;
            dstList = visible.list1.source;
            medType = "med1";
        } else {
            listID = visible.list2.id;
            newList = data.new_list_2;
            dstList = visible.list2.source;
            medType = "med2";
        }
        
        /*
         * The attribute breakdown for a given item is in one of two
         * lists: data.reconciled (if it's related to one or more items)
         * or data.newList (if it's unique to its original list).
         * 
         * Relevant item attributes: id, name, dose, units, and instructions.
         * Only id and name are required. Route, frequency, and drug class are
         * not provided.
         */
        for (var i = 0; i < data.reconciled.length; i++) {
            populateItem(data.reconciled[i][medType], listID, dstList);
        }
        
        for (var i = 0; i < newList.length; i++) {
            populateItem(newList[i], listID, dstList);
        }
    }
    
    function populateItem(med, listID, dstList) {
        var id = med.id;
        var attributes = {};
        var dosage = "";
        
        if ("dose" in med) {
            dosage = med.dose;
            
            if ("units" in med) {
                dosage += " " + med.units.toLowerCase();
            }
        }
        attributes[visible.ATTR_ROUTE] = "";
        attributes[visible.ATTR_FREQUENCY] = "";
        attributes[visible.ATTR_DOSAGE] = [dosage];
        attributes[visible.ATTR_DRUG_CLASS] = [""];
        attributes[visible.ATTR_INSTRUCTIONS] =
                ["instructions" in med ? med.instructions : ""];
        
        visible.items[id] = {
            listID: listID,
            id: id,
            name: med.medication_name
                    // strip all-cals
                    .toLowerCase()
                    // ensure first letter is capitalized
                    .replace(/^[a-z]/, function() {
                        return arguments[0].toUpperCase();
                    }),
            attributes: attributes
        };
        dstList.push(id);
    }
    
    function populateShadows() {
        for (var id in visible.items) {
            var item = visible.items[id];
            
            // originals will always be associated with the primary group
            item.groupByOffset = 0;
            
            // originals are not shadows, and currently have no shadows
            item.isShadow = false;
            item.isShadowed = false;
            
            // search for potential shadows
            for (var attributeName in visible.attributes) {
                var attribute = visible.attributes[attributeName];
                
                if (attribute.type === visible.ATTR_TYPE_CATEGORICAL) {
                    if (attributeName in item.attributes) {
                        var values = item.attributes[attributeName];
                        
                        if (values.length > 1) {
                            /*
                             * Prepare shadows; these "shadows" will only appear
                             * when the user groups by this particular
                             * attribute.
                             * 
                             * For group affiliation [ A, B, C ]:
                             *   - the original will be grouped with A,
                             *   - shadow 0 will be grouped with B, and
                             *   - shadow 1 will be grouped with C.
                             * 
                             * Acting on the original will act on all shadows;
                             * acting on a shadow will similarly act on the
                             * original (and all other shadows).
                             */
                            for (var i = 1; i < values.length; i++) {
                                // convention: originalID_shadowID
                                var shadowID = id + "_" + (i - 1);
                                
                                // create the shadow from the original
                                visible.shadows[shadowID] = {};
                                $.extend(true, visible.shadows[shadowID],
                                        visible.items[id]);
                                        
                                var shadow = visible.shadows[shadowID];
                                
                                shadow.id = shadowID;
                                shadow.isShadow = true;
                                shadow.isShadowed = false;
                                shadow.groupByOffset = i;
                                
                                // original now has a shadow
                                visible.items[id].isShadowed = true;
                                
                                // for convenience, hash in items as well
                                visible.items[shadowID] = {};
                                $.extend(visible.items[shadowID],
                                        visible.shadows[shadowID]);
                                        
                                // hash from original to shadow
                                if (id in visible.itemsToShadows) {
                                    visible.itemsToShadows[id].push(shadowID);
                                } else {
                                    visible.itemsToShadows[id] = [shadowID];
                                }
                                
                                // hash from shadow to original
                                visible.shadowsToItems[shadowID] = id;
                            }
                        }
                    }
                }
            }
        }
    }
    
    function detectAttributes() {
        visible.attributes[visible.ATTR_NAME] = {
                    type: visible.ATTR_TYPE_GENERAL,
                    display: true
                };
        visible.attributes[visible.ATTR_ROUTE] = {
                    type: visible.ATTR_TYPE_CATEGORICAL,
                    display: true
                };
        visible.attributes[visible.ATTR_FREQUENCY] = {
                    type: visible.ATTR_TYPE_GENERAL,
                    display: true
                };
        visible.attributes[visible.ATTR_DOSAGE] = {
                    type: visible.ATTR_TYPE_NUMERIC,
                    display: true
                };
        visible.attributes[visible.ATTR_DRUG_CLASS] = {
                    type: visible.ATTR_TYPE_CATEGORICAL,
                    display: false
                };
        visible.attributes[visible.ATTR_SUBITEM] = {
                    type: visible.ATTR_TYPE_GENERAL,
                    display: false
                };
        visible.attributes[visible.ATTR_INSTRUCTIONS] = {
                    type: visible.ATTR_TYPE_GENERAL,
                    display: false
                };
    }
    
    function detectRelationships(data) {
        var i, identical = [], similar = [];
        
        for (var i = 0; i < data.reconciled.length; i++) {
            var set = data.reconciled[i];
            
            // based on the information provided, only these can differ
            var differences = [visible.ATTR_NAME, visible.ATTR_DOSAGE]
            
            // add related sets
            if (set.mechanism === "Identical strings") {
                identical.push([set.med1.id, set.med2.id]);
            } else {
                var differences = [];
                
                if (!("DRUG_NAME" in set.identical)) {
                    differences.push(visible.ATTR_NAME);
                }
                
                if (set.med1.dose && !("DOSE" in set.identical)) {
                    differences.push(visible.ATTR_DOSAGE);
                }
                similar.push({
                    items: [set.med1.id, set.med2.id],
                    differences: differences
                });
            }
        }
        
        for (i = 0; i < identical.length; i++) {
            var set = identical[i];
            
            for (var j = 0; j < set.length; j++) {
                visible.identical[set[j]] = set;
            }
        }
        
        for (i = 0; i < similar.length; i++) {
            set = similar[i];
            
            for (j = 0; j < set.items.length; j++) {
                visible.similar[set.items[j]] = set;
            }
        }
        
        for (var i = 0; i < data.new_list_1.length; i++) {
            visible.unique1.push(data.new_list_1[i].id);
        }
        
        for (var i = 0; i < data.new_list_2.length; i++) {
            visible.unique2.push(data.new_list_2[i].id);
        }
    }
    
    
    // sort
    function groupThenSort(a, b) {
        var groupOrder = visible.groupBy ?
                attributeSort(a, b, visible.groupBy) : 0;
        
        if (groupOrder === 0) {
            var sortOrder = visible.sortBy ?
                    attributeSort(a, b, visible.sortBy) :
                    visible.items[a].id - visible.items[b].id;
                    
            if (visible.sortBy && sortOrder === 0) {
                return visible.items[a].id - visible.items[b].id;
            }
            return sortOrder;
        }
        return groupOrder;
    }
    
    function attributeSort(a, b, attribute) {
        var itemA = visible.items[a];
        var itemB = visible.items[b];
        var attributeA, attributeB;
        
        if (attribute === visible.ATTR_NAME) {
            attributeA = itemA.name;
            attributeB = itemB.name;
        } else {
            attributeA = itemA.attributes[attribute][
                    (visible.multigroup ? itemA.groupByOffset : 0)];
            attributeB = itemB.attributes[attribute][
                    (visible.multigroup ? itemB.groupByOffset : 0)];
        }
        
        if (visible.attributes[attribute].type === visible.ATTR_TYPE_NUMERIC) {
            attributeA = parseFloat(attributeA);
            attributeB = parseFloat(attributeB);
        }
        
        if (attributeA < attributeB) {
            return -1;
        } else if (attributeA > attributeB) {
            return 1;
        } else {
            return 0;
        }
    }
    
    
    // filter
    function actionFilter(element, index, array) {
        var $item = $("#" + element);
        
        if (visible.afterAction === visible.AFTER_ACTION_REMOVE &&
                !$item.hasClass("undecided")) {
            return false;
        }
        return true;
    }
    
    function nameFilter(element, index, array) {
        var $item = $("#" + element);
        
        if (visible.filterOn.length > 0 &&
                visible.items[element].name.toLowerCase()
                .indexOf(visible.filterOn) === -1) {
            return false;
        }
        return true;
    }
    
    function unifiedFilter(element, index, array) {
        var keep = actionFilter(element, index, array);
        
        if (keep) {
            keep = nameFilter(element, index, array);
        }
        visible.toggleItem($("#" + element), keep ?
                controller.toggleOnDelay * visible.FILTER_DELAY_SCALE :
                controller.toggleOffDelay / visible.FILTER_DELAY_SCALE,
                keep);
        return keep;
    }
    
    
    // expose interface ///////////////////////////////////////////////////////
    return visible;
}(window.model = window.model || {}, $, undefined);
