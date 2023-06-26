Results = []
page = 0
results_per_page = 50
mode = "questions"

function search(query){
    Results = []
    query = query.toLowerCase()
    for (let subject of filters.selected){
        for (let question of Questions[subject]){
            if (question.tossup_question.toLowerCase().includes(query) || question.tossup_answer.toLowerCase().includes(query) || question.id.toString() === query){
                Results.push(question)
           }
        }
    }
    return Results
}

function search_stars(query){
    let Stars__search = new Set(Stars)
    Results = []
    query = query.toLowerCase()
    for (let subject of filters.selected){
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

    $("#search__statistics").html(`${Results.length} Result${Results.length === 1 ? "" : "s"} in ${((performance.now() - start)/1000).toFixed(3)} Seconds<br>${results_per_page} results per page`)
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
        $("#toggle_questions").data("mode", "stars").html("<i class=\"fa-solid fa-earth-americas\"></i> Search All Questions")
    }else{
        mode = "questions"
        search_and_display("")
        $("#toggle_questions").data("mode", "questions").html("<i class=\"fa-solid fa-star\"></i> Search Starred Items")
    }
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
			avatar: '../static/scibowlbot.png',
			bot: true,
			roleColor: '#ee82ee',
		},
	},
}

let filters;
let userdata;

window.onload = ()=>{
    fetch_questions()

    let options = {}

    for (let option in abbrev){
        options[abbrev[option]] = new Option(emoji[abbrev[option]], option, abbrev[option])
    }

    let selected = JSON.parse(localStorage.filters ?? JSON.stringify(Object.values(abbrev)))

    filters = new SelectMenu(options, selected, "#filter_subjects")
}