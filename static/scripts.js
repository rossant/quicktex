LS_NAME = "quicktex-list";


function utoa(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}


function getTitle () {
    return $("#title-form").val();
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


function deleteFromList (key) {
    var l = getList();
    delete l[key];
    setList(l);
}


function getListItem (title) {
    for (let child of $("#list-items").children()) {
        if (child.text() == title) {
            return child;
        }
    }
}


function loadAll () {
    var l = getList();
    console.debug("Loading all items from local storage.")
    for (let title in l) {
        var text = l[title];
        $("#list-items").append('<a href="#" class="list-group-item list-group-item-action">' + title + '</a>');
    }
    select(Object.keys(l)[0]);
}


function setDefaultList () {
    if (count() > 0) { return; }
    console.debug("Setting default list.")
    addToList('untitled', 'Hello world!');
}


function select (title) {
    for (let child of $("#list-items a")) {
        child = $(child);
        if (child.text() == title) {
            console.debug("Selecting", title);
            currentItem().removeClass("active");
            child.addClass("active");
            $("#textarea").val(getList()[title]);
            $("#title-form").val(title);
            run();
            return true;
        }
    }
}


function titles () {
    return Object.keys(getList());
}


function count () {
    return titles().length;
}


function saveCurrent () {
    var title = getTitle();
    var text = currentCode();
    console.debug("Saving", title);
    addToList(title, text);
    currentItem().text(title);
};


function deleteCurrent () {
    if (count() == 0) { return; }
    var title = getTitle();
    log.debug("Delete", title);
    deleteFromList(title);
    $("#list-items a.active").remove();
    select(titles()[0]);
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
    setDefaultList();
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
