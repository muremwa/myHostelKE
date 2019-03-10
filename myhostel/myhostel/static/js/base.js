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
var leftButton = document.querySelector('.left');
var rightButton = document.querySelector('.right');

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
    console.log(pos);
    overImg.src = i.src;
    over.style.display = "";
    if (pos==maxI) {
        rightButton.style.visibility = 'hidden';
        leftButton.style.visibility = 'visible';
    } else if (pos==0) {
        leftButton.style.visibility = 'hidden';
        rightButton.style.visibility = 'visible';
    } else {
        leftButton.style.visibility = 'visible';
        rightButton.style.visibility = 'visible';
    }
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

    if (pos==0) {
        this.style.visibility = 'hidden';
    }
    if (pos<maxI) {
        rightButton.style.visibility = 'visible';
    }
})

$(document).on('click', '.right', function () {
    overImg.src = ima[pos+1]
    pos+=1;

    if (pos==maxI) {
        this.style.visibility = "hidden";
    }
    if (pos>0) {
        leftButton.style.visibility = 'visible'
    }
})

