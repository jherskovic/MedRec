$(function() {
    populateTable("stop");
    populateTable("start");
    populateTable("continue");
});

function populateTable(name) {
    var list = utils.getStorageItem(name);
    
    if (list.length > 0) {
        var $body = $("body");
        var $header = $("<h3>Please " + name + " taking </h3>");
        var $table = $("<table></table>");
        $table.attr("id", name);
        
        var medications = list.split("\n");
        
        for (var i = 0; i < medications.length; i++) {
            var $tr = $("<tr></tr>");
            var attributes = medications[i].split("\t");
            
            for (var j = 0; j < attributes.length; j++) {
                $tr.append("<td>" + attributes[j] + "</td>");
            }
            $table.append($tr);
        }
        $body.append($header);
        $body.append($table);
    }
}
