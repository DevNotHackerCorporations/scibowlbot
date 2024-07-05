window.onload = async () => {
    await fetch_questions()

    if (document.body.scrollWidth <= 900 && !isfullscreen || document.body.scrollWidth > 900 && isfullscreen){
        $("#focused_options_fullscreen").click()
    }

    await render_suggestion(suggestion_name)
}

const render_suggestion = async (name) => {
    console.log("rendering", name)
    let suggestion = issues_list[name]

    if (suggestion.open) {
        document.querySelector("#change_status_open").selected = true
    }else{
        document.querySelector("#change_status_closed").selected = true
    }

    document.querySelector("#focused_id").innerText = name
    document.querySelector("#focused_detail_time").innerText = (new Date(suggestion.filed*1000))
        .toLocaleTimeString([], {year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'})
    document.querySelector("#detail__reported_name").innerText = suggestion.sender_name
    document.querySelector("#detail__reported_name").setAttribute("data-content", suggestion.sender_name)
    document.querySelector("#detail__reported_id").innerText = suggestion.sender_id
    document.querySelector("#detail__reported_id").setAttribute("data-content", suggestion.sender_id)
    document.querySelector("#detail__question_id").innerText = "#" + suggestion.question_id
    document.querySelector("#detail__response").setAttribute("data-content", suggestion.response || "<No Response Given>")
    document.querySelector("#detail__response").innerText = suggestion.response || "<No Response Given>"

    document.querySelector("#focused_question").innerHTML = format_question(get_question_by_ID(suggestion.question_id), new Set(Stars), suggestion.response)
    await apply_question_callbacks()
}

window.onresize = () =>{
    if (document.body.scrollWidth <= 900 && !isfullscreen || document.body.scrollWidth > 900 && isfullscreen){
        $("#focused_options_fullscreen").click()
    }
}


let isfullscreen = false;
$("#focused_options_fullscreen").click(()=>{
    $("body").toggleClass("hide")
    if (isfullscreen){
        $("#focused_options_fullscreen i").addClass("fa-up-right-and-down-left-from-center").removeClass("fa-down-left-and-up-right-to-center")
    }else{
        $("#focused_options_fullscreen i").removeClass("fa-up-right-and-down-left-from-center").addClass("fa-down-left-and-up-right-to-center")
    }
    isfullscreen = !isfullscreen
})

$("code").click((e)=>{
    navigator.clipboard.writeText($(e.currentTarget).data("content"))
    setTimeout(()=>{alert("Copied to clipboard")}, 100)
})

$("#change_status").change(async ()=>{
    let raw_response = await fetch("/suggestions/api/toggle_status", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({target: suggestion_name})
    })
    location.reload()
})