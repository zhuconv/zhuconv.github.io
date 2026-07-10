/*==================== MENU SHOW Y HIDDEN ====================*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/*===== MENU SHOW =====*/
/* Validate if constant exists */
if(navToggle){
    navToggle.addEventListener('click', () =>{
        navMenu.classList.add('show-menu')
    })
}

/*===== MENU HIDDEN =====*/
/* Validate if constant exists */
if(navClose){
    navClose.addEventListener('click', () =>{
        navMenu.classList.remove('show-menu')
    })
}

/*==================== REMOVE MENU MOBILE ====================*/
const navLink = document.querySelectorAll('.nav__link')

function linkAction(){
    const navMenu = document.getElementById('nav-menu')
    // When we click on each nav__link, we remove the show-menu class
    navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))

/*==================== PUBLICATIONS ====================*/

// from: http://www.robots.ox.ac.uk/~vedaldi/assets/hidebib.js
function hideallbibs()
{
    var el = document.getElementsByTagName("div") ;
    for (var i = 0 ; i < el.length ; ++i) {
        if (el[i].className == "paper") {
            var bib = el[i].getElementsByTagName("pre") ;
            if (bib.length > 0) {
                bib [0] .style.display = 'none' ;
            }
        }
    }
}

function togglebib(paperid)
{
    var paper = document.getElementById(paperid) ;
    var bib = paper.getElementsByTagName('pre') ;
    if (bib.length > 0) {
        if (bib [0] .style.display == 'none') {
            bib [0] .style.display = 'block' ;
        } else {
            bib [0] .style.display = 'none' ;
        }
    }
}

function toggleblock(blockId)
{
   var block = document.getElementById(blockId);
   if (block.style.display == 'none') {
    block.style.display = 'block' ;
   } else {
    block.style.display = 'none' ;
   }
}

function hideblock(blockId)
{
   var block = document.getElementById(blockId);
   block.style.display = 'none' ;
}

/*==================== PAPER TEASER ASPECT PADDING ====================*/
function initTeaserAspectPadding()
{
    var teaserImages = document.querySelectorAll('.research__content-teaser img');
    var targetRatio = 1;
    var ratioTolerance = 0.02;

    function markPaddingDirection(image)
    {
        if (!image.naturalWidth || !image.naturalHeight) {
            return;
        }

        var teaser = image.closest('.research__content-teaser');
        if (!teaser) {
            return;
        }

        var imageRatio = image.naturalWidth / image.naturalHeight;
        var paddingDirection = 'none';

        if (imageRatio > targetRatio + ratioTolerance) {
            paddingDirection = 'vertical';
        } else if (imageRatio < targetRatio - ratioTolerance) {
            paddingDirection = 'horizontal';
        }

        teaser.setAttribute('data-padding', paddingDirection);
    }

    teaserImages.forEach(function(image) {
        if (image.complete) {
            markPaddingDirection(image);
        } else {
            image.addEventListener('load', function() {
                markPaddingDirection(image);
            }, { once: true });
        }
    });
}

/*==================== IMAGE LIGHTBOX ====================*/
function initImageLightbox()
{
    var zoomImages = document.querySelectorAll('.research__content-teaser img, .paper__section-grid img, .js-image-zoom');
    if (!zoomImages.length) {
        return;
    }

    var lightbox = document.createElement('div');
    lightbox.className = 'image-lightbox';
    lightbox.setAttribute('role', 'dialog');
    lightbox.setAttribute('aria-modal', 'true');
    lightbox.setAttribute('aria-label', 'Enlarged image');
    lightbox.innerHTML =
        '<button class="image-lightbox__close" type="button" aria-label="Close enlarged image">&times;</button>' +
        '<figure class="image-lightbox__figure">' +
            '<img class="image-lightbox__image" alt="">' +
            '<figcaption class="image-lightbox__caption"></figcaption>' +
        '</figure>';

    document.body.appendChild(lightbox);

    var lightboxImage = lightbox.querySelector('.image-lightbox__image');
    var lightboxCaption = lightbox.querySelector('.image-lightbox__caption');
    var closeButton = lightbox.querySelector('.image-lightbox__close');
    var activeTrigger = null;

    function openLightbox(image)
    {
        activeTrigger = image;
        lightboxImage.src = image.currentSrc || image.src;
        lightboxImage.alt = image.alt || '';
        lightboxCaption.textContent = image.alt || '';
        lightbox.classList.add('is-open');
        document.body.classList.add('image-lightbox-open');
        closeButton.focus();
    }

    function closeLightbox()
    {
        lightbox.classList.remove('is-open');
        document.body.classList.remove('image-lightbox-open');
        lightboxImage.removeAttribute('src');

        if (activeTrigger) {
            activeTrigger.focus();
            activeTrigger = null;
        }
    }

    zoomImages.forEach(function(image) {
        image.classList.add('js-image-zoom');

        if (!image.hasAttribute('tabindex')) {
            image.tabIndex = 0;
        }

        if (!image.hasAttribute('role')) {
            image.setAttribute('role', 'button');
        }

        if (!image.hasAttribute('title')) {
            image.setAttribute('title', 'Click to enlarge');
        }

        image.addEventListener('click', function() {
            openLightbox(image);
        });

        image.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openLightbox(image);
            }
        });
    });

    closeButton.addEventListener('click', closeLightbox);

    lightbox.addEventListener('click', function(event) {
        if (event.target === lightbox) {
            closeLightbox();
        }
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && lightbox.classList.contains('is-open')) {
            closeLightbox();
        }
    });
}

initTeaserAspectPadding();
initImageLightbox();
