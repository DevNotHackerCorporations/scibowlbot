CURRENT_SUGGESTION = suggestion_name || localStorage.CURRENT_SUGGESTION || ""
CURRENT_NUM = 0

window.onload = async () => {
    await fetch_questions()

    if (document.body.scrollWidth <= 900 && !isfullscreen || document.body.scrollWidth > 900 && isfullscreen){
        $("#focused_options_fullscreen").click()
    }

    if (CURRENT_SUGGESTION){
        await render_suggestion(CURRENT_SUGGESTION)
    }else{
        await document.querySelector("#issues_list").children[0].onclick()
    }
}

const render_suggestion = async (name) => {
    document.querySelector("#issue_list_" + CURRENT_SUGGESTION).scrollIntoView()
    document.querySelectorAll(".highlighted").forEach(e=>e.classList.remove("highlighted"))
    document.querySelector("#issue_list_" + name).classList.add("highlighted")


    CURRENT_NUM = IDS.indexOf(name) + 1
    document.querySelector("#focused_info span").innerText = CURRENT_NUM

    CURRENT_SUGGESTION = name
    localStorage.CURRENT_SUGGESTION = CURRENT_SUGGESTION
    console.log("rendering", name)
    let suggestion = issues_list[name]

    if (suggestion.open) {
        document.querySelector("#change_status_open").selected = true
        document.querySelector("#change_status").classList.add("open")
        document.querySelector("#change_status").classList.remove("close")
    }else{
        document.querySelector("#change_status_closed").selected = true
        document.querySelector("#change_status").classList.add("close")
        document.querySelector("#change_status").classList.remove("open")
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

    document.querySelector("#discussion_messages").innerHTML = ""

    for (let message of suggestion.discussion){
        document.querySelector("#discussion_messages").innerHTML += render_message(message)
    }
}

const render_message = (message) => {
    return `
        <div class="message">
            <div class="left">
                <img src="${get_avatar_link(message["avatar"], message["name"], message["id"])}" width="40" height="40"
                data-avatar="${message["avatar"]}" data-name="${message["name"]}" data-id="${message["id"]}"
                onerror="error(this)">
            </div>
            <div class="right">
                <div class="desc">
                    <div class="author">${message.name}</div>
                    <div class="time">${(new Date(Number(message.time * 1000)))
        .toLocaleTimeString([], {year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'})}</div>
                </div>
                <div class="content">
                    ${message.message}
                </div>
            </div>
        </div>
    `
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

$("#change_status").change(()=>{
    let raw_response = fetch("/suggestions/api/toggle_status", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({target: CURRENT_SUGGESTION})
    })

    issues_list[CURRENT_SUGGESTION].open = !issues_list[CURRENT_SUGGESTION].open
    render_suggestion(CURRENT_SUGGESTION)
})

document.querySelector("#add_discussion input").onkeydown = async (e) => {
    console.log(e)
    if (e.key !== "Enter"){
        return
    }


    document.querySelector("#add_discussion input").disabled = true
    let message = document.querySelector("#add_discussion input").value
    document.querySelector("#add_discussion input").value = ""

    let raw_response = await fetch("/suggestions/api/add_discussion", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: CURRENT_SUGGESTION,
            name: me.global_name,
            avatar: me.avatar,
            user_id: me.id,
            message: message
        })
    })

    let response = await raw_response.json()

    issues_list[CURRENT_SUGGESTION].discussion.push(response)
    document.querySelector("#discussion_messages").innerHTML += render_message(response)
    document.querySelector("#add_discussion input").disabled = false
}

const get_avatar_link = (avatar, name, id, force=false) => {
    if (avatar && avatar !== " /" && !force){
        return `https://cdn.discordapp.com/avatars/${ id }/${ avatar }.png`
    }
    else{
        if (name.includes("#") && name.split("#").at(-1) !== 0){
            return `https://cdn.discordapp.com/embed/avatars/${Number(name.split("#").at(-1)) % 5}.png`
        }
        else{
            return `https://cdn.discordapp.com/embed/avatars/${(BigInt(id) >> 22n) % 6n}.png` // BigInt weirdness
        }
    }
}

const error = (element) => {
    element.removeEventListener("onerror", element.onerror)
    element.src = get_avatar_link(element.getAttribute("data-avatar"), element.getAttribute("data-name"), element.getAttribute("data-id"), true)
}

document.querySelector("#focused_options_up").onclick = () => {
    if (CURRENT_NUM >= IDS.length){
        return
    }

    render_suggestion(IDS[CURRENT_NUM])
}

document.querySelector("#focused_options_down").onclick = () => {
    if (CURRENT_NUM <= 1){
        return
    }

    render_suggestion(IDS[CURRENT_NUM - 2])
}