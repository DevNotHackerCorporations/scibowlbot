$(".close").click((e)=>{
    $(e.currentTarget).parent().parent().parent().toggle()
})

$("#edit__question_textarea").on("input", ()=>{
    $("#edit__question_textarea").css("height", "auto").height($("#edit__question_textarea").prop("scrollHeight"))
})

$("#edit__save").click(()=>{
    $("#edit__wrapper").hide()
})