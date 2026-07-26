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

/*==================== LIGHT / DARK THEME ====================*/
const themeToggle = document.getElementById('theme-toggle'),
      themeIcon = themeToggle ? themeToggle.querySelector('i') : null,
      themeMedia = window.matchMedia('(prefers-color-scheme: dark)'),
      themeStorageKey = 'homepage-theme'

function getSavedTheme(){
    try {
        const theme = localStorage.getItem(themeStorageKey)
        return theme === 'light' || theme === 'dark' ? theme : null
    } catch (_) {
        return null
    }
}

function saveTheme(theme){
    try {
        localStorage.setItem(themeStorageKey, theme)
    } catch (_) {}
}

function applyTheme(theme){
    const isDark = theme === 'dark'
    document.documentElement.dataset.theme = isDark ? 'dark' : 'light'

    if(themeToggle && themeIcon){
        const label = isDark ? 'Switch to light mode' : 'Switch to dark mode'
        themeIcon.classList.toggle('uil-sun', isDark)
        themeIcon.classList.toggle('uil-moon', !isDark)
        themeToggle.setAttribute('aria-label', label)
        themeToggle.title = label
    }
}

applyTheme(document.documentElement.dataset.theme)

if(themeToggle){
    themeToggle.addEventListener('click', () => {
        const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'
        applyTheme(nextTheme)
        saveTheme(nextTheme)
    })
}

function followSystemTheme(event){
    if(!getSavedTheme()){
        applyTheme(event.matches ? 'dark' : 'light')
    }
}

if(themeMedia.addEventListener){
    themeMedia.addEventListener('change', followSystemTheme)
} else if(themeMedia.addListener){
    themeMedia.addListener(followSystemTheme)
}

/*==================== PAPER IMAGE LIGHTBOX ====================*/
function initPaperImageLightbox(){
    const paperImages = document.querySelectorAll(
        '.research__content-teaser img, .paper__section-grid img, .js-image-zoom'
    )

    if(!paperImages.length){
        return
    }

    const lightbox = document.createElement('div')
    lightbox.className = 'image-lightbox'
    lightbox.setAttribute('role', 'dialog')
    lightbox.setAttribute('aria-modal', 'true')
    lightbox.setAttribute('aria-label', 'Enlarged paper image')
    lightbox.setAttribute('aria-hidden', 'true')
    lightbox.innerHTML = `
        <button class="image-lightbox__close" type="button" aria-label="Close enlarged image" title="Close">
            <i class="uil uil-times" aria-hidden="true"></i>
        </button>
        <figure class="image-lightbox__figure">
            <img class="image-lightbox__image" alt="">
            <figcaption class="image-lightbox__caption"></figcaption>
        </figure>
    `
    document.body.appendChild(lightbox)

    const enlargedImage = lightbox.querySelector('.image-lightbox__image')
    const caption = lightbox.querySelector('.image-lightbox__caption')
    const closeButton = lightbox.querySelector('.image-lightbox__close')
    let sourceImage = null

    function openLightbox(image){
        sourceImage = image
        enlargedImage.src = image.currentSrc || image.src
        enlargedImage.alt = image.alt
        caption.textContent = image.title || image.alt
        caption.hidden = !caption.textContent
        lightbox.classList.add('is-open')
        lightbox.setAttribute('aria-hidden', 'false')
        document.body.classList.add('image-lightbox-open')
        closeButton.focus()
    }

    function closeLightbox(){
        if(!lightbox.classList.contains('is-open')){
            return
        }

        lightbox.classList.remove('is-open')
        lightbox.setAttribute('aria-hidden', 'true')
        document.body.classList.remove('image-lightbox-open')
        enlargedImage.removeAttribute('src')

        if(sourceImage){
            sourceImage.focus()
            sourceImage = null
        }
    }

    paperImages.forEach(image => {
        image.classList.add('paper-image-zoom')
        image.tabIndex = 0
        image.setAttribute('role', 'button')
        image.setAttribute('aria-haspopup', 'dialog')
        image.addEventListener('click', () => openLightbox(image))
        image.addEventListener('keydown', event => {
            if(event.key === 'Enter' || event.key === ' '){
                event.preventDefault()
                openLightbox(image)
            }
        })
    })

    closeButton.addEventListener('click', closeLightbox)
    lightbox.addEventListener('click', event => {
        if(event.target === lightbox){
            closeLightbox()
        }
    })
    document.addEventListener('keydown', event => {
        if(event.key === 'Escape'){
            closeLightbox()
        }
    })
}

initPaperImageLightbox()

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
   if (block) {
       block.style.display = 'none' ;
   }
}
