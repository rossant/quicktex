LS_NAME = "quicktex-list";


function utoa(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}


function getTitle () {
    return $("#textarea").val().split('\n')[0].substring(1);
}


function currentItem () {
    return $("#list-items .active");
}


function currentCode () {
    return $("#textarea").val();
}


function getList () {
    var l = JSON.parse(localStorage.getItem(LS_NAME));
    if (!l) l = {};
    return l;
}


function setList (l) {
    localStorage.setItem(LS_NAME, JSON.stringify(l));
}


function addToList (key, val) {
    var l = getList();
    l[key] = val;
    setList(l);
}


function getItem (title) {
    for (let child of $("#list-items").children()) {
        if (child.text() == title) {
            return child;
        }
    }
}


function saveCurrent () {
    var title = getTitle();
    var text = currentCode();

    if (!select(title)) {
        currentItem().text(title);
    }

    addToList(title, text);
};


function load (title) {
    var text = getList()[title];
    $("#textarea").val(text);
}


function loadAll () {
    var l = getList();
    for (let title in l) {
        var text = l[title];
        $("#list-items").append('<a href="#" class="list-group-item list-group-item-action">' + title + '</a>');
    }
}


function select (title) {
    for (let child of $("#list-items a")) {
        child = $(child);
        if (child.text() == title) {
            currentItem().removeClass("active");
            child.addClass("active");
            load(title);
            return true;
        }
    }
}


function run () {
    var text = currentCode();
    var b64 = utoa(text);
    var url = "/latex/" + b64;
    $("#img").attr("src", url);

    var getUrl = window.location;
    var baseUrl = getUrl.protocol + "//" + getUrl.host;

    copyToClipboard("file:///home/cyrille/git/quicktex/sony/output.svg");
    saveCurrent();

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
    loadAll();

    $("#list-items a").on("click", function (e) {
        e.preventDefault();
        select($(this).text());
    });

    $('#textarea').keydown(function (event) {
        if ((event.keyCode == 10 || event.keyCode == 13) && event.ctrlKey) {
            run();
        }
    });
});
