let quiz;

class Quiz {
    constructor(questions) {
        this.questions = questions
        this.current_question = 1
        this.score = 0
        this.headerContainer = document.querySelector('.question-title')
        this.listContainer = document.querySelector('#answer-list')
    }
}


