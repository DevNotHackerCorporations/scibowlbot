Questions = {}
Results = []
page = 0
results_per_page = 50
Stars = JSON.parse(localStorage.stars ?? "[]")
mode = "questions"

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

function abbreviations(subject){
    if (abbrev[subject]){
        return abbrev[subject]
    } else if (subject.startsWith("WEIRD")){
        return "weird"
    }
    return "crazy"
}

function toTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
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
        res = await res.json()
        Questions[subject] = res
    }
}

function search(query){
    Results = []
    query = query.toLowerCase()
    for (let subject in Questions){
        for (let question of Questions[subject]){
            if (question.tossup_question.toLowerCase().includes(query) || question.tossup_answer.toLowerCase().includes(query) || question.id.toString() === query){
                Results.push(question)
           }
        }
    }
    return Results
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

function format_question(question, stars){
    return `<div class="result${stars.has(question.id.toString()) ? ' starred' : ''}" data-id="${question.id}">
        <div class="result__data">
            <h1>${question.category} - ${question.tossup_format}</h1>
            <b>${question.source} (ID: ${question.id})</b>
            <span>${question.tossup_question.replaceAll("\n", "<br>")}</span>
            <span><b>ANSWER: </b> ${question.tossup_answer}</span>
        </div>
        <div class="result__btns">
            <div class="result__btn edit"><i class="fa-solid fa-pen-to-square"></i> Edit</div>
            <div class="result__btn star" data-id="${question.id}"><i class="fa-solid fa-star"></i> ${stars.has(question.id.toString()) ? 'Unstar' : 'Star'}</div>
        </div>
    </div>`
}

function search_stars(query){
    let Stars__search = new Set(Stars)
    Results = []
    query = query.toLowerCase()
    for (let subject in Questions){
        for (let i = 0; i < Questions[subject].length; i++){
            question = Questions[subject][i]
            if (
                Stars__search.has(question.id.toString())
                && (question.tossup_question.toLowerCase().includes(query)
                    || question.tossup_answer.toLowerCase().includes(query)
                    || question.id.toString() === query)){
                Results.push(question)
           }
        }
    }
    return Results
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

function search_and_display(query){
    let Stars__lookup = new Set(Stars);
    $("search__statistics").text("Searching...")
    $("#results").html("")
    page = 0
    let start = performance.now()
    if (mode === "stars"){
        search_stars(query)
    }else{
        search(query)
    }

    let count = 0
    while (count < results_per_page && count < Results.length){
        let question = Results[count]
        $("#results").append(format_question(question, Stars__lookup))
        count++
    }
    apply_question_callbacks()

    let amount = Math.ceil(Results.length / results_per_page)
    let res;
    if (amount <= 1){
        res = `<div class="page_link highlighted" data-goto="0">1</div>`
    }else{
        res = `<div id="next_page">
            <div class="page_link disabled" data-goto="prev"><i class="fa fa-angle-left"></i></div>
            <div class="page_link highlighted" data-goto="0">1</div>
            <div class="page_link" data-goto="1">2</div>`

        if (amount > 4){
            res += `<div class="page_link" data-goto="custom">...</div>`
        }
        if (amount === 3){
            res += `<div class="page_link" data-goto="2">3</div>`
        }
        else if (amount === 4){
            res += `<div class="page_link" data-goto="2">3</div>`
            res += `<div class="page_link" data-goto="3">4</div>`
        }else if (amount > 4){
            res += `<div class="page_link" data-goto="${amount - 2}">${amount - 1}</div>`
            res += `<div class="page_link" data-goto="${amount - 1}">${amount}</div>`
        }

        res += `<div class="page_link" data-goto="next"><i class="fa fa-angle-right"></i></div></div>`
    }

    $("#next_page").html(res)

    $(".page_link").click((e)=>{
        let element = $(e.currentTarget)
        if ((element.data("goto") ?? "").toString() === page.toString()){
            return
        }
        let goto = element.data("goto")
        let size = Math.ceil(Results.length / results_per_page)
        if (goto === "prev" && page !== 0){
            page -= 1
        }else if (goto === "next" && page !== size){
            page += 1
        }else if (goto === "custom"){
            let input = Number(prompt("Page Number"))
            if (1 <= input && input <= size){
                page = input - 1
            }
        }else{
            page = goto
        }

        $(".page_link").removeClass("highlighted disabled")

        if (page === 0 || page === 1 || page === size - 1 || page === size - 2){
            $(".page_link[data-goto="+page+"]").addClass("highlighted")
            $(".page_link[data-goto=custom]").html("...")
        }else{
            $(".page_link[data-goto=custom]").html(page + 1).addClass("highlighted")
        }

        if (page === 0){
            $(".page_link[data-goto=prev]").addClass("disabled")
        }
        if (page === size - 1){
            $(".page_link[data-goto=next]").addClass("disabled")
        }

        $("#results").html("")

        let count = page * results_per_page
        while (count < (page + 1) * results_per_page && count < Results.length){
            let question = Results[count]
            $("#results").append(format_question(question, Stars__lookup))
            count++
        }
        apply_question_callbacks()
        $("#results").animate({scrollTop: 0}, {duration: 0})
    })

    $("#search__statistics").text(`${Results.length} Result${Results.length === 1 ? "" : "s"} in ${((performance.now() - start)/1000).toFixed(3)} Seconds`)
}

$("#search").keyup((e)=>{
    if (e.key === "Enter"){
        search_and_display($("#search").val().trim())
    }
})

$("#search__button").click(()=>{search_and_display($("#search").val().trim())})

$("#toggle_questions").click(() => {
    if ($("#toggle_questions").data("mode") === "questions"){
        mode = "stars"
        search_and_display("")
        $("#toggle_questions").data("mode", "stars").html("Search All Questions")
    }else{
        mode = "questions"
        search_and_display("")
        $("#toggle_questions").data("mode", "questions").html("Search Starred Items")
    }
})

$(".close").click((e)=>{
    $(e.currentTarget).parent().parent().parent().toggle()
})

$("#edit__question_textarea").on("input", ()=>{
    $("#edit__question_textarea").css("height", "auto").height($("#edit__question_textarea").prop("scrollHeight"))
})

$("#edit__save").click(()=>{
    $("#edit__wrapper").hide()
})

// Disord message config stuff
window.$discordMessage = {
	profiles: {
		user: {
			author: 'Discord User',
			avatar: 'green',
		},
		scibowlbot: {
			author: 'scibowlbot',
			avatar: './assets/scibowlbot.png',
			bot: true,
			roleColor: '#ee82ee',
		},
	},
}

window.onload = ()=>{
    fetch_questions()
}