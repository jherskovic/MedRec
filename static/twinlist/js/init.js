$(function() {
    // fetch data, prep interface
    model.dataset = utils.getStorageItem("dataset");
    var jsonSource = utils.qs["json_src"];
    
    //if (model.dataset === model.DATASET_SAMPLE_JSON) {
    //    jsonSource = "/json/sample.json";
    //}
    
    $.getJSON(jsonSource, function(data) {
        model.loadData(data);
        controller.init();
        
        // introduce the demo once and only once
        if (!utils.getStorageItem("hide_welcome")) {
            $(".help-modal").addClass("show");
            utils.setStorageItem("hide_welcome", "true", 1);
        } else {
            $(".help-modal").children(".welcome").hide();
        }
    });
});
