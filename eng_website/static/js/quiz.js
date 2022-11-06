let quiz
let startButton
let mainContent
let questionNumberElement
let questionTitle
let answerContentTemplate
let submitButton


class Quiz {
    constructor() {
        this.questions = JSON.parse(document.getElementById('quiz_questions').textContent)
        this.results = JSON.parse(document.getElementById('quiz_results').textContent)
        this.currentQuestion = 1
        this.score = 0
    }

    setNextQuestion() {
        this.currentQuestion++
    }

    getCurrentQuestion() {
        if (this.currentQuestion <= this.questions.length)
            return this.questions[this.currentQuestion - 1];

    }

    isQuizEnded() {
        return this.currentQuestion > this.questions.length
    }


    isAnswerCorrect(answerIndex) {
        return this.questions[this.currentQuestion - 1].answers[answerIndex].correct
    }

    updateScore() {
        this.score++
    }
}

function answerElementHandler(event) {
    let answerElement = event.target
    while (answerElement.getAttribute('answer') == null) {
        answerElement = answerElement.parentElement
    }

    let answerIndex = Number(answerElement.getAttribute('answer'))
    let correct = quiz.isAnswerCorrect(answerIndex)
    if (correct) {
        quiz.updateScore()
    }

    setAnswersIcons()
    submitButton.style.display = "inline"
}

function setAnswersIcons() {
    let answerIndex
    let iconElement
    let counter

    answers.childNodes.forEach(function (answerElement, index) {
        answerIndex = Number(answerElement.getAttribute('answer'))
        iconElement = answerElement.querySelector(".answer-icon")
        counter = answerElement.querySelector(".answer-counter")


        counter.textContent = null

        if (quiz.isAnswerCorrect(answerIndex)) {
            iconElement.className += ' fa fa-check'
        } else {
            iconElement.className += ' fa fa-times'
        }
    })

}

function submitButtonHandler(event) {
    quiz.setNextQuestion()
    if (quiz.isQuizEnded()) {
        showQuizResult()
    } else {
        showCurrentQuestion()
    }

}

function showQuizResult() {
    let resultContentTemplate = document.getElementById("test_result_template").content.firstElementChild.cloneNode(true)

    let resultElement = resultContentTemplate.querySelector('#your-result')
    resultElement.textContent += quiz.score

    let resultDescriptionElement = resultContentTemplate.querySelector('#description-result')
    let description
    for (const result of quiz.results) {
        if (result.max_value >= quiz.score && result.min_value <= quiz.score) {
            description = result.content
            break
        }
    }

    resultDescriptionElement.textContent = description

    mainContent.innerHTML = resultContentTemplate.innerHTML

}

function showCurrentQuestion() {
    let question = quiz.getCurrentQuestion()
    questionNumberElement.textContent = 'Вопрос ' + quiz.currentQuestion + '/' + quiz.questions.length
    questionTitle.textContent = question.content

    let answerElements = []

    submitButton.style.display = "none"


    question.answers.forEach(function (answer, index) {
        let answerElement = answerContentTemplate.content.firstElementChild.cloneNode(true)
        answerElement.setAttribute('answer', index)

        let counter = answerElement.querySelector(".answer-counter")
        counter.textContent = index + 1 + ')'

        let title = answerElement.querySelector(".answer-title:first-child")
        title.textContent = answer.content

        answerElement.addEventListener("click", answerElementHandler)

        answerElements.push(answerElement)
    })

    answers.replaceChildren(...answerElements)
}

function createAnswerTemplate() {
    let questionTemplate = document.getElementById("question-template").content.firstElementChild.cloneNode(true)
    mainContent.innerHTML = questionTemplate.innerHTML

    questionNumberElement = mainContent.querySelector('#question-number')
    questionTitle = mainContent.querySelector('#question-title')
    answers = mainContent.querySelector('#answers')
    answerContentTemplate = document.getElementById("answer-item-template")
    submitButton = document.getElementById('submit-button')
    submitButton.addEventListener('click', submitButtonHandler)
}


quiz = new Quiz()
startButton = document.getElementById('test-start')
mainContent = document.getElementById('main_content')

startButton.onclick = function start_quiz() {
    createAnswerTemplate()
    showCurrentQuestion()
}


