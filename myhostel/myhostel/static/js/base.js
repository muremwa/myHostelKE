$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});


// overview
var b = document.getElementsByTagName('body')[0];
var over = document.querySelector(".over-view");
var overImg = document.querySelector('#over-view-image');
var mainImg = document.querySelector("#big-image");
var ima;
var pos;
var maxI;
var di;

$(document).on('click', '.close-js-over', function () {
    over.style.display = 'none';
    b.style.height = "";
    b.style.overflow = "scroll";
})

function changeBigImage (i) {
    var path = mainImg.src;
    mainImg.src = i.src;
    i.src = path;
}

function enlargeImages (i) {
    document.getElementsByTagName('nav')[0].scrollIntoView();
    b.style.height = '100vh';
    b.style.overflow = 'hidden';
    di = document.querySelector('.danger-image');
    ima = allImages();
    for (image in ima) {
        if (i.src == ima[image]) {
            pos = ima.indexOf(ima[image]);
        }
    }
    overImg.src = i.src;
    over.style.display = "";
}

$(document).on('click', '.over-js-img', function () {
    if (window.innerWidth < 700) {
        changeBigImage(this);
    } else {
        enlargeImages(this);
    }
})

function allImages () {
    var images = document.getElementsByClassName('small-images');
    var t = new Array();
    for (i in images) {
        if (images[i].src) {
            t.push(images[i].src);
        }
        
    }
    maxI = t.length-1;
    return t;
}


$(document).on('click', '.left', function () {
    overImg.src = ima[pos-1]
    pos-=1;

    if (pos<0) {
        pos = maxI+1;
    }
})

$(document).on('click', '.right', function () {
    overImg.src = ima[pos+1]
    pos+=1;

    if (pos>maxI) {
        pos = -1;
    }
})

