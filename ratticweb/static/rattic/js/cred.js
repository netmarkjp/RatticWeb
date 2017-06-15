$("#reload-otp").on(
    "click", 
    function(ev){
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
    });
