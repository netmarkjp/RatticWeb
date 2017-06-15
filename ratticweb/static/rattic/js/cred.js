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
