/*
Over view js logic for the file '../templates/home/over_view.html'
*/

const imageDivs =[... document.getElementsByClassName("over-js-img")];
const overViewImage = document.getElementById("over-view-image");
const body = document.getElementsByTagName("body")[0];
let images;
let count = 0;
let position;



function collectAllImages (start) {
    /*
    collect urls for all images (main and other hostel and room images)
    */
    let images = imageDivs.map(element => element.src);
    const startIndex = images.findIndex(source => source === start);

    // the image shall now start with the image clicked then others follow
    images = images.concat(
        // remove all src(s) that come before startSource and put the at the end of the array
        images.splice(0, startIndex)
    );
    
    return images;
};


function closeOverView() {
    /*
    Closes the over view
    */
    document.getElementById("over-main").style.display = "none";
    document.documentElement.scrollTop = position;
    body.style.height = "";
    body.style.overflow = "";
    count = 0;
};


function addImageToOverView(prev) {
    /*
    change the src attribute of the overall image
    */
    const imageSource = prev? images[count - 1]: images[count + 1];

    if (imageSource !== undefined) {
        overViewImage.src = imageSource;
        count = prev? count - 1: count + 1;
    } else {
        // if you get to the end of the array of images, cycle back to the other end
        if (prev) {
            count = images.length;
        } else {
            count = -1;            
        }
        addImageToOverView(prev);
    }
};


function nextImage(e) {
    /* 
    display the next image
    */
    if (count < images.length) {
        addImageToOverView(false);
    }
};


function previousImage(e) {
    /* 
    display the previous image
    */
    if (count > -1) {
        addImageToOverView(true);
    }

};


function startOverView(e) {
    /*
    Main event to show images
    */


    // remember position on page
    position = pageYOffset;
    // scroll to top of the page
    document.documentElement.scrollTop = 0;

    // show the over view pane
    const overViewPane = document.getElementById("over-main");
    overViewPane.style.display = "";
    body.style.height = "100vh";
    body.style.overflow = "hidden";


    // activate close button
    document.getElementById("close-over-view").addEventListener('click', closeOverView);

    images = collectAllImages(e.target.src);
    overViewImage.src = images[count];

    // activate next image button
    document.getElementById("next-image").addEventListener('click', nextImage);

    // activate previous image button
    document.getElementById("previous-image").addEventListener('click', previousImage);
};


// add a click listener to all imageDivs
imageDivs.forEach(div => div.addEventListener('click', startOverView));
