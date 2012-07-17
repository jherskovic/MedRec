var controller = function(controller, jQuery) {
////// visible ////////////////////////////////////////////////////////////////
    var visible = {};
    
    
    // animation speed ////////////////////////////////////////////////////////
    visible.animationSpeed = 0;
    visible.animationDuration = 0;
    visible.animationDelay = 0;
    visible.toggleOnDelay = 0;
    visible.toggleOffDelay = 0;
    
    
    // methods ////////////////////////////////////////////////////////////////
    visible.init = function() {
        // fetch data to display
        viewData = model.viewData(true, true);

        // prepare interface
        populateDOM();
        prepareTransitions();
        prepareHandlers();
        
        setAnimationSpeed(utils.getStorageItem("animationSpeed") ||
                ANIMATION_SPEED_3);

        // browser-specific css oddity
        if ($.browser.mozilla) {
            $("#content td").css("height", "3.5em");
        }
        
        // nothing has been processed yet
        for (var id in model.items) {
            linkAction[id] = true;
        }

        // indicate current dataset
        var dataset = utils.getStorageItem("dataset");

        if (dataset) {
            $("#dataset").val(dataset);
        } else {
            $("#dataset").val(model.DATASET_DEFAULT);
        }
        redraw();
    };
    
    
// hidden /////////////////////////////////////////////////////////////////////    
    
    // pseudo constants ///////////////////////////////////////////////////////
    var LIST_1_UNIQUE_INDEX = 0;
    var LIST_1_INDEX = 1;
    var LIST_IDENTICAL_INDEX = 2;
    var LIST_2_INDEX = 3;
    var LIST_2_UNIQUE_INDEX = 4;
    var NUM_ROWS = {};
    var NUM_COLUMNS = 5;

    var STATE_SEPARATE = 0;
    var STATE_IDENTICAL = 1;
    var STATE_UNIQUE = 2;
    var STATE_SIMILAR = 3;
    var STATE_COMPACT = 4;
    var NUM_STATES = 5;
    
    var BASE_ANIMATION_DURATION = 800;
    var ANIMATION_SPEED_0 = "__ANIMATION_SPEED_0__";
    var ANIMATION_SPEED_1 = "__ANIMATION_SPEED_1__";
    var ANIMATION_SPEED_2 = "__ANIMATION_SPEED_2__";
    var ANIMATION_SPEED_3 = "__ANIMATION_SPEED_3__";
    var ANIMATION_SPEED_4 = "__ANIMATION_SPEED_4__";
    var ANIMATION_SPEED_5 = "__ANIMATION_SPEED_5__";
    var ANIMATION_SPEED_COEFFICIENTS = [0, 1.5, 1.25, 1, 0.75, 0.5];

    var WHITE = "#ffffff";
    var NEUTRAL_GRAY = "#f5f5f5";
    var CONTRAST_GRAY = "#dedbd5";
    
    
    // data ///////////////////////////////////////////////////////////////////
    var viewData = [];

    var headers = [];
    var previousHeader = "";
    var currentHeader = "";

    var state = STATE_SEPARATE;
    var positions = {};
    var keyframes = {};
    
    var linkAction = {};
    var done = false;
    
    
    // initialization /////////////////////////////////////////////////////////
    function prepareTransitions() {
        // calculate column positions exactly once; they won't change
        calculateColumns();

        // row positions, however, will
        calculatePositions();
    }

    function populateDOM() {
        var $container = $("#content");

        populateBackdrop($container);
        populateItems($container);
        populateScrolltips($("#scrolltips"));       // for positioning freedom
        
        // start shadowing
        $(".shadow").hide();
    }

    function populateItems($container) {
        // prepare item container
        var $items = $("<div></div>");
        $items.attr("class", "items");

        // populate all items and all shadows
        for (var id in model.items) {
            var item = model.items[id];
            var differences = [];

            var $div = $("<div></div>");
            $div.attr("id", id);
            $div.attr("class", "undecided");
            
            if (item.isShadow) {
                $div.addClass("shadow");
            }

            var $span = $("<span></span>");
            $span.attr("class", "item-name");
            $span.text(item.name);

            if (id in model.similar) {
                differences = model.similar[id].differences;

                if (differences.indexOf(model.ATTR_NAME) != -1) {
                    $span.addClass("difference");
                }
            }
            $div.append($span);
            $div.append("<br />");

            for (var attribute in item.attributes) {
                if (model.attributes[attribute].display) {
                    $span = $("<span></span>");
                    $span.text(item.attributes[attribute].toString());

                    if (id in model.similar) {
                        if (differences.indexOf(attribute) != -1) {
                            $span.addClass("difference");
                        }
                    }
                    $div.append($span);
                }
            }
            $items.append($div);
        }
        $container.append($items);
    }

    function populateBackdrop($container) {
        // prepare column headers and empty cells
        var $table = $("<table></table>");
        var $thead = $("<thead></thead>");

        for (var i = 0; i < NUM_COLUMNS; i++) {
            var $th = $("<th></th>");
            var $accept = $("<a></a>");
            $accept.attr("href", "#");
            $accept.attr("class", "accept-all");
            $accept.text("accept");
            $accept.click({
                index : i,
                accept : true
            }, processRemaining);

            var $reject = $("<a></a>");
            $reject.attr("href", "#");
            $reject.attr("class", "reject-all");
            $reject.text("reject");
            $reject.click({
                index : i,
                accept : false
            }, processRemaining);

            var $span = $("<span></span>");

            switch (i) {
                case LIST_1_UNIQUE_INDEX:
                    $span.text(model.list1.name + " unique");
                    break;
                case LIST_1_INDEX:
                    $span.text(model.list1.name);
                    break;
                case LIST_IDENTICAL_INDEX:
                    $span.text("Identical");
                    break;
                case LIST_2_INDEX:
                    $span.text(model.list2.name);
                    break;
                case LIST_2_UNIQUE_INDEX:
                    $span.text(model.list2.name + " unique");
                    break;
            }
            $th.append($span);
            $th.append("<br />");
            $th.append($accept);
            $th.append("<span>/</span>");
            $th.append($reject);
            $th.append("<span> remaining</span>");
            $thead.append($th);

            // by default, only list 1 and list 2 are visible
            if (i % 2 === 0) {
                toggleHeader($th, false);
            } else {
                toggleHeader($th, true);
            }
        }
        $table.append($thead);

        // plug table with empty placeholders (default height is a heuristic)
        var $tbody = $("<tbody></tbody>");

        for (i = 0; i < NUM_COLUMNS * 2; i++) {
            var $tr = $("<tr></tr>");

            for (var j = 0; j < NUM_COLUMNS; j++) {
                $tr.append("<td></td>");
            }
            $tbody.append($tr);
        }
        $table.append($thead);
        $table.append($tbody);
        $container.append($table);

        // add container for header labels
        var $div = $("<div></div>");
        $div.attr("id", "header-labels");
        $container.append($div);
    }

    function populateScrolltips($container) {
        // tell users to look up
        var $up = $("<div></div>");
        $up.attr("id", "up");
        $up.attr("class", "scrolltip");

        // tell users to look down
        var $down = $("<div></div>");
        $down.attr("id", "down");
        $down.attr("class", "scrolltip");

        $container.append($up);
        $container.append($down);
    }

    function prepareHandlers() {
        // item interaction
        $(".items > div").mousedown(clickHandler)
                .mouseover(mouseoverHandler)
                .mouseout(mouseoutHandler)
                .bind("contextmenu", function() {
                    // free right click for item action
                    return false;
                });
        
        // help modal
        $(".help-modal").css("top", $("header").height());

        $("#help").click(function() {
            $(".help-modal").addClass("show");
        });

        $(".help-close").click(function() {
            $(".help-modal .welcome").remove();
            $(".help-modal").removeClass("show");
        });
        
        // alert modal
        $("#alert-close").click(function() {
            $(".alert-modal").removeClass("show");
        });
        
        // options panel
        $("#options-panel").hide();

        $("#options").click(function() {
            var $options = $("#options");

            if ($options.hasClass("selected")) {
                $options.removeClass("selected");
                $("#options-panel").slideUp("fast", function() {
                    redraw(true, true, true);
                });
            } else {
                $options.addClass("selected");
                $("#options-panel").slideDown("fast", function() {
                    redraw(true, true, true);
                });
            }
        });

        $("#dataset").change(function() {
            if ($(this).val() !== model.dataset) {
                utils.setStorageItem("dataset", $(this).val());
                location.reload();
            }
        });

        $("#groupBy").change(function() {
            model.groupBy = $(this).val();

            // force; grouping in compact looks strange
            if (state > STATE_SIMILAR) {
                state = STATE_SIMILAR;
            }

            if ($(this).val().length === 0) {
                if (visible.animationSpeed === ANIMATION_SPEED_0) {
                    $("#similar").addClass("inactive");
                } else {
                    $("#similar").removeClass("inactive");
                }
                $("#compact").removeClass("inactive");
            } else {
                $("#similar").removeClass("inactive");
                $("#compact").addClass("inactive");
            }
            redraw(true, true);
        });
        
        $("#multigroup").click(function() {
            model.multigroup = $("#multigroup:checked").length === 0 ?
                false : true;
            redraw(true, true);
        });

        $("#sortBy").change(function() {
            model.sortBy = $(this).val();
            redraw(true, true);
        });

        $("#filterOn").keyup(function() {
            model.filterOn = $(this).val();
            redraw(true, true);
        });

        $("#separate").click(function() {
            changeState(STATE_SEPARATE);
        });

        $("#identical").click(function() {
            changeState(STATE_IDENTICAL);
        });

        $("#unique").click(function() {
            changeState(STATE_UNIQUE);
        });

        $("#similar").click(function() {
            changeState(STATE_SIMILAR);
        });

        $("#compact").click(function() {
            if (!model.groupBy) {
                changeState(STATE_COMPACT);
            }
        });

        $("#grayout").click(function() {
            if (!$(this).hasClass("selected")) {
                $("#remove").removeClass("selected");
                $(this).addClass("selected");

                model.afterAction = model.AFTER_ACTION_GRAYOUT;
                redraw(true, true);
            }
        });

        $("#remove").click(function() {
            if (!$(this).hasClass("selected")) {
                $("#grayout").removeClass("selected");
                $(this).addClass("selected");

                model.afterAction = model.AFTER_ACTION_REMOVE;
                redraw(true, true);
            }
        });
        
        // basic controls
        $("#compare").click(function() {
            changeState(STATE_COMPACT);
        });

        $("#confirm").click(function() {
            signoff();
        });
        
        // retry (reset + don't ignore cache)
        $("#retry").click(function() {
            location.reload();
        });
        $("#logo").click(function() {
            location.reload();
        });

        // resize with window
        $(window).resize(function() {
            redraw(true, true, true);
        });
        
        // hidden animation toggle
        $(window).keydown(function(event) {
            switch (event.which) {
                case 48:                            // the '0' key
                    setAnimationSpeed(ANIMATION_SPEED_0);
                    break;
                case 49:                            // the '1' key
                    setAnimationSpeed(ANIMATION_SPEED_1);
                    break;
                case 50:                            // the '2' key
                    setAnimationSpeed(ANIMATION_SPEED_2);
                    break;
                case 51:                            // the '3' key
                    setAnimationSpeed(ANIMATION_SPEED_3);
                    break;
                case 52:                            // the '4' key
                    setAnimationSpeed(ANIMATION_SPEED_4);
                    break;
                case 53:                            // the '5' key
                    setAnimationSpeed(ANIMATION_SPEED_5);
                    break;
            }
        });
    }
    
    
    // event listeners ////////////////////////////////////////////////////////
    function mouseoverHandler() {
        var id = $(this).attr("id");
        var item = model.items[id];
        
        // hover appropriate items
        hoverItem(id, true);
        hoverRelated(id, true);
        hoverScrolltips(id, true);
        
        if (item.isShadow) {
            var shadowed = model.getShadowed(id);
            
            hoverShadowed(id, true);
            hoverShadows(shadowed, true);
            hoverRelated(shadowed, true);
        } else if (item.isShadowed) {
            hoverShadows(id, true);
        }

        // update item detail
        var $detail = $("#detail td:last-child");
        var fullDescription = item.name + " | ";

        for (var attributeName in model.attributes) {
            if (attributeName in item.attributes) {
                var values = item.attributes[attributeName];
                var valuesString = "";

                if (values.length > 1) {
                    var values = item.attributes[attributeName];

                    for (var i = 0; i < values.length; i++) {

                        if (attributeName === model.ATTR_SUBITEM) {
                            var subitem = values[i];
                            valuesString += subitem.name + " (" +
                                    subitem.attributes[model.ATTR_DOSAGE] +
                                    ")";
                        } else {
                            valuesString += values[i];
                        }
                        valuesString += ", ";
                    }
                    valuesString = valuesString.slice(0, -2);
                } else {
                    valuesString = values.toString();
                }
                
                if (valuesString.trim() !== "") {
                    fullDescription += valuesString + " | ";
                }
            }
        }
        fullDescription = fullDescription.slice(0, -3);
        $detail.text(fullDescription);
    }

    function mouseoutHandler() {
        var id = $(this).attr("id");
        var item = model.items[id];
        
        hoverItem(id, false);
        hoverRelated(id, false);
        hoverScrolltips(id, false);
        
        if (item.isShadow) {
            var shadowed = model.getShadowed(id);
            
            hoverShadowed(id, false);
            hoverShadows(shadowed, false);
            hoverRelated(shadowed, false);
        } else if (item.isShadowed) {
            hoverShadows(id, false);
        }

        $("#detail td:last-child").text("Nothing to display.");
    }

    function clickHandler(event) {
        var dst;

        // TODO: very useful for debugging, keep until final ship
        console.log($(this).attr("id"));
        console.log(model.items[$(this).attr("id")]
                .attributes[model.ATTR_DRUG_CLASS]);

        if (event.which === 1) {                // left click
            if ($(this).hasClass("undecided")) {
                dst = "accepted";
            } else if ($(this).hasClass("accepted")) {
                dst = "rejected";
            } else if ($(this).hasClass("rejected")) {
                dst = "undecided";
            }
        } else if (event.which === 3) {         // right click
            if ($(this).hasClass("undecided")) {
                dst = "rejected";
            } else if ($(this).hasClass("accepted")) {
                dst = "undecided";
            } else if ($(this).hasClass("rejected")) {
                dst = "accepted";
            }
        }

        if (dst) {
            processItem($(this).attr("id"), dst);
        }
    }

    function hoverItem(id, mouseover) {
        var item = model.items[id];
        var $item = $("#" + id);

        if (mouseover) {
            $item.addClass("item-hover");
            $item.css("opacity", "1");

            if ($item.hasClass("undecided")) {
                $item.addClass("undecided-hover");
            }
        } else {
            $item.removeClass("item-hover");

            if ($item.hasClass("undecided")) {
                $item.removeClass("undecided-hover");
            }
        }
    }

    function hoverRelated(id, mouseover) {
        var related = (state < STATE_IDENTICAL) ? model.getRelated(id) :
                model.getSimilar(id);

        for (var i = 0; i < related.length; i++) {
            var relatedID = related[i];
            var relatedItem = model.items[relatedID];

            hoverItem(relatedID, mouseover);
            
            if (relatedItem.isShadowed) {
                hoverShadows(relatedID, mouseover);
            }
        }
    }
    
    function hoverShadows(id, mouseover) {
        if (model.items[id].isShadowed) {
            var shadows = model.getShadows(id);
            
            for (var i = 0; i < shadows.length; i++) {
                hoverItem(shadows[i], mouseover);
            }
        }
    }
    
    function hoverShadowed(id, mouseover) {
        if (model.items[id].isShadow) {
            hoverItem(model.getShadowed(id), mouseover);
        }
    }

    function hoverScrolltips(id, mouseover) {
        $("div.scrolltip").removeClass("scrolltip-pop");

        if (mouseover) {
            // gather set of relevant items
            var item = model.items[id];
            var related = model.getRelated(id);
            var checkItems = {};
            
            if (item.isShadow) {
                var shadowed = model.getShadowed(id);
                
                related.push(shadowed);
                related = related.concat(model.getRelated(shadowed));
            } else if (item.isShadowed) {
                related = related.concat(model.getVisibleShadows(id));
            }
            
            for (var i = 0; i < related.length; i++) {
                var relatedID = related[i];
                
                if (model.items[relatedID].isShadowed) {
                    related = related.concat(
                            model.getVisibleShadows(relatedID));
                }
            }
            
            // remove duplicates
            for (var i = 0; i < related.length; i++) {
                checkItems[related[i]] = true;
            }
            
            // check set of relevant items
            var numObscured = {
                "neither" : 0,
                "above" : 0,
                "below" : 0
            };
            
            for (var id in checkItems) {
                numObscured[isOffscreen(id)]++;
            }
            
            if (numObscured["above"] > 0) {
                $("#up").text("...more (" + numObscured["above"] + ")");
                $("#up").addClass("scrolltip-pop");
            }
            
            if (numObscured["below"] > 0) {
                $("#down").text("...more (" + numObscured["below"] + ")");
                $("#down").addClass("scrolltip-pop");
            }
        }
    }
    
    function isOffscreen(id) {
        var status = "neither";
        var $content = $("#content");
        var divHeight = $(".items div").outerHeight();
        var topEdge = $content.scrollTop();
        var bottomEdge = topEdge + $content.outerHeight();
        var position = done ?
            offsetToPosition(id) :
            offsetToPosition(positions[id][state]);
            
        if ((position.y + divHeight) < topEdge ||
                topEdge > (position.y + divHeight * 0.75)) {
            status = "above";
        } else if (position.y > bottomEdge ||
                    (position.y + divHeight * 0.25) > bottomEdge) {
            status = "below";
        }
        return status;
    }
    
    
    // item action ////////////////////////////////////////////////////////////
    function processItem(id, dst) {
        // act on shadow = act on item
        actOnSet(model.items[id].isShadow ? model.getShadowed(id) : id, dst);
    }
    
    function actOnSet(id, dst) {
        var identical = model.getIdentical(id);
        var similar = model.getSimilar(id);
        
        // always link actions on identical sets
        for (var i = 0; i < identical.length; i++) {
            actOnItem(identical[i], dst === "accepted" ? "rejected" : dst);
        }
        
        // only link actions on similar sets for the first click
        if (linkAction[id] && similar.length > 0) {
            for (var i = 0; i < similar.length; i++) {
                /*
                 * The first click either accepts or rejects an item. Only one
                 * one member of a set may be accepted at a time; therefore,
                 * no matter the first click, all but one member of a set will
                 * be rejected.
                 */
                actOnItem(similar[i], "rejected");
            }
            
            if (dst === "rejected") {
                var related = model.getRelated(id);
                var next = related[0];
                
                if (next in model.identical) {
                    // ensure that next is always visible
                    next = model.identical[next][0];
                }
                actOnItem(next, "accepted");
            }
        }
        actOnItem(id, dst);
    }
    
    function actOnItem(id, dst) {
        // act on item
        decide(id, dst);
        
        // act on shadows
        var shadows = model.getShadows(id);
        
        for (var i = 0; i < shadows.length; i++) {
            decide(shadows[i], dst);
        }
    }
    
    function decide(id, dst) {
        var $item = $("#" + id);
        var checkID = model.items[id].isShadow ? model.getShadowed(id) : id;
        
        $item.removeClass("accepted rejected undecided undecided-hover");
        
        if (dst === "undecided") {
            $item.addClass("undecided-hover");
            
            if (state >= STATE_SIMILAR) {
                $item.children(".difference").addClass("highlight");
            }
        } else {
            $item.children(".difference").removeClass("highlight");
        }
        $item.addClass(dst);
        
        /*
         * Actions on members of identical sets are always linked.
         * 
         * Only the first action on a similar set is linked.
         */
        linkAction[id] = checkID in model.identical ? true : false;
    }

    function processRemaining(event) {
        var col = keyframes[state][event.data.index];

        for (var i = 0; i < col.length; i++) {
            var ids = col[i];
            
            for (var j = 0; j < ids.length; j++) {
                var id = ids[j];
                var dst = (event.data.accept) ? "accepted" : "rejected";
                
                if ($("#" + id).hasClass("undecided")) {
                    processItem(id, dst);
                }
            }
        }
    }
    
    
    // state and animation ////////////////////////////////////////////////////
    function redraw(sort, filter, immediate) {
        // tweak proportions
        $("#content").height($(window).height() - $("header").height() -
                $("#options-panel").height() - $("#detail").height() -
                $("footer").height());
        $("footer img").css("height", $("header").height() * 0.75);
        $("#detail").css("marginTop", $("#content").outerHeight(true));
        
        adjustScrolltips();

        if (immediate) {
            viewData = model.viewData(sort, filter);
            calculatePositions();

            $(".items div").each(function() {
                animateItem($(this).attr("id"), state,
                        visible.animationDelay / 4);
            });
        } else if (done) {
            // redraw final 2-column view
            $(".items div").css("opacity", "1");

            $(".items div").each(function() {
                animateItem($(this).attr("id"));
            });
        } else {
            viewData = model.viewData(sort, filter);
            calculatePositions();
            changeState(state);
        }
    }

    function changeState(toState) {
        if (state === toState) {
            transition(state, state);
        } else {
            if (model.groupBy && toState > STATE_SIMILAR) {
                // grouping doesn't make sense in STATE_COMPACT
                toState = STATE_SIMILAR;
            }
            
            if (visible.animationSpeed === ANIMATION_SPEED_0) {
                if (toState === STATE_SEPARATE) {
                    // hide headers
                    var $header = $("#content th:nth-child(" +
                            (LIST_1_INDEX + 1) + ")");
                    $header.children("span:first-child")
                            .text(model.list1.name);
                    $header = $("#content th:nth-child(" +
                            (LIST_2_INDEX + 1) + ")");
                    $header.children("span:first-child")
                            .text(model.list2.name);
                            
                    for (var i = 0; i < NUM_COLUMNS; i = i + 2) {
                        var $header = $("#content th:nth-child(" +
                                (i + 1) + ")");
                        toggleHeader($header, false);
                    }
                    $(".difference").removeClass("highlight");
                } else {
                    toState = model.groupBy ?
                            STATE_SIMILAR : STATE_COMPACT;
                            
                    // show headers
                    var $header = $("#content th:nth-child(" +
                            (LIST_1_INDEX + 1) + ")");
                    $header.children("span:first-child")
                            .text(model.list1.name + " similar");
                    $header = $("#content th:nth-child(" +
                            (LIST_2_INDEX + 1) + ")");
                    $header.children("span:first-child")
                            .text(model.list2.name + " similar");
                            
                    for (var i = 0; i < NUM_COLUMNS; i = i + 2) {
                        var $header = $("#content th:nth-child(" +
                                (i + 1) + ")");
                        toggleHeader($header, true);
                    }
                    $(".undecided").children(".difference")
                            .addClass("highlight");
                }
                
                // no animation, jump to destination state
                transition(toState, toState);
            } else {
                var offset = (state < toState) ? 1 : -1;
                var i = state;
                
                while (i !== toState) {
                    transition(state, i + offset);
                    i += offset;
                }
            }
            state = toState;
        }
        $("#separate, #identical, #unique, #similar, #compact")
                .removeClass("selected");

        // indicate destination state
        switch (state) {
            case STATE_SEPARATE:
                $("#separate").addClass("selected");
                break;
            case STATE_IDENTICAL:
                $("#identical").addClass("selected");
                break;
            case STATE_UNIQUE:
                $("#unique").addClass("selected");
                break;
            case STATE_SIMILAR:
                $("#similar").addClass("selected");
                break;
            case STATE_COMPACT:
                $("#compact").addClass("selected");
                break;
        }
    }

    function transition(from, to) {
        var delay = 0;
        var offset = Math.abs(to - from);

        if (from < to) {
            delay = transitionTime(state, to - 1);
        } else if (from > to) {
            delay = transitionTime(state, to + 1);
        }

        setTimeout(function() {
            // adjust table height
            adjustBackdrop(to);

            // adjust headers
            adjustHeaders(from, to);

            // update row background colors
            $("#content td").css("background", "");
            
            var $tbody = $("#content tbody");
            var height = $tbody.children().length;

            for (var i = 0; i < height; i++) {
                $tbody.children(":nth-child(" + (i + 1) + ")")
                        .css("background", "");
            }

            if (model.groupBy) {
                var color = WHITE;

                for (var i = 0; i < headers.length; i++) {
                    var header = headers[i];
                    var start = "thresholdRowStart";
                    var end = "thresholdRowEnd";
                    var threshold = STATE_SIMILAR;

                    for (var j = 0; j < header.items.length; j++) {
                        var id = header.items[j];

                        if (positions[id].threshold < threshold) {
                            threshold = positions[id].threshold;
                        }
                    }

                    if (state < threshold) {
                        start = "initialRowStart";
                        end = "initialRowEnd";
                    }

                    if (header.hasOwnProperty(start) &&
                            header.hasOwnProperty(end)) {
                        for (var j = header[start]; j < header[end]; j++) {
                            $tbody.children(":nth-child(" + (j + 1) + ")")
                                    .css("background", color);
                        }
                        color = (color === WHITE) ? NEUTRAL_GRAY : WHITE;
                    }
                }
            } else if (to === STATE_COMPACT) {
                // paint white first
                $("#content td").css("background", WHITE);
                
                // block unique and identical
                var height = Math.max(model.unique1.length,
                        model.unique2.length,
                        keyframes[to][LIST_IDENTICAL_INDEX].length);
                var block = [LIST_1_UNIQUE_INDEX, LIST_2_UNIQUE_INDEX,
                        LIST_IDENTICAL_INDEX];
                
                for (var i = 0; i < height; i++) {
                    for (var j = 0; j < block.length; j++) {
                        $tbody.children(":nth-child(" + (i + 1) + ")")
                                .children(":nth-child(" +
                                (block[j] + 1) + ")")
                                .css("background", NEUTRAL_GRAY);
                    }
                }
                
                // stripe similar
                var color = CONTRAST_GRAY;
                var col = keyframes[to][LIST_1_INDEX];
                var striped = {};
                
                for (var i = 0; i < col.length; i++) {
                    var ids = col[i];
                    
                    for (var j = 0; j < ids.length; j++) {
                        var id = ids[j];
                        
                        if (id !== undefined &&
                                striped[id] === undefined) {
                            // color single item
                            var pos = positions[id][to];
                            
                            $tbody.children(":nth-child(" +
                                    (pos.row + 1) + ")")
                                    .children("td")
                                    .css("background", color);
                            striped[id] = true;
                            
                            // color related items accordingly
                            var related = model.getRelated(id);
                            
                            for (var j = 0; j < related.length; j++) {
                                id = related[j];
                                pos = positions[id][to];
                                
                                $tbody.children(":nth-child(" +
                                        (pos.row + 1) + ")")
                                        .children("td")
                                        .css("background", color);
                                striped[id] = true;
                            }
                            color = color === WHITE ?
                                    CONTRAST_GRAY : WHITE;
                        }
                    }
                }
            } else {
                // stripe rows for legibility
                for (var i = 0; i < height; i++) {
                    if (i % 2 !== 0) {
                        $tbody.children(":nth-child(" + (i + 1) + ")")
                                .css("background", NEUTRAL_GRAY);
                    }
                }
            }

            // animate column headers
            if (from < to) {
                switch (to) {
                    case STATE_IDENTICAL:
                        var header = $("#content th:nth-child(" +
                                (LIST_IDENTICAL_INDEX + 1) + ")");
                        toggleHeader(header, true);
                        break;
                    case STATE_UNIQUE:
                        var header = $("#content th:nth-child(" +
                                (LIST_1_UNIQUE_INDEX + 1) + ")");
                        toggleHeader(header, true);
                        header = $("#content th:nth-child(" +
                                (LIST_2_UNIQUE_INDEX + 1) + ")");
                        toggleHeader(header, true);
                        header = $("#content th:nth-child(" +
                                (LIST_1_INDEX + 1) + ")");
                        header.children("span:first-child")
                                .text(model.list1.name + " similar");
                        header = $("#content th:nth-child(" +
                                (LIST_2_INDEX + 1) + ")");
                        header.children("span:first-child")
                                .text(model.list2.name + " similar");
                        break;
                    case STATE_SIMILAR:
                        var header = $("#content th:nth-child(" +
                                (LIST_1_INDEX + 1) + ")");
                        header = $("#content th:nth-child(" +
                                (LIST_2_INDEX + 1) + ")");

                        $(".undecided").children(".difference")
                                .addClass("highlight");
                        break;
                }
            } else {
                switch (to) {
                    case STATE_SEPARATE:
                        var header = $("#content th:nth-child(" +
                                (LIST_IDENTICAL_INDEX + 1) + ")");

                        for (var i = 0; i < NUM_COLUMNS; i++) {
                            var header = $("#content th:nth-child(" +
                                    (i + 1) + ")");

                            if (i % 2 == 0) {
                                toggleHeader(header, false);
                            } else {
                                toggleHeader(header, true);
                            }
                        }
                        break;
                    case STATE_IDENTICAL:
                        var header = $("#content th:nth-child(" +
                                (LIST_1_UNIQUE_INDEX + 1) + ")");
                        toggleHeader(header, false);
                        header = $("#content th:nth-child(" +
                                (LIST_2_UNIQUE_INDEX + 1) + ")")
                        toggleHeader(header, false);

                        var header = $("#content th:nth-child(" +
                                (LIST_1_INDEX + 1) + ")");
                        header.children("span:first-child")
                                .text(model.list1.name);
                        header = $("#content th:nth-child(" +
                                (LIST_2_INDEX + 1) + ")");
                        header.children("span:first-child")
                                .text(model.list2.name);
                        header = $("#content th:nth-child(" +
                                (LIST_IDENTICAL_INDEX + 1) + ")");
                        toggleHeader(header, true);
                        break;
                    case STATE_UNIQUE:
                        var header = $("#content th:nth-child(" +
                                (LIST_1_INDEX + 1) + ")");
                        header = $("#content th:nth-child(" +
                                (LIST_2_INDEX + 1) + ")");

                        $(".difference").removeClass("highlight");
                        break;
                }
            }

            // animate items
            if (to > from) {
                if (to === STATE_IDENTICAL) {
                    animateIdentical(to);
                } else if (to === STATE_UNIQUE) {
                    animateUnique(to);
                } else {
                    animateDefault(to);
                }
            } else {
                animateDefault(to);
            }
        }, delay);
    }

    function animateIdentical(toState) {
        var i = 0;
        var checked = {}, animated = {};

        for (var id in model.identical) {
            if (checked[id] === undefined) {
                var set = model.identical[id];
                
                for (var j = 0; j < set.length; j++) {
                    var checkID = set[j];
                    
                    if (model.items[checkID].isShadowed) {
                        set = set.concat(model.getShadows(checkID));
                    }
                }
                checked[id] = true;

                for (var j = 0; j < set.length; j++) {
                    checked[set[j]] = true;
                }
                animateSet(set, toState, (i > 0) ?
                        (i * visible.animationDuration) +
                        (i * visible.animationDelay) : 0, animated);
                i++;
            }
        }
    }

    function animateUnique(toState) {
        var unique1 = model.unique1, unique2 = model.unique2;
        
        for (var i = 0; i < model.unique1.length; i++) {
            var id = model.unique1[i];
            var item = model.items[id];
            
            if (item.isShadowed) {
                unique1 = unique1.concat(model.getShadows(id));
            }
        }
        
        for (var i = 0; i < model.unique2.length; i++) {
            var id = model.unique2[i];
            var item = model.items[id];
            
            if (item.isShadowed) {
                unique1 = unique1.concat(model.getShadows(id));
            }
        }
        
        // animate left first, then right
        animateSet(unique1, toState, 0)
        animateSet(unique2, toState, visible.animationDuration +
                visible.animationDelay);
    }

    function animateDefault(toState) {
        $(".items div").each(function() {
            animateItem($(this).attr("id"), toState);
        });
    }

    function animateSet(set, toState, delay, animated) {
        setTimeout(function() {
            for (var i = 0; i < set.length; i++) {
                var id = set[i];

                if (animated) {
                    if (animated[id] === undefined) {
                        animated[id] = true;
                        animateItem(id, toState);
                    }
                } else {
                    animateItem(id, toState);
                }
            }
        }, delay);
    }

    function animateItem(id, toState, duration) {
        var $item = $("#" + id);
        var position = (toState !== undefined) ?
                offsetToPosition(positions[id][toState]) :
                offsetToPosition(positions[id]);

        $item.animate({
            "left" : position.x,
            "top" : position.y
        }, {
            duration : duration ? duration : visible.animationDuration,
            easing : "easeInOutCubic"
        });
        
        // handle identical overlap
        if (id in model.identical) {
            if (state < STATE_IDENTICAL) {
                if (id in model.hidden) {
                    delete model.hidden[id];
                    model.toggleItem($item, visible.toggleOnDelay, true);
                }
            } else {
                if (model.identical[id].indexOf(parseFloat(id)) !== 0) {
                    model.hidden[id] = true;
                    model.toggleItem($item, visible.toggleOffDelay, false);
                }
            }
        }
    }

    function toggleHeader($header, show) {
        $header.children().toggle(show);
    }

    function topOffset() {
        return $("#content th").outerHeight(true);
    }

    function columnWidth() {
        return $("#content td").outerWidth(true);
    }

    function rowHeight() {
        var $td = $("#content td");
        var td = $td.height();
        var padding = parseFloat($td.css("paddingTop")) +
                parseFloat($td.css("paddingBottom"));

        return td + padding;
    }

    function offsetToPosition(offset) {
        return {
            x : offset.col * columnWidth(),
            y : (offset.row * rowHeight()) + topOffset()
        };
    }

    function transitionTime(from, to) {
        var delay = 0;

        if (from < to) {
            for (i = from + 1; i <= to; i++) {
                if (i === STATE_IDENTICAL) {
                    delay += transitionIdenticalTime();
                } else if (i === STATE_UNIQUE) {
                    delay += 2 * (visible.animationDuration +
                            visible.animationDelay);
                } else {
                    delay += visible.animationDuration +
                            visible.animationDelay;
                }
            }
        } else if (from > to) {
            for (i = from; i >= to + 1; i--) {
                delay += visible.animationDuration + visible.animationDelay;
            }
        }
        return delay;
    }

    function transitionIdenticalTime() {
        var numSets = 0;
        var checked = {};

        for (var id in model.identical) {
            if (checked[id] === undefined) {
                var set = model.getIdentical(id);
                checked[id] = true;

                for (var j = 0; j < set.length; j++) {
                    checked[set[j]] = true;
                }
                numSets++;
            }
        }
        return (numSets * visible.animationDuration) +
                (numSets * visible.animationDelay);
    }
    
    function setAnimationSpeed(speed) {
        // adjust speed
        visible.animationSpeed = speed;
        utils.setStorageItem("animationSpeed", speed);
        
        // by default, intermediate states are active
        $("#identical").removeClass("inactive");
        $("#unique").removeClass("inactive");
        $("#similar").removeClass("inactive");
        
        if (speed === ANIMATION_SPEED_0) {
            // no animation = no intermediate states
            $("#identical").addClass("inactive");
            $("#unique").addClass("inactive");
            
            if (!model.groupBy) {
                $("#similar").addClass("inactive");
            }
        }
        
        if (speed === ANIMATION_SPEED_0) {
            // use neutral (median) animation speed for single transition
            visible.animationDuration = BASE_ANIMATION_DURATION *
                    ANIMATION_SPEED_COEFFICIENTS[
                        Math.floor(ANIMATION_SPEED_COEFFICIENTS.length / 2)
                        ];
        } else {
            var coefficient = speed.replace(/[^0-5]+/g, "");
            visible.animationDuration = BASE_ANIMATION_DURATION *
                    ANIMATION_SPEED_COEFFICIENTS[coefficient];
        }
        
        // adjust delays accordingly
        visible.animationDelay = visible.animationDuration * 0.75;
        visible.toggleOnDelay = visible.animationDelay / 4;
        visible.toggleOffDelay = visible.animationDelay * 0.95;
    }
    
    
    // position calculation ///////////////////////////////////////////////////
    function calculateColumns() {
        for (var id in model.items) {
            var checkID = id;
            var checkItem = model.items[id];
            var side = (checkItem.listID === model.list1.id) ? -1 : 1;
            var threshold = STATE_UNIQUE;
            var initialCol = Math.floor(NUM_COLUMNS / 2) + side;
            var finalCol = initialCol + side;
            
            if (checkItem.isShadow) {
                // calculate column based on original
                checkID = model.getShadowed(id);
            }

            if (checkID in model.similar) {
                threshold = STATE_SIMILAR;
                finalCol = initialCol;
            }

            if (checkID in model.identical) {
                threshold = STATE_IDENTICAL;
                finalCol = Math.floor(NUM_COLUMNS / 2);

                /*
                 * If all members of an identical set belong to the same list,
                 * simply merge them; the middle column is reserved for items
                 * that are identical among both lists.
                 */
                var identical = model.getIdentical(checkID);

                for (var j = 0; j < identical.length; j++) {
                    if (model.items[identical[j]].listID !==
                                checkItem.listID) {
                        break;
                    }
                }

                if (j === identical.length) {
                    finalCol = initialCol;

                    // TODO: hack, should really support STATE_IDENTICAL

                    threshold = STATE_SIMILAR;
                }
            }
            positions[id] = {
                threshold : threshold,
                initialCol : initialCol,
                finalCol : finalCol
            };
        }
    }

    function calculatePositions() {
        // clear rows
        for (var i = 0; i < viewData.length; i++) {
            var position = positions[viewData[i]];

            if (position.hasOwnProperty("initialRow")) {
                delete position.initialRow;
            }

            if (position.hasOwnProperty("thresholdRow")) {
                delete position.thresholdRow;
            }

            if (position.hasOwnProperty("finalRow")) {
                delete position.finalRow;
            }
        }

        // (re-)calculate
        calculateRows();
        calculateKeyframes();
        
        /*
         * Shadow originals even when hidden; shadows should appear to
         * spawn from, and disappear into, their shadowed (original) items.
         */
        for (var id in model.shadows) {
            var item = model.items[id];
            var position = positions[id];
            var shadowedPosition = positions[model.getShadowed(id)];
            
            if (id in model.hidden) {
                $.extend(true, position, shadowedPosition);
            }
        }
    }

    function calculateRows() {
        var initialRows = [0, 0];
        var thresholdRows = [], finalRows = [];
        var bumped = [];

        for (var i = 0; i < NUM_COLUMNS; i++) {
            thresholdRows.push(0);
            finalRows.push(0);
        }

        // reset headers
        headers = [];
        currentHeader = "";
        previousHeader = "";

        for (i = 0; i < viewData.length; i++) {
            var id = viewData[i];
            var position = positions[id];

            // impose group restriction on spatial position
            if (model.groupBy) {
                previousHeader = currentHeader;
                currentHeader = model.items[id].attributes[model.groupBy]
                        [model.items[id].groupByOffset];

                if (currentHeader.toLowerCase() !==
                        previousHeader.toLowerCase()) {
                    var row = Math.max(initialRows[0], initialRows[1]);
                    initialRows[0] = row;
                    initialRows[1] = row;

                    var thresholdRow = thresholdRows[0];
                    var finalRow = finalRows[0];

                    for (var j = 1; j < NUM_COLUMNS; j++) {
                        thresholdRow = Math.max(thresholdRow,
                                thresholdRows[j]);
                        finalRow = Math.max(finalRow, finalRows[j]);
                    }

                    for (j = 0; j < NUM_COLUMNS; j++) {
                        thresholdRows[j] = thresholdRow;
                        finalRows[j] = finalRow;
                    }

                    if (previousHeader.length > 0) {
                        var previous = headers[headers.length - 1];

                        previous.initialRowEnd = row;
                        previous.thresholdRowEnd = thresholdRow;
                    }
                    headers.push({
                        label : currentHeader,
                        initialRowStart : row,
                        thresholdRowStart : thresholdRow,
                        items : [id]
                    });
                } else {
                    headers[headers.length - 1].items.push(id);
                }
            }
            position.initialRow = (model.items[id].listID === model.list1.id) ?
                    initialRows[0]++ :
                    initialRows[1]++;
            calculateRow(id, "thresholdRow", thresholdRows);
            calculateRow(id, "finalRow", finalRows, bumped);
        }

        // re-align bumped-down items
        var height = Math.max(finalRows[LIST_1_UNIQUE_INDEX],
                finalRows[LIST_1_INDEX], finalRows[LIST_IDENTICAL_INDEX],
                finalRows[LIST_2_INDEX], finalRows[LIST_2_UNIQUE_INDEX]);

        for (i = 0; i < NUM_COLUMNS; i++) {
            finalRows[i] = height;
        }

        for (i = 0; i < bumped.length; i++) {
            calculateRow(bumped[i], "finalRow", finalRows);
        }

        if (model.groupBy && headers.length > 0) {
            var header = headers[headers.length - 1];

            header.initialRowEnd = Math.max(initialRows[0], initialRows[1]);
            header.thresholdRowEnd = Math.max(
                    thresholdRows[LIST_1_UNIQUE_INDEX],
                    thresholdRows[LIST_1_INDEX],
                    thresholdRows[LIST_IDENTICAL_INDEX],
                    thresholdRows[LIST_2_INDEX],
                    thresholdRows[LIST_2_UNIQUE_INDEX]);
            header.finalRowEnd = height;
        }
    }

    function calculateRow(id, type, rows, bumped) {
        var position = positions[id];
        var identical = model.getIdentical(id);
        var similar = model.getSimilar(id);
        var bump = false;

        // row already calculated
        if (position.hasOwnProperty(type)) {
            return;
        }

        // bump similar items down
        if (bumped) {
            if (id in model.similar) {
                bump = true;
            } else if (id in model.identical) {
                for (var i = 0; i < identical.length; i++) {
                    if (identical[i] in similar) {
                        bump = true;
                        break;
                    }
                }
            }
        }

        if (bump) {
            bumped.push(id);

            return;
        }

        // position self
        position[type] = rows[position.finalCol];

        // position identical items
        for (i = 0; i < identical.length; i++) {
            var relatedPosition = positions[identical[i]];

            if (!relatedPosition.hasOwnProperty(type)) {
                relatedPosition[type] = position[type];
            }
        }

        // position similar items
        rows[position.finalCol]++;

        for (i = 0; i < similar.length; i++) {
            relatedPosition = positions[similar[i]];

            if (!relatedPosition.hasOwnProperty(type)) {
                if (model.groupBy) {
                    if (model.items[similar[i]]
                            .attributes[model.groupBy][0] === currentHeader) {
                        relatedPosition[type] =
                                rows[relatedPosition.finalCol]++;
                    }
                } else {
                    relatedPosition[type] = rows[relatedPosition.finalCol]++;
                }
            }
        }

        // re-align
        if (type === "thresholdRow") {
            var height = Math.max(rows[LIST_1_UNIQUE_INDEX],
                    rows[LIST_1_INDEX], rows[LIST_IDENTICAL_INDEX],
                    rows[LIST_2_INDEX], rows[LIST_2_UNIQUE_INDEX]);

            for (i = 0; i < NUM_COLUMNS; i++) {
                rows[i] = height;
            }
        } else {
            var height = Math.max(rows[LIST_1_INDEX],
                    rows[LIST_IDENTICAL_INDEX], rows[LIST_2_INDEX]);

            for (i = LIST_1_INDEX; i <= LIST_2_INDEX; i++) {
                rows[i] = height;
            }
        }
    }

    function calculateKeyframes() {
        keyframes = {};

        for (var i = 0; i < NUM_STATES; i++) {
            keyframes[i] = [];
            NUM_ROWS[i] = 0;

            for (var j = 0; j < NUM_COLUMNS; j++) {
                keyframes[i][j] = [];
            }
        }

        for (i = 0; i < viewData.length; i++) {
            var id = viewData[i];
            var position = positions[id];
            var col;

            // initial position
            for (j = 0; j < position.threshold; j++) {
                position[j] = {
                    row : position.initialRow,
                    col : position.initialCol
                };
                col = keyframes[j][position.initialCol];
                
                if (col[position.initialRow] === undefined) {
                    col[position.initialRow] = [];
                }
                col[position.initialRow].push(id);
                NUM_ROWS[j] = Math.max(NUM_ROWS[j], position.initialRow + 1);
            }

            // threshold position
            for (; j < STATE_COMPACT; j++) {
                position[j] = {
                    row : position.thresholdRow,
                    col : position.finalCol
                };
                col = keyframes[j][position.finalCol];
                
                if (col[position.thresholdRow] === undefined) {
                    col[position.thresholdRow] = [];
                }
                col[position.thresholdRow].push(id);
                NUM_ROWS[j] = Math.max(NUM_ROWS[j], position.thresholdRow + 1);
            }

            // final (compact) position
            position[j] = {
                row : position.finalRow,
                col : position.finalCol
            };
            col = keyframes[j][position.finalCol];
            
            if (col[position.finalRow] === undefined) {
                col[position.finalRow] = [];
            }
            col[position.finalRow].push(id);
            NUM_ROWS[j] = Math.max(NUM_ROWS[j], position.finalRow + 1);
        }
        
        // set empty cells to [] rather than undefined
        var height = Math.max(NUM_ROWS[LIST_1_UNIQUE_INDEX],
                NUM_ROWS[LIST_1_INDEX],
                NUM_ROWS[LIST_IDENTICAL_INDEX],
                NUM_ROWS[LIST_2_INDEX],
                NUM_ROWS[LIST_2_UNIQUE_INDEX]);
        
        for (i = 0; i < NUM_STATES; i++) {
            for (j = 0; j < NUM_COLUMNS; j++) {
                var col = keyframes[i][j];
                
                for (var k = 0; k < height; k++) {
                    if (col[k] === undefined) {
                        col[k] = [];
                    }
                } 
            }
        }
    }
    
    function adjustBackdrop(toState) {
        var $tbody = $("#content > table > tbody");
        var currentHeight = $tbody.children("tr").length;
        var newHeight = NUM_ROWS[toState];

        if (currentHeight < newHeight) {
            var difference = newHeight - currentHeight;

            for (var i = 0; i < difference; i++) {
                var $tr = $("<tr></tr>");

                for (var j = 0; j < NUM_COLUMNS; j++) {
                    $tr.append("<td></td>");
                }
                $tbody.append($tr);
            }
        } else if (currentHeight > newHeight) {
            for (var i = currentHeight; i > newHeight; i--) {
                $tbody.children(":nth-child(" + i + ")").remove();
            }
        }
    }

    function adjustHeaders(from, to) {
        $("#header-labels span").remove();
        adjustCellPadding();

        if (model.groupBy) {
            for (var i = 0; i < headers.length; i++) {
                var header = headers[i];
                var row = header.thresholdRowStart;
                var $span = $("<span></span>");
                var threshold = STATE_SIMILAR;

                for (var j = 0; j < header.items.length; j++) {
                    var id = header.items[j];

                    if (positions[id].threshold < threshold) {
                        threshold = positions[id].threshold;
                    }
                }

                if (state < threshold) {
                    row = header.initialRowStart;
                }
                $span.attr("class", "header-label");
                $span.text(header.label[0].toUpperCase() +
                        header.label.slice(1));
                $span.css("left", 0);
                $span.css("top", topOffset() + (row * rowHeight()));
                $("#header-labels").append($span);
            }
        }
    }

    function adjustCellPadding() {
        if (model.groupBy) {
            $(".items div").css("paddingTop", "0.9em");
            $(".items div").css("paddingBottom", "0.1em");
            $(".items div").css("paddingLeft", "0.5em");
            $(".items div").css("paddingRight", "0.5em");
        } else {
            $(".items div").css("paddingTop", "0.6em");
            $(".items div").css("paddingBottom", "0.4em");
            $(".items div").css("paddingLeft", "0.5em");
            $(".items div").css("paddingRight", "0.5em");
        }
    }

    function adjustScrolltips() {
        var top = topOffset() + ($("#options").hasClass("selected") ?
                $("#options-panel").height() : 0);
        var bottom = top + $("#content").height() -
                ($("#content td").outerHeight(true) * 0.3);
        
        // hand-tweaked positions, adjust as appropriate
        $("#up").css("top", top);
        $("#down").css("top", bottom);
        $("#up, #down").css("right", $(window).width() * 0.05);
    }
    
    
    // closure ////////////////////////////////////////////////////////////////
    function signoff() {
        var errorMessage = checkCompletion();
        
        if (errorMessage.length > 0) {
            $(".alert-modal p").empty();
            $(".alert-modal p").append(errorMessage);
            $(".alert-modal").addClass("show");
            
            return;
        }

        // reset necessary components
        model.filterOn = "";
        model.sortBy = model.ATTR_NAME;     // adhere to customary default sort
        model.groupBy = "";
        model.afterAction = model.AFTER_ACTION_GRAYOUT;
        model.hidden = {};
        state = -1;                         // states now obsolete
        viewData = model.viewData(true, true);

        // gather accepted / rejected items
        var accepted = [], rejected = [];

        for (var i = 0; i < viewData.length; i++) {
            var id = viewData[i];
            var $item = $("#" + id);

            if ($item.hasClass("accepted")) {
                accepted.push(id);
            } else {
                rejected.push(id);
            }
        }

        // calculate final positions
        var row = 0;

        for (var i = 0; i < accepted.length; i++) {
            positions[accepted[i]] = {
                row : row++,
                col : 0
            };
        }
        row = 0;

        for (i = 0; i < rejected.length; i++) {
            positions[rejected[i]] = {
                row : row++,
                col : 1
            };
        }

        // remove defunct controls
        $("#options-panel").slideUp();
        
        $("header li ul").remove();
        $("header ul").append("<ul></li>" +
                '<a href="#" id="retry">start over?</a></li></ul>');
        
        $("#retry").click(function() {
            location.reload();
        });
        
        $("#content table").remove();
        $("#header-labels").remove();
        
        $("div .scrolltip").remove();
        $("div .shadow").remove();
        
        $(".items > div").unbind("mousedown");
        $(".items > div").unbind("contextmenu");
        
        model.groupBy = "";

        // prepare backdrop
        adjustCellPadding();
        
        var $container = $("#content");
        var $table = $("<table></table>");
        var $thead = $("<thead></thead>");
        var $th = $("<th></th>");
        $th.text("Accepted");
        $thead.append($th);
        $th = $("<th></th>");
        $th.text("Rejected");
        $thead.append($th);

        $table.append($thead);

        var $tbody = $("<tbody></tbody>");
        var height = Math.max(accepted.length, rejected.length);

        for (var i = 0; i < height; i++) {
            var $tr = $("<tr></tr>");
            $tr.append("<td></td><td></td>");
            $tbody.append($tr);
        }
        $table.append($tbody);
        $container.append($table);

        // truncate to two columns, preserving old column width
        $table.width("40%");
        $("#detail table").width("40%");

        // stripe rows for legibility
        for (i = 0; i < $tbody.children().length; i++) {
            if (i % 2 === 0) {
                $tbody.children(":nth-child(" + (i + 1) + ")")
                        .css("background", NEUTRAL_GRAY);
            }
        }

        // provide some semblance of closure
        var $button = $("<button></button>");
        $button.attr("id", "signoff");
        $button.text("Sign off");
        $container.append("<br />");
        $container.append($button);

        $("#signoff").click(function() {
            var $message = $(".alert-modal p");
            $message.empty();

            var $p = $("<p></p>");
            $p.append("<h4>The final reconciled list has been submitted.<h4>");
            $message.append($p);
            $p = $("<p></p>");
            $p.append("At this point, the demo is complete. If you'd like " +
                    " to try again, please click " +
                    "<strong><a href='#' id='signoff_reset'>start over?</a>" +
                    "</strong> to reset the interface.");
            $message.append($p);

            $("#signoff_reset").click(function() {
                location.reload()(true);
            });
            $(".alert-modal").addClass("show");
        });
        
        // prepare patient summary
        $button = $("<button></button>");
        $button.attr("id", "summary");
        $button.text("View patient summary");
        $container.append($button);
        
        $("#summary").click(function() {
            saveItemActions();
            window.open("summary.html");
        });
        
        // ensure all necessary items are visible
        $(".items div").css("z-index", "100")
        
        // reposition items
        redraw();
    }
    
    function checkCompletion() {
        // if there are still undecided items, can't sign off
        var left = 0, checked = {};
        
        for (var id in model.items) {
            if (model.items[id].isShadow || id in checked) {
                continue;
            }
            var $item = $("#" + id);
            checked[id] = true;
            
            if ($item.hasClass("undecided")) {
                if (state > STATE_SEPARATE) {
                    // at this point, they appear to be one item
                    var identical = model.getIdentical(id);
                    
                    for (var i = 0; i < identical.length; i++) {
                        checked[identical[i]] = true;
                    }
                }
                left++;
            }
        }
        
        if (left > 0) {
            return "Hold on, there " +
                    (left > 1 ? "are" : "is") + " still <strong>" + left +
                    "</strong> drug" + (left > 1 ? "s" : "") + " left!";
        }
        done = true;
        
        return "";
    }
    
    function saveItemActions() {
        var stop = "", start = "", cont = "";
        
        for (var id in model.items) {
            var item = model.items[id];
            
            if (item.isShadow) {
                continue;
            }
            var $item = $("#" + id);
            var frequency = item.attributes[model.ATTR_FREQUENCY].toString();
            
            // expand abbreviations
            frequency = frequency.replace(/w/i, " weeks");
            frequency = frequency.replace(/h/i, " hours");
            frequency = frequency.replace(/B\.?I\.?D\.?/i, "two times as day");
            frequency = frequency.replace(/T\.?I\.?D\.?/i,
                    "three times a day");
            frequency = frequency.replace(/Q\.?I\.?D\.?/i, "four times a day");
            frequency = frequency.replace(/q/i, "every ");
            
            var itemString = item.name + "\t" + frequency + "\t" +
                    item.attributes[model.ATTR_DOSAGE] + "\n";
            
            if (item.listID === model.list1.id && $item.hasClass("accepted")) {
                cont = cont + itemString;
            } else if (item.listID === model.list1.id &&
                    $item.hasClass("rejected")) {
                stop = stop + itemString;
            } else if (item.listID === model.list2.id &&
                    $item.hasClass("accepted")) {
                start = start + itemString;
            }
        }
        stop = stop.trimRight();
        start = start.trimRight();
        cont = cont.trimRight();
        
        utils.setStorageItem("stop", stop);
        utils.setStorageItem("start", start);
        utils.setStorageItem("continue", cont);
    }
    
    
    // expose interface ///////////////////////////////////////////////////////
    return visible;
}(window.controller = window.controller || {}, $, undefined);
