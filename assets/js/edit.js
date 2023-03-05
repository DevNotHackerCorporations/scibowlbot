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
    for (let subject in Questions){
        for (let question of Questions[subject]){
            if (question.tossup_question.includes(query) || question.tossup_answer.includes(query) || question.id.toString() === query){
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
    while (count < 50){
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