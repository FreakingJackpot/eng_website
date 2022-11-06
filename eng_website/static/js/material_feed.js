let data
let topicsButton
let phrasebookButton
let articlesButton
let testsButton
let feedElementTemplate
let materialFeedList

$(document).ready(function () {
    let dataElement = document.getElementById('materials_by_sections')
    data = JSON.parse(dataElement.textContent)
    dataElement.remove()
    topicsButton = document.getElementById('topics-button')
    phrasebookButton = document.getElementById('phrasebook-button')
    articlesButton = document.getElementById('articles-button')
    testsButton = document.getElementById('tests-button')
    feedElementTemplate = document.getElementById("feed-item-template")
    materialFeedList = document.getElementById("material-feed-list")

    topicsButton.addEventListener('click', topicsHandler)
    phrasebookButton.addEventListener('click', phrasebookHandler)
    articlesButton.addEventListener('click', articlesHandler)
    testsButton.addEventListener('click', testsHandler)

    showFeedElements('topics', 'ТОПИК')
    topicsButton.className = 'tabs-link button-transparent active'

});

function topicsHandler(event) {
    showFeedElements('topics', 'ТОПИК')
    let currentActiveButton = document.querySelector('.tabs-link button-transparent active:first-child')
    currentActiveButton.className = 'tabs-link button-transparent'
    topicsButton.className = 'tabs-link button-transparent active'
}

function phrasebookHandler(event) {
    showFeedElements('phrasebook', 'РАЗГОВОРНИК')
    let currentActiveButton = document.querySelector('.tabs-link button-transparent active:first-child')
    currentActiveButton.className = 'tabs-link button-transparent'
    phrasebookButton.className = 'tabs-link button-transparent active'
}

function articlesHandler(event) {
    showFeedElements('articles', 'СТАТЬЯ')
    let currentActiveButton = document.querySelector('.tabs-link button-transparent active:first-child')
    currentActiveButton.className = 'tabs-link button-transparent'
    articlesButton.className = 'tabs-link button-transparent active'
}

function testsHandler(event) {
    showFeedElements('tests', 'ТЕСТ')
    let currentActiveButton = document.querySelector('.tabs-link button-transparent active:first-child')
    currentActiveButton.className = 'tabs-link button-transparent'
    testsButton.className = 'tabs-link button-transparent active'
}

function showFeedElements(section, ruSectionName) {
    let items = data[section]

    let feedElements = []

    items.forEach(function (feedItem, index) {
        let feedElement = feedElementTemplate.content.firstElementChild.cloneNode(true)
        feedElement.className += ' ' + section

        let header = feedElement.querySelector(".feed-item-header:first-child")
        header.style.backgroundImage = `url('${feedItem.img_url}')`

        let views = feedElement.querySelector(".activity-views:first-child")
        views.textContent = feedItem.views

        let link = feedElement.querySelector(".feed-item-content-link")
        link.href = feedItem.url

        let content = feedElement.querySelector(".feed-item-content:first-child")
        content.innerHTML = `<h4>${feedItem.title}</h4>`

        let tape = feedElement.querySelector(".info-tape:first-child")
        tape.href = `/${section}`
        tape.textContent = ruSectionName

        feedElements.push(feedElement)
    })

    materialFeedList.replaceChildren(...feedElements)
}

