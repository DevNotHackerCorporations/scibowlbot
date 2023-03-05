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
    page = 0
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
        }else{
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
            $("#results").append(`
            <div class="result">
                <h1>${question.category} - ${question.tossup_format}</h1>
                <b>${question.source} (ID: ${question.id})</b>
                <span>${question.tossup_question.replaceAll("\n", "<br>")}</span>
                <span><b>ANSWER: </b> ${question.tossup_answer}</span>
            </div>`)
            count++
        }
        $("#results").animate({scrollTop: 0}, "smooth")
    })

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