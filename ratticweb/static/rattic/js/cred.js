var reloadOTP = function(ev){
        var url = window.location.origin + ev.currentTarget.attributes.dest.value
        fetch(url, {
            method: "GET",
            credentials: 'include'
        }).then(function(response) {
            return response.json();
        }, function(err){
            console.log(err);
        }).then(function(json){
            $("#otp").text(json.otp);
        });
};
$("#reload-otp-initial").on("click", reloadOTP);
$("#reload-otp").on("click", reloadOTP);

$("#qr_image_file").on("change", function(ev){
    console.log("start upload");
    var form = new FormData(document.getElementById("qr_image_file_form"));
    console.log(form.action);
    var url = window.location.origin + $("#qr_image_file_form").attr("action");
    fetch(url, {
        method: "POST",
        credentials: "include",
        body: form
    }).then(function(response) {
        return response.json();
    }, function(err){
        console.log(err);
    }).then(function(json){
        console.log("json");
        console.log(json);
        $("#id_two_factor_auth_secret").text(json.secret_key);
    });
    console.log("end upload");
});
$("#two_factor_auth_secret_qr_image_input").on("click", function(ev){
    $("#qr_image_file").click();
});
