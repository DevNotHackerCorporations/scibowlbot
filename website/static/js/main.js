Questions = {}
Stars = JSON.parse(localStorage.stars ?? "[]")

abbrev = {
    "ASTRONOMY": "astro",
    "BIOLOGY": "bio",
    "CHEMISTRY": "chem",
    "CRAZY": "crazy",
    "COMPUTER SCIENCE": "cs",
    "EARTH AND SPACE": "eas",
    "ENERGY": "energy",
    "EARTH SCIENCE": "es",
    "GENERAL SCIENCE": "gen",
    "MATH": "math",
    "PHYSICS": "phy",
    "WEIRD": "weird"
}

emoji = {
    "phy": "🍎",
    "gen": "🧪",
    "energy": "⚡",
    "eas": "🌃",
    "chem": "⚛",
    "bio": "🧬",
    "astro": "🪐",
    "math": "🔢",
    "es": "🌎",
    "cs": "💻",
    "weird": "🙃",
    "crazy": "😝"
}

function abbreviations(subject){
    if (abbrev[subject]){
        return abbrev[subject]
    } else if (subject.startsWith("WEIRD")){
        return "weird"
    }
    return "crazy"
}

function getCookie(c_name) {
    let c_value = " " + document.cookie;
    let c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start === -1) {
        c_value = null;
    }
    else {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end === -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start,c_end));
    }
    return c_value;
}

String.prototype.toCapitalCase = function () {
    return this.toLowerCase().split(" ").map(word => word[0].toUpperCase() + word.substring(1)).join(" ")
}

Stars.push = function(data) { // override is awesome
  Array.prototype.push.call(this, data);
  localStorage.stars = JSON.stringify(this)
  return this
}

Stars.clear = function(){
    this.length = 0
    localStorage.stars = "[]"
}

Stars.remove = function(id){
    let index = Stars.indexOf(id);
    if (index === -1){
        return false
    }
    Stars.splice(index, 1);
    localStorage.stars = JSON.stringify(this)
    return true;
}

async function fetch_questions(){
    for (let subject of ["astro", "bio", "chem", "crazy", "cs", "eas", "energy", "es", "gen", "math", "phy", "weird"]){
        let res = await fetch(`https://raw.githubusercontent.com/DevNotHackerCorporations/scibowlbot/main/questions/${subject}.json`)
        //let res = await fetch(`/questions/${subject}.json`)
        res = await res.json()
        Questions[subject] = res
    }
}

function apply_question_callbacks(){
    $(".result__btn.star").click((e)=>{
        let element = $(e.currentTarget)
        let id = element.data("id").toString()
        if (element.text() === " Star"){
            Stars.push(id)
            element.html("<i class=\"fa-solid fa-star\"></i> Unstar")
            element.parent().parent().addClass("starred")
        }else{
            Stars.remove(id)
            element.html("<i class=\"fa-solid fa-star\"></i> Star")
            element.parent().parent().removeClass("starred")
        }
    })
    $(".result__btn.edit").click((e)=>{
        let element = $(e.currentTarget)
        let id = element.parent().parent().data("id")
        let question = get_question_by_ID(id)

        $("#edit__wrapper").show()
        $("#edit__invoke_subject").html(abbreviations(question.category))
        $("#edit__question_subject").val(abbreviations(question.category))
        $("#edit__question_type").val(question.tossup_format)
        $("#edit__question_textarea").val(question.tossup_question).height($("#edit__question_textarea").prop("scrollHeight"))
        $("#edit__answer_textarea").html(question.tossup_answer)
        $("#edit__source").html(question.source)
        $("#edit__embed").attr("embed-title", "Question ID: " + id)
    })
}

function format_question(question, stars, user=""){
    let user_formatted = ""
    if (user){
        user_formatted = `<span><b>USER ANSWER: </b> <code data-content="${user}">${user}</code> </span>`
    }

    return `<div class="result${stars.has(question.id.toString()) ? ' starred' : ''}" data-id="${question.id}">
        <div class="result__data">
            <h1>${question.category} - ${question.tossup_format}</h1>
            <b>${question.source} (ID: ${question.id})</b>
            <span>${question.tossup_question.replaceAll("\n", "<br>")}</span>
            <span><b>ANSWER: </b> ${question.tossup_answer}</span>${user_formatted}
        </div>
        <div class="result__btns">
            <div class="result__btn edit"><i class="fa-solid fa-pen-to-square"></i> Edit</div>
            <div class="result__btn star" data-id="${question.id}"><i class="fa-solid fa-star"></i> ${stars.has(question.id.toString()) ? 'Unstar' : 'Star'}</div>
        </div>
    </div>`
}

function get_question_by_ID(id){
    id = id.toString()
    for (let subject in Questions){
        for (let question of Questions[subject]){
            if (question.id.toString() === id){
                return question
            }
        }
    }
    return {}
}

class SelectMenu{
    constructor (options, selected, selector) {
        this.options = options
        this.selected = selected
        this.selector = selector

        $(`${this.selector} .select_title`).click(()=>{
            $(`${this.selector} .select_body`).attr("tabindex", "0").focus()
        })

        let obj = this;

        $(`${this.selector} .select_select_all`).click(()=>{
            obj.selected = Object.keys(obj.options)
            localStorage.filters = JSON.stringify(obj.selected)
            obj.reconstruct()
        })

        $(`${this.selector} .select_deselect_all`).click(()=>{
            obj.selected = []
            localStorage.filters = JSON.stringify(obj.selected)
            obj.reconstruct()
        })

        this.reconstruct()
    }

    reconstruct(){
        $(`${this.selector} .select_selected, ${this.selector} .select_body_container`).html("")

        for (let option of this.selected){
            $(`${this.selector} .select_selected`).append(`<div class="selected_option" data-value="${this.options[option].value}">${this.options[option].emoji}</div>`)
        }

        for (let option of Object.values(this.options)){
            $(`${this.selector} .select_body_container`).append(`<div data-value="${option.value}" class="option ${this.selected.includes(option.value) ? 'selected' : ''}"><div class="emoji_container">${option.emoji}</div> <div class="title">${option.name.toCapitalCase()}</div> <div class="check"><i class="fa-solid fa-circle-check"></i></div></div>`)
        }

        let obj = this

        $(`${this.selector} .select_body_container .option`).click((e)=>{
            let value = $(e.currentTarget).data("value")

            if (obj.selected.includes(value)){
                obj.selected.splice(obj.selected.indexOf(value), 1)
            }else{
                obj.selected.push(value)
            }

            localStorage.filters = JSON.stringify(obj.selected)

            obj.selected.sort()
            obj.reconstruct()
        })

        twemoji.parse(document.querySelector(this.selector))
    }
}

class Option{
    constructor (emoji, name, value) {
        this.emoji = emoji
        this.name = name
        this.value = value
    }
}