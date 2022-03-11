// {#  Set Cookies with /user #}
function setCookie(cname, cvalue, exdays=365) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    var SameSite = "SameSite=Lax";
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/"+ ";" + SameSite;
}

    // {#  Get Cookies with /user #}
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "NewUser";
}

    // {#  Check if cookie is set #}
async function checkCookie() {
    var user = getCookie("CookieMonster");
    var nameToReturn = ''
    await $.ajax({
        type: "POST",
        url: "/user",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            token: user
        }),
        complete: function (data) {
            if (user !== "NewUser") {
                nameToReturn = "Hello Again, " + data.responseJSON.username;
                console.log("Hello Again, " + data.responseJSON.username);
            } else {
                setCookie("CookieMonster", data.responseJSON.token)
                nameToReturn = "Hello " + data.responseJSON.username;
                console.log("Hello, " + data.responseJSON.username);
            }
        }
    });
    return nameToReturn;
    }