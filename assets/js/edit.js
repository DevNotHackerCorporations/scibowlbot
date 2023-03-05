Questions = {}
Results = []
page = 0
results_per_page = 50

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

function search_and_display(query){
    if (!query){
        return
    }
    $("search__statistics").text("Searching...")
    $("#results").html("")
    let start = performance.now()
    search(query)

    let count = 0
    while (count < results_per_page && count < Results.length){
        let question = Results[count]
        $("#results").append(`
        <div class="result">
            <h1>${question.category} - ${question.tossup_format}</h1>
            <b>${question.source} (ID: ${question.id})</b>
            <span>${question.tossup_question.replaceAll("\n", "<br>")}</span>
            <span><b>ANSWER: </b> ${question.tossup_answer}</span>
        </div>`)
        count++
    }

    let amount = Math.ceil(Results.length / results_per_page)
    if (amount < 1){
        $("#results").append(`<div id="next_page"><div class="page_link highlighted" data-goto="0">1</div></div>`)
    }else{
        let res = `<div id="next_page">
            <div class="page_link"><i class="fa fa-angle-left" id="next_page_PREV"></i></div>
            <div class="page_link" data-goto="0">1</div>
            <div class="page_link" data-goto="1">2</div>`

            if (amount > 4){
                res += `<div class="page_link" id="next_page_CUSTOM">...</div>`
            }
            if (amount === 3){
                res += `<div class="page_link" data-goto="2">3</div>`
            }
            else if (amount === 4){
                res += `<div class="page_link" data-goto="2">3</div>`
                res += `<div class="page_link" data-goto="3">4</div>`
            }else{
                res += `<div class="page_link" data-goto="${amount - 2}">${amount - 1}</div>`
                res += `<div class="page_link" data-goto="${amount - 1}">${amount}</div>`
            }

        res += `<div class="page_link"><i class="fa fa-angle-right" id="next_page_NEXT"></i></div></div>`
        $("#results").append(res)
    }

    $("#search__statistics").text(`${Results.length} Result${Results.length === 1 ? "" : "s"} in ${((performance.now() - start)/1000).toFixed(3)} Seconds`)
}

$("#search").keyup((e)=>{
    if (e.key === "Enter"){
        search_and_display($("#search").val().trim())
    }
})

$("#search__button").click(()=>{search_and_display($("#search").val().trim())})

window.onload = ()=>{
    fetch_questions()
}