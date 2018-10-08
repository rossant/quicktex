function utoa(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}


function run () {
    var text = $("#textarea").val();
    var b64 = utoa(text);
    var url = "/latex/" + b64;
    $("#img").attr("src", url);

    var getUrl = window.location;
    var baseUrl = getUrl.protocol + "//" + getUrl.host;

    download("data:image/gif;base64," + b64, "file.svg", "image/svg+xml");

    $("#textarea").focus();
};


function copyToClipboard(text){
    var dummy = document.createElement("input");
    document.body.appendChild(dummy);
    dummy.setAttribute('value', text);
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
}


window.addEventListener('load', function() {
    $('#textarea').keydown(function (event) {
        if ((event.keyCode == 10 || event.keyCode == 13) && event.ctrlKey) {
            run();
        }
    });
});
