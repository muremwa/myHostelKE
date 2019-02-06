$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});


window.images = document.getElementsByClassName('small-images');
// overview
var b = document.getElementsByTagName('body')[0];
var over = document.querySelector(".over-view");
var overImg = document.querySelector('#over-view-image');
var ima;
var pos;
var maxI;
var di;

$(document).on('click', '.close-js-over', function () {
    over.style.display = 'none';
    b.style.height = "";
    b.style.overflow = "scroll";
})

$(document).on('click', '.over-js-img', function () {
    document.getElementsByTagName('nav')[0].scrollIntoView();
    b.style.height = '100vh';
    b.style.overflow = 'hidden';
    di = document.querySelector('.danger-image');
    ima = allImages();
    for (image in ima) {
        if (this.src == ima[image]) {
            pos = ima.indexOf(ima[image]);
        }
    }
    overImg.src = this.src;
    over.style.display = "";
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

