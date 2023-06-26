window.onload = async () => {
    await fetch_questions()
    await $("#focused_question").html(format_question(get_question_by_ID(Number(focused_question)), new Set(Stars)))
    apply_question_callbacks()
    $("#focused_detail_time span").html((new Date(Number($("#focused_detail_time span").html()+"000"))).toLocaleTimeString([], {year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'}))

    if (document.body.scrollWidth <= 900 && !isfullscreen || document.body.scrollWidth > 900 && isfullscreen){
        $("#focused_options_fullscreen").click()
    }
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