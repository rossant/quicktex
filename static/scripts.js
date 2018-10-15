LS_NAME = "quicktex-list";


function utoa(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}


function currentItem () {
    return $("#list-items .active");
}


function currentTitle () {
    return $("#title-form").val();
}


function currentCode () {
    return $("#textarea").val();
}


function getListItem (title) {
    for (let child of $("#list-items").children()) {
        if (child.text() == title) {
            return child;
        }
    }
}


function save () {
    var title = currentTitle();
    var text = currentCode();
    console.debug("Saving", title);
    $.ajax({
        url: '/images/' + title,
        type: 'POST',
        data: {
            content: text
        },
        success: function (response) {
            select(title);
        }
    });
}


function remove () {
    if (count() == 0) { return; }
    var title = currentTitle();
    log.debug("Delete", title);
    $.ajax({
        url: '/images/' + title,
        type: 'DELETE',
        success: function (response) {
            $("#list-items a.active").remove();
            select(titles()[0]);
        }
    });
}


function loadAll () {
    $.get('/images', function (data) {
        var images = data["images"];
        console.debug("Loading all items.")
        for (let title of images) {
            $("#list-items").append('<a href="#" class="list-group-item list-group-item-action">' + title + '</a>');
        }
        select(images[0]);
    });
}


function select (title) {
    for (let child of $("#list-items a")) {
        child = $(child);
        if (child.text() == title) {
            console.debug("Selecting", title);
            currentItem().removeClass("active");
            child.addClass("active");

            $("#title-form").val(title);
            var url = '/images/' + title;
            $("#img").attr("src", url);
            $.get(url + '/code', function (data) {
                $("#textarea").val(data["response"]);
            });
        }
    }
}


function run () {
    var title = currentTitle()
    var text = currentCode();
    save();
    copyToClipboard("file:///home/cyrille/git/quicktex/.cache/" + title + ".svg");
    $("#textarea").focus()

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
